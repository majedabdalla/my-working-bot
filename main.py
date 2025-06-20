"""
Main entry point for MultiLangTranslator Bot
"""

import logging
import os
from telegram.ext import Application

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Get bot token
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise ValueError("BOT_TOKEN environment variable not set")
        
        # Create application
        application = Application.builder().token(token).build()
        
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
        
        # Start the bot
        logger.info("Starting bot...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
