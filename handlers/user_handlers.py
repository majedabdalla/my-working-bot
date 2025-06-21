"""
Enhanced user handlers module for MultiLangTranslator Bot
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from localization import get_text, get_user_language
from data_handler import get_user_data, update_user_data
from core.session import get_session_manager
import config

logger = logging.getLogger(__name__)

def create_main_keyboard(user_id: str, language: str = "en") -> list:
    """Create main menu keyboard based on user's language."""
    keyboard = [
        [KeyboardButton(get_text(user_id, "menu_search"))],
        [KeyboardButton(get_text(user_id, "menu_profile")), KeyboardButton(get_text(user_id, "menu_settings"))],
        [KeyboardButton(get_text(user_id, "menu_help")), KeyboardButton(get_text(user_id, "menu_payment"))],
        [KeyboardButton(get_text(user_id, "disconnect"))]
    ]
    return keyboard

def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command - profile setup."""
    user = update.effective_user
    user_id = str(user.id)
    
    # Initialize user data
    user_data = get_user_data(user_id)
    if not user_data:
        user_data = {
            "user_id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language": config.DEFAULT_LANGUAGE,
            "profile_complete": False
        }
        update_user_data(user_id, user_data)
    
    # Get session manager
    session_manager = get_session_manager()
    
    # Check if profile is already complete
    if user_data.get("profile_complete", False):
        # Show main menu
        keyboard = create_main_keyboard(user_id, user_data.get("language", "en"))
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        
        profile_text = get_text(
            user_id, "profile_complete",
            name=user_data.get("name", "Unknown"),
            age=user_data.get("age", "Unknown"),
            gender=user_data.get("gender", "Unknown"),
            country=user_data.get("country", "Unknown"),
            language=user_data.get("language", "Unknown")
        )
        
        update.message.reply_text(
            profile_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return
    
    # Start profile setup
    session_manager.set_session_state(user_id, "awaiting_language")
    
    # Language selection keyboard
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")],
        [InlineKeyboardButton("🇯🇵 日本語", callback_data="lang_ja")],
        [InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        get_text(user_id, "welcome"),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

def menu_command(update: Update, context: CallbackContext) -> None:
    """Handle /menu command."""
    user = update.effective_user
    user_id = str(user.id)
    
    user_data = get_user_data(user_id)
    
    if not user_data.get("profile_complete", False):
        update.message.reply_text(
            get_text(user_id, "profile_incomplete"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Create and send main menu
    keyboard = create_main_keyboard(user_id, user_data.get("language", "en"))
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    update.message.reply_text(
        get_text(user_id, "main_menu"),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

def handle_language_selection(update: Update, context: CallbackContext) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Extract language code
    lang_code = query.data.replace("lang_", "")
    
    # Update user data
    user_data = get_user_data(user_id)
    user_data["language"] = lang_code
    update_user_data(user_id, user_data)
    
    # Get session manager
    session_manager = get_session_manager()
    session_manager.set_session_state(user_id, "awaiting_name")
    
    # Answer callback and ask for name
    query.answer()
    query.edit_message_text(
        get_text(user_id, "language_set"),
        parse_mode=ParseMode.HTML
    )
    
    # Ask for name
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=get_text(user_id, "enter_name"),
        parse_mode=ParseMode.HTML
    )

def handle_text_input(update: Update, context: CallbackContext) -> None:
    """Handle text input during profile setup."""
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text.strip()
    
    # Get session manager
    session_manager = get_session_manager()
    state = session_manager.get_session_state(user_id)
    
    if state == "awaiting_name":
        # Validate name
        if len(text) < 2 or len(text) > 50:
            update.message.reply_text(
                "❌ Please enter a valid name (2-50 characters):",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Save name and ask for age
        user_data = get_user_data(user_id)
        user_data["name"] = text
        update_user_data(user_id, user_data)
        
        session_manager.set_session_state(user_id, "awaiting_age")
        update.message.reply_text(
            get_text(user_id, "enter_age"),
            parse_mode=ParseMode.HTML
        )
        
    elif state == "awaiting_age":
        # Validate age
        try:
            age = int(text)
            if age < 13:
                update.message.reply_text(
                    get_text(user_id, "age_too_young"),
                    parse_mode=ParseMode.HTML
                )
                return
            elif age > 99:
                update.message.reply_text(
                    get_text(user_id, "invalid_age"),
                    parse_mode=ParseMode.HTML
                )
                return
        except ValueError:
            update.message.reply_text(
                get_text(user_id, "invalid_age"),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Save age and ask for gender
        user_data = get_user_data(user_id)
        user_data["age"] = age
        update_user_data(user_id, user_data)
        
        session_manager.set_session_state(user_id, "awaiting_gender")
        
        # Gender selection keyboard
        keyboard = [
            [InlineKeyboardButton(get_text(user_id, "male"), callback_data="gender_male")],
            [InlineKeyboardButton(get_text(user_id, "female"), callback_data="gender_female")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            get_text(user_id, "select_gender"),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

def handle_gender_selection(update: Update, context: CallbackContext) -> None:
    """Handle gender selection callback."""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Extract gender
    gender = query.data.replace("gender_", "")
    
    # Update user data
    user_data = get_user_data(user_id)
    user_data["gender"] = gender
    update_user_data(user_id, user_data)
    
    # Get session manager
    session_manager = get_session_manager()
    session_manager.set_session_state(user_id, "awaiting_country")
    
    # Answer callback
    query.answer()
    query.edit_message_text(
        f"✅ Gender: {get_text(user_id, gender)}",
        parse_mode=ParseMode.HTML
    )
    
    # Country selection keyboard
    countries = [
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
        ("🇧🇷", "Brazil", "br"),
        ("🇲🇽", "Mexico", "mx"),
        ("🇮🇳", "India", "in"),
        ("🌍", "Other", "other")
    ]
    
    keyboard = []
    for flag, name, code in countries:
        keyboard.append([InlineKeyboardButton(f"{flag} {name}", callback_data=f"country_{code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=get_text(user_id, "select_country"),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

def handle_country_selection(update: Update, context: CallbackContext) -> None:
    """Handle country selection callback."""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Extract country code
    country_code = query.data.replace("country_", "")
    
    # Country mapping
    country_names = {
        "us": "United States",
        "gb": "United Kingdom", 
        "ca": "Canada",
        "au": "Australia",
        "de": "Germany",
        "fr": "France",
        "es": "Spain",
        "it": "Italy",
        "ru": "Russia",
        "cn": "China",
        "jp": "Japan",
        "kr": "South Korea",
        "sa": "Saudi Arabia",
        "eg": "Egypt",
        "br": "Brazil",
        "mx": "Mexico",
        "in": "India",
        "other": "Other"
    }
    
    country_name = country_names.get(country_code, "Unknown")
    
    # Update user data and complete profile
    user_data = get_user_data(user_id)
    user_data["country"] = country_name
    user_data["country_code"] = country_code
    user_data["profile_complete"] = True
    update_user_data(user_id, user_data)
    
    # Clear session state
    session_manager = get_session_manager()
    session_manager.clear_session(user_id)
    
    # Answer callback
    query.answer()
    query.edit_message_text(
        f"✅ Country: {country_name}",
        parse_mode=ParseMode.HTML
    )
    
    # Show completed profile and main menu
    keyboard = create_main_keyboard(user_id, user_data.get("language", "en"))
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    profile_text = get_text(
        user_id, "profile_complete",
        name=user_data.get("name", "Unknown"),
        age=user_data.get("age", "Unknown"),
        gender=user_data.get("gender", "Unknown"),
        country=country_name,
        language=user_data.get("language", "Unknown")
    )
    
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=profile_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )