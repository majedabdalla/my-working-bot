"""
User handlers module for MultiLangTranslator Bot
"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

# Initialize core modules with fallbacks
try:
    from core.session import get_session_manager
    from core.database import get_database_manager
    from data_handler import get_user_data, update_user_data
    from localization import get_text
except ImportError as e:
    logger.warning(f"Some imports failed: {e}")
    
    # Fallback functions
    def get_user_data(user_id):
        return {}
    
    def update_user_data(user_id, data):
        pass
    
    def get_text(user_id, key, **kwargs):
        return f"Text: {key}"

async def start(update: Update, context: CallbackContext):
    """Handle /start command - ASYNC"""
    try:
        user = update.effective_user
        user_id = str(user.id)
        
        # Get or create user data
        user_data = get_user_data(user_id)
        if not user_data:
            user_data = {
                "user_id": user_id,
                "name": user.first_name,
                "username": user.username,
                "language": user.language_code or "en",
                "profile_complete": False,
                "premium": False,
                "blocked": False
            }
            update_user_data(user_id, user_data)
        
        welcome_text = get_text(user_id, "welcome", name=user.first_name)
        if welcome_text.startswith("Text:"):
            welcome_text = f"Welcome {user.first_name}! 🎉\n\nThis is MultiLangTranslator Bot - your gateway to connecting with people from different languages and cultures around the world!"
        
        await update.message.reply_text(welcome_text)
        
    except Exception as e:
        logger.error(f"Error in start command for user {user.id}: {e}")
        try:
            await update.message.reply_text("An error occurred. Please try again.")
        except:
            pass

async def help_command(update: Update, context: CallbackContext):
    """Handle /help command - ASYNC"""
    try:
        user_id = str(update.effective_user.id)
        help_text = get_text(user_id, "help_text")
        
        if help_text.startswith("Text:"):
            help_text = """
🤖 **MultiLangTranslator Bot Help**

**Available Commands:**
/start - Start the bot and create your profile
/help - Show this help message
/profile - Manage your profile
/search - Find language partners
/settings - Bot settings
/cancel - Cancel current operation

**Features:**
🌍 Connect with people worldwide
💬 Multi-language support
🔍 Advanced partner search
⭐ Premium features available

Need more help? Contact support!
            """
        
        await update.message.reply_text(help_text)
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")

async def profile_command(update: Update, context: CallbackContext):
    """Handle /profile command - ASYNC"""
    try:
        await update.message.reply_text("📝 Profile management coming soon!")
        
    except Exception as e:
        logger.error(f"Error in profile command: {e}")

async def settings_command(update: Update, context: CallbackContext):
    """Handle /settings command - ASYNC"""
    try:
        await update.message.reply_text("⚙️ Settings coming soon!")
        
    except Exception as e:
        logger.error(f"Error in settings command: {e}")

async def cancel_command(update: Update, context: CallbackContext):
    """Handle /cancel command - ASYNC"""
    try:
        await update.message.reply_text("❌ Operation cancelled.")
        
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")

async def handle_text_message(update: Update, context: CallbackContext):
    """Handle text messages - ASYNC"""
    try:
        user_id = str(update.effective_user.id)
        text = update.message.text
        
        # Basic echo for now
        await update.message.reply_text(f"You said: {text}")
        
    except Exception as e:
        logger.error(f"Error handling text message: {e}")

async def handle_contact(update: Update, context: CallbackContext):
    """Handle contact messages - ASYNC"""
    try:
        contact = update.message.contact
        await update.message.reply_text(f"📞 Thanks for sharing your contact: {contact.first_name}")
        
    except Exception as e:
        logger.error(f"Error handling contact: {e}")

async def handle_photo(update: Update, context: CallbackContext):
    """Handle photo messages - ASYNC"""
    try:
        await update.message.reply_text("📸 Photo received!")
        
    except Exception as e:
        logger.error(f"Error handling photo: {e}")

async def handle_document(update: Update, context: CallbackContext):
    """Handle document messages - ASYNC"""
    try:
        document = update.message.document
        await update.message.reply_text(f"📄 Document received: {document.file_name}")
        
    except Exception as e:
        logger.error(f"Error handling document: {e}")

async def handle_callback_query(update: Update, context: CallbackContext):
    """Handle callback queries - ASYNC"""
    try:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("✅ Button pressed!")
        
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")

def register_user_handlers(application):
    """Register all user handlers with the application"""
    try:
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("settings", settings_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        logger.info("User handlers registered successfully")
        
    except Exception as e:
        logger.error(f"Error registering user handlers: {e}")
        raise