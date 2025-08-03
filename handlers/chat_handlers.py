#!/usr/bin/env python3
"""
Chat handlers for Telegram Anonymous Chat Bot
"""
import logging
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from config import GENDERS, HOBBIES
from database import (
    find_partner, add_to_queue, remove_from_queue, create_chat_session,
    end_chat_session, is_in_chat, get_chat_partner, is_profile_complete,
    is_user_pro, get_user_profile, cleanup_expired_queues
)
from handlers.decorators import check_ban_status, auto_update_profile, require_profile
from utils.keyboards import get_main_menu, get_chat_menu

logger = logging.getLogger(__name__)

@check_ban_status
@auto_update_profile
async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start chat command - find partner or join queue"""
    user_id = update.effective_user.id
    
    # Check if user is already in chat
    if is_in_chat(user_id):
        await update.message.reply_text(
            "❗ Kamu sudah dalam chat. Gunakan /stop untuk mengakhiri chat terlebih dahulu."
        )
        return
    
    # Check if profile is complete
    if not is_profile_complete(user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Lengkapi Profil", callback_data="complete_profile")],
            [InlineKeyboardButton("Lanjutkan & Cari Acak", callback_data="skip_profile")]
        ])
        await update.message.reply_text(
            "👋 Selamat datang di Anonymous Chat!\nProfilmu belum lengkap.",
            reply_markup=keyboard
        )
        return
    
    await start_partner_search(update, context)

async def start_partner_search(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                             gender_pref=None, hobby_pref=None, age_min=None, age_max=None):
    """Start searching for a chat partner"""
    user_id = update.effective_user.id
    
    # Clean up expired queue entries first
    cleanup_expired_queues()
    
    # Try to find an available partner
    partner_id = find_partner(user_id, gender_pref, hobby_pref, age_min, age_max)
    
    if partner_id:
        # Partner found - create chat session
        create_chat_session(user_id, partner_id)
        
        # Notify both users
        await update.message.reply_text(
            "🎉 Partner ditemukan! Chat dimulai.\n"
            "Gunakan /stop untuk mengakhiri chat atau /next untuk mencari partner baru.",
            reply_markup=get_chat_menu()
        )
        
        try:
            await context.bot.send_message(
                partner_id,
                "🎉 Partner ditemukan! Chat dimulai.\n"
                "Gunakan /stop untuk mengakhiri chat atau /next untuk mencari partner baru.",
                reply_markup=get_chat_menu()
            )
        except Exception as e:
            logger.error(f"Failed to notify partner {partner_id}: {e}")
            # If we can't notify partner, end the session
            end_chat_session(user_id)
            await update.message.reply_text(
                "❌ Gagal menghubungi partner. Silakan coba lagi.",
                reply_markup=get_main_menu()
            )
            return
        
        logger.info(f"Chat session created between {user_id} and {partner_id}")
    else:
        # No partner found - add to queue
        is_pro = is_user_pro(user_id)
        add_to_queue(user_id, gender_pref, hobby_pref, age_min, age_max, is_pro)
        
        pref_text = ""
        if gender_pref:
            pref_text += f"\n• Gender: {gender_pref}"
        if hobby_pref:
            pref_text += f"\n• Hobi: {hobby_pref}"
        if age_min and age_max:
            pref_text += f"\n• Umur: {age_min}-{age_max}"
        
        await update.message.reply_text(
            f"🔍 Mencari partner...{pref_text}\n"
            f"{'✨ Mode Pro aktif' if is_pro else ''}\n\n"
            "Kamu akan dinotifikasi ketika partner ditemukan. "
            "Gunakan /stop untuk membatalkan pencarian.",
            reply_markup=get_main_menu()
        )
        
        # Start background task to find partner
        asyncio.create_task(background_partner_search(context, user_id, gender_pref, hobby_pref, age_min, age_max))

async def background_partner_search(context: ContextTypes.DEFAULT_TYPE, user_id: int,
                                  gender_pref=None, hobby_pref=None, age_min=None, age_max=None):
    """Background task to keep searching for partner"""
    max_attempts = 30  # Search for 5 minutes (30 attempts * 10 seconds)
    attempt = 0
    
    while attempt < max_attempts:
        await asyncio.sleep(10)  # Wait 10 seconds between attempts
        attempt += 1
        
        # Check if user is still in queue
        try:
            partner_id = find_partner(user_id, gender_pref, hobby_pref, age_min, age_max)
            if partner_id:
                # Remove from queue and create session
                remove_from_queue(user_id)
                create_chat_session(user_id, partner_id)
                
                # Notify both users
                try:
                    await context.bot.send_message(
                        user_id,
                        "🎉 Partner ditemukan! Chat dimulai.\n"
                        "Gunakan /stop untuk mengakhiri chat atau /next untuk mencari partner baru.",
                        reply_markup=get_chat_menu()
                    )
                    
                    await context.bot.send_message(
                        partner_id,
                        "🎉 Partner ditemukan! Chat dimulai.\n"
                        "Gunakan /stop untuk mengakhiri chat atau /next untuk mencari partner baru.",
                        reply_markup=get_chat_menu()
                    )
                    
                    logger.info(f"Background search: Chat session created between {user_id} and {partner_id}")
                    return
                    
                except Exception as e:
                    logger.error(f"Failed to notify users in background search: {e}")
                    end_chat_session(user_id)
                    continue
        
        except Exception as e:
            logger.error(f"Error in background partner search: {e}")
            continue
    
    # If no partner found after max attempts, remove from queue
    try:
        remove_from_queue(user_id)
        await context.bot.send_message(
            user_id,
            "⏰ Pencarian partner timeout. Silakan coba lagi nanti.",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Failed to notify user about search timeout: {e}")

@check_ban_status
@require_profile
async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop current chat or cancel search"""
    user_id = update.effective_user.id
    
    if is_in_chat(user_id):
        # End current chat session
        partner_id = end_chat_session(user_id)
        await update.message.reply_text(
            "💔 Chat diakhiri. Terima kasih!",
            reply_markup=get_main_menu()
        )
        
        if partner_id:
            try:
                await context.bot.send_message(
                    partner_id,
                    "💔 Partner mengakhiri chat. Terima kasih!",
                    reply_markup=get_main_menu()
                )
            except Exception as e:
                logger.error(f"Failed to notify partner about chat end: {e}")
    else:
        # Cancel search if in queue
        remove_from_queue(user_id)
        await update.message.reply_text(
            "❌ Pencarian dibatalkan.",
            reply_markup=get_main_menu()
        )

@check_ban_status
@require_profile
async def next_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Find next partner"""
    user_id = update.effective_user.id
    
    if is_in_chat(user_id):
        # End current chat and start new search
        partner_id = end_chat_session(user_id)
        
        if partner_id:
            try:
                await context.bot.send_message(
                    partner_id,
                    "💔 Partner mencari chat baru. Terima kasih!",
                    reply_markup=get_main_menu()
                )
            except Exception as e:
                logger.error(f"Failed to notify partner about next: {e}")
        
        await update.message.reply_text("🔄 Mencari partner baru...")
        await start_partner_search(update, context)
    else:
        await update.message.reply_text(
            "❗ Kamu tidak sedang dalam chat. Gunakan /start untuk memulai.",
            reply_markup=get_main_menu()
        )

@check_ban_status
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward message to chat partner"""
    user_id = update.effective_user.id
    
    # Skip if it's a command
    if update.message.text and update.message.text.startswith('/'):
        return
    
    partner_id = get_chat_partner(user_id)
    if not partner_id:
        return
    
    try:
        # Forward the message to partner
        if update.message.text:
            await context.bot.send_message(partner_id, update.message.text)
        elif update.message.photo:
            await context.bot.send_photo(partner_id, update.message.photo[-1].file_id, 
                                       caption=update.message.caption)
        elif update.message.voice:
            await context.bot.send_voice(partner_id, update.message.voice.file_id)
        elif update.message.video:
            await context.bot.send_video(partner_id, update.message.video.file_id,
                                       caption=update.message.caption)
        elif update.message.document:
            await context.bot.send_document(partner_id, update.message.document.file_id,
                                          caption=update.message.caption)
        elif update.message.sticker:
            await context.bot.send_sticker(partner_id, update.message.sticker.file_id)
        elif update.message.audio:
            await context.bot.send_audio(partner_id, update.message.audio.file_id,
                                       caption=update.message.caption)
        elif update.message.location:
            await context.bot.send_location(partner_id, update.message.location.latitude,
                                          update.message.location.longitude)
        
    except Exception as e:
        logger.error(f"Failed to forward message from {user_id} to {partner_id}: {e}")
        await update.message.reply_text(
            "❌ Gagal mengirim pesan ke partner. Partner mungkin sudah keluar dari chat."
        )