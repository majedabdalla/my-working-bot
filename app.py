"""
Flask web application for keeping the bot alive on Render
"""

from flask import Flask, render_template_string
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Home page"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MultiLangTranslator Bot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .feature { margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 MultiLangTranslator Bot</h1>
            <div class="status">
                <strong>Status:</strong> ✅ Bot is running and ready to connect people worldwide!
            </div>
            
            <h2>Features:</h2>
            <div class="feature">🌍 Connect with people from different countries</div>
            <div class="feature">💬 Multi-language support (English, Arabic, Hindi, Indonesian)</div>
            <div class="feature">🔍 Advanced partner search</div>
            <div class="feature">⭐ Premium features available</div>
            
            <h2>How to use:</h2>
            <ol>
                <li>Find the bot on Telegram</li>
                <li>Send /start to begin</li>
                <li>Complete your profile</li>
                <li>Start connecting with people!</li>
            </ol>
            
            <p style="text-align: center; margin-top: 30px; color: #666;">
                <small>Bot is hosted and running 24/7</small>
            </p>
        </div>
    </body>
    </html>
    ''')

@app.route('/ping')
def ping():
    """Ping endpoint for uptime monitoring"""
    return {'status': 'ok', 'message': 'Bot is running'}

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'MultiLangTranslator Bot'}

def run_bot():
    """Run the Telegram bot in a separate thread"""
    try:
        logger.info("Starting bot thread...")
        from main import main
        main()
    except Exception as e:
        logger.error(f"Error running bot: {e}")

import os
import threading
import time

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Bot thread started")
    
    # Give the bot a moment to start
    time.sleep(2)
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)