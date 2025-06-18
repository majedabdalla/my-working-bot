"""
Modified main.py with improved error handling and data validation
for MultiLangTranslator Bot
"""
import requests
import traceback
import os
import json
import logging
import threading
from telegram import Update, Bot
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler,
                          CallbackContext)
import importlib
# Import configuration
import config

# Import core modules
from core.session import init_session_manager
from core.database import init_database_manager
from core.security import init_spam_protection
from core.notifications import init_notification_manager
from core.data_validation import initialize_data_directories, validate_and_repair_data_files

# Import handlers
from handlers.user_handlers import register_user_handlers
from handlers.admin_handlers import register_admin_handlers
from handlers.search_handlers import register_search_handlers
from handlers.payment_handlers import register_payment_handlers
from handlers.menu_handlers import register_menu_handlers, menu_command, handle_menu_selection

# Import web server for keep-alive
from keep_alive import start_server


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-fallback-key")
DEEPSEEK_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_deepseek_fix(error_message, code_snippet):
    """Get code fix from DeepSeek-R1 API"""
    prompt = f"""
    Fix this Telegram bot error in Python code:
    {error_message}
    
    Current code snippet:
    ```python
    {code_snippet}
    ```
    
    Return ONLY the fixed code block with no explanations.
    """
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"DeepSeek API error: {str(e)}")
        return None

def apply_code_fix(file_path, fixed_code):
    """Apply fixed code to file"""
    try:
        with open(file_path, "w") as f:
            f.write(fixed_code)
        logger.info(f"Applied fix to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to apply fix: {str(e)}")
        return False
# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_data_directories():
    """Setup necessary directories and files."""
    # Use the new data validation module to initialize all directories and files
    success = initialize_data_directories(config)

    if not success:
        logger.warning(
            "Some data directories or files could not be initialized properly."
        )

    # Validate and repair data files if needed
    validation_results = validate_and_repair_data_files(config)

    # Log validation results
    for file_name, is_valid in validation_results.items():
        if not is_valid:
            logger.warning(f"File validation failed for {file_name}")


def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")

    try:
        # Setup data directories and initialize files
        setup_data_directories()

        # Create the Updater and pass it your bot's token
        updater = Updater(token=config.BOT_TOKEN)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Initialize bot data
        dispatcher.bot_data.update({
            "supported_languages": config.SUPPORTED_LANGUAGES,
            "admin_ids": [str(config.ADMIN_ID)],
            "target_group_id": config.TARGET_GROUP_ID,
            "payeer_account": config.PAYEER_ACCOUNT,
            "bitcoin_address": config.BITCOIN_ADDRESS,

            # Conversation states
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

        with open("data/regions_countries.json", "r", encoding="utf-8") as f:
            dispatcher.bot_data["countries_by_region"] = json.load(f)
        # Load countries by region from file
        try:
            with open("data/regions_countries.json", "r",
                      encoding="utf-8") as f:
                dispatcher.bot_data["countries_by_region"] = json.load(f)
        except Exception as e:
            logger.warning(f"Couldn't load regions_countries.json: {e}")
            dispatcher.bot_data["countries_by_region"] = {}

        # Initialize core modules
        session_manager = init_session_manager("data/sessions.json")
        db_manager = init_database_manager(config.USER_DATA_FILE,
                                           config.PENDING_PAYMENTS_FILE)
        spam_protection = init_spam_protection()
        notification_manager = init_notification_manager(
            updater.bot, dispatcher.bot_data["admin_ids"])

        # Register handlers
        register_user_handlers(dispatcher)
        register_admin_handlers(dispatcher)
        register_search_handlers(dispatcher)
        register_payment_handlers(dispatcher)

        # Register menu handlers (now includes handler registration internally)
        register_menu_handlers(dispatcher)
        from telegram.ext import MessageHandler, Filters
      dispatcher.add_handler(CommandHandler("fixcode", fix_code_command))


        # Register callback query handler for premium toggle
        dispatcher.add_handler(CallbackQueryHandler(toggle_premium_callback, pattern="^toggle_premium_"))

        # Add error handler
        dispatcher.add_error_handler(error_handler)

        # Start the Bot
        updater.start_polling()

        # Log that the bot has started
        logger.info("Bot started. Press Ctrl+C to stop.")
      

        # Keep the main thread running so the bot doesn't stop
        # We use threading event instead of just updater.idle() because we need to return control to Flask
        import threading
        stop_event = threading.Event()
        return stop_event  # Return the event so it can be used to stop the bot if needed

    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise


def error_handler(update, context):
    """Handle errors with DeepSeek auto-fix"""
    error = context.error
    tb = traceback.format_exc()
    
    logger.error(f"Update {update} caused error: {error}\n{tb}", exc_info=True)
    
    # Get current code
    current_file = os.path.abspath(__file__)
    with open(current_file, "r") as f:
        current_code = f.read()
    
    # Get fix from DeepSeek
    fixed_code = get_deepseek_fix(f"{error}\n\n{tb}", current_code)
    
    if fixed_code:
        # Apply fix and restart
        if apply_code_fix(current_file, fixed_code):
            # Notify admin
            if context.bot_data and "admin_ids" in context.bot_data:
                for admin_id in context.bot_data["admin_ids"]:
                    try:
                        context.bot.send_message(
                            admin_id,
                            f"🛠️ Applied auto-fix for error:\n{error}\nRestarting bot..."
                        )
                    except:
                        pass
            
            # Graceful restart
            threading.Thread(target=restart_bot).start()
            return
    
    # Fallback to original error handling
    try:
        if context.bot_data and "admin_ids" in context.bot_data:
            admin_ids = context.bot_data["admin_ids"]
            for admin_id in admin_ids:
                try:
                    context.bot.send_message(
                        chat_id=admin_id,
                        text=f"⚠️ Bot Error:\n{error}\n\nTraceback:\n{tb}"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error in error handler: {e}", exc_info=True)

def restart_bot():
    """Restart the bot process"""
    logger.info("Restarting bot after fix...")
    os.kill(os.getpid(), 9)  # Force restart

# Global variable to store the bot thread and stop event
bot_thread = None
bot_stop_event = None

def fix_code_command(update: Update, context: CallbackContext) -> None:
    """Manually trigger code fixing"""
    if str(update.effective_user.id) not in context.bot_data["admin_ids"]:
        update.message.reply_text("❌ Admin only command")
        return
    
    update.message.reply_text("🔄 Analyzing code for improvements...")
    
    current_file = os.path.abspath(__file__)
    with open(current_file, "r") as f:
        current_code = f.read()
    
    prompt = """
    Review this Telegram bot code and improve it:
    - Fix any bugs or potential issues
    - Optimize performance
    - Add proper error handling
    - Follow PEP8 guidelines
    
    Return ONLY the improved code block.
    """
    
    fixed_code = get_deepseek_fix(prompt, current_code)
    
    if fixed_code and apply_code_fix(current_file, fixed_code):
        update.message.reply_text("✅ Code improved! Restarting bot...")
        threading.Thread(target=restart_bot).start()
    else:
        update.message.reply_text("❌ Failed to improve code")
      
def start_bot_in_thread():
    """Start the bot in a separate thread and ensure it stays running."""
    global bot_thread, bot_stop_event

    # If a bot thread is already running, do nothing
    if bot_thread and bot_thread.is_alive():
        logger.info("Bot is already running.")
        return

    # If we have a previous stop event, set it to stop any zombie threads
    if bot_stop_event:
        bot_stop_event.set()

    # Function to run in the thread
    def bot_worker():
        try:
            # Start the bot and get the stop event
            event = main()
            # Wait for the stop event to be set
            event.wait()
        except Exception as e:
            logger.error(f"Error in bot thread: {e}", exc_info=True)

            # Try to restart the bot after a delay if it crashes
            import time
            time.sleep(10)
            logger.info("Attempting to restart bot after crash...")
            start_bot_in_thread()

    # Create and start the thread
    bot_thread = threading.Thread(target=bot_worker, daemon=True)
    bot_thread.start()
    logger.info("Bot thread started")


# When this module is imported, automatically start the bot
#start_bot_in_thread()

# Export app for the gunicorn server
from app import app

if __name__ == "__main__":
    try:
        main().wait()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
