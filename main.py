"""
Main entry point for MultiLangTranslator
"""

import logging
import os
import threading
import time
import asyncio
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
    """Handle errors in the bot - ASYNC VERSION"""
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

def initialize_core_modules():
    """Initialize all core modules"""
    try:
        # Initialize session manager
        from core.session import init_session_manager
        init_session_manager()
        logger.info("Session manager initialized")
        
        # Initialize database manager
        from core.database import init_database_manager
        init_database_manager()
        logger.info("Database manager initialized")
        
        # Initialize other core modules
        from core.security import init_spam_protection
        init_spam_protection()
        logger.info("Spam protection initialized")
        
        from core.notifications import init_notification_manager
        init_notification_manager()
        logger.info("Notification manager initialized")
        
    except ImportError as e:
        logger.warning(f"Some core modules not available: {e}")
    except Exception as e:
        logger.error(f"Error initializing core modules: {e}")

def main():
    """Main function to start the bot"""
    try:
        # Start Flask server in background thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"Flask server started on port {os.environ.get('PORT', 10000)}")
        
        # Initialize core modules
        initialize_core_modules()
        
        # Get bot token
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise ValueError("BOT_TOKEN environment variable not set")
        
        # Create application
        application = (
            Application.builder()
            .token(token)
            .concurrent_updates(True)
            .build()
        )
        
        # Add ASYNC error handler
        application.add_error_handler(error_handler)
        
        # Register handlers with error handling
        def register_handlers(application):
            """Register all handlers with the application"""
            try:
                # Register user handlers
                from handlers.user_handlers import register_user_handlers
                register_user_handlers(application)
                logger.info("User handlers registered")
                
                # Register callback handlers for inline menus
                from handlers.callback_handlers import register_callback_handlers
                register_callback_handlers(application)
                logger.info("Callback handlers registered")
                
                # Register admin handlers
                from handlers.admin_handlers import register_admin_handlers
                register_admin_handlers(application)
                logger.info("Admin handlers registered")
                
                # Register search handlers
                from handlers.search_handlers import register_search_handlers
                register_search_handlers(application)
                logger.info("Search handlers registered")
                
                # Register payment handlers
                from handlers.payment_handlers import register_payment_handlers
                register_payment_handlers(application)
                logger.info("Payment handlers registered")
                
                # Register menu handlers
                from handlers.menu_handlers import register_menu_handlers
                register_menu_handlers(application)
                logger.info("Menu handlers registered")
            except ImportError as e:
                logger.error(f"Failed to import handlers: {e}")
        
        # Wait a bit before starting to ensure any previous instance has stopped
        logger.info("Waiting 5 seconds before starting bot...")
        time.sleep(5)
        
        # Start the bot
        logger.info("Starting Telegram bot...")
        application.run_polling(
            drop_pending_updates=True,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
