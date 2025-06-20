"""
Security module using telegram library features
"""

import time
import logging
from typing import Dict, Set
from collections import defaultdict
from telegram.ext import BaseRateLimiter
from telegram.ext.filters import BaseFilter

logger = logging.getLogger(__name__)

class CustomRateLimiter(BaseRateLimiter):
    """Custom rate limiter implementation"""
    
    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries
        self.user_attempts = defaultdict(int)
        self.blocked_users: Set[str] = set()
    
    async def process_request(self, callback, args, kwargs, **_kwargs):
        """Process rate limited request"""
        try:
            return await callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            raise

class SpamFilter(BaseFilter):
    """Filter to detect spam messages"""
    
    def __init__(self):
        super().__init__()
        self.blocked_users: Set[str] = set()
        self.message_counts = defaultdict(list)
    
    def filter(self, message):
        if not message.from_user:
            return True
            
        user_id = str(message.from_user.id)
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            return False
        
        # Check message frequency
        now = time.time()
        user_messages = self.message_counts[user_id]
        
        # Remove old messages (older than 1 minute)
        user_messages[:] = [msg_time for msg_time in user_messages if now - msg_time < 60]
        
        # Add current message
        user_messages.append(now)
        
        # Block if too many messages
        if len(user_messages) > 10:
            self.blocked_users.add(user_id)
            logger.warning(f"User {user_id} blocked for spam")
            return False
        
        return True

# Global instances
_spam_filter = None

def init_spam_protection():
    """Initialize spam protection"""
    global _spam_filter
    if _spam_filter is None:
        _spam_filter = SpamFilter()
        logger.info("Spam protection initialized")
    return _spam_filter

def get_spam_protection():
    """Get spam protection filter"""
    global _spam_filter
    if _spam_filter is None:
        _spam_filter = init_spam_protection()
    return _spam_filter
