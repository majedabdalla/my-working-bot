"""
App module for MultiLangTranslator Bot

This module provides a Flask application for the web server
that keeps the bot running on Replit.
"""

from flask import Flask, request, jsonify, render_template_string

# Create Flask app
app = Flask(__name__)

# Simple HTML template for the home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MultiLangTranslator Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4285f4;
            text-align: center;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            background-color: #e8f5e9;
            border-radius: 4px;
            text-align: center;
        }
        .info {
            margin-top: 20px;
            line-height: 1.6;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MultiLangTranslator Bot</h1>
        
        <div class="status">
            <h2>Status: Online</h2>
            <p>The bot is currently running and ready to use!</p>
        </div>
        
        <div class="info">
            <h3>About the Bot</h3>
            <p>MultiLangTranslator is a Telegram bot that helps users connect with others who speak different languages. It supports multiple languages and provides advanced features for finding language partners.</p>
            
            <h3>Features</h3>
            <ul>
                <li>Multilingual support (English, Arabic, Hindi, Indonesian)</li>
                <li>Advanced user profile management</li>
                <li>Partner search by language, gender, region, and country</li>
                <li>Premium features for advanced users</li>
                <li>Admin dashboard for monitoring and management</li>
            </ul>
            
            <h3>How to Use</h3>
            <p>Search for the bot on Telegram and start a conversation. Use the /start command to set up your profile and begin using the bot.</p>
        </div>
        
        <div class="footer">
            <p>© 2025 MultiLangTranslator Bot</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Home route that returns a simple HTML page."""
    return render_template_string(HOME_TEMPLATE)

@app.route('/ping')
def ping():
    """Ping route for UptimeRobot to keep the bot alive."""
    return jsonify({"status": "ok", "message": "Bot is alive"})

@app.route('/status')
def status():
    """Status route that returns more detailed information about the bot."""
    import psutil
    import time
    
    # Get system information
    cpu_percent = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    uptime = int(time.time() - psutil.boot_time())
    
    # Format uptime
    days, remainder = divmod(uptime, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    
    # Return status information
    return jsonify({
        "status": "ok",
        "uptime": uptime_str,
        "cpu_percent": f"{cpu_percent}%",
        "memory_used": f"{memory_info.percent}%",
        "disk_used": f"{disk_info.percent}%",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    })

# When this module is imported, do nothing
# The server will be started by the keep_alive module
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
