"""
Script to clear webhook and reset bot
"""

import os
import requests

def clear_webhook():
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("BOT_TOKEN not found")
        return
    
    # Clear webhook
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    response = requests.post(url)
    print(f"Clear webhook response: {response.json()}")
    
    # Get bot info
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    print(f"Bot info: {response.json()}")

if __name__ == '__main__':
    clear_webhook()