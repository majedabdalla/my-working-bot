"""
README for MultiLangTranslator Bot

A professional Telegram bot for connecting users across language barriers
with advanced features, multilingual support, and robust administration.
"""

# MultiLangTranslator Bot

## Overview

MultiLangTranslator is a professional Telegram bot designed to connect users who speak different languages. The bot supports multiple languages (English, Arabic, Hindi, and Indonesian) and provides a range of features for users to find language partners based on various criteria.

## Features

### Core Features
- **Multilingual Support**: Full support for English, Arabic, Hindi, and Indonesian
- **Advanced Session Management**: Persistent user sessions with state tracking
- **Dynamic Menu System**: Context-aware menu that adapts to user language and permissions
- **User Profiles**: Comprehensive user profiles with language, gender, region, and country
- **Partner Search**: Find language partners based on various criteria

### Premium Features
- **Advanced Search**: Search by region and country (premium users only)
- **Unlimited Contacts**: Connect with unlimited language partners
- **Priority Matching**: Get matched with other users first
- **Ad-Free Experience**: No advertisements or promotions

### Admin Features
- **Admin Dashboard**: Comprehensive admin controls
- **User Management**: View, block, and manage users
- **Payment Verification**: Verify premium payments
- **Broadcast Messages**: Send messages to all users
- **System Statistics**: View bot usage statistics
- **Message Forwarding**: All files and chat logs are forwarded to a designated admin group

### Security Features
- **Spam Protection**: Rate limiting and abuse detection
- **Blacklisting**: Block abusive users
- **Content Filtering**: Filter inappropriate content

## Project Structure

```
MultiLangTranslator/
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── database.py         # Database operations
│   ├── message_forwarder.py # Message forwarding to admin group
│   ├── notifications.py    # Notification system
│   ├── security.py         # Spam protection and security
│   └── session.py          # Session management
├── handlers/               # Message handlers
│   ├── admin_handlers.py   # Admin command handlers
│   ├── payment_handlers.py # Payment processing handlers
│   ├── search_handlers.py  # Partner search handlers
│   └── user_handlers.py    # User command handlers
├── locales/                # Language files
│   ├── ar.json             # Arabic translations
│   ├── en.json             # English translations
│   ├── hi.json             # Hindi translations
│   └── id.json             # Indonesian translations
├── ui/                     # User interface components
│   ├── __init__.py
│   ├── keyboards.py        # Keyboard layouts
│   └── menu.py             # Menu system
├── app.py                  # Flask web application
├── config.py               # Configuration settings
├── keep_alive.py           # UptimeRobot integration
├── localization.py         # Localization utilities
├── main.py                 # Main entry point
└── validation.py           # Validation utilities
```

## Setup and Configuration

1. Set your bot token in `config.py`
2. Set admin ID in `config.py`
3. Set target group ID for message forwarding in `config.py`
4. Configure payment accounts in `config.py`
5. Deploy to Replit or your preferred hosting platform
6. Set up UptimeRobot to ping the `/ping` endpoint to keep the bot running

## Commands

- `/start` - Start the bot and create your profile
- `/menu` - Show the main menu
- `/hidemenu` - Hide the main menu
- `/help` - Show help information
- `/profile` - Update your profile
- `/search` - Search for language partners
- `/payment` - Activate premium features
- `/settings` - Manage your settings
- `/cancel` - Cancel current operation

## Admin Commands

- `/admin` - Access admin dashboard
- `/broadcast` - Send message to all users
- `/stats` - View system statistics
- `/block` - Block a user
- `/unblock` - Unblock a user
- `/verify` - Verify a payment

## UptimeRobot Integration

The bot includes a keep-alive mechanism for Replit hosting. Set up UptimeRobot to ping the `/ping` endpoint every 5 minutes to prevent the bot from sleeping.

## Multilingual Support

The bot supports multiple languages and automatically detects user language preferences. All UI elements, messages, and commands are available in all supported languages.

## Premium Features

Premium features are activated after payment verification by an admin. The bot supports Payeer and Bitcoin payments, with transaction verification through the admin dashboard.

## Security and Privacy

All messages, files, and chat logs between users are forwarded to a designated admin group for monitoring and moderation. User data is stored securely and is only accessible to admins.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.
