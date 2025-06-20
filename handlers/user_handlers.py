"""
User handlers module for MultiLangTranslator Bot
"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
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
        return f"Missing: {key}"

def create_main_menu_keyboard(user_id: str):
    """Create the main menu keyboard using translations"""
    keyboard = [
        [KeyboardButton(get_text(user_id, "menu_profile")), KeyboardButton(get_text(user_id, "menu_search"))],
        [KeyboardButton(get_text(user_id, "menu_settings")), KeyboardButton(get_text(user_id, "menu_help"))],
        [KeyboardButton(get_text(user_id, "menu_payment"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def create_inline_menu(user_id: str):
    """Create inline menu with buttons using translations"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "menu_profile"), callback_data="profile")],
        [InlineKeyboardButton(get_text(user_id, "menu_search"), callback_data="search")],
        [InlineKeyboardButton(get_text(user_id, "menu_settings"), callback_data="settings")],
        [InlineKeyboardButton(get_text(user_id, "menu_help"), callback_data="help")],
        [InlineKeyboardButton(get_text(user_id, "menu_payment"), callback_data="premium")]
    ]
    return InlineKeyboardMarkup(keyboard)

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
        
        # Send welcome message with menu
        await update.message.reply_text(
            welcome_text,
            reply_markup=create_main_menu_keyboard(user_id)
        )
        
        # Also send inline menu
        menu_text = get_text(user_id, "main_menu")
        await update.message.reply_text(
            menu_text,
            reply_markup=create_inline_menu(user_id)
        )
        
    except Exception as e:
        logger.error(f"Error in start command for user {user.id}: {e}")
        try:
            await update.message.reply_text("An error occurred. Please try again.")
        except:
            pass

async def menu_command(update: Update, context: CallbackContext):
    """Handle /menu command - ASYNC"""
    try:
        user_id = str(update.effective_user.id)
        menu_text = get_text(user_id, "main_menu")
        
        await update.message.reply_text(
            menu_text,
            reply_markup=create_inline_menu(user_id)
        )
        
    except Exception as e:
        logger.error(f"Error in menu command: {e}")

async def help_command(update: Update, context: CallbackContext):
    """Handle /help command - ASYNC"""
    try:
        user_id = str(update.effective_user.id)
        help_text = get_text(user_id, "help_text")
        
        await update.message.reply_text(help_text)
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")

async def profile_command(update: Update, context: CallbackContext):
    """Handle /profile command - ASYNC"""
    try:
        user = update.effective_user
        user_id = str(user.id)
        
        profile_text = get_text(user_id, "profile_info", 
                               name=user.first_name,
                               language=user.language_code or "en",
                               status="Active")
        
        await update.message.reply_text(profile_text)
        
    except Exception as e:
        logger.error(f"Error in profile command: {e}")

async def search_command(update: Update, context: CallbackContext):
    """Handle /search command - ASYNC"""
    try:
        user_id = str(update.effective_user.id)
        search_text = get_text(user_id, "search_partners")
        
        await update.message.reply_text(search_text)
        
    except Exception as e:
        logger.error(f"Error in search command: {e}")

async def settings_command(update: Update, context: CallbackContext):
    """Handle /settings command - ASYNC"""
    try:
        user_id = str(update.effective_user.id)
        settings_text = get_text(user_id, "settings_menu")
        
        await update.message.reply_text(settings_text)
        
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
        
        # Get translated button texts to match against
        profile_text = get_text(user_id, "menu_profile")
        search_text = get_text(user_id, "menu_search")
        settings_text = get_text(user_id, "menu_settings")
        help_text = get_text(user_id, "menu_help")
        payment_text = get_text(user_id, "menu_payment")
        
        # Handle menu button presses
        if text == profile_text or text == "👤 Profile":
            await profile_command(update, context)
        elif text == search_text or text == "🔍 Search Partners":
            await search_command(update, context)
        elif text == settings_text or text == "⚙️ Settings":
            await settings_command(update, context)
        elif text == help_text or text == "❓ Help":
            await help_command(update, context)
        elif text == payment_text or text == "💳 Premium":
            premium_text = get_text(user_id, "premium_info")
            await update.message.reply_text(premium_text)
        else:
            # Echo other messages
            await update.message.reply_text(f"You said: {text}")
        
    except Exception as e:
        logger.error(f"Error handling text message: {e}")

async def handle_callback_query(update: Update, context: CallbackContext):
    """Handle callback queries - ASYNC"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        data = query.data
        
        if data == "profile":
            profile_text = get_text(user_id, "profile_info", 
                                   name=query.from_user.first_name,
                                   language=query.from_user.language_code or "en",
                                   status="Active")
            await query.edit_message_text(profile_text, reply_markup=create_inline_menu())
            
        elif data == "search":
            search_text = get_text(user_id, "search_partners")
            await query.edit_message_text(search_text, reply_markup=create_inline_menu())
            
        elif data == "settings":
            settings_text = get_text(user_id, "settings_menu")
            await query.edit_message_text(settings_text, reply_markup=create_inline_menu())
            
        elif data == "help":
            help_text = get_text(user_id, "help_text")
            await query.edit_message_text(help_text, reply_markup=create_inline_menu())
            
        elif data == "premium":
            premium_text = get_text(user_id, "premium_info")
            await query.edit_message_text(premium_text, reply_markup=create_inline_menu())
        
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")

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

def register_user_handlers(application):
    """Register all user handlers with the application"""
    try:
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("menu", menu_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("search", search_command))
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