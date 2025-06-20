import json
import os
import logging
from typing import Dict, List, Any, Optional
import config

# Initialize logger
logger = logging.getLogger(__name__)


def ensure_directory_exists(file_path: str) -> None:
    """Ensure the directory for a file exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")


def load_json_file(file_path: str, default_value: Any = None) -> Any:
    """Load data from a JSON file, with error handling."""
    if default_value is None:
        default_value = {}

    try:
        ensure_directory_exists(file_path)
        if not os.path.exists(file_path):
            logger.info(
                f"File not found at {file_path}, creating new one with default value"
            )
            save_json_file(file_path, default_value)
            return default_value

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {file_path}: {e}")
        return default_value
    except Exception as e:
        logger.error(f"Error loading from {file_path}: {e}")
        return default_value


def save_json_file(file_path: str, data: Any) -> bool:
    """Save data to a JSON file, with error handling."""
    try:
        ensure_directory_exists(file_path)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {e}")
        return False


# User data functions
def load_user_data() -> Dict[str, Dict[str, Any]]:
    """Load user data from file."""
    return load_json_file(config.USER_DATA_FILE, {})


def get_all_users() -> List[Dict[str, Any]]:
    """Get a list of all users with complete profiles and not blocked."""
    all_users = load_user_data()
    return [{
        "user_id": user_id,
        "name": user.get("name", "Unknown"),
        "language": user.get("language", "Unknown"),
        "gender": user.get("gender", "Unknown"),
        "country": user.get("country", "Unknown"),
        "username": user.get("username", None)
    } for user_id, user in all_users.items()
            if user.get("profile_complete") and not user.get("blocked", False)]


def save_user_data(data: Dict[str, Dict[str, Any]]) -> bool:
    """Save user data to file."""
    return save_json_file(config.USER_DATA_FILE, data)


def get_user_data(user_id: str) -> Dict[str, Any]:
    """Get data for a specific user."""
    all_users = load_user_data()
    return all_users.get(str(user_id), {})

def update_user_data(user_id: str, data: Dict[str, Any]) -> bool:
    """Update data for a specific user."""
    all_users = load_user_data()
    if str(user_id) not in all_users:
        all_users[str(user_id)] = {}

    # ⚠️ تأكد من دمج البيانات بدلاً من استبدالها
    all_users[str(user_id)].update(data)
    return save_user_data(all_users)


def is_user_blocked(user_id: str) -> bool:
    """Check if a user is blocked."""
    user_data = get_user_data(user_id)
    return user_data.get("blocked", False)


def is_premium_user(user_id: str) -> bool:
    """Check if a user has premium status."""
    user_data = get_user_data(user_id)
    return user_data.get("premium", False)


def has_complete_profile(user_id: str) -> bool:
    """Check if a user has a complete profile."""
    user_data = get_user_data(user_id)
    return user_data.get("profile_complete", False)


# Payment data functions
def load_pending_payments() -> List[Dict[str, Any]]:
    """Load pending payments data from file."""
    return load_json_file(config.PENDING_PAYMENTS_FILE, [])


def save_pending_payments(data: List[Dict[str, Any]]) -> bool:
    """Save pending payments data to file."""
    return save_json_file(config.PENDING_PAYMENTS_FILE, data)


# Regions and countries data
def load_regions_countries() -> Dict[str, List[str]]:
    """Load regions and countries data from file."""
    return load_json_file(config.REGIONS_COUNTRIES_FILE, {})


def get_all_regions() -> List[str]:
    """Get all available regions."""
    return list(load_regions_countries().keys())


def get_countries_in_region(region: str) -> List[str]:
    """Get all countries in a specific region."""
    regions_countries = load_regions_countries()
    return regions_countries.get(region, [])


def is_country_in_region(country: str, region: str) -> bool:
    """Check if a country is in a specific region."""
    countries = get_countries_in_region(region)
    return country in countries


def find_matching_users(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find users matching the specified search criteria."""
    try:
        # Validate criteria
        if not criteria or not isinstance(criteria, dict):
            logger.error("find_matching_users: Invalid criteria provided")
            return []
            
        all_users = load_user_data()
        
        if not all_users:
            logger.warning("find_matching_users: No users data loaded")
            return []
            
        matching_users = []
        current_user_id = str(criteria.get("user_id", ""))

        for user_id, user_data in all_users.items():
            try:
                # Skip if user_data is None or not a dict
                if not user_data or not isinstance(user_data, dict):
                    continue
                    
                # Skip if profile is not complete, user is blocked, or user is searching for themselves
                if (not user_data.get("profile_complete", False)
                        or user_data.get("blocked", False)
                        or str(user_id) == current_user_id):
                    continue

                match = True

                # Check language match
                if criteria.get("language") and criteria["language"] != "any":
                    user_language = user_data.get("language")
                    if not user_language or user_language != criteria["language"]:
                        match = False

                # Check gender match
                if criteria.get("gender") and criteria["gender"] != "any":
                    user_gender = user_data.get("gender")
                    if not user_gender or user_gender != criteria["gender"]:
                        match = False

                # Check country match
                if criteria.get("country") and criteria["country"] != "any":
                    user_country = user_data.get("country")
                    if not user_country or user_country != criteria["country"]:
                        match = False

                if match:
                    matching_users.append({
                        "user_id": str(user_id),
                        "name": user_data.get("name", "Unknown"),
                        "language": user_data.get("language", "Unknown"),
                        "gender": user_data.get("gender", "Unknown"),
                        "country": user_data.get("country", "Unknown"),
                        "username": user_data.get("username", None)
                    })
                    
            except Exception as e:
                logger.error(f"Error processing user {user_id} in find_matching_users: {e}")
                continue

        return matching_users
        
    except Exception as e:
        logger.error(f"Error in find_matching_users: {e}")
        return []


def get_all_users() -> List[Dict[str, Any]]:
    """Get a list of all users who are online and looking for a partner."""
    all_users = load_user_data()
    return [{
        "user_id": user_id,
        "name": user_data.get("name", "Unknown"),
        "language": user_data.get("language", "Unknown"),
        "gender": user_data.get("gender", "Unknown"),
        "country": user_data.get("country", "Unknown"),
        "username": user_data.get("username", None),
    } for user_id, user_data in all_users.items()
            if user_data.get("profile_complete", False)
            and not user_data.get("blocked", False)
            and user_data.get("status", "idle") == "searching"]
