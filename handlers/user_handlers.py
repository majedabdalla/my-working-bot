"""
User handlers module for MultiLangTranslator Bot
"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
from telegram.ext import CallbackContext

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

def help_command(update: Update, context: CallbackContext):
    """Handle /help command"""
    pass

def profile_command(update: Update, context: CallbackContext):
    """Handle /profile command"""
    pass

def settings_command(update: Update, context: CallbackContext):
    """Handle /settings command"""
    pass

def cancel_command(update: Update, context: CallbackContext):
    """Handle /cancel command"""
    pass

def register_user_handlers(application):
    """Register all user handlers with the application"""
    try:
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("settings", settings_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.DOCUMENT, handle_document))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        logger.info("User handlers registered successfully")
        
    except Exception as e:
        logger.error(f"Error registering user handlers: {e}")
        raise

def handle_text_message(update: Update, context: CallbackContext):
    """Handle text messages"""
    try:
        # Your text message handling logic
        pass
    except Exception as e:
        logger.error(f"Error handling text message: {e}")

def handle_contact(update: Update, context: CallbackContext):
    """Handle contact messages"""
    try:
        # Your contact handling logic
        pass
    except Exception as e:
        logger.error(f"Error handling contact: {e}")

def handle_photo(update: Update, context: CallbackContext):
    """Handle photo messages"""
    try:
        # Your photo handling logic
        pass
    except Exception as e:
        logger.error(f"Error handling photo: {e}")

def handle_document(update: Update, context: CallbackContext):
    """Handle document messages"""
    try:
        # Your document handling logic
        pass
    except Exception as e:
        logger.error(f"Error handling document: {e}")

def handle_callback_query(update: Update, context: CallbackContext):
    """Handle callback queries"""
    try:
        # Your callback query handling logic
        pass
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")