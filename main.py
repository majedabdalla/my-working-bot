"""
Stable version of MultiLangTranslator Bot without auto-fix feature
"""
import traceback
import os
import json
import logging
from logging.handlers import RotatingFileHandler  # ADD THIS
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import sys

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# File handler (rotating)
file_handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Workaround for Python 3.13 compatibility
try:
    from PIL import Image
    
    def get_image_type(file_path):
        try:
            with Image.open(file_path) as img:
                return img.format
        except Exception:
            return None

except ImportError as e:
    import mimetypes
    logger.error(f"Image processing imports failed: {e}")
    
    def get_image_type(file_path):
        try:
            mime, _ = mimetypes.guess_type(file_path)
            return mime.split('/')[-1].upper() if mime else None
        except Exception:
            return None

# Import configuration
import config

# Import core modules
from core.session import init_session_manager
from core.database import init_database_manager
try:
    from core.security import init_spam_protection, get_spam_protection
except ImportError as e:
    print(f"Import error: {e}")
    # Create fallback functions
    def init_spam_protection():
        pass
    
    def get_spam_protection():
        return None
from core.notifications import init_notification_manager
from core.data_validation import initialize_data_directories, validate_and_repair_data_files

# Import handlers
from handlers.user_handlers import register_user_handlers
from handlers.admin_handlers import register_admin_handlers
from handlers.search_handlers import register_search_handlers
from handlers.payment_handlers import register_payment_handlers
from handlers.menu_handlers import register_menu_handlers
from handlers.admin_handlers import toggle_premium_callback

async def maintenance_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle maintenance mode"""
    if config.MAINTENANCE_MODE:
        if update.message:
            await update.message.reply_text("⚠️ Bot is under maintenance. Please try again later.")
        elif update.callback_query:
            await update.callback_query.answer("Bot is under maintenance. Please try again later.", show_alert=True)
        return True  # Block further processing
    return False  # Continue processing

def setup_data_directories():
    """Setup necessary directories and files."""
    success = initialize_data_directories(config)
    if not success:
        logger.warning("Some data directories/files could not be initialized")

    validation_results = validate_and_repair_data_files(config)
    for file_name, is_valid in validation_results.items():
        if not is_valid:
            logger.warning(f"File validation failed for {file_name}")

def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")
    
    # Create lock file to prevent multiple instances
    lock_file = 'bot.lock'
    if os.path.exists(lock_file):
        logger.error("Another bot instance is already running. Exiting.")
        return
    
    with open(lock_file, 'w') as f:
        f.write("1")
    
    try:
        setup_data_directories()

        application = ApplicationBuilder().token(config.BOT_TOKEN).build()
        dispatcher = application

        # Initialize bot data
        dispatcher.bot_data.update({
            "supported_languages": config.SUPPORTED_LANGUAGES,
            "admin_ids": [str(config.ADMIN_ID)],
            "target_group_id": config.TARGET_GROUP_ID,
            "payeer_account": config.PAYEER_ACCOUNT,
            "bitcoin_address": config.BITCOIN_ADDRESS,
            "SELECT_LANG": config.SELECT_LANG,
            "SELECT_GENDER": config.SELECT_GENDER,
            "SELECT_REGION": config.SELECT_REGION,
            "SELECT_COUNTRY_IN_REGION": config.SELECT_COUNTRY_IN_REGION,
            "SEARCH_PARTNER_LANG": config.SEARCH_PARTNER_LANG,
            "SEARCH_PARTNER_GENDER": config.SEARCH_PARTNER_GENDER,
            "SEARCH_PARTNER_REGION": config.SEARCH_PARTNER_REGION,
            "SEARCH_PARTNER_COUNTRY": config.SEARCH_PARTNER_COUNTRY,
            "PAYMENT_PROOF": config.PAYMENT_PROOF
        })

        # Load countries data
        try:
            with open("data/regions_countries.json", "r", encoding="utf-8") as f:
                dispatcher.bot_data["countries_by_region"] = json.load(f)
        except Exception as e:
            logger.error(f"Couldn't load regions_countries.json: {e}")
            dispatcher.bot_data["countries_by_region"] = {}

        # Initialize core modules
        init_session_manager("data/sessions.json")
        init_database_manager(config.USER_DATA_FILE, config.PENDING_PAYMENTS_FILE)
        init_spam_protection(application)
        init_notification_manager(application.bot, dispatcher.bot_data["admin_ids"])
        
        # ADD MAINTENANCE HANDLERS HERE
        dispatcher.add_handler(MessageHandler(filters.ALL, maintenance_check), group=-1)
        dispatcher.add_handler(CallbackQueryHandler(maintenance_check), group=-1)

        # Register handlers
        register_user_handlers(dispatcher)
        register_admin_handlers(dispatcher)
        register_search_handlers(dispatcher)
        register_payment_handlers(dispatcher)
        register_menu_handlers(dispatcher)
        
        # Fixed callback handler pattern
        dispatcher.add_handler(CallbackQueryHandler(
            toggle_premium_callback, 
            pattern="^toggle_premium_"
        ))

        # Add error handler
        application.add_error_handler(error_handler)
        
        logger.info("Bot started. Press Ctrl+C to stop.")
        application.run_polling(drop_pending_updates=True)

    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
    finally:
        # Clean up lock file
        if os.path.exists(lock_file):
            os.remove(lock_file)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors gracefully"""
    error = context.error
    tb = traceback.format_exc()
    
    # Log the error
    logger.error(f"Error: {error}\nTraceback:\n{tb}")
    
    # Notify admin (shortened message)
    try:
        if context.bot_data.get("admin_ids"):
            for admin_id in context.bot_data["admin_ids"]:
                try:
                    error_msg = f"⚠️ Bot Error:\n{type(error).__name__}: {str(error)[:200]}"
                    await context.bot.send_message(admin_id, text=error_msg)
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

if __name__ == "__main__":
    try:
        main()  # FIXED: Call without arguments
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
