"""
Core module initialization
"""

import logging

logger = logging.getLogger(__name__)

# Global instances
_session_manager = None
_database_manager = None
_spam_protection = None
_notification_manager = None

def init_session_manager():
    """Initialize session manager"""
    global _session_manager
    try:
        from .session import SessionManager
        _session_manager = SessionManager()
        logger.info("Session manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize session manager: {e}")
        # Create a dummy session manager
        class DummySessionManager:
            def get_session(self, user_id, conversation_type="default"):
                return {"state": None, "data": {}}
        _session_manager = DummySessionManager()

def init_database_manager():
    """Initialize database manager"""
    global _database_manager
    try:
        from .database import DatabaseManager
        _database_manager = DatabaseManager()
        logger.info("Database manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database manager: {e}")

def init_spam_protection():
    """Initialize spam protection"""
    global _spam_protection
    try:
        from .security import SpamProtection
        _spam_protection = SpamProtection()
        logger.info("Spam protection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize spam protection: {e}")

def init_notification_manager():
    """Initialize notification manager"""
    global _notification_manager
    try:
        from .notifications import NotificationManager
        _notification_manager = NotificationManager()
        logger.info("Notification manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize notification manager: {e}")
