"""
Configuration file for MultiLangTranslator Bot
"""

import os
from typing import List

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'MultiLangTranslatorBot')

# Language Configuration
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "ar", "hi", "id"]

# Admin Configuration
ADMIN_IDS = [
    int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') 
    if x.strip().isdigit()
]

# Database Configuration (for future use)
DATABASE_URL = os.getenv('DATABASE_URL')

# Feature Flags
ENABLE_PREMIUM = True
ENABLE_SEARCH = True
ENABLE_NOTIFICATIONS = True

# Rate Limiting
MAX_MESSAGES_PER_MINUTE = 20
MAX_SEARCHES_PER_HOUR = 10

# Premium Configuration
PREMIUM_PRICE = 5.00  # USD
PREMIUM_DURATION_DAYS = 30

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Webhook Configuration (for production)
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PORT = int(os.getenv('PORT', 8443))

print(f"Config loaded - Bot token: {'✅ Set' if BOT_TOKEN else '❌ Missing'}")
print(f"Admin IDs: {ADMIN_IDS}")
print(f"Default language: {DEFAULT_LANGUAGE}")
