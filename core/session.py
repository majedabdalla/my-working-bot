"""
Enhanced session management module for MultiLangTranslator Bot
"""

import json
import time
import threading
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Enhanced session manager with chat partner and history support."""
    
    def __init__(self):
        self.sessions = {}
        self.chat_partners = {}  # user_id -> partner_id mapping
        self.chat_histories = {}  # user_id -> list of messages
        self.lock = threading.Lock()
    
    def get_session_state(self, user_id: str) -> Optional[str]:
        """Get current session state for user."""
        with self.lock:
            user_id_str = str(user_id)
            if user_id_str in self.sessions:
                return self.sessions[user_id_str].get("state")
            return None
    
    def set_session_state(self, user_id: str, state: str) -> None:
        """Set session state for user."""
        with self.lock:
            user_id_str = str(user_id)
            if user_id_str not in self.sessions:
                self.sessions[user_id_str] = {}
            self.sessions[user_id_str]["state"] = state
            self.sessions[user_id_str]["last_activity"] = time.time()
    
    def clear_session(self, user_id: str) -> None:
        """Clear session for user."""
        with self.lock:
            user_id_str = str(user_id)
            if user_id_str in self.sessions:
                del self.sessions[user_id_str]
    
    def set_chat_partner(self, user_id: str, partner_id: str) -> None:
        """Set chat partner for user."""
        with self.lock:
            user_id_str = str(user_id)
            partner_id_str = str(partner_id)
            self.chat_partners[user_id_str] = partner_id_str
            
            # Initialize chat history
            if user_id_str not in self.chat_histories:
                self.chat_histories[user_id_str] = []
    
    def get_chat_partner(self, user_id: str) -> Optional[str]:
        """Get chat partner for user."""
        with self.lock:
            user_id_str = str(user_id)
            return self.chat_partners.get(user_id_str)
    
    def clear_chat_partner(self, user_id: str) -> None:
        """Clear chat partner for user."""
        with self.lock:
            user_id_str = str(user_id)
            if user_id_str in self.chat_partners:
                del self.chat_partners[user_id_str]
    
    def add_message_to_history(self, user_id: str, message_data: Dict[str, Any]) -> None:
        """Add message to chat history."""
        with self.lock:
            user_id_str = str(user_id)
            if user_id_str not in self.chat_histories:
                self.chat_histories[user_id_str] = []
            
            # Add timestamp to message
            message_data["timestamp"] = time.time()
            self.chat_histories[user_id_str].append(message_data)
            
            # Keep only last 100 messages to prevent memory issues
            if len(self.chat_histories[user_id_str]) > 100:
                self.chat_histories[user_id_str] = self.chat_histories[user_id_str][-100:]
    
    def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get chat history for user."""
        with self.lock:
            user_id_str = str(user_id)
            return self.chat_histories.get(user_id_str, []).copy()
    
    def clear_chat_history(self, user_id: str) -> None:
        """Clear chat history for user."""
        with self.lock:
            user_id_str = str(user_id)
            if user_id_str in self.chat_histories:
                del self.chat_histories[user_id_str]
    
    def cleanup_expired_sessions(self, max_age: int = 3600) -> None:
        """Clean up expired sessions (older than max_age seconds)."""
        current_time = time.time()
        expired_users = []
        
        with self.lock:
            for user_id, session_data in self.sessions.items():
                last_activity = session_data.get("last_activity", 0)
                if current_time - last_activity > max_age:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                del self.sessions[user_id]
                logger.info(f"Cleaned up expired session for user {user_id}")

# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

# Decorator functions for backward compatibility
def require_profile(func):
    """Decorator to require complete profile."""
    def wrapper(update, context):
        from data_handler import get_user_data
        user_id = str(update.effective_user.id)
        user_data = get_user_data(user_id)
        
        if not user_data.get("profile_complete", False):
            from localization import get_text
            update.message.reply_text(
                get_text(user_id, "profile_incomplete"),
                parse_mode="HTML"
            )
            return
        
        return func(update, context)
    return wrapper

def require_premium(func):
    """Decorator to require premium subscription."""
    def wrapper(update, context):
        from data_handler import get_user_data
        from localization import get_text
        user_id = str(update.effective_user.id)
        user_data = get_user_data(user_id)
        
        if not user_data.get("premium", False):
            update.message.reply_text(
                get_text(user_id, "premium_required"),
                parse_mode="HTML"
            )
            return
        
        return func(update, context)
    return wrapper

# Legacy functions for backward compatibility
def get_chat_partner(user_id: str) -> Optional[str]:
    """Get chat partner for user (legacy function)."""
    return get_session_manager().get_chat_partner(user_id)

def clear_chat_partner(user_id: str) -> None:
    """Clear chat partner for user (legacy function)."""
    get_session_manager().clear_chat_partner(user_id)
