"""
Menu handlers for MultiLangTranslator Bot
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from localization import get_text
from data_handler import get_user_data
from handlers.search_handlers import search_partner, disconnect_chat

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

def handle_menu_button(update: Update, context: CallbackContext) -> None:
    """Handle menu button presses."""
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text
    
    user_data = get_user_data(user_id)
    
    if not user_data.get("profile_complete", False):
        update.message.reply_text(
            get_text(user_id, "profile_incomplete"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Handle different menu options
    if text == get_text(user_id, "menu_search"):
        search_partner(update, context)
        
    elif text == get_text(user_id, "menu_profile"):
        show_profile(update, context)
        
    elif text == get_text(user_id, "menu_settings"):
        show_settings(update, context)
        
    elif text == get_text(user_id, "menu_help"):
        show_help(update, context)
        
    elif text == get_text(user_id, "menu_payment"):
        show_payment_info(update, context)
        
    elif text == get_text(user_id, "disconnect"):
        disconnect_chat(update, context)
        
    else:
        # Unknown menu option
        update.message.reply_text(
            get_text(user_id, "error_occurred"),
            parse_mode=ParseMode.HTML
        )

def show_profile(update: Update, context: CallbackContext) -> None:
    """Show user profile information."""
    user = update.effective_user
    user_id = str(user.id)
    
    user_data = get_user_data(user_id)
    
    profile_text = get_text(
        user_id, "profile_info",
        name=user_data.get("name", "Unknown"),
        age=user_data.get("age", "Unknown"),
        gender=user_data.get("gender", "Unknown"),
        country=user_data.get("country", "Unknown"),
        language=user_data.get("language", "Unknown")
    )
    
    update.message.reply_text(
        profile_text,
        parse_mode=ParseMode.HTML
    )

def show_settings(update: Update, context: CallbackContext) -> None:
    """Show settings menu."""
    user = update.effective_user
    user_id = str(user.id)
    
    update.message.reply_text(
        get_text(user_id, "settings_menu"),
        parse_mode=ParseMode.HTML
    )

def show_help(update: Update, context: CallbackContext) -> None:
    """Show help information."""
    user = update.effective_user
    user_id = str(user.id)
    
    update.message.reply_text(
        get_text(user_id, "help_text"),
        parse_mode=ParseMode.HTML
    )

def show_payment_info(update: Update, context: CallbackContext) -> None:
    """Show payment information."""
    user = update.effective_user
    user_id = str(user.id)
    
    update.message.reply_text(
        get_text(user_id, "payment_info"),
        parse_mode=ParseMode.HTML
    )

def hide_menu(update: Update, context: CallbackContext) -> None:
    """Hide the menu keyboard."""
    user = update.effective_user
    user_id = str(user.id)
    
    update.message.reply_text(
        get_text(user_id, "menu_hidden"),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML
    )
