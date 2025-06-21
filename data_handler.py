"""
Data handler module for MultiLangTranslator Bot
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# In-memory storage for development (replace with database in production)
user_data_storage = {}

def get_user_data(user_id: str) -> Dict[str, Any]:
    """Get user data by user ID"""
    try:
        user_id = str(user_id)
        
        # Return stored data or default data
        default_data = {
            "user_id": user_id,
            "name": "User",
            "language": "en",
            "profile_complete": False,
            "created_at": None,
            "last_active": None
        }
        
        return user_data_storage.get(user_id, default_data)
        
    except Exception as e:
        logger.error(f"Error getting user data for {user_id}: {e}")
        return {
            "user_id": user_id,
            "name": "User",
            "language": "en",
            "profile_complete": False
        }

def update_user_data(user_id: str, data: Dict[str, Any]) -> bool:
    """Update user data"""
    try:
        user_id = str(user_id)
        
        # Get existing data
        existing_data = get_user_data(user_id)
        
        # Update with new data
        existing_data.update(data)
        
        # Store updated data
        user_data_storage[user_id] = existing_data
        
        logger.info(f"Updated user data for {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating user data for {user_id}: {e}")
        return False

def get_all_users() -> List[str]:
    """Get all user IDs"""
    try:
        return list(user_data_storage.keys())
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []

def has_complete_profile(user_id: str) -> bool:
    """Check if user has complete profile"""
    try:
        user_data = get_user_data(user_id)
        return user_data.get("profile_complete", False)
    except Exception as e:
        logger.error(f"Error checking profile completeness for {user_id}: {e}")
        return False

def find_matching_users(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find users matching the specified search criteria."""
    all_users = user_data_storage
    matching_users = []

    for user_id, user_data in all_users.items():
        # Skip if user is searching for themselves
        if str(user_id) == str(criteria.get("user_id", 0)):
            continue

        match = True

        # Check language match
        if criteria.get("language") and criteria["language"] != "any":
            if user_data.get("language") != criteria["language"]:
                match = False

        # Check gender match
        if criteria.get("gender") and criteria["gender"] != "any":
            if user_data.get("gender") != criteria["gender"]:
                match = False

        # Check country match
        if criteria.get("country") and criteria["country"] != "any":
            if user_data.get("country") != criteria["country"]:
                match = False

        if match:
            matching_users.append({
                "user_id": user_id,
                "name": user_data.get("name", "Unknown"),
                "language": user_data.get("language", "Unknown"),
                "gender": user_data.get("gender", "Unknown"),
                "country": user_data.get("country", "Unknown"),
                "username": user_data.get("username", None)
            })

    return matching_users

def save_user_data_to_file():
    """Save user data to file (backup)"""
    try:
        with open('user_data_backup.json', 'w') as f:
            json.dump(user_data_storage, f, indent=2)
        logger.info("User data saved to backup file")
    except Exception as e:
        logger.error(f"Error saving user data to file: {e}")

def load_user_data_from_file():
    """Load user data from file (restore)"""
    try:
        if os.path.exists('user_data_backup.json'):
            with open('user_data_backup.json', 'r') as f:
                global user_data_storage
                user_data_storage = json.load(f)
            logger.info("User data loaded from backup file")
    except Exception as e:
        logger.error(f"Error loading user data from file: {e}")

# Initialize data on import
load_user_data_from_file()
