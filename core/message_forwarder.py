"""
Message forwarder module for MultiLangTranslator Bot
"""

import logging
from typing import Dict, List, Any, Optional
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime
import config

logger = logging.getLogger(__name__)

class MessageForwarder:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.target_group_id = config.TARGET_GROUP_ID
    
    def forward_connection_log(self, user1_data: Dict, user2_data: Dict) -> None:
        """Forward connection log to admin group."""
        try:
            message = (
                "🔗 **New Chat Connection**\n\n"
                f"**User 1:**\n"
                f"• Name: {user1_data.get('name', 'Unknown')}\n"
                f"• ID: {user1_data.get('user_id', 'Unknown')}\n"
                f"• Language: {user1_data.get('language', 'Unknown')}\n"
                f"• Country: {user1_data.get('country', 'Unknown')}\n\n"
                f"**User 2:**\n"
                f"• Name: {user2_data.get('name', 'Unknown')}\n"
                f"• ID: {user2_data.get('user_id', 'Unknown')}\n"
                f"• Language: {user2_data.get('language', 'Unknown')}\n"
                f"• Country: {user2_data.get('country', 'Unknown')}\n\n"
                f"Chat started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            self.bot.send_message(
                chat_id=self.target_group_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to forward connection log: {e}")
    
    def forward_chat_log(self, user1_data: Dict, user2_data: Dict, chat_history: List[Dict]) -> None:
        """Forward chat history to admin group."""
        try:
            header = (
                "📝 **Chat History**\n\n"
                f"**Participants:**\n"
                f"• {user1_data.get('name', 'Unknown')} (ID: {user1_data.get('user_id', 'Unknown')})\n"
                f"• {user2_data.get('name', 'Unknown')} (ID: {user2_data.get('user_id', 'Unknown')})\n\n"
                f"**Messages:**\n"
            )
            
            # Send header
            self.bot.send_message(
                chat_id=self.target_group_id,
                text=header,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Send each message in chat history
            for msg in chat_history[-20:]:  # Last 20 messages
                sender_name = user1_data.get('name', 'Unknown') if msg['sender_id'] == user1_data.get('user_id') else user2_data.get('name', 'Unknown')
                
                if msg.get('text'):
                    message_text = f"**{sender_name}:** {msg['text']}"
                    self.bot.send_message(
                        chat_id=self.target_group_id,
                        text=message_text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                # Forward media if exists
                if msg.get('media_type') and msg.get('file_id'):
                    try:
                        if msg['media_type'] == 'photo':
                            self.bot.send_photo(
                                chat_id=self.target_group_id,
                                photo=msg['file_id'],
                                caption=f"Photo from {sender_name}"
                            )
                        elif msg['media_type'] == 'document':
                            self.bot.send_document(
                                chat_id=self.target_group_id,
                                document=msg['file_id'],
                                caption=f"Document from {sender_name}"
                            )
                        elif msg['media_type'] == 'video':
                            self.bot.send_video(
                                chat_id=self.target_group_id,
                                video=msg['file_id'],
                                caption=f"Video from {sender_name}"
                            )
                        elif msg['media_type'] == 'audio':
                            self.bot.send_audio(
                                chat_id=self.target_group_id,
                                audio=msg['file_id'],
                                caption=f"Audio from {sender_name}"
                            )
                        elif msg['media_type'] == 'voice':
                            self.bot.send_voice(
                                chat_id=self.target_group_id,
                                voice=msg['file_id'],
                                caption=f"Voice message from {sender_name}"
                            )
                    except Exception as e:
                        logger.error(f"Failed to forward media: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to forward chat log: {e}")
    
    def forward_user_message(self, sender_data: Dict, receiver_id: str, message_data: Dict) -> None:
        """Forward individual message to admin group for monitoring."""
        try:
            header = f"💬 **Message Monitor**\n\nFrom: {sender_data.get('name', 'Unknown')} (ID: {sender_data.get('user_id', 'Unknown')})\nTo: {receiver_id}\n\n"
            
            if message_data.get('text'):
                full_message = header + f"**Message:** {message_data['text']}"
                self.bot.send_message(
                    chat_id=self.target_group_id,
                    text=full_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Forward media
            if message_data.get('media_type') and message_data.get('file_id'):
                self.bot.send_message(
                    chat_id=self.target_group_id,
                    text=header + f"**Media Type:** {message_data['media_type']}",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                try:
                    if message_data['media_type'] == 'photo':
                        self.bot.send_photo(
                            chat_id=self.target_group_id,
                            photo=message_data['file_id']
                        )
                    elif message_data['media_type'] == 'document':
                        self.bot.send_document(
                            chat_id=self.target_group_id,
                            document=message_data['file_id']
                        )
                    elif message_data['media_type'] == 'video':
                        self.bot.send_video(
                            chat_id=self.target_group_id,
                            video=message_data['file_id']
                        )
                    elif message_data['media_type'] == 'audio':
                        self.bot.send_audio(
                            chat_id=self.target_group_id,
                            audio=message_data['file_id']
                        )
                    elif message_data['media_type'] == 'voice':
                        self.bot.send_voice(
                            chat_id=self.target_group_id,
                            voice=message_data['file_id']
                        )
                except Exception as e:
                    logger.error(f"Failed to forward media to admin: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to forward user message: {e}")

# Global instance
_message_forwarder = None

def get_message_forwarder(bot: Bot = None) -> MessageForwarder:
    """Get the global message forwarder instance."""
    global _message_forwarder
    if _message_forwarder is None and bot:
        _message_forwarder = MessageForwarder(bot)
    return _message_forwarder
