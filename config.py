"""
Configuration settings for MultiLangTranslator Bot
"""

import os
from typing import Dict, List

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = os.getenv("ADMIN_ID", "YOUR_ADMIN_ID_HERE")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID", "YOUR_TARGET_GROUP_ID_HERE")
# Default Settings
DEFAULT_LANGUAGE = "en"
MAX_USERS_PER_SEARCH = 10
SESSION_TIMEOUT = 3600  # 1 hour in seconds
CHAT_HISTORY_LIMIT = 100  # Maximum messages to keep in history

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ar": "العربية",
    "hi": "हिंदी", 
    "id": "Bahasa Indonesia",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "ru": "Русский",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어"
}

# Premium Features
PREMIUM_FEATURES = [
    "priority_matching",
    "advanced_search",
    "unlimited_chats",
    "no_ads"
]

# Payment Configuration
PAYMENT_METHODS = {
    "payeer": {
        "account": "P1234567890",
        "name": "Payeer"
    },
    "bitcoin": {
        "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "name": "Bitcoin"
    }
}

# File Paths
USER_DATA_FILE = "user_data.json"
LOCALES_DIR = "locales"

# Rate Limiting
RATE_LIMIT_MESSAGES = 30  # messages per minute
RATE_LIMIT_SEARCHES = 5   # searches per hour

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Database Configuration (if using database instead of JSON)
DATABASE_URL = os.getenv("DATABASE_URL", None)
DATABASE_TYPE = "json"  # "json" or "postgresql" or "sqlite"

# Security Settings
ENABLE_SPAM_PROTECTION = True
MAX_MESSAGE_LENGTH = 4096
BLOCKED_WORDS = [
    # Add blocked words here
]

# Feature Flags
ENABLE_PREMIUM_FEATURES = True
ENABLE_ADMIN_NOTIFICATIONS = True
ENABLE_CHAT_LOGGING = True
ENABLE_USER_ANALYTICS = False

# Validation Rules
MIN_AGE = 13
MAX_AGE = 99
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50

# Countries List
COUNTRIES = [
    ("🇺🇸", "United States", "us"),
    ("🇬🇧", "United Kingdom", "gb"),
    ("🇨🇦", "Canada", "ca"),
    ("🇦🇺", "Australia", "au"),
    ("🇩🇪", "Germany", "de"),
    ("🇫🇷", "France", "fr"),
    ("🇪🇸", "Spain", "es"),
    ("🇮🇹", "Italy", "it"),
    ("🇷🇺", "Russia", "ru"),
    ("🇨🇳", "China", "cn"),
    ("🇯🇵", "Japan", "jp"),
    ("🇰🇷", "South Korea", "kr"),
    ("🇸🇦", "Saudi Arabia", "sa"),
    ("🇪🇬", "Egypt", "eg"),
    ("🇦🇪", "UAE", "ae"),
    ("🇮🇳", "India", "in"),
    ("🇵🇰", "Pakistan", "pk"),
    ("🇧🇩", "Bangladesh", "bd"),
    ("🇮🇩", "Indonesia", "id"),
    ("🇲🇾", "Malaysia", "my"),
    ("🇹🇭", "Thailand", "th"),
    ("🇻🇳", "Vietnam", "vn"),
    ("🇵🇭", "Philippines", "ph"),
    ("🇧🇷", "Brazil", "br"),
    ("🇲🇽", "Mexico", "mx"),
    ("🇦🇷", "Argentina", "ar"),
    ("🇨🇱", "Chile", "cl"),
    ("🇿🇦", "South Africa", "za"),
    ("🇳🇬", "Nigeria", "ng"),
    ("🇰🇪", "Kenya", "ke"),
    ("🇹🇷", "Turkey", "tr"),
    ("🇮🇷", "Iran", "ir"),
    ("🇮🇱", "Israel", "il"),
    ("🌍", "Other", "other")
]

# Gender Options
GENDERS = [
    ("👨", "Male", "male"),
    ("👩", "Female", "female")
]

# Language Options for Profile
PROFILE_LANGUAGES = [
    ("🇺🇸", "English", "en"),
    ("🇸🇦", "العربية", "ar"),
    ("🇮🇳", "हिंदी", "hi"),
    ("🇮🇩", "Bahasa Indonesia", "id"),
    ("🇪🇸", "Español", "es"),
    ("🇫🇷", "Français", "fr"),
    ("🇩🇪", "Deutsch", "de"),
    ("🇮🇹", "Italiano", "it"),
    ("🇷🇺", "Русский", "ru"),
    ("🇨🇳", "中文", "zh"),
    ("🇯🇵", "日本語", "ja"),
    ("🇰🇷", "한국어", "ko")
]

# Validation Functions
def validate_age(age_str: str) -> tuple[bool, int]:
    """Validate age input."""
    try:
        age = int(age_str)
        if MIN_AGE <= age <= MAX_AGE:
            return True, age
        return False, 0
    except ValueError:
        return False, 0

def validate_name(name: str) -> bool:
    """Validate name input."""
    if not name or len(name.strip()) < MIN_NAME_LENGTH:
        return False
    if len(name.strip()) > MAX_NAME_LENGTH:
        return False
    return True

def is_premium_feature(feature: str) -> bool:
    """Check if a feature requires premium subscription."""
    return feature in PREMIUM_FEATURES

# Environment Validation
def validate_config() -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("BOT_TOKEN not set")
    
    if ADMIN_ID == "YOUR_ADMIN_ID_HERE":
        errors.append("ADMIN_ID not set")
    
    if TARGET_GROUP_ID == "YOUR_TARGET_GROUP_ID_HERE":
        errors.append("TARGET_GROUP_ID not set")
    
    return errors
