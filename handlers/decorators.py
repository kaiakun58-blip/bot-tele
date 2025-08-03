#!/usr/bin/env python3
"""
Decorators for Telegram Anonymous Chat Bot
"""
import time
from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from config import OWNER_ID
from database import get_user_ban_status, unban_user, create_or_update_user

def check_ban_status(func):
    """Decorator to check if user is banned"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        is_banned, banned_until = get_user_ban_status(user_id)
        
        if is_banned:
            if banned_until > int(time.time()):
                ban_end = datetime.fromtimestamp(banned_until).strftime("%Y-%m-%d %H:%M")
                await update.message.reply_text(f"🚫 Kamu di-ban hingga {ban_end}")
                return
            else:
                # Unban user if ban period has expired
                unban_user(user_id)
        
        return await func(update, context, *args, **kwargs)
    return wrapper

def owner_only(func):
    """Decorator to restrict access to owner only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("❌ Hanya owner yang bisa menggunakan perintah ini.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def auto_update_profile(func):
    """Decorator to automatically update user profile"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        create_or_update_user(user.id, user.username)
        return await func(update, context, *args, **kwargs)
    return wrapper

def require_profile(func):
    """Decorator to require complete profile"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from database import is_profile_complete
        
        user_id = update.effective_user.id
        if not is_profile_complete(user_id):
            await update.message.reply_text(
                "❗ Kamu perlu melengkapi profil dulu. Gunakan /profile untuk melengkapi."
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper