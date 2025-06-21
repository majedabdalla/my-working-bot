"""
Callback handlers for inline keyboard buttons
"""

import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

# Import with fallbacks
try:
    from localization import get_text
    from data_handler import get_user_data
except ImportError as e:
    logger.warning(f"Import error: {e}")
    def get_text(user_id, key, **kwargs):
        return f"Text: {key}"
    def get_user_data(user_id):
        return {}

async def handle_inline_menu_callback(update: Update, context: CallbackContext):
    """Handle inline menu button callbacks"""
    try:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        user_id = str(user.id)
        callback_data = query.data
        
        logger.info(f"Callback from user {user_id}: {callback_data}")
        
        if callback_data == "profile":
            await handle_profile_callback(query, user_id, user)
        elif callback_data == "search":
            await handle_search_callback(query, user_id)
        elif callback_data == "settings":
            await handle_settings_callback(query, user_id)
        elif callback_data == "help":
            await handle_help_callback(query, user_id)
        elif callback_data == "premium":
            await handle_premium_callback(query, user_id)
        else:
            await query.edit_message_text("❌ Unknown option selected.")
            
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        try:
            await query.edit_message_text("❌ An error occurred. Please try again.")
        except:
            pass

async def handle_profile_callback(query, user_id: str, user):
    """Handle profile button callback"""
    try:
        user_data = get_user_data(user_id)
        profile_text = get_text(user_id, "profile_info", 
                               name=user.first_name,
                               language=user_data.get("language", "en"),
                               status="Active" if user_data.get("profile_complete") else "Incomplete")
        
        await query.edit_message_text(profile_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error in profile callback: {e}")
        await query.edit_message_text("❌ Error loading profile")

async def handle_search_callback(query, user_id: str):
    """Handle search button callback"""
    try:
        search_text = get_text(user_id, "search_partners")
        await query.edit_message_text(search_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error in search callback: {e}")
        await query.edit_message_text("❌ Error loading search")

async def handle_settings_callback(query, user_id: str):
    """Handle settings button callback"""
    try:
        settings_text = get_text(user_id, "settings_menu")
        await query.edit_message_text(settings_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error in settings callback: {e}")
        await query.edit_message_text("❌ Error loading settings")

async def handle_help_callback(query, user_id: str):
    """Handle help button callback"""
    try:
        help_text = get_text(user_id, "help_text")
        await query.edit_message_text(help_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error in help callback: {e}")
        await query.edit_message_text("❌ Error loading help")

async def handle_premium_callback(query, user_id: str):
    """Handle premium button callback"""
    try:
        premium_text = get_text(user_id, "premium_info")
        await query.edit_message_text(premium_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error in premium callback: {e}")
        await query.edit_message_text("❌ Error loading premium info")

def register_callback_handlers(application):
    """Register callback handlers"""
    from telegram.ext import CallbackQueryHandler
    
    # Register inline menu callback handler
    application.add_handler(CallbackQueryHandler(
        handle_inline_menu_callback,
        pattern="^(profile|search|settings|help|premium)$"
    ))
    
    logger.info("Callback handlers registered")