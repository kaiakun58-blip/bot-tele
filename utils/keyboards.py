#!/usr/bin/env python3
"""
Keyboard layouts for Telegram Anonymous Chat Bot
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    """Get main menu keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Find a partner"), KeyboardButton("Search Pro")],
        [KeyboardButton("My Profile"), KeyboardButton("Upgrade to Pro")],
        [KeyboardButton("Play Quiz"), KeyboardButton("Join Group")],
    ], resize_keyboard=True)

def get_chat_menu():
    """Get chat menu keyboard"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("Next"), KeyboardButton("Stop"), KeyboardButton("Feedback"), KeyboardButton("Poll")],
        [KeyboardButton("Secret Mode")],
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