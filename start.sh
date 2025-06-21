#!/bin/bash

# MultiLangTranslator Bot Startup Script

echo "🚀 Starting MultiLangTranslator Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Install required packages
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ]; then
    echo "⚠️  BOT_TOKEN environment variable is not set."
    echo "Please set your bot token: export BOT_TOKEN='your_bot_token_here'"
    exit 1
fi

# Check if ADMIN_ID is set
if [ -z "$ADMIN_ID" ]; then
    echo "⚠️  ADMIN_ID environment variable is not set."
    echo "Please set your admin ID: export ADMIN_ID='your_admin_id_here'"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p locales
mkdir -p logs
mkdir -p data

# Check if locale files exist
if [ ! -f "locales/en.json" ]; then
    echo "❌ Locale files not found. Please ensure all locale files are in the locales/ directory."
    exit 1
fi

# Start the bot
echo "✅ Starting bot..."
python3 main.py