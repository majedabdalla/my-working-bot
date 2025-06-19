"""
Modified main.py with DeepSeek integration for auto-fixing
and improved error handling for MultiLangTranslator Bot
"""
import requests
import traceback
import os
import json
import logging
import threading
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, filters,
                          ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

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
from handlers.menu_handlers import register_menu_handlers

# Fix: Import missing callback handler
from handlers.admin_handlers import toggle_premium_callback

# Workaround for Python 3.13 compatibility
try:
    import imghdr
except ImportError:
    import mimetypes as imghdr  # Fallback for Python 3.13+
# Configure logging FIRST to capture all logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__name__)

DEEPSEEK_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_deepseek_fix(error_message, code_snippet):
    """Get code fix from DeepSeek-R1 API"""
    # SECURITY: Get API key from environment
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("DeepSeek API key missing!")
        return None

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
        "Authorization": f"Bearer {api_key}",
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

def restart_bot():
    """Restart the bot process"""
    logger.info("Restarting bot after fix...")
    os.kill(os.getpid(), 9)  # Force restart

def fix_code_command(update: Update, context: CallbackContext) -> None:
    """Manually trigger code fixing"""
    if str(update.effective_user.id) not in context.bot_data.get("admin_ids", []):
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

    try:
        setup_data_directories()

        updater = Updater(token=config.BOT_TOKEN)
        dispatcher = updater.dispatcher

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

        # Load countries data - SINGLE LOAD ATTEMPT
        try:
            with open("data/regions_countries.json", "r", encoding="utf-8") as f:
                dispatcher.bot_data["countries_by_region"] = json.load(f)
        except Exception as e:
            logger.error(f"Couldn't load regions_countries.json: {e}")
            dispatcher.bot_data["countries_by_region"] = {}

        # Initialize core modules
        init_session_manager("data/sessions.json")
        init_database_manager(config.USER_DATA_FILE, config.PENDING_PAYMENTS_FILE)
        init_spam_protection()
        init_notification_manager(updater.bot, dispatcher.bot_data["admin_ids"])

        # Register handlers
        register_user_handlers(dispatcher)
        register_admin_handlers(dispatcher)
        register_search_handlers(dispatcher)
        register_payment_handlers(dispatcher)
        register_menu_handlers(dispatcher)
        
        # FIXED INDENTATION: Command handler registration
        dispatcher.add_handler(CommandHandler("fixcode", fix_code_command))
        
        # Fixed callback handler pattern
        dispatcher.add_handler(CallbackQueryHandler(
            toggle_premium_callback, 
            pattern="^toggle_premium_"
        ))

        dispatcher.add_error_handler(error_handler)
        updater.start_polling()
        logger.info("Bot started. Press Ctrl+C to stop.")

        # Use updater.idle() for proper shutdown handling
        updater.idle()

    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise

def error_handler(update, context):
    """Handle errors with DeepSeek auto-fix"""
    error = context.error
    tb = traceback.format_exc()
    
    logger.error(f"Update {update} caused error: {error}\n{tb}", exc_info=True)
    
    # Only attempt fixes for coding errors (not network/timeout issues)
    if not isinstance(error, (ConnectionError, TimeoutError)):
        current_file = os.path.abspath(__file__)
        with open(current_file, "r") as f:
            current_code = f.read()
        
        fixed_code = get_deepseek_fix(f"{error}\n\n{tb}", current_code)
        
        if fixed_code and apply_code_fix(current_file, fixed_code):
            # Notify admin
            if context.bot_data.get("admin_ids"):
                for admin_id in context.bot_data["admin_ids"]:
                    try:
                        context.bot.send_message(
                            admin_id,
                            f"🛠️ Applied auto-fix for error:\n{error}\nRestarting bot..."
                        )
                    except:
                        pass
            
            threading.Thread(target=restart_bot).start()
            return
    
    # Fallback error reporting
    try:
        if context.bot_data.get("admin_ids"):
            for admin_id in context.bot_data["admin_ids"]:
                try:
                    context.bot.send_message(
                        admin_id,
                        text=f"⚠️ Bot Error:\n{error}\n\nTraceback:\n{tb}"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        # Critical error - wait before restart
        threading.Event().wait(60)
        os.execv(sys.executable, ['python'] + sys.argv)
