"""
Web service for MultiLangTranslator Bot
Provides health checks and keeps the service alive
"""

import os
import subprocess
import threading
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Global variable to track bot process
bot_process = None
bot_status = {"running": False, "last_check": None}

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "MultiLangTranslator Bot"
    })

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
