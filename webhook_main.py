"""
Webhook version of MultiLangTranslator Bot
"""

import logging
import os
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global application instance
application = None

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "MultiLangTranslator Bot",
        "mode": "webhook"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates"""
    try:
        if application is None:
            return jsonify({"error": "Bot not initialized"}), 500
            
        # Get the update from Telegram
        update = Update.de_json(request.get_json(), application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

def create_app():
    """Initialize the bot application"""
    global application
    
    try:
        # Get bot token
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise ValueError("BOT_TOKEN environment variable not set")
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Register handlers
        try:
            from handlers.user_handlers import register_user_handlers
            register_user_handlers(application)
            logger.info("User handlers registered")
        except ImportError as e:
            logger.error(f"Failed to import user handlers: {e}")
        
        # Set webhook
        webhook_url = os.getenv('WEBHOOK_URL')  # Set this in Render environment
        if webhook_url:
            application.bot.set_webhook(url=f"{webhook_url}/webhook")
            logger.info(f"Webhook set to: {webhook_url}/webhook")
        
        logger.info("Bot application initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        raise

if __name__ == '__main__':
    create_app()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)