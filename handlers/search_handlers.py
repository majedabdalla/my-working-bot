"""
Enhanced search handlers module for MultiLangTranslator Bot
"""

import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from localization import get_text
from data_handler import get_user_data, get_all_users
from core.session import get_session_manager
from core.message_forwarder import get_message_forwarder

logger = logging.getLogger(__name__)

def search_partner(update: Update, context: CallbackContext) -> None:
    """Search for a chat partner."""
    user = update.effective_user
    user_id = str(user.id)
    
    # Check if user has complete profile
    user_data = get_user_data(user_id)
    if not user_data.get("profile_complete", False):
        update.message.reply_text(
            get_text(user_id, "profile_incomplete"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check if user is already in a chat
    session_manager = get_session_manager()
    current_partner = session_manager.get_chat_partner(user_id)
    
    if current_partner:
        update.message.reply_text(
            get_text(user_id, "already_in_chat"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Search for available partners
    update.message.reply_text(
        get_text(user_id, "searching_partner"),
        parse_mode=ParseMode.HTML
    )
    
    # Find random partner
    partner_data = find_random_partner(user_id)
    
    if not partner_data:
        update.message.reply_text(
            get_text(user_id, "no_partners"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Show partner info with contact button
    partner_text = get_text(
        user_id, "partner_found",
        name=partner_data.get("name", "Unknown"),
        language=partner_data.get("language", "Unknown"),
        gender=partner_data.get("gender", "Unknown"),
        country=partner_data.get("country", "Unknown")
    )
    
    keyboard = [[
        InlineKeyboardButton(
            get_text(user_id, "contact_partner"),
            callback_data=f"contact_{partner_data['user_id']}"
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        partner_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

def find_random_partner(current_user_id: str) -> dict:
    """Find a random available partner."""
    all_users = get_all_users()
    session_manager = get_session_manager()
    
    # Filter available users
    available_users = []
    for user_id, user_data in all_users.items():
        if (user_id != current_user_id and 
            user_data.get("profile_complete", False) and
            not user_data.get("blocked", False) and
            not session_manager.get_chat_partner(user_id)):  # Not already in chat
            
            available_users.append(user_data)
    
    if not available_users:
        return None
    
    return random.choice(available_users)

def disconnect_chat(update: Update, context: CallbackContext) -> None:
    """Disconnect from current chat."""
    user = update.effective_user
    user_id = str(user.id)
    
    session_manager = get_session_manager()
    partner_id = session_manager.get_chat_partner(user_id)
    
    if not partner_id:
        update.message.reply_text(
            get_text(user_id, "no_active_chat"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Get user data for chat log
    user_data = get_user_data(user_id)
    partner_data = get_user_data(partner_id)
    
    # Get chat history
    chat_history = session_manager.get_chat_history(user_id)
    
    # Forward chat log to admin
    message_forwarder = get_message_forwarder()
    if message_forwarder and chat_history:
        message_forwarder.forward_chat_log(user_data, partner_data, chat_history)
    
    # Clear chat connections
    session_manager.clear_chat_partner(user_id)
    session_manager.clear_chat_partner(partner_id)
    
    # Clear chat history
    session_manager.clear_chat_history(user_id)
    session_manager.clear_chat_history(partner_id)
    
    # Notify both users
    update.message.reply_text(
        get_text(user_id, "you_disconnected"),
        parse_mode=ParseMode.HTML
    )
    
    try:
        context.bot.send_message(
            chat_id=int(partner_id),
            text=get_text(partner_id, "partner_disconnected"),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to notify partner {partner_id}: {e}")

# Callback handlers (keep existing ones but they won't be used much now)
def contact_user_callback(update: Update, context: CallbackContext) -> None:
    """Handle contact user callback."""
    query = update.callback_query
    user = query.from_user
    user_id = str(user.id)
    
    # Extract target user ID
    target_id = query.data.replace("contact_", "")
    
    # Get user data
    user_data = get_user_data(user_id)
    target_data = get_user_data(target_id)
    
    if not target_data:
        query.answer()
        query.edit_message_text(
            get_text(user_id, "user_not_found"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check if target user is still available
    session_manager = get_session_manager()
    if session_manager.get_chat_partner(target_id):
        query.answer()
        query.edit_message_text(
            get_text(user_id, "user_not_found"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Establish chat connection
    session_manager.set_chat_partner(user_id, target_id)
    session_manager.set_chat_partner(target_id, user_id)
    
    # Notify both users
    query.answer()
    query.edit_message_text(
        get_text(user_id, "contact_established"),
        parse_mode=ParseMode.HTML
    )
    
    # Notify target user
    try:
        context.bot.send_message(
            chat_id=int(target_id),
            text=get_text(
                target_id, "new_contact",
                name=user_data.get("name", "Unknown")
            ),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to notify target user {target_id}: {e}")
    
    # Forward connection log to admin
    message_forwarder = get_message_forwarder()
    if message_forwarder:
        message_forwarder.forward_connection_log(user_data, target_data)

def accept_contact_callback(update: Update, context: CallbackContext) -> None:
    """Handle accept contact callback - legacy function."""
    # This function is kept for compatibility but not used in the new flow
    pass

def decline_contact_callback(update: Update, context: CallbackContext) -> None:
    """Handle decline contact callback - legacy function."""
    # This function is kept for compatibility but not used in the new flow
    pass
