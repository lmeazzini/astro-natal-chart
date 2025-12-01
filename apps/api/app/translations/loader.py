"""
Translation loader for backend i18n support.

This module provides a centralized translation system similar to frontend i18next,
with caching for performance and fallback to English for missing translations.
"""

from functools import lru_cache
from typing import Any

SUPPORTED_LANGUAGES = ["en-US", "pt-BR"]
DEFAULT_LANGUAGE = "en-US"


# All translations organized by language
_TRANSLATIONS: dict[str, dict[str, Any]] = {
    "en-US": {},
    "pt-BR": {},
}


def _load_translations() -> None:
    """Load all translation modules into memory."""
    from app.translations.en_US import translations as en_translations
    from app.translations.pt_BR import translations as pt_translations

    _TRANSLATIONS["en-US"] = en_translations
    _TRANSLATIONS["pt-BR"] = pt_translations


def _ensure_loaded() -> None:
    """Ensure translations are loaded (lazy initialization)."""
    if not _TRANSLATIONS["en-US"]:
        _load_translations()


@lru_cache(maxsize=1000)
def get_translation(key: str, language: str = "en-US") -> Any:
    """
    Get a translation by key for the specified language.

    Uses dot notation for nested keys (e.g., "lunar_phases.new_moon.name").
    Falls back to English if key not found in requested language.
    Falls back to the key itself if not found in English either.

    Args:
        key: Translation key using dot notation (e.g., "planets.Sun")
        language: Language code ("en-US" or "pt-BR")

    Returns:
        Translated value (string, list, dict, etc.), or the key if not found

    Examples:
        >>> get_translation("planets.Sun", "pt-BR")
        "Sol"
        >>> get_translation("lunar_phases.new_moon.name", "en-US")
        "New Moon"
        >>> get_translation("solar_phases.first.signs", "en-US")
        ["Aries", "Taurus", "Gemini"]
    """
    _ensure_loaded()

    # Normalize language code
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE

    # Try to get from requested language
    result = _get_nested(_TRANSLATIONS.get(language, {}), key)
    if result is not None:
        return result

    # Fallback to English
    if language != DEFAULT_LANGUAGE:
        result = _get_nested(_TRANSLATIONS.get(DEFAULT_LANGUAGE, {}), key)
        if result is not None:
            return result

    # Return key as fallback (for strings) or None (for non-strings)
    return key


def _get_nested(data: dict[str, Any], key: str) -> Any | None:
    """
    Get a nested value from a dictionary using dot notation.

    Args:
        data: Dictionary to search in
        key: Key using dot notation (e.g., "planets.Sun")

    Returns:
        Value if found (any type), None otherwise
    """
    keys = key.split(".")
    current = data

    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None

    # Return any type (strings, lists, dicts, etc.)
    return current


def get_all_translations(language: str = "en-US") -> dict[str, Any]:
    """
    Get all translations for a language.

    Args:
        language: Language code ("en-US" or "pt-BR")

    Returns:
        Complete translations dictionary for the language
    """
    _ensure_loaded()

    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE

    return _TRANSLATIONS.get(language, {})


def clear_cache() -> None:
    """Clear the translation cache (useful for testing)."""
    get_translation.cache_clear()
