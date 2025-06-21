"""
Main entry point for MultiLangTranslator Bot
"""

import logging
import os
import threading
import time
import sys
from flask import Flask, jsonify
from telegram.ext import Application
from telegram.error import Conflict, NetworkError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app for health checks
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "MultiLangTranslator Bot",
        "message": "Bot is active and polling for updates"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/ping')
def ping():
    return jsonify({"status": "pong"})

def run_flask():
    """Run Flask app in a separate thread"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

async def error_handler(update, context):
    """Handle errors in the bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if isinstance(context.error, Conflict):
        logger.error("Bot conflict detected - another instance may be running")
        return
        
    if isinstance(context.error, NetworkError):
        logger.error("Network error occurred, bot will retry automatically")
        return
    
    # Handle other errors
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

def register_handlers_safely(application):
    """Register handlers with detailed error reporting"""
    handlers_registered = []
    
    # Try to register user handlers
    try:
        logger.info("Attempting to register user handlers...")
        from handlers.user_handlers import register_user_handlers
        register_user_handlers(application)
        handlers_registered.append("user_handlers")
        logger.info("✅ User handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register user handlers: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Try to register callback handlers
    try:
        logger.info("Attempting to register callback handlers...")
        from handlers.callback_handlers import register_callback_handlers
        register_callback_handlers(application)
        handlers_registered.append("callback_handlers")
        logger.info("✅ Callback handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register callback handlers: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Try to register menu handlers
    try:
        logger.info("Attempting to register menu handlers...")
        from handlers.menu_handlers import register_menu_handlers
        register_menu_handlers(application)
        handlers_registered.append("menu_handlers")
        logger.info("✅ Menu handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register menu handlers: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Try to register search handlers
    try:
        logger.info("Attempting to register search handlers...")
        from handlers.search_handlers import register_search_handlers
        register_search_handlers(application)
        handlers_registered.append("search_handlers")
        logger.info("✅ Search handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register search handlers: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Try to register payment handlers
    try:
        logger.info("Attempting to register payment handlers...")
        from handlers.payment_handlers import register_payment_handlers
        register_payment_handlers(application)
        handlers_registered.append("payment_handlers")
        logger.info("✅ Payment handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register payment handlers: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Try to register admin handlers
    try:
        logger.info("Attempting to register admin handlers...")
        from handlers.admin_handlers import register_admin_handlers
        register_admin_handlers(application)
        handlers_registered.append("admin_handlers")
        logger.info("✅ Admin handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register admin handlers: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info(f"Successfully registered handlers: {handlers_registered}")
    
    if not handlers_registered:
        logger.error("❌ NO HANDLERS WERE REGISTERED! Bot will not respond to any commands.")
        return False
    
    return True

def main():
    """Main function to start the bot"""
    try:
        # Start Flask server in background thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"Flask server started on port {os.environ.get('PORT', 10000)}")
        
        # Get bot token
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise ValueError("BOT_TOKEN environment variable not set")
        
        logger.info("Creating Telegram application...")
        
        # Create application
        application = (
            Application.builder()
            .token(token)
            .concurrent_updates(True)
            .build()
        )
        
        # Add error handler
        application.add_error_handler(error_handler)
        logger.info("Error handler added")
        
        # Register handlers with detailed error reporting
        logger.info("Starting handler registration...")
        success = register_handlers_safely(application)
        
        if not success:
            logger.error("Failed to register any handlers. Exiting.")
            sys.exit(1)
        
        # Wait a bit before starting
        logger.info("Waiting 3 seconds before starting bot...")
        time.sleep(3)
        
        # Start the bot
        logger.info("🚀 Starting Telegram bot...")
        application.run_polling(
            drop_pending_updates=True,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"💥 Failed to start bot: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

if __name__ == '__main__':
    main()
