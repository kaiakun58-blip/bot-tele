#!/usr/bin/env python3
"""
ObrolanId - Anonymous Chat Bot
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
    is_user_pro, get_user_stats, mask_username, get_top_users, is_in_chat
)
from handlers.decorators import check_ban_status, auto_update_profile, owner_only
from handlers.chat_handlers import start_chat, stop_chat, next_partner, forward_message
from handlers.pro_search_handlers import (
    search_pro_command, search_type_callback, handle_gender_selection,
    handle_hobby_selection, handle_age_input, pro_search_cancel
)
from handlers.payment_handlers import (
    handle_upgrade_pro, handle_payment_selection, handle_payment_confirmation,
    demo_payment_command
)
from utils.keyboards import (
    get_main_menu, get_chat_menu, get_gender_keyboard, 
    get_language_keyboard, get_hobbies_keyboard, get_gender_search_keyboard,
    get_context_keyboard
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
    user_name = update.effective_user.first_name
    
    # Check if this is first time user
    profile = get_user_profile(user_id)
    is_new_user = not profile or not profile.get('gender')
    
    if is_new_user:
        # Welcome message for new users
        welcome_text = f"""
🎉 *Selamat datang di ObrolanId, {user_name}!*

🤖 *Tentang ObrolanId:*
Bot untuk chat anonim dengan orang-orang baru dari seluruh Indonesia dan dunia!

✨ *Fitur Utama:*
• 💬 Chat anonim 1-on-1
• 🔍 Cari partner secara acak
• 👥 Profil lengkap dengan foto dan bio
• 🎯 Search Pro (filter gender, hobi, umur)
• 🎮 Quiz berhadiah poin
• 🔒 Mode rahasia
• 🌐 Support Bahasa Indonesia & English

📋 *Perintah Utama:*
/start - Tampilkan menu utama
/profile - Lengkapi profil untuk pengalaman terbaik
/find - Cari partner chat
/help - Bantuan lengkap
/stats - Lihat statistik bot

💡 *Tips:* Lengkapi profil untuk hasil pencarian yang lebih baik!
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Lengkapi Profil", callback_data="complete_profile")],
            [InlineKeyboardButton("🔍 Langsung Cari Partner", callback_data="skip_profile")]
        ])
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    # Returning user
    is_pro = is_user_pro(user_id)
    pro_status = "✨ Pro User" if is_pro else "📋 Regular User"
    points = profile.get('points', 0)
    is_chatting = is_in_chat(user_id)
    
    await update.message.reply_text(
        f"🎉 Selamat datang kembali, {user_name}!\n\n"
        f"{pro_status} • 📊 Poin: {points}\n\n"
        f"Pilih menu di bawah untuk memulai:",
        reply_markup=get_context_keyboard(user_id, is_chatting, is_pro)
    )

@check_ban_status
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - show available commands"""
    help_text = """
 🤖 *ObrolanId - Help & Commands*

 *Perintah Utama:*
 /start - Mulai bot dan lihat menu utama
 /profile - Atur profil kamu
 /find - Cari partner chat
 /help - Tampilkan bantuan ini
 /stats - Lihat statistik bot

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
 - Profil lengkap = hasil pencarian lebih baik
 - Gunakan /report untuk laporkan user bermasalah
 - Hormati pengguna lain dan ikuti aturan
 - User tanpa profil tetap bisa chat (mode basic)
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ========== Profile Management ==========

@check_ban_status
@auto_update_profile
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start profile setup conversation"""
    user_id = update.effective_user.id
    # Clear any existing conversation data
    context.user_data.clear()
    
    await update.message.reply_text(
        "📝 Mari lengkapi profilmu!\n\n"
        "Pilih gender kamu:",
        reply_markup=get_gender_keyboard()
    )
    return PROFILE_GENDER

async def profile_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender selection"""
    gender = update.message.text.strip()
    
    # Debug logging
    logger.info(f"User {update.effective_user.id} selected gender: {gender}")
    
    if gender not in GENDERS:
        await update.message.reply_text(
            f"❌ Pilihan tidak valid: '{gender}'\n"
            f"Pilih salah satu: {', '.join(GENDERS)}",
            reply_markup=get_gender_keyboard()
        )
        return PROFILE_GENDER
    
    context.user_data['gender'] = gender
    await update.message.reply_text(
        f"✅ Gender tersimpan: {gender}\n\n"
        "Berapa umur kamu? (Masukkan angka 13-100)",
        reply_markup=None  # Remove keyboard
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
    
    user_is_pro = is_user_pro(user_id)
    await update.message.reply_text(
        "🎉 Profil berhasil dibuat!\n"
        "Sekarang kamu bisa mulai mencari partner chat.",
        reply_markup=get_main_menu(user_is_pro)
    )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

async def profile_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel profile setup"""
    user_id = update.effective_user.id
    user_is_pro = is_user_pro(user_id)
    is_chatting = is_in_chat(user_id)
    
    await update.message.reply_text(
        "❌ Setup profil dibatalkan.",
        reply_markup=get_context_keyboard(user_id, is_chatting, user_is_pro)
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
async def handle_gender_search_non_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender search for non-Pro users"""
    user_id = update.effective_user.id
    
    if is_user_pro(user_id):
        await update.message.reply_text(
            "✨ Kamu sudah Pro! Gunakan 'Search Pro' untuk akses fitur lengkap.",
            reply_markup=get_main_menu(True)
        )
        return
    
    await update.message.reply_text(
        "👥 *Search by Gender - Free Feature*\n\n"
        "Pilih gender preference untuk partner:\n\n"
        "💡 *Tip:* Upgrade ke Pro untuk fitur lebih lengkap:\n"
        "• Search by Hobby\n"
        "• Search by Age Range\n"
        "• Advanced Multi-Filter\n"
        "• Priority Matching",
        parse_mode='Markdown',
        reply_markup=get_gender_search_keyboard()
    )

async def handle_basic_gender_search(update: Update, context: ContextTypes.DEFAULT_TYPE, gender_pref: str):
    """Handle basic gender search for non-Pro users"""
    user_id = update.effective_user.id
    
    await update.message.reply_text(
        f"🔍 Mencari partner dengan gender: {gender_pref or 'Any'}\n\n"
        "Sedang mencari partner yang cocok...",
        reply_markup=get_chat_menu()
    )
    
    # Start search with gender preference
    from handlers.chat_handlers import start_partner_search
    await start_partner_search(update, context, gender_pref=gender_pref)

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
        # This will be handled by the ConversationHandler
        return
    
    elif query.data == "skip_profile":
        await query.edit_message_text(
            "🔍 Mode Basic - Mencari partner...\n"
            "Profil tidak lengkap tapi tetap bisa chat!"
        )
        # Create a proper message update for start_chat
        fake_update = Update(
            update_id=update.update_id,
            message=query.message,
            callback_query=None
        )
        await start_chat(fake_update, context)
    
    elif query.data == "edit_profile":
        await query.edit_message_text("Gunakan /profile untuk mengedit profil.")
    
    elif query.data == "view_stats":
        fake_update = Update(
            update_id=update.update_id,
            message=query.message,
            callback_query=None
        )
        await stats_command(fake_update, context)
    
    elif query.data == "upgrade_pro":
        await handle_upgrade_pro(update, context)

# ========== Message Handlers ==========

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages based on current state"""
    text = update.message.text
    user_id = update.effective_user.id
    is_pro = is_user_pro(user_id)
    is_chatting = is_in_chat(user_id)
    
    # Dynamic text matching with emoji support
    if text in ["Find a partner", "🔍 Find Partner"]:
        await start_chat(update, context)
    elif text in ["My Profile", "👤 My Profile"]:
        await my_profile(update, context)
    elif text in ["Stop", "🛑 Stop"]:
        await stop_chat(update, context)
    elif text in ["Next", "⏭️ Next"]:
        await next_partner(update, context)
    elif text in ["Search Pro", "🎯 Search Pro"]:
        await search_pro_command(update, context)
    elif text in ["Upgrade to Pro", "✨ Upgrade to Pro"]:
        await handle_upgrade_pro(update, context)
    elif text == "👥 Search by Gender":
        await handle_gender_search_non_pro(update, context)
    elif text in ["📊 Stats"]:
        await stats_command(update, context)
    elif text == "🔍 Help":
        await help_command(update, context)
    elif text in ["Secret Mode", "🔒 Secret Mode"]:
        await update.message.reply_text("🔒 Mode rahasia akan aktif untuk chat berikutnya.")
    elif text in ["Feedback", "⭐ Feedback"]:
        await update.message.reply_text("⭐ Terima kasih! Fitur feedback akan segera tersedia.")
    elif text == "🔙 Back to Menu":
        await update.message.reply_text(
            "🏠 Menu Utama",
            reply_markup=get_context_keyboard(user_id, is_chatting, is_pro)
        )
    # Gender selection for non-Pro search
    elif text in ["👨 Male", "👩 Female", "🌈 Other", "🎲 Any Gender"]:
        gender = text.split(" ")[1] if " " in text else "Any"
        if gender == "Any":
            gender = None
        await handle_basic_gender_search(update, context, gender)
    elif text in ["Play Quiz", "🎮 Play Quiz", "Join Group"]:
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
    application.add_handler(CommandHandler("upgrade", handle_upgrade_pro))
    application.add_handler(CommandHandler("pay", demo_payment_command))
    
    # ========== Conversation Handlers ==========
    profile_conv = ConversationHandler(
        entry_points=[
            CommandHandler("profile", profile_command),
            CallbackQueryHandler(lambda u, c: profile_command(u, c), pattern="^complete_profile$")
        ],
        states={
            PROFILE_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_gender)],
            PROFILE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_age)],
            PROFILE_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_bio)],
            PROFILE_PHOTO: [MessageHandler(filters.PHOTO, profile_photo)],
            PROFILE_LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_language)],
            PROFILE_HOBBY: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_hobby)],
        },
        fallbacks=[CommandHandler("cancel", profile_cancel)],
        per_chat=True,
        per_user=True,
        per_message=False,
        allow_reentry=True
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
    # Payment handlers (must be before general callback handler)
    application.add_handler(CallbackQueryHandler(handle_payment_selection, pattern=r"^(buy_pro_|redeem_pro|payment_methods)"))
    application.add_handler(CallbackQueryHandler(handle_payment_confirmation, pattern=r"^confirm_"))
    application.add_handler(CallbackQueryHandler(handle_upgrade_pro, pattern=r"^upgrade_pro$"))
    
    # General callback handler (must be last)
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