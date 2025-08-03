#!/usr/bin/env python3
"""
Dynamic keyboard layouts for ObrolanId
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(is_pro=False):
    """Get dynamic main menu keyboard based on user status"""
    if is_pro:
        return ReplyKeyboardMarkup([
            [KeyboardButton("🔍 Find Partner"), KeyboardButton("🎯 Search Pro")],
            [KeyboardButton("👤 My Profile"), KeyboardButton("📊 Stats")],
            [KeyboardButton("🎮 Play Quiz"), KeyboardButton("🔍 Help")],
        ], resize_keyboard=True)
    else:
        return ReplyKeyboardMarkup([
            [KeyboardButton("🔍 Find Partner"), KeyboardButton("👥 Search by Gender")],
            [KeyboardButton("👤 My Profile"), KeyboardButton("✨ Upgrade to Pro")],
            [KeyboardButton("📊 Stats"), KeyboardButton("🔍 Help")],
        ], resize_keyboard=True)

def get_chat_menu():
    """Get chat session keyboard - focused on chat controls"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("⏭️ Next"), KeyboardButton("🛑 Stop")],
        [KeyboardButton("🔒 Secret Mode"), KeyboardButton("⭐ Feedback")],
    ], resize_keyboard=True)

def get_group_menu():
    """Get group chat menu keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Leave Group"), KeyboardButton("Poll")],
    ], resize_keyboard=True)

def get_gender_keyboard():
    """Get gender selection keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Male"), KeyboardButton("Female")],
        [KeyboardButton("Other")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_language_keyboard():
    """Get language selection keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("English"), KeyboardButton("Indonesian")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_hobbies_keyboard():
    """Get hobbies selection keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Music"), KeyboardButton("Sports"), KeyboardButton("Gaming")],
        [KeyboardButton("Travel"), KeyboardButton("Reading"), KeyboardButton("Cooking")],
        [KeyboardButton("Drawing"), KeyboardButton("Coding"), KeyboardButton("Photography")],
        [KeyboardButton("Other")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_gender_search_keyboard():
    """Get gender search keyboard for non-Pro users"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("👨 Male"), KeyboardButton("👩 Female")],
        [KeyboardButton("🌈 Other"), KeyboardButton("🎲 Any Gender")],
        [KeyboardButton("🔙 Back to Menu")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_context_keyboard(user_id, is_in_chat=False, is_pro=False):
    """Get context-aware keyboard based on user session"""
    if is_in_chat:
        # User is in chat session - show chat controls
        return get_chat_menu()
    else:
        # User is in main menu - show main options
        return get_main_menu(is_pro)