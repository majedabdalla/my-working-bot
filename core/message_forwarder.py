"""
Message forwarder module for MultiLangTranslator Bot
"""

import logging
from typing import Dict, List, Any, Optional
from telegram import Bot
from telegram.constants import ParseMode
import config

logger = logging.getLogger(__name__)

class MessageForwarder:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.target_group_id = config.TARGET_GROUP_ID
    
    def forward_connection_log(self, user1_data: Dict, user2_data: Dict) -> None:
        """Forward connection log to admin group."""
        from datetime import datetime
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
                
                message_text = f"**{sender_name}:** {msg.get('text', '[Media]')}"
                
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
                    except Exception as e:
                        logger.error(f"Failed to forward media: {e}")
        except Exception as e:
            logger.error(f"Failed to forward chat log: {e}")
