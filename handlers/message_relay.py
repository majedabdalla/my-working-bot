"""
Message relay handler for chat between users
"""

import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from core.session import get_session_manager
from data_handler import get_user_data
from localization import get_text

logger = logging.getLogger(__name__)

def handle_user_message(update: Update, context: CallbackContext) -> None:
    """Handle messages from users in active chats."""
    user = update.effective_user
    user_id = str(user.id)
    message = update.message
    
    # Get session manager
    session_manager = get_session_manager()
    
    # Check if user has an active chat partner
    partner_id = session_manager.get_chat_partner(user_id)
    
    if not partner_id:
        # User is not in an active chat, ignore the message
        return
    
    # Get user data for logging
    user_data = get_user_data(user_id)
    
    # Prepare message data for history
    message_data = {
        "from_user_id": user_id,
        "from_name": user_data.get("name", "Unknown"),
        "message_type": "text",
        "content": ""
    }
    
    try:
        # Handle different message types
        if message.text:
            message_data["message_type"] = "text"
            message_data["content"] = message.text
            
            # Forward text message
            context.bot.send_message(
                chat_id=int(partner_id),
                text=message.text,
                parse_mode=ParseMode.HTML
            )
            
        elif message.photo:
            message_data["message_type"] = "photo"
            message_data["content"] = "📷 Photo"
            
            # Forward photo
            context.bot.send_photo(
                chat_id=int(partner_id),
                photo=message.photo[-1].file_id,
                caption=message.caption or ""
            )
            
        elif message.document:
            message_data["message_type"] = "document"
            message_data["content"] = f"📄 Document: {message.document.file_name or 'Unknown'}"
            
            # Forward document
            context.bot.send_document(
                chat_id=int(partner_id),
                document=message.document.file_id,
                caption=message.caption or ""
            )
            
        elif message.video:
            message_data["message_type"] = "video"
            message_data["content"] = "🎥 Video"
            
            # Forward video
            context.bot.send_video(
                chat_id=int(partner_id),
                video=message.video.file_id,
                caption=message.caption or ""
            )
            
        elif message.audio:
            message_data["message_type"] = "audio"
            message_data["content"] = "🎵 Audio"
            
            # Forward audio
            context.bot.send_audio(
                chat_id=int(partner_id),
                audio=message.audio.file_id,
                caption=message.caption or ""
            )
            
        elif message.voice:
            message_data["message_type"] = "voice"
            message_data["content"] = "🎤 Voice message"
            
            # Forward voice message
            context.bot.send_voice(
                chat_id=int(partner_id),
                voice=message.voice.file_id,
                caption=message.caption or ""
            )
            
        elif message.sticker:
            message_data["message_type"] = "sticker"
            message_data["content"] = f"🎭 Sticker: {message.sticker.emoji or ''}"
            
            # Forward sticker
            context.bot.send_sticker(
                chat_id=int(partner_id),
                sticker=message.sticker.file_id
            )
            
        elif message.location:
            message_data["message_type"] = "location"
            message_data["content"] = f"📍 Location: {message.location.latitude}, {message.location.longitude}"
            
            # Forward location
            context.bot.send_location(
                chat_id=int(partner_id),
                latitude=message.location.latitude,
                longitude=message.location.longitude
            )
            
        else:
            # Unsupported message type
            logger.warning(f"Unsupported message type from user {user_id}")
            return
        
        # Add message to both users' chat history
        session_manager.add_message_to_history(user_id, message_data)
        session_manager.add_message_to_history(partner_id, message_data)
        
        logger.info(f"Message relayed from {user_id} to {partner_id}: {message_data['message_type']}")
        
    except Exception as e:
        logger.error(f"Failed to relay message from {user_id} to {partner_id}: {e}")
        
        # Notify sender about delivery failure
        try:
            message.reply_text(
                get_text(user_id, "message_delivery_failed"),
                parse_mode=ParseMode.HTML
            )
        except Exception as reply_error:
            logger.error(f"Failed to notify user about delivery failure: {reply_error}")

def handle_callback_query(update: Update, context: CallbackContext) -> None:
    """Handle callback queries (inline button presses)."""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Answer the callback query to remove loading state
    query.answer()
    
    # Handle different callback types
    if query.data.startswith("contact_"):
        from handlers.search_handlers import contact_user_callback
        contact_user_callback(update, context)
    elif query.data.startswith("decline_contact_"):
        from handlers.search_handlers import decline_contact_callback
        decline_contact_callback(update, context)
    else:
        logger.warning(f"Unknown callback query: {query.data}")