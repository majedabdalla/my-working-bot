"""
User handlers module for MultiLangTranslator Bot
"""

import logging
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

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

async def start_command(update: Update, context: CallbackContext):
    """Handle /start command"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Update user data
    user_data = {
        "user_id": user_id,
        "name": user.first_name,
        "username": user.username,
        "language": "en",  # Default language
        "profile_complete": False,
        "last_active": "now"
    }
    update_user_data(user_id, user_data)
    
    # Send welcome message
    welcome_text = get_text(user_id, "welcome", name=user.first_name)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=create_main_menu_keyboard(user_id),
        parse_mode=ParseMode.HTML
    )

async def menu_command(update: Update, context: CallbackContext):
    """Handle /menu command"""
    user = update.effective_user
    user_id = str(user.id)
    
    menu_text = get_text(user_id, "main_menu")
    
    await update.message.reply_text(
        menu_text,
        reply_markup=create_inline_menu(user_id),
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: CallbackContext):
    """Handle /help command"""
    user = update.effective_user
    user_id = str(user.id)
    
    help_text = get_text(user_id, "help_text")
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML
    )

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
    """Handle /search command - find a random partner"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Get all users
    from data_handler import get_all_users
    all_users = get_all_users()
    
    # Find potential partners (exclude self)
    potential_partners = [uid for uid in all_users if uid != user_id]
    
    if not potential_partners:
        await update.message.reply_text(
            get_text(user_id, "no_partners_found", default="No partners available right now. Try again later!")
        )
        return
    
    # Select random partner
    import random
    partner_id = random.choice(potential_partners)
    partner_data = get_user_data(partner_id)
    
    # Create contact button
    keyboard = InlineKeyboardMarkup([ [
        InlineKeyboardButton(
            get_text(user_id, "contact_partner", default="📞 Contact Partner"),
            callback_data=f"contact_{partner_id}"
        )
    ]])
    
    partner_info = get_text(
        user_id, 
        "partner_found",
        default="🎉 Partner Found!\n\n👤 Name: {name}\n🌍 Language: {language}",
        name=partner_data.get("name", "Unknown"),
        language=partner_data.get("language", "Unknown")
    )
    
    await update.message.reply_text(
        partner_info,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

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

async def handle_contact_callback(update: Update, context: CallbackContext):
    """Handle contact partner callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = str(user.id)
    
    # Extract partner ID from callback data
    partner_id = query.data.replace("contact_", "")
    partner_data = get_user_data(partner_id)
    
    if not partner_data:
        await query.edit_message_text("❌ Partner not found.")
        return
    
    # Notify both users
    contact_info = get_text(
        user_id,
        "contact_established",
        default="✅ Contact established!\n\n👤 Partner: {name}\n📱 Username: @{username}",
        name=partner_data.get("name", "Unknown"),
        username=partner_data.get("username", "No username")
    )
    
    await query.edit_message_text(contact_info, parse_mode=ParseMode.HTML)
    
    # Notify partner
    try:
        partner_notification = get_text(
            partner_id,
            "new_contact",
            default="🔔 New Contact!\n\n👤 {name} wants to connect with you!\n📱 Username: @{username}",
            name=user.first_name,
            username=user.username or "No username"
        )
        
        await context.bot.send_message(
            chat_id=partner_id,
            text=partner_notification,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to notify partner {partner_id}: {e}")

async def handle_menu_callback(update: Update, context: CallbackContext):
    """Handle menu button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = str(user.id)
    
    callback_data = query.data
    
    if callback_data == "search":
        # Trigger search functionality
        await search_from_callback(query, user_id, context)
    else:
        # Handle other menu options
        response_text = get_text(user_id, f"{callback_data}_info", default=f"{callback_data.title()} feature coming soon!")
        await query.edit_message_text(response_text, parse_mode=ParseMode.HTML)

async def search_from_callback(query, user_id: str, context: CallbackContext):
    """Handle search from inline menu"""
    from data_handler import get_all_users
    all_users = get_all_users()
    
    # Find potential partners (exclude self)
    potential_partners = [uid for uid in all_users if uid != user_id]
    
    if not potential_partners:
        await query.edit_message_text(
            get_text(user_id, "no_partners_found", default="No partners available right now. Try again later!")
        )
        return
    
    # Select random partner
    import random
    partner_id = random.choice(potential_partners)
    partner_data = get_user_data(partner_id)
    
    # Create contact button
    keyboard = InlineKeyboardMarkup([ [
        InlineKeyboardButton(
            get_text(user_id, "contact_partner", default="📞 Contact Partner"),
            callback_data=f"contact_{partner_id}"
        )
    ]])
    
    partner_info = get_text(
        user_id, 
        "partner_found",
        default="🎉 Partner Found!\n\n👤 Name: {name}\n🌍 Language: {language}",
        name=partner_data.get("name", "Unknown"),
        language=partner_data.get("language", "Unknown")
    )
    
    await query.edit_message_text(
        partner_info,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

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
    """Register all user handlers"""
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # Callback handlers for menu and contact
    application.add_handler(CallbackQueryHandler(handle_menu_callback, pattern="^(profile|search|settings|help|premium)$"))
    application.add_handler(CallbackQueryHandler(handle_contact_callback, pattern="^contact_"))
    
    logger.info("User handlers registered successfully")