"""
Main entry point for MultiLangTranslator Bot
"""

import logging
import os
import threading
import time
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

def error_handler(update, context):
    """Handle errors in the bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if isinstance(context.error, Conflict):
        logger.error("Bot conflict detected - another instance may be running")
        # Don't restart automatically to avoid infinite conflicts
        return
    
    if isinstance(context.error, NetworkError):
        logger.error("Network error occurred, bot will retry automatically")
        return

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
        
        # Create application with conflict handling
        application = (
            Application.builder()
            .token(token)
            .concurrent_updates(True)
            .build()
        )
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Register handlers with error handling
        try:
            from handlers.user_handlers import register_user_handlers
            register_user_handlers(application)
            logger.info("User handlers registered")
        except ImportError as e:
            logger.error(f"Failed to import user handlers: {e}")
        
        try:
            from handlers.admin_handlers import register_admin_handlers
            register_admin_handlers(application)
            logger.info("Admin handlers registered")
        except ImportError as e:
            logger.error(f"Failed to import admin handlers: {e}")
        
        try:
            from handlers.search_handlers import register_search_handlers
            register_search_handlers(application)
            logger.info("Search handlers registered")
        except ImportError as e:
            logger.error(f"Failed to import search handlers: {e}")
        
        try:
            from handlers.payment_handlers import register_payment_handlers
            register_payment_handlers(application)
            logger.info("Payment handlers registered")
        except ImportError as e:
            logger.error(f"Failed to import payment handlers: {e}")
        
        try:
            from handlers.menu_handlers import register_menu_handlers
            register_menu_handlers(application)
            logger.info("Menu handlers registered")
        except ImportError as e:
            logger.error(f"Failed to import menu handlers: {e}")
        
        # Wait a bit before starting to ensure any previous instance has stopped
        logger.info("Waiting 10 seconds before starting bot to avoid conflicts...")
        time.sleep(10)
        
        # Start the bot with retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Starting Telegram bot (attempt {retry_count + 1}/{max_retries})...")
                application.run_polling(
                    drop_pending_updates=True,
                    close_loop=False
                )
                break  # If successful, break out of retry loop
                
            except Conflict as e:
                retry_count += 1
                logger.error(f"Conflict error (attempt {retry_count}): {e}")
                
                if retry_count < max_retries:
                    wait_time = 30 * retry_count  # Exponential backoff
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Please ensure no other bot instances are running.")
                    raise
                    
            except Exception as e:
                logger.error(f"Unexpected error starting bot: {e}")
                raise
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
