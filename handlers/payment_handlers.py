#!/usr/bin/env python3
"""
Payment handlers for Pro membership in ObrolanId
"""
import logging
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import ContextTypes
# Remove unused imports

from config import PRO_WEEK_PRICE, PRO_MONTH_PRICE
from database import is_user_pro, update_user_profile, get_user_profile, add_user_points
from handlers.decorators import check_ban_status
from utils.keyboards import get_main_menu

logger = logging.getLogger(__name__)

@check_ban_status
async def handle_upgrade_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Pro upgrade request"""
    query = update.callback_query if update.callback_query else None
    user_id = update.effective_user.id
    
    if is_user_pro(user_id):
        text = "✨ Kamu sudah Pro User!\n\nNikmati semua fitur premium:"
        features = """
• 🎯 Search by Gender, Hobby, Age
• ⚡ Priority Matching  
• 🔍 Advanced Search Filters
• 📊 Detailed Statistics
• 🎮 Exclusive Quiz Rewards
• 👑 Pro Badge
        """
        
        if query:
            await query.edit_message_text(text + features)
        else:
            await update.message.reply_text(text + features, reply_markup=get_main_menu())
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pro 1 Minggu - Rp 10,000", callback_data="buy_pro_week")],
        [InlineKeyboardButton("💎 Pro 1 Bulan - Rp 35,000", callback_data="buy_pro_month")],
        [InlineKeyboardButton("🎯 Tukar 1000 Poin", callback_data="redeem_pro_points")],
        [InlineKeyboardButton("💰 Cara Pembayaran", callback_data="payment_methods")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="back_main")]
    ])
    
    pro_text = """
✨ *Upgrade ke Pro Membership*

🎯 *Pro Features:*
• Search by Gender (Male/Female/Other)
• Search by Hobby preference
• Search by Age range (18-25, dll)
• Advanced multi-filter search
• Priority partner matching
• Exclusive quiz rewards
• Pro badge & status

💰 *Harga:*
• 1 Minggu: Rp 10,000
• 1 Bulan: Rp 35,000

🎮 *Alternatif:*
• Tukar 1000 poin = 7 hari Pro

Pilih paket yang kamu inginkan:
    """
    
    if query:
        await query.edit_message_text(pro_text, parse_mode='Markdown', reply_markup=keyboard)
    else:
        await update.message.reply_text(pro_text, parse_mode='Markdown', reply_markup=keyboard)

async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment package selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "buy_pro_week":
        await initiate_payment(query, context, "week", PRO_WEEK_PRICE, 7)
    
    elif query.data == "buy_pro_month":
        await initiate_payment(query, context, "month", PRO_MONTH_PRICE, 30)
        
    elif query.data == "redeem_pro_points":
        await handle_points_redemption(query, context)
        
    elif query.data == "payment_methods":
        await show_payment_methods(query, context)
        
    elif query.data == "back_main":
        await query.edit_message_text("🏠 Menu Utama")
        await query.message.reply_text("Pilih menu:", reply_markup=get_main_menu())

async def initiate_payment(query, context: ContextTypes.DEFAULT_TYPE, duration: str, price: int, days: int):
    """Initiate payment process"""
    user_id = query.from_user.id
    
    # For demo purposes, we'll simulate payment with manual confirmation
    # In production, integrate with payment gateway like Midtrans, DANA, etc.
    
    payment_text = f"""
💳 *Pembayaran Pro {duration.title()}*

📦 Paket: Pro {days} hari
💰 Harga: Rp {price:,}

🏦 *Metode Pembayaran:*
Untuk demo ini, ketik: `/pay {duration}` untuk simulasi pembayaran berhasil

*Metode Pembayaran Real (untuk implementasi):*
• Transfer Bank (BCA, Mandiri, BRI)  
• E-Wallet (DANA, OVO, GoPay)
• QRIS
• Pulsa

📞 *Support:* Hubungi admin untuk bantuan pembayaran
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Konfirmasi Bayar Demo", callback_data=f"confirm_pay_{duration}")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="upgrade_pro")]
    ])
    
    await query.edit_message_text(payment_text, parse_mode='Markdown', reply_markup=keyboard)

async def handle_points_redemption(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle points redemption for Pro"""
    user_id = query.from_user.id
    profile = get_user_profile(user_id)
    current_points = profile.get('points', 0)
    
    if current_points < 1000:
        await query.edit_message_text(
            f"❌ *Poin Tidak Cukup*\n\n"
            f"Poin kamu: {current_points}\n"
            f"Diperlukan: 1000 poin\n"
            f"Kurang: {1000 - current_points} poin\n\n"
            f"💡 Cara dapat poin:\n"
            f"• Main quiz harian\n"
            f"• Chat dengan user baru\n"
            f"• Rating partner 5 bintang\n"
            f"• Login harian",
            parse_mode='Markdown'
        )
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Tukar 1000 Poin", callback_data="confirm_redeem_points")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="upgrade_pro")]
    ])
    
    await query.edit_message_text(
        f"🎯 *Tukar Poin ke Pro*\n\n"
        f"Poin kamu: {current_points}\n"
        f"Tukar: 1000 poin → 7 hari Pro\n\n"
        f"Konfirmasi penukaran?",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

async def show_payment_methods(query, context: ContextTypes.DEFAULT_TYPE):
    """Show available payment methods"""
    payment_info = """
💳 *Metode Pembayaran*

🏦 *Transfer Bank:*
• BCA: 1234567890 (a.n. ObrolanId)
• Mandiri: 0987654321
• BRI: 1122334455

📱 *E-Wallet:*
• DANA: 081234567890
• OVO: 081234567890  
• GoPay: 081234567890

📷 *QRIS:*
Scan kode QR yang akan dikirim

📞 *Pulsa:*
Transfer pulsa ke 081234567890

⚠️ *Penting:*
• Kirim bukti transfer ke admin
• Sertakan username Telegram kamu
• Pro akan aktif dalam 1-24 jam
• Hubungi admin jika ada masalah

📞 *Admin Support:* @admin_obrolanid
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Hubungi Admin", url="https://t.me/admin_obrolanid")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="upgrade_pro")]
    ])
    
    await query.edit_message_text(payment_info, parse_mode='Markdown', reply_markup=keyboard)

# Demo payment commands
async def demo_payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demo payment command for testing"""
    if not context.args:
        await update.message.reply_text(
            "❌ Format: `/pay week` atau `/pay month`"
        )
        return
    
    duration = context.args[0].lower()
    if duration not in ['week', 'month']:
        await update.message.reply_text(
            "❌ Durasi harus 'week' atau 'month'"
        )
        return
    
    user_id = update.effective_user.id
    
    # Grant Pro access
    days = 7 if duration == 'week' else 30
    pro_expires_at = int(time.time()) + (days * 24 * 60 * 60)
    
    update_user_profile(user_id, pro_expires_at=pro_expires_at)
    
    await update.message.reply_text(
        f"🎉 *Pembayaran Demo Berhasil!*\n\n"
        f"✨ Kamu sekarang Pro User selama {days} hari\n"
        f"⏰ Berlaku hingga: {datetime.fromtimestamp(pro_expires_at).strftime('%d/%m/%Y %H:%M')}\n\n"
        f"🎯 Nikmati semua fitur Pro:\n"
        f"• Search by Gender/Hobby/Age\n"
        f"• Priority Matching\n"
        f"• Advanced Filters\n\n"
        f"Gunakan /searchpro untuk mulai!",
        parse_mode='Markdown',
        reply_markup=get_main_menu()
    )

async def handle_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment confirmation"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith("confirm_pay_"):
        duration = query.data.replace("confirm_pay_", "")
        days = 7 if duration == 'week' else 30
        pro_expires_at = int(time.time()) + (days * 24 * 60 * 60)
        
        update_user_profile(user_id, pro_expires_at=pro_expires_at)
        
        await query.edit_message_text(
            f"🎉 *Pembayaran Demo Berhasil!*\n\n"
            f"✨ Kamu sekarang Pro User selama {days} hari\n"
            f"⏰ Berlaku hingga: {datetime.fromtimestamp(pro_expires_at).strftime('%d/%m/%Y %H:%M')}\n\n"
            f"🎯 Fitur Pro sudah aktif!\n"
            f"Gunakan /searchpro untuk mencoba.",
            parse_mode='Markdown'
        )
        
        await query.message.reply_text(
            "🏠 Menu Utama - Sekarang dengan akses Pro!",
            reply_markup=get_main_menu()
        )
    
    elif query.data == "confirm_redeem_points":
        profile = get_user_profile(user_id)
        current_points = profile.get('points', 0)
        
        if current_points >= 1000:
            # Deduct points and grant Pro
            new_points = current_points - 1000
            pro_expires_at = int(time.time()) + (7 * 24 * 60 * 60)  # 7 days
            
            update_user_profile(user_id, points=new_points, pro_expires_at=pro_expires_at)
            
            await query.edit_message_text(
                f"🎉 *Penukaran Poin Berhasil!*\n\n"
                f"✅ -1000 poin\n"
                f"✨ +7 hari Pro membership\n"
                f"📊 Sisa poin: {new_points}\n\n"
                f"Pro aktif hingga: {datetime.fromtimestamp(pro_expires_at).strftime('%d/%m/%Y %H:%M')}",
                parse_mode='Markdown'
            )
            
            await query.message.reply_text(
                "🏠 Menu Utama - Pro membership aktif!",
                reply_markup=get_main_menu()
            )
        else:
            await query.edit_message_text("❌ Poin tidak cukup!")

# Add these to bot.py handlers
def add_payment_handlers(application):
    """Add payment handlers to application"""
    application.add_handler(CallbackQueryHandler(handle_payment_selection, pattern=r"^(buy_pro_|redeem_pro|payment_methods)"))
    application.add_handler(CallbackQueryHandler(handle_payment_confirmation, pattern=r"^confirm_"))
    application.add_handler(CommandHandler("pay", demo_payment_command))