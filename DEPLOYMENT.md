# MultiLangTranslator Bot Deployment Guide

## Quick Setup

1. **Set Environment Variables:**
```bash
export BOT_TOKEN="your_bot_token_from_botfather"
export ADMIN_ID="your_telegram_user_id"
export TARGET_GROUP_ID="your_admin_group_id"
```

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the Bot:**
```bash
python main.py
```

## For Replit Deployment

1. Fork this repository to Replit
2. Set environment variables in Replit Secrets:
   - `BOT_TOKEN`: Your bot token from BotFather
   - `ADMIN_ID`: Your Telegram user ID
   - `ADMIN_GROUP_ID`: Admin group ID for forwarding messages
3. Run the project

## For Local Development

1. Clone the repository
2. Create a `.env` file:
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_id_here
ADMIN_GROUP_ID=your_admin_group_id_here
```
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Features Implemented

✅ Multi-language support (English, Arabic, Hindi, Indonesian)
✅ User profile creation and management
✅ Partner search and matching
✅ Real-time chat between users
✅ Message forwarding to admin group
✅ Chat history logging
✅ Premium features framework
✅ Admin controls
✅ Session management
✅ Error handling and logging

## Bot Commands

- `/start` - Create/update profile
- `/menu` - Show main menu
- `/search` - Find chat partner
- `/disconnect` - End current chat
- `/help` - Show help information
- `/profile` - View profile

## Admin Features

- All chats are logged and forwarded to admin group
- Premium user management
- User statistics and monitoring
- Broadcast messaging capability

The bot is now ready for deployment and use!
