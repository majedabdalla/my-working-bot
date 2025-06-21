"""
Search handlers module for MultiLangTranslator Bot
"""

import logging
import random
from typing import Dict, List, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from localization import get_text
from data_handler import get_user_data, find_matching_users, update_user_data
from core.session import get_session_manager
from core.message_forwarder import get_message_forwarder

logger = logging.getLogger(__name__)

def search_partner(update: Update, context: CallbackContext) -> None:
    """Handle partner search command."""
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
    
    # Send searching message
    update.message.reply_text(
        get_text(user_id, "searching_partner"),
        parse_mode=ParseMode.HTML
    )
    
    # Find matching users
    search_criteria = {
        "user_id": user_id,
        "language": "any",  # Search for any language
        "gender": "any",    # Search for any gender
        "country": "any"    # Search for any country
    }
    
    matching_users = find_matching_users(search_criteria)
    
    if not matching_users:
        update.message.reply_text(
            get_text(user_id, "no_partners"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Select random partner
    partner = random.choice(matching_users)
    partner_id = str(partner["user_id"])
    
    # Check if partner is already in chat
    partner_current_chat = session_manager.get_chat_partner(partner_id)
    if partner_current_chat:
        update.message.reply_text(
            get_text(user_id, "no_partners"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Automatically connect both users
    session_manager.set_chat_partner(user_id, partner_id)
    session_manager.set_chat_partner(partner_id, user_id)
    
    # Get message forwarder
    message_forwarder = get_message_forwarder()
    
    # Notify both users
    user_message = get_text(user_id, "contact_established") + "\n\n" + get_text(
        user_id, "new_contact",
        name=partner.get("name", "Unknown")
    )
    
    partner_message = get_text(partner_id, "contact_established") + "\n\n" + get_text(
        partner_id, "new_contact", 
        name=user_data.get("name", "Unknown")
    )
    
    # Send notifications
    update.message.reply_text(user_message, parse_mode=ParseMode.HTML)
    
    # Send message to partner
    try:
        context.bot.send_message(
            chat_id=int(partner_id),
            text=partner_message,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to notify partner {partner_id}: {e}")
    
    # Log the connection to admin group
    message_forwarder.forward_connection_log(user_data, partner)

def disconnect_chat(update: Update, context: CallbackContext) -> None:
    """Handle chat disconnection."""
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
    
    # Get chat history before clearing
    chat_history = session_manager.get_chat_history(user_id)
    
    # Clear chat partners
    session_manager.clear_chat_partner(user_id)
    session_manager.clear_chat_partner(partner_id)
    
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
        logger.error(f"Failed to notify partner {partner_id} about disconnection: {e}")
    
    # Send chat history to admin group
    message_forwarder = get_message_forwarder()
    user_data = get_user_data(user_id)
    partner_data = get_user_data(partner_id)
    message_forwarder.forward_chat_log(user_data, partner_data, chat_history)

# Callback handlers (keep existing ones but they won't be used much now)
def contact_user_callback(update: Update, context: CallbackContext) -> None:
    """Handle contact user callback - now automatically connects."""
    query = update.callback_query
    query.answer()
    
    user = update.effective_user
    user_id = str(user.id)
    
    # Extract target user ID from callback data
    target_id = query.data.replace("contact_", "")
    
    session_manager = get_session_manager()
    
    # Automatically connect users
    session_manager.set_chat_partner(user_id, target_id)
    session_manager.set_chat_partner(target_id, user_id)
    
    # Get user data
    user_data = get_user_data(user_id)
    target_data = get_user_data(target_id)
    
    if not target_data:
        query.edit_message_text(
            get_text(user_id, "user_not_found"),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Notify both users
    query.edit_message_text(
        get_text(user_id, "contact_established"),
        parse_mode=ParseMode.HTML
    )
    
    try:
        context.bot.send_message(
            chat_id=int(target_id),
            text=get_text(target_id, "new_contact", name=user_data.get("name", "Unknown")),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to notify target user {target_id}: {e}")
