"""
Keep-alive module for MultiLangTranslator Bot

This module provides a simple web server to keep the bot running on Replit
by responding to pings from UptimeRobot.
"""

import logging
import threading
from flask import Flask, request, jsonify

# Initialize logger
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    """Home route that returns a simple message."""
    return "MultiLangTranslator Bot is running!"

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

def start_server(host='0.0.0.0', port=8080):
    """
    Start the Flask server in a separate thread.
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    def run_server():
        app.run(host=host, port=port)
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    logger.info(f"Keep-alive server started on {host}:{port}")
    
    return server_thread

# When this module is imported, automatically start the server
if __name__ != "__main__":
    try:
        start_server()
    except Exception as e:
        logger.error(f"Error starting keep-alive server: {e}")
