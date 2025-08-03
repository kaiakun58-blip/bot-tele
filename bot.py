#!/usr/bin/env python3
"""
Telegram Anonymous Chat Bot - Refactored Version
A comprehensive anonymous chat bot with advanced features including:
- Anonymous 1-on-1 and group chat
- Advanced search with filters (Pro feature)
- User profiles with hobbies
- Points system and leaderboard
- Quiz games with rewards
- Content moderation
- Feedback and rating system
- Secret mode for temporary messages
- Multi-language support
"""

import logging
import time
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

from config import BOT_TOKEN, OWNER_ID, GENDERS, HOBBIES, LANGS, REPORT_REASONS
from database import (
    is_profile_complete, get_user_profile, update_user_profile,
    is_user_pro, get_user_stats, mask_username, get_top_users
)
from handlers.decorators import check_ban_status, auto_update_profile, owner_only
from handlers.chat_handlers import start_chat, stop_chat, next_partner, forward_message
from handlers.pro_search_handlers import (
    search_pro_command, search_type_callback, handle_gender_selection,
    handle_hobby_selection, handle_age_input, pro_search_cancel
)
from utils.keyboards import (
    get_main_menu, get_chat_menu, get_gender_keyboard, 
    get_language_keyboard, get_hobbies_keyboard
)

# ========== Logging ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== Conversation States ==========
from config import (
    PROFILE_GENDER, PROFILE_AGE, PROFILE_BIO, PROFILE_PHOTO, PROFILE_LANG, PROFILE_HOBBY,
    SEARCH_TYPE, SEARCH_GENDER, SEARCH_HOBBY, SEARCH_AGE_MIN, SEARCH_AGE_MAX
)

# ========== Main Commands ==========

@check_ban_status
@auto_update_profile
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - welcome message and menu"""
    user_id = update.effective_user.id
    
    if not is_profile_complete(user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Lengkapi Profil", callback_data="complete_profile")],
            [InlineKeyboardButton("Lanjutkan & Cari Acak", callback_data="skip_profile")]
        ])
        await update.message.reply_text(
            "👋 Selamat datang di Anonymous Chat!\n"
            "Bot ini memungkinkan kamu chat anonim dengan orang lain.\n\n"
            "Profilmu belum lengkap. Lengkapi profil untuk pengalaman yang lebih baik!",
            reply_markup=keyboard
        )
        return
    
    await update.message.reply_text(
        "🎉 Selamat datang kembali!\n"
        "Pilih menu di bawah untuk memulai:",
        reply_markup=get_main_menu()
    )

@check_ban_status
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - show available commands"""
    help_text = """
🤖 *Anonymous Chat Bot - Help*

*Perintah Utama:*
/start - Mulai bot dan lihat menu utama
/profile - Atur profil kamu
/help - Tampilkan bantuan ini

*Fitur Chat:*
• Find a partner - Cari partner chat acak
• Search Pro - Pencarian advanced (Pro users)
• Next - Ganti partner saat chat
• Stop - Akhiri chat

*Fitur Lain:*
• My Profile - Lihat dan edit profil
• Play Quiz - Main quiz berhadiah
• Join Group - Gabung group chat
• Secret Mode - Mode pesan sementara
• Feedback - Beri rating partner

*Pro Features:*
✨ Pencarian berdasarkan gender, hobi, dan umur
✨ Priority matching
✨ Akses fitur premium

*Tips:*
- Lengkapi profil untuk pengalaman terbaik
- Gunakan /report untuk laporkan user bermasalah
- Hormati pengguna lain dan ikuti aturan
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ========== Profile Management ==========

@check_ban_status
@auto_update_profile
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start profile setup conversation"""
    await update.message.reply_text(
        "📝 Mari lengkapi profilmu!\n\n"
        "Pilih gender kamu:",
        reply_markup=get_gender_keyboard()
    )
    return PROFILE_GENDER

async def profile_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender selection"""
    gender = update.message.text
    if gender not in GENDERS:
        await update.message.reply_text("❌ Pilihan tidak valid. Pilih dari tombol yang tersedia.")
        return PROFILE_GENDER
    
    context.user_data['gender'] = gender
    await update.message.reply_text(
        "✅ Gender tersimpan!\n\n"
        "Berapa umur kamu? (Masukkan angka)"
    )
    return PROFILE_AGE

async def profile_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle age input"""
    try:
        age = int(update.message.text)
        if age < 13 or age > 100:
            await update.message.reply_text("❌ Umur harus antara 13-100 tahun.")
            return PROFILE_AGE
        
        context.user_data['age'] = age
        await update.message.reply_text(
            "✅ Umur tersimpan!\n\n"
            "Ceritakan sedikit tentang diri kamu (bio):"
        )
        return PROFILE_BIO
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka yang valid.")
        return PROFILE_AGE

async def profile_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bio input"""
    bio = update.message.text
    if len(bio) < 10:
        await update.message.reply_text("❌ Bio minimal 10 karakter.")
        return PROFILE_BIO
    
    context.user_data['bio'] = bio
    await update.message.reply_text(
        "✅ Bio tersimpan!\n\n"
        "Kirim foto profil kamu:"
    )
    return PROFILE_PHOTO

async def profile_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo upload"""
    if not update.message.photo:
        await update.message.reply_text("❌ Kirim foto, bukan file lain.")
        return PROFILE_PHOTO
    
    photo_id = update.message.photo[-1].file_id
    context.user_data['photo_id'] = photo_id
    
    await update.message.reply_text(
        "✅ Foto tersimpan!\n\n"
        "Pilih bahasa utama:",
        reply_markup=get_language_keyboard()
    )
    return PROFILE_LANG

async def profile_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    language = update.message.text
    if language not in LANGS:
        await update.message.reply_text("❌ Pilihan tidak valid.")
        return PROFILE_LANG
    
    context.user_data['language'] = language
    await update.message.reply_text(
        "✅ Bahasa tersimpan!\n\n"
        "Pilih hobi utama kamu:",
        reply_markup=get_hobbies_keyboard()
    )
    return PROFILE_HOBBY

async def profile_hobby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hobby selection and save profile"""
    hobby = update.message.text
    if hobby not in HOBBIES:
        await update.message.reply_text("❌ Pilihan tidak valid.")
        return PROFILE_HOBBY
    
    # Save all profile data
    user_id = update.effective_user.id
    profile_data = {
        'gender': context.user_data['gender'],
        'age': context.user_data['age'],
        'bio': context.user_data['bio'],
        'photo_id': context.user_data['photo_id'],
        'language': context.user_data['language'],
        'hobbies': [hobby]
    }
    
    update_user_profile(user_id, **profile_data)
    
    await update.message.reply_text(
        "🎉 Profil berhasil dibuat!\n"
        "Sekarang kamu bisa mulai mencari partner chat.",
        reply_markup=get_main_menu()
    )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

async def profile_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel profile setup"""
    await update.message.reply_text(
        "❌ Setup profil dibatalkan.",
        reply_markup=get_main_menu()
    )
    context.user_data.clear()
    return ConversationHandler.END

@check_ban_status
async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's current profile"""
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)
    
    if not profile:
        await update.message.reply_text(
            "❗ Profil belum dibuat. Gunakan /profile untuk membuat profil."
        )
        return
    
    pro_status = "✨ Pro User" if is_user_pro(user_id) else "📋 Regular User"
    hobbies_text = ", ".join(profile.get('hobbies', [])) or "Tidak ada"
    
    profile_text = f"""
👤 *Profil Kamu*

{pro_status}
📊 Poin: {profile.get('points', 0)}

👥 Gender: {profile.get('gender', 'Tidak diset')}
🎂 Umur: {profile.get('age', 'Tidak diset')}
🌐 Bahasa: {profile.get('language', 'Tidak diset')}
🎯 Hobi: {hobbies_text}

📝 Bio: {profile.get('bio', 'Tidak ada bio')}
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Edit Profil", callback_data="edit_profile")],
        [InlineKeyboardButton("Lihat Statistik", callback_data="view_stats")]
    ])
    
    if profile.get('photo_id'):
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=profile['photo_id'],
            caption=profile_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            profile_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

# ========== Statistics and Leaderboard ==========

@check_ban_status
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    stats = get_user_stats()
    top_users = get_top_users(5)
    
    leaderboard = "\n".join([
        f"{i+1}. {mask_username('')} - {points} poin"
        for i, (user_id, points) in enumerate(top_users)
    ])
    
    stats_text = f"""
📊 *Statistik Bot*

👥 Total Users: {stats['total_users']}
💬 Chat Aktif: {stats['active_chats']}
📋 Laporan 24h: {stats['reports_24h']}

🏆 *Top 5 Users:*
{leaderboard or 'Belum ada data'}
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# ========== Callback Query Handlers ==========

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "complete_profile":
        await query.edit_message_text("Mari lengkapi profil!")
        await profile_command(update, context)
    
    elif query.data == "skip_profile":
        await query.edit_message_text(
            "⚠️ Profil tidak lengkap mungkin mempengaruhi pengalaman chat kamu."
        )
        await start_chat(update, context)
    
    elif query.data == "edit_profile":
        await query.edit_message_text("Gunakan /profile untuk mengedit profil.")
    
    elif query.data == "view_stats":
        await stats_command(update, context)

# ========== Message Handlers ==========

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages based on current state"""
    text = update.message.text
    
    if text == "Find a partner":
        await start_chat(update, context)
    elif text == "My Profile":
        await my_profile(update, context)
    elif text == "Stop":
        await stop_chat(update, context)
    elif text == "Next":
        await next_partner(update, context)
    elif text == "Search Pro":
        await search_pro_command(update, context)
    elif text in ["Upgrade to Pro", "Play Quiz", "Join Group"]:
        await update.message.reply_text(
            f"🚧 Fitur '{text}' sedang dalam pengembangan. "
            "Akan segera tersedia di update berikutnya!"
        )
    else:
        # Forward to chat partner if in chat
        await forward_message(update, context)

# ========== Job Queue ==========

async def daily_leaderboard_job(context: ContextTypes.DEFAULT_TYPE):
    """Daily leaderboard job for admin"""
    stats = get_user_stats()
    top_users = get_top_users(5)
    
    leaderboard = "\n".join([
        f"{i+1}. {mask_username('')} - {points} poin"
        for i, (user_id, points) in enumerate(top_users)
    ])
    
    message = f"""
📊 *Laporan Harian Bot*

👥 Total Users: {stats['total_users']}
💬 Chat Aktif: {stats['active_chats']}
📋 Laporan 24h: {stats['reports_24h']}

🏆 *Top 5 Users:*
{leaderboard or 'Belum ada data'}

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    await context.bot.send_message(
        OWNER_ID, 
        message, 
        parse_mode='Markdown'
    )

# ========== Admin Commands ==========

@owner_only
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to get detailed stats"""
    await stats_command(update, context)

# ========== Main Function ==========

def main():
    """Main function to start the bot"""
    # Initialize database
    from database import db_manager
    logger.info("Database initialized")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ========== Command Handlers ==========
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("admin", admin_stats))
    
    # Chat handlers
    application.add_handler(CommandHandler("find", start_chat))
    application.add_handler(CommandHandler("stop", stop_chat))
    application.add_handler(CommandHandler("next", next_partner))
    application.add_handler(CommandHandler("searchpro", search_pro_command))
    
    # ========== Conversation Handlers ==========
    profile_conv = ConversationHandler(
        entry_points=[CommandHandler("profile", profile_command)],
        states={
            PROFILE_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_gender)],
            PROFILE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_age)],
            PROFILE_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_bio)],
            PROFILE_PHOTO: [MessageHandler(filters.PHOTO, profile_photo)],
            PROFILE_LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_language)],
            PROFILE_HOBBY: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_hobby)],
        },
        fallbacks=[CommandHandler("cancel", profile_cancel)]
    )
    application.add_handler(profile_conv)
    
    # Pro Search Conversation
    pro_search_conv = ConversationHandler(
        entry_points=[CommandHandler("searchpro", search_pro_command)],
        states={
            SEARCH_TYPE: [CallbackQueryHandler(search_type_callback)],
            SEARCH_GENDER: [CallbackQueryHandler(handle_gender_selection)],
            SEARCH_HOBBY: [CallbackQueryHandler(handle_hobby_selection)],
            SEARCH_AGE_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_age_input)],
        },
        fallbacks=[CommandHandler("cancel", pro_search_cancel)]
    )
    application.add_handler(pro_search_conv)
    
    # ========== Callback Query Handler ==========
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    
    # ========== Message Handlers ==========
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_text_message
    ))
    
    # Handle all other messages (photos, voice, etc.)
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND & ~filters.TEXT,
        forward_message
    ))
    
    # ========== Job Queue ==========
    job_queue = application.job_queue
    job_queue.run_daily(
        daily_leaderboard_job, 
        time=datetime.now().replace(hour=23, minute=59, second=0)
    )
    
    # ========== Start Bot ==========
    logger.info("🤖 Bot started successfully!")
    logger.info(f"🔧 Loaded handlers: {len(application.handlers)} groups")
    
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()