import json
import os
import logging
from typing import Dict, Any
import config
from data_handler import get_user_data

# Initialize logger
logger = logging.getLogger(__name__)

# Cache for loaded translations
loaded_translations = {}

# Add this helper function for better error handling
def safe_load_translation_file(lang_code: str) -> bool:
    """Safely load translation file with error handling."""
    try:
        load_translation_file(lang_code)
        return True
    except FileNotFoundError:
        logger.warning(f"Translation file not found for language: {lang_code}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in translation file for {lang_code}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error loading translation file for {lang_code}: {e}")
        return False

def load_translation_file(lang_code: str) -> Dict[str, str]:
    """Load a translation file for a specific language."""
    if lang_code in loaded_translations:
        return loaded_translations[lang_code]

    try:
        file_path = os.path.join(config.LOCALES_DIR, f"{lang_code}.json")
        with open(file_path, "r", encoding="utf-8") as file:
            translations = json.load(file)
            loaded_translations[lang_code] = translations
            return translations
    except FileNotFoundError:
        logger.warning(
            f"Translation file for {lang_code} not found at {file_path}. Falling back to default language."
        )
        if lang_code != config.DEFAULT_LANGUAGE:
            return load_translation_file(config.DEFAULT_LANGUAGE)
        return {}
    except json.JSONDecodeError as e:
        logger.error(
            f"Error decoding JSON from translation file {file_path}: {e}")
        if lang_code != config.DEFAULT_LANGUAGE:
            return load_translation_file(config.DEFAULT_LANGUAGE)
        return {}
    except Exception as e:
        logger.error(
            f"Unexpected error loading translation file {file_path}: {e}")
        if lang_code != config.DEFAULT_LANGUAGE:
            return load_translation_file(config.DEFAULT_LANGUAGE)
        return {}


def get_user_language(user_id: str) -> str:
    """Get the language code for a specific user."""
    try:
        # Validate input
        if not user_id or not isinstance(user_id, str):
            return config.DEFAULT_LANGUAGE
            
        user_data = get_user_data(user_id)
        
        # Handle None or empty user_data
        if not user_data or not isinstance(user_data, dict):
            return config.DEFAULT_LANGUAGE
            
        language = user_data.get("language", config.DEFAULT_LANGUAGE)
        
        # Validate language code
        if not language or not isinstance(language, str):
            return config.DEFAULT_LANGUAGE
            
        return language
        
    except Exception as e:
        print(f"Error getting user language for {user_id}: {e}")
        return config.DEFAULT_LANGUAGE


def get_text(user_id: str, key: str, lang_code: str = None, **kwargs) -> str:
    """Get a localized text string for a user."""
    try:
        # Validate inputs
        if not key or not isinstance(key, str):
            return "Invalid translation key"
            
        if not user_id or not isinstance(user_id, str):
            user_id = "default"
            
        # ✅ احصل على اللغة مباشرة من بيانات المستخدم
        if lang_code is None:
            try:
                user_data = get_user_data(user_id)
                effective_lang = user_data.get("language", config.DEFAULT_LANGUAGE) if user_data else config.DEFAULT_LANGUAGE
            except Exception as e:
                logger.error(f"Error getting user data for {user_id}: {e}")
                effective_lang = config.DEFAULT_LANGUAGE
        else:
            effective_lang = lang_code

        # Validate language code
        if not effective_lang or not isinstance(effective_lang, str):
            effective_lang = config.DEFAULT_LANGUAGE

        # ✅ حمّل ملف الترجمة من الكاش أو الملف
        if effective_lang not in loaded_translations:
            try:
                load_translation_file(effective_lang)
            except Exception as e:
                logger.error(f"Error loading translation file for {effective_lang}: {e}")
                # If loading fails, try default language
                if effective_lang != config.DEFAULT_LANGUAGE:
                    try:
                        load_translation_file(config.DEFAULT_LANGUAGE)
                        effective_lang = config.DEFAULT_LANGUAGE
                    except Exception as e2:
                        logger.error(f"Error loading default translation file: {e2}")
                        return f"Translation error: {key}"

        translations = loaded_translations.get(effective_lang, {})

        # ✅ fallback إلى اللغة الافتراضية إذا لم توجد الترجمة
        if not translations or key not in translations:
            # Prevent infinite recursion by checking if we're already using default language
            if effective_lang != config.DEFAULT_LANGUAGE:
                try:
                    return get_text(user_id, key, config.DEFAULT_LANGUAGE, **kwargs)
                except Exception as e:
                    logger.error(f"Error in fallback translation for key '{key}': {e}")
                    return f"Missing translation: {key}"
            else:
                logger.warning(f"Missing translation key '{key}' in default language '{config.DEFAULT_LANGUAGE}'")
                return f"Missing translation: {key}"

        message = translations[key]
        
        # Validate message
        if not isinstance(message, str):
            logger.error(f"Invalid message type for key '{key}': {type(message)}")
            return f"Invalid translation: {key}"
            
        # Apply formatting if kwargs provided
        if kwargs:
            try:
                # Validate kwargs before formatting
                safe_kwargs = {}
                for k, v in kwargs.items():
                    if isinstance(k, str) and v is not None:
                        safe_kwargs[k] = str(v)
                        
                message = message.format(**safe_kwargs)
            except KeyError as e:
                logger.error(
                    f"Missing placeholder {e} in translation key '{key}' for language '{effective_lang}'"
                )
                # Return message without formatting rather than failing
                return message
            except Exception as e:
                logger.error(
                    f"Error formatting message for key '{key}' in language '{effective_lang}': {e}"
                )
                return message

        return message
        
    except Exception as e:
        logger.error(f"Unexpected error in get_text for key '{key}', user '{user_id}': {e}")
        return f"Translation error: {key}"

# Preload all supported languages
def preload_translations():
    """Preload all supported language translations into memory."""
    for lang_code in config.SUPPORTED_LANGUAGES.keys():
        load_translation_file(lang_code)
    logger.info(
        f"Preloaded translations for: {', '.join(config.SUPPORTED_LANGUAGES.keys())}"
    )


# Initialize translations
preload_translations()
