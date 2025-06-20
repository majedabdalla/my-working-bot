"""
Localization module for MultiLangTranslator Bot
"""

import json
import logging
import os
from typing import Dict, Any
import config

logger = logging.getLogger(__name__)

# Cache for loaded translations
loaded_translations: Dict[str, Dict[str, str]] = {}

def load_translation_file(language_code: str) -> Dict[str, str]:
    """Load translation file for a specific language from locals folder."""
    try:
        # Try different possible file paths
        possible_paths = [
            f"locals/{language_code}.json",
            f"locals/{language_code.lower()}.json",
            f"locals/{language_code.upper()}.json",
            f"translations/{language_code}.json",  # fallback
            f"lang/{language_code}.json"  # another common pattern
        ]
        
        translations = {}
        file_loaded = False
        
        for file_path in possible_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        translations = json.load(f)
                    logger.info(f"Loaded translations for '{language_code}' from {file_path}")
                    file_loaded = True
                    break
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error loading {file_path}: {e}")
                    continue
        
        if not file_loaded:
            logger.warning(f"No translation file found for language '{language_code}' in any of: {possible_paths}")
            # Create basic fallback translations
            translations = create_fallback_translations(language_code)
        
        # Cache the translations
        loaded_translations[language_code] = translations
        return translations
        
    except Exception as e:
        logger.error(f"Unexpected error loading translations for '{language_code}': {e}")
        return create_fallback_translations(language_code)

def create_fallback_translations(language_code: str) -> Dict[str, str]:
    """Create basic fallback translations when files are missing."""
    return {
        "welcome": "Welcome {name}! 🎉\n\nThis is MultiLangTranslator Bot - your gateway to connecting with people from different languages and cultures around the world!\n\nUse the menu below to get started:",
        "help_text": "🤖 **MultiLangTranslator Bot Help**\n\n**Available Commands:**\n/start - Start the bot\n/menu - Show main menu\n/help - Show help\n/profile - Manage profile\n/search - Find partners\n/settings - Bot settings\n\n**Features:**\n🌍 Connect with people worldwide\n💬 Multi-language support\n🔍 Advanced partner search\n⭐ Premium features available",
        "main_menu": "🏠 **Main Menu**\n\nChoose an option from the buttons below:",
        "menu_profile": "👤 Profile",
        "menu_search": "🔍 Search Partners", 
        "menu_settings": "⚙️ Settings",
        "menu_help": "❓ Help",
        "menu_payment": "💳 Premium",
        "profile_info": "👤 **Your Profile**\n\nName: {name}\nLanguage: {language}\nStatus: {status}",
        "search_partners": "🔍 **Find Language Partners**\n\nSearching for people to connect with...",
        "settings_menu": "⚙️ **Settings**\n\nManage your preferences here.",
        "premium_info": "⭐ **Premium Features**\n\n• Advanced search filters\n• Unlimited connections\n• Priority matching\n• Ad-free experience"
    }

def get_user_language(user_id: str) -> str:
    """Get the language code for a specific user."""
    try:
        from data_handler import get_user_data
        user_data = get_user_data(user_id)
        return user_data.get("language", config.DEFAULT_LANGUAGE)
    except ImportError:
        logger.warning("data_handler not available, using default language")
        return config.DEFAULT_LANGUAGE
    except Exception as e:
        logger.error(f"Error getting user language for {user_id}: {e}")
        return config.DEFAULT_LANGUAGE

def get_text(user_id: str, key: str, lang_code: str = None, **kwargs) -> str:
    """Get a localized text string for a user."""
    try:
        # Get the effective language
        if lang_code is None:
            try:
                user_data = get_user_data(user_id) if 'get_user_data' in globals() else {}
                effective_lang = user_data.get("language", config.DEFAULT_LANGUAGE)
            except:
                effective_lang = config.DEFAULT_LANGUAGE
        else:
            effective_lang = lang_code

        # Load translation file if not cached
        if effective_lang not in loaded_translations:
            load_translation_file(effective_lang)

        translations = loaded_translations.get(effective_lang, {})

        # Fallback to default language if translation not found
        if not translations or key not in translations:
            if effective_lang != config.DEFAULT_LANGUAGE:
                return get_text(user_id, key, config.DEFAULT_LANGUAGE, **kwargs)
            else:
                logger.warning(f"Missing translation key '{key}' in default language '{config.DEFAULT_LANGUAGE}'")
                return f"Missing translation: {key}"

        message = translations[key]
        
        # Format message with provided kwargs
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError as e:
                logger.error(f"Missing placeholder {e} in translation key '{key}' for language '{effective_lang}'")
            except Exception as e:
                logger.error(f"Error formatting message for key '{key}': {e}")

        return message
        
    except Exception as e:
        logger.error(f"Error getting text for key '{key}', user '{user_id}': {e}")
        return f"Error: {key}"

def preload_translations():
    """Preload common translations to improve performance."""
    try:
        # Get list of available translation files
        locals_dir = "locals"
        if not os.path.exists(locals_dir):
            logger.warning(f"Locals directory '{locals_dir}' not found")
            return
        
        translation_files = [f for f in os.listdir(locals_dir) if f.endswith('.json')]
        
        if not translation_files:
            logger.warning(f"No translation files found in '{locals_dir}'")
            return
        
        languages = []
        for file in translation_files:
            lang_code = file.replace('.json', '')
            languages.append(lang_code)
            load_translation_file(lang_code)
        
        logger.info(f"Preloaded translations for: {', '.join(languages)}")
        
    except Exception as e:
        logger.error(f"Error preloading translations: {e}")

def get_available_languages() -> list:
    """Get list of available languages."""
    try:
        locals_dir = "locals"
        if not os.path.exists(locals_dir):
            return [config.DEFAULT_LANGUAGE]
        
        translation_files = [f for f in os.listdir(locals_dir) if f.endswith('.json')]
        languages = [f.replace('.json', '') for f in translation_files]
        
        if not languages:
            return [config.DEFAULT_LANGUAGE]
        
        return languages
        
    except Exception as e:
        logger.error(f"Error getting available languages: {e}")
        return [config.DEFAULT_LANGUAGE]

# Import get_user_data if available
try:
    from data_handler import get_user_data
except ImportError:
    logger.warning("data_handler not available for localization")
    def get_user_data(user_id):
        return {}

# Preload translations on module import
preload_translations()
