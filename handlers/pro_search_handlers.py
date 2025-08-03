#!/usr/bin/env python3
"""
Pro Search handlers for Telegram Anonymous Chat Bot
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from config import GENDERS, HOBBIES, SEARCH_TYPE, SEARCH_GENDER, SEARCH_HOBBY, SEARCH_AGE_MIN, SEARCH_AGE_MAX
from database import is_user_pro, add_to_queue, find_partner, create_chat_session
from handlers.decorators import check_ban_status, require_profile
from handlers.chat_handlers import start_partner_search
from utils.keyboards import get_main_menu, get_gender_keyboard, get_hobbies_keyboard

logger = logging.getLogger(__name__)

@check_ban_status
@require_profile
async def search_pro_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Pro Search conversation"""
    user_id = update.effective_user.id
    
    if not is_user_pro(user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Upgrade ke Pro", callback_data="upgrade_pro")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="back_main")]
        ])
        await update.message.reply_text(
            "🔒 *Pro Search - Premium Feature*\n\n"
            "Fitur ini hanya tersedia untuk Pro users!\n\n"
            "✨ *Pro Search Benefits:*\n"
            "• Search by gender preference\n"
            "• Search by hobby preference\n" 
            "• Search by age range\n"
            "• Priority matching\n"
            "• Advanced filters\n\n"
            "Upgrade sekarang untuk akses unlimited!",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return ConversationHandler.END
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Search by Gender", callback_data="search_gender")],
        [InlineKeyboardButton("🎯 Search by Hobby", callback_data="search_hobby")],
        [InlineKeyboardButton("🎂 Search by Age", callback_data="search_age")],
        [InlineKeyboardButton("🔄 Advanced Search", callback_data="search_advanced")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_main")]
    ])
    
    await update.message.reply_text(
        "✨ *Pro Search - Choose Your Preference*\n\n"
        "Pilih jenis pencarian yang kamu inginkan:",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return SEARCH_TYPE

async def search_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search type selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "search_gender":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Male", callback_data="gender_Male")],
            [InlineKeyboardButton("👩 Female", callback_data="gender_Female")],
            [InlineKeyboardButton("🌈 Other", callback_data="gender_Other")],
            [InlineKeyboardButton("🎲 Any Gender", callback_data="gender_Any")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_search")]
        ])
        await query.edit_message_text(
            "👥 *Search by Gender*\n\n"
            "Pilih gender preference untuk partner:",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return SEARCH_GENDER
        
    elif query.data == "search_hobby":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(hobby, callback_data=f"hobby_{hobby}")] 
            for hobby in HOBBIES[:9]  # First 9 hobbies
        ] + [
            [InlineKeyboardButton(HOBBIES[9], callback_data=f"hobby_{HOBBIES[9]}")],  # "Other"
            [InlineKeyboardButton("🎲 Any Hobby", callback_data="hobby_Any")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_search")]
        ])
        await query.edit_message_text(
            "🎯 *Search by Hobby*\n\n"
            "Pilih hobby preference untuk partner:",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return SEARCH_HOBBY
        
    elif query.data == "search_age":
        await query.edit_message_text(
            "🎂 *Search by Age Range*\n\n"
            "Masukkan umur minimum (13-100):"
        )
        return SEARCH_AGE_MIN
        
    elif query.data == "search_advanced":
        context.user_data['search_prefs'] = {}
        await query.edit_message_text(
            "🔄 *Advanced Search*\n\n"
            "Kita akan setup preferensi lengkap step by step.\n\n"
            "Pertama, pilih gender preference:"
        )
        # Show gender selection for advanced search
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Male", callback_data="adv_gender_Male")],
            [InlineKeyboardButton("👩 Female", callback_data="adv_gender_Female")],
            [InlineKeyboardButton("🌈 Other", callback_data="adv_gender_Other")],
            [InlineKeyboardButton("🎲 Any Gender", callback_data="adv_gender_Any")]
        ])
        await query.edit_message_text(
            "🔄 *Advanced Search - Step 1/3*\n\n"
            "Pilih gender preference:",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return SEARCH_GENDER
        
    elif query.data == "back_main":
        await query.edit_message_text("🔙 Kembali ke menu utama...")
        await query.message.reply_text(
            "🏠 Menu Utama",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END

async def handle_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender preference selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("gender_"):
        gender_pref = query.data.replace("gender_", "")
        # Start search immediately with gender preference
        await query.edit_message_text(
            f"✨ Mencari partner dengan gender: *{gender_pref}*\n\n"
            "Sedang mencari partner yang cocok...",
            parse_mode='Markdown'
        )
        
        # Start search with gender preference
        user_id = query.from_user.id
        gender_filter = None if gender_pref == "Any" else gender_pref
        await start_partner_search(update, context, gender_pref=gender_filter)
        return ConversationHandler.END
        
    elif query.data.startswith("adv_gender_"):
        # Advanced search - save gender and move to hobby
        gender_pref = query.data.replace("adv_gender_", "")
        context.user_data['search_prefs']['gender'] = None if gender_pref == "Any" else gender_pref
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(hobby, callback_data=f"adv_hobby_{hobby}")] 
            for hobby in HOBBIES[:9]
        ] + [
            [InlineKeyboardButton(HOBBIES[9], callback_data=f"adv_hobby_{HOBBIES[9]}")],
            [InlineKeyboardButton("🎲 Any Hobby", callback_data="adv_hobby_Any")]
        ])
        
        await query.edit_message_text(
            f"🔄 *Advanced Search - Step 2/3*\n\n"
            f"✅ Gender: {gender_pref}\n"
            f"Sekarang pilih hobby preference:",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return SEARCH_HOBBY

async def handle_hobby_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hobby preference selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("hobby_"):
        hobby_pref = query.data.replace("hobby_", "")
        # Start search immediately with hobby preference
        await query.edit_message_text(
            f"✨ Mencari partner dengan hobby: *{hobby_pref}*\n\n"
            "Sedang mencari partner yang cocok...",
            parse_mode='Markdown'
        )
        
        user_id = query.from_user.id
        hobby_filter = None if hobby_pref == "Any" else hobby_pref
        await start_partner_search(update, context, hobby_pref=hobby_filter)
        return ConversationHandler.END
        
    elif query.data.startswith("adv_hobby_"):
        # Advanced search - save hobby and move to age
        hobby_pref = query.data.replace("adv_hobby_", "")
        context.user_data['search_prefs']['hobby'] = None if hobby_pref == "Any" else hobby_pref
        
        await query.edit_message_text(
            f"🔄 *Advanced Search - Step 3/3*\n\n"
            f"✅ Gender: {context.user_data['search_prefs'].get('gender', 'Any')}\n"
            f"✅ Hobby: {hobby_pref}\n\n"
            f"Masukkan range umur yang diinginkan:\n"
            f"Format: min-max (contoh: 18-25)\n"
            f"Atau ketik 'any' untuk semua umur",
            parse_mode='Markdown'
        )
        return SEARCH_AGE_MIN

async def handle_age_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle age range input"""
    text = update.message.text.lower().strip()
    
    if text == "any":
        # No age filter
        age_min = age_max = None
        age_text = "Any"
    else:
        try:
            if "-" in text:
                age_min, age_max = map(int, text.split("-"))
            else:
                age_min = age_max = int(text)
            
            if age_min < 13 or age_max > 100 or age_min > age_max:
                await update.message.reply_text(
                    "❌ Range umur tidak valid. Masukkan range 13-100 atau 'any'"
                )
                return SEARCH_AGE_MIN
            
            age_text = f"{age_min}-{age_max}" if age_min != age_max else str(age_min)
            
        except ValueError:
            await update.message.reply_text(
                "❌ Format tidak valid. Gunakan format: min-max (contoh: 18-25) atau 'any'"
            )
            return SEARCH_AGE_MIN
    
    # Get preferences from context or use current input
    if 'search_prefs' in context.user_data:
        # Advanced search
        gender_pref = context.user_data['search_prefs'].get('gender')
        hobby_pref = context.user_data['search_prefs'].get('hobby')
        prefs_text = f"Gender: {gender_pref or 'Any'}, Hobby: {hobby_pref or 'Any'}, Age: {age_text}"
    else:
        # Age-only search
        gender_pref = hobby_pref = None
        prefs_text = f"Age: {age_text}"
    
    await update.message.reply_text(
        f"✨ *Mencari partner dengan preferensi:*\n{prefs_text}\n\n"
        "Sedang mencari partner yang cocok...",
        parse_mode='Markdown'
    )
    
    # Start search with all preferences
    await start_partner_search(update, context, gender_pref, hobby_pref, age_min, age_max)
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

async def pro_search_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel Pro Search"""
    await update.message.reply_text(
        "❌ Pro Search dibatalkan.",
        reply_markup=get_main_menu()
    )
    context.user_data.clear()
    return ConversationHandler.END