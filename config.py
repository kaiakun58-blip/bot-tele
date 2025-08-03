#!/usr/bin/env python3
"""
Configuration file for Telegram Anonymous Chat Bot
"""
import os
from typing import List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, will use environment variables directly
    pass

# ========== Bot Configuration ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
    print("❌ Error: BOT_TOKEN tidak ditemukan!")
    print("📝 Cara setup:")
    print("1. Copy .env.example ke .env")
    print("2. Edit .env dan masukkan bot token dari @BotFather")
    print("3. Atau set environment variable: export BOT_TOKEN='your_actual_token'")
    exit(1)

OWNER_ID_STR = os.getenv("OWNER_ID", "123456789")
try:
    OWNER_ID = int(OWNER_ID_STR)
except ValueError:
    print("❌ Error: OWNER_ID harus berupa angka!")
    exit(1)

DB_PATH = os.getenv("DB_PATH", "bot_database.db")

# ========== NSFW Moderation ==========
NSFW_API_KEY = os.getenv("NSFW_API_KEY", "YOUR_MODERATECONTENT_API_KEY")
NSFW_API_URL = "https://api.moderatecontent.com/moderate/"

# ========== Pro Pricing ==========
PRO_WEEK_PRICE = int(os.getenv("PRO_WEEK_PRICE", "1000"))
PRO_MONTH_PRICE = int(os.getenv("PRO_MONTH_PRICE", "3500"))

# ========== Quiz Configuration ==========
QUIZ_LIMIT_WINNERS = int(os.getenv("QUIZ_LIMIT_WINNERS", "5"))

# ========== Constants ==========
LANGS: List[str] = ["English", "Indonesian"]
GENDERS: List[str] = ["Male", "Female", "Other"]
HOBBIES: List[str] = [
    "Music", "Sports", "Gaming", "Travel", "Reading", 
    "Cooking", "Drawing", "Coding", "Photography", "Other"
]

MODERATION_WORDS: List[str] = [
    "anjing", "babi", "kontol", "bangsat", "memek", "ngentot"
]

REPORT_REASONS: List[str] = [
    "Spam", "SARA", "Pornografi", "Kata Kasar", "Penipuan", "Lainnya"
]

# ========== Conversation States ==========
PROFILE_GENDER, PROFILE_AGE, PROFILE_BIO, PROFILE_PHOTO, PROFILE_LANG, PROFILE_HOBBY = range(6)
SEARCH_TYPE, SEARCH_GENDER, SEARCH_HOBBY, SEARCH_AGE_MIN, SEARCH_AGE_MAX = range(6, 11)
QUIZ_ANSWER = 11