"""
User handlers module for MultiLangTranslator Bot
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Union

# Telegram imports
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, 
    InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
)
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, MessageHandler, filters, ConversationHandler

# Local imports - organize to avoid circular imports
try:
    from localization import get_text
    from data_handler import update_user_data, get_user_data
    from handlers.menu_handlers import create_main_keyboard
    from core.session import require_profile, get_session_manager, get_chat_partner, clear_chat_partner
    from core.database import get_database_manager
    from core.notifications import get_notification_manager
    from core.security import get_spam_protection
except ImportError as e:
    logging.error(f"Import error in user_handlers: {e}")
    # Define fallback functions
    def get_text(user_id, key, **kwargs):
        return f"Text for {key}"
    
    def create_main_keyboard(user_id):
        return [[KeyboardButton("Menu")]]

# Initialize logger
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> int:
    """
    Handle the /start command.
    
    This is the entry point for new users and returning users.
    """
    try:
        if not update or not update.effective_user:
            logger.error("start: Invalid update object")
            return
            
        user = update.effective_user
        user_id = str(user.id)
        
        # Get or create user session
        session_manager = get_session_manager()
        session = session_manager.get_session(user_id)
        
        # Get database manager
        db_manager = get_database_manager()

        # Get user data
        user_data = db_manager.get_user_data(user_id)

        # Check if user has a complete profile
        required_fields = ["language", "gender", "region", "country"]
        has_profile = all(field in user_data for field in required_fields)

        if has_profile:
            # User has a profile, show welcome back message
            language = user_data.get("language", "en")

            # Update user name if changed
            if user.first_name and (user_data.get("name") != user.first_name):
                db_manager.update_user_data(user_id, {"name": user.first_name})

            # Send welcome back message
            update.message.reply_text(get_text(user_id,
                                               "welcome_existing_user",
                                               name=user.first_name),
                                      parse_mode=ParseMode.HTML)

            # Show main menu
            keyboard = create_main_keyboard(user_id)
            update.message.reply_text(
                get_text(user_id, "main_menu"),
                reply_markup=ReplyKeyboardMarkup(keyboard)
            )

            return ConversationHandler.END
        else:
            # New user, start profile creation
            db_manager.update_user_data(user_id, {
                "name": user.first_name,
                "username": user.username,
                "language": "en",  # اللغة الافتراضية
                "profile_complete": False
            })

            # Show language selection
            languages = context.bot_data.get("supported_languages", {})
            keyboard = [[KeyboardButton(name)] for code, name in languages.items()]

            update.message.reply_text(get_text(user_id,
                                               "welcome_new_user",
                                               lang_code="en"),
                                      reply_markup=ReplyKeyboardMarkup(
                                          keyboard, one_time_keyboard=True))

            return context.bot_data.get("SELECT_LANG", 0)

    except Exception as e:
        logger.error(f"Error in start command for user {user_id if 'user_id' in locals() else 'unknown'}: {e}")
        try:
            update.message.reply_text("An error occurred. Please try again.")
        except:
            pass