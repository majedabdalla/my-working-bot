"""
Main module for MultiLangTranslator Bot
"""

import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode
import config
from handlers.user_handlers import (
    start, menu_command, handle_text_input,
    handle_language_selection, handle_gender_selection, handle_country_selection
)
from handlers.search_handlers import search_partner, disconnect_chat, contact_user_callback
from handlers.menu_handlers import handle_menu_button, show_help
from handlers.message_relay import handle_user_message
from core.message_forwarder import get_message_forwarder
from flask import Flask
import threading

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running! 🤖"

@app.route('/ping')
def ping():
    return "pong"

def run_flask():
    """Run Flask server in a separate thread."""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def handle_callback_query(update, context):
    """Handle all callback queries."""
    query = update.callback_query
    data = query.data
    
    if data.startswith("lang_"):
        handle_language_selection(update, context)
    elif data.startswith("gender_"):
        handle_gender_selection(update, context)
    elif data.startswith("country_"):
        handle_country_selection(update, context)
    elif data.startswith("contact_"):
        contact_user_callback(update, context)
    else:
        query.answer("Unknown action")

def handle_message(update, context):
    """Handle all text messages."""
    user_id = str(update.effective_user.id)
    
    # Check if user is in profile setup
    from core.session import get_session_manager
    session_manager = get_session_manager()
    state = session_manager.get_session_state(user_id)
    
    if state in ["awaiting_name", "awaiting_age"]:
        handle_text_input(update, context)
        return
    
    # Check if user is in active chat
    partner_id = session_manager.get_chat_partner(user_id)
    if partner_id:
        handle_user_message(update, context)
        return
    
    # Handle menu buttons
    handle_menu_button(update, context)

def main():
    """Start the bot."""
    logger.info("🚀 Starting Telegram bot...")
    
    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Initialize message forwarder
    get_message_forwarder(application.bot)
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("search", search_partner))
    application.add_handler(CommandHandler("disconnect", disconnect_chat))
    application.add_handler(CommandHandler("help", show_help))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Text message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Media message handlers
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.DOCUMENT | filters.VIDEO | 
         filters.AUDIO | filters.VOICE | filters.STICKER | 
         filters.LOCATION) & ~filters.COMMAND,
        handle_user_message
    ))
    
    # Start the bot
    logger.info("✅ Bot started successfully!")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()
