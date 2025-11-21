"""
Translation service for i18n support.

Loads JSON translation files and provides a simple interface for translating messages.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from loguru import logger

from app.core.config import settings
from app.core.context import get_locale

# Directory containing translation files
TRANSLATIONS_DIR = Path(__file__).parent / "translations"

# Supported locales
SUPPORTED_LOCALES = ["pt-BR", "en-US"]
DEFAULT_LOCALE = settings.DEFAULT_LOCALE


class Translator:
    """Translation service that loads and caches translations from JSON files."""

    def __init__(self) -> None:
        """Initialize the translator with loaded translations."""
        self._translations: dict[str, dict[str, Any]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all translation files from the translations directory."""
        for locale in SUPPORTED_LOCALES:
            file_path = TRANSLATIONS_DIR / f"{locale.replace('-', '_')}.json"
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        self._translations[locale] = json.load(f)
                    logger.debug(f"Loaded translations for {locale}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse translations for {locale}: {e}")
                    self._translations[locale] = {}
            else:
                logger.warning(f"Translation file not found: {file_path}")
                self._translations[locale] = {}

    def get(
        self,
        key: str,
        locale: str | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Get a translated message by key.

        Args:
            key: The translation key (e.g., "auth.invalid_credentials")
            locale: The locale to use (defaults to context locale or DEFAULT_LOCALE)
            **kwargs: Variables to interpolate in the message

        Returns:
            The translated message, or the key if not found
        """
        # Get locale from context if not provided
        if locale is None:
            locale = get_locale() or DEFAULT_LOCALE

        # Normalize locale (e.g., "en" -> "en-US", "pt" -> "pt-BR")
        locale = self._normalize_locale(locale)

        # Get translations for the locale
        translations = self._translations.get(locale, {})

        # Fall back to default locale if key not found
        if not translations:
            translations = self._translations.get(DEFAULT_LOCALE, {})

        # Navigate nested keys (e.g., "auth.invalid_credentials")
        value = self._get_nested(translations, key)

        # If not found in requested locale, try default locale
        if value is None and locale != DEFAULT_LOCALE:
            default_translations = self._translations.get(DEFAULT_LOCALE, {})
            value = self._get_nested(default_translations, key)

        # If still not found, return the key itself
        if value is None:
            logger.warning(f"Translation not found: {key} (locale: {locale})")
            return key

        # Interpolate variables
        if kwargs:
            try:
                return value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing variable in translation {key}: {e}")
                return value

        return value

    def _normalize_locale(self, locale: str) -> str:
        """Normalize locale string to supported format."""
        # Map common variants
        locale_map = {
            "en": "en-US",
            "en_US": "en-US",
            "en-us": "en-US",
            "pt": "pt-BR",
            "pt_BR": "pt-BR",
            "pt-br": "pt-BR",
        }
        return locale_map.get(locale, locale)

    def _get_nested(self, data: dict[str, Any], key: str) -> str | None:
        """Get a value from a nested dict using dot notation."""
        keys = key.split(".")
        value: Any = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value if isinstance(value, str) else None

    def reload(self) -> None:
        """Reload all translation files."""
        self._translations.clear()
        self._load_translations()
        logger.info("Translations reloaded")


# Singleton instance
_translator: Translator | None = None


@lru_cache(maxsize=1)
def get_translator() -> Translator:
    """Get the global translator instance (cached)."""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator


def translate(key: str, locale: str | None = None, **kwargs: Any) -> str:
    """
    Convenience function to translate a message.

    Args:
        key: The translation key (e.g., "auth.invalid_credentials")
        locale: The locale to use (defaults to context locale)
        **kwargs: Variables to interpolate in the message

    Returns:
        The translated message
    """
    return get_translator().get(key, locale, **kwargs)


# Alias for convenience
_ = translate
