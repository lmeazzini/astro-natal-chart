"""
Internationalization (i18n) module for the API.

Provides translation services for error messages and user-facing strings,
as well as locale-aware formatting for dates, numbers, and currencies.
"""

from app.core.context import get_locale
from app.core.i18n.formatting import (
    format_currency,
    format_date,
    format_datetime,
    format_degree,
    format_number,
    format_percentage,
    format_time,
)
from app.core.i18n.translator import Translator, get_translator, translate

# Supported locales
SUPPORTED_LOCALES = ["pt-BR", "en-US"]
DEFAULT_LOCALE = "pt-BR"

# Locale normalization map
_LOCALE_MAP = {
    "en": "en-US",
    "en_US": "en-US",
    "en-us": "en-US",
    "pt": "pt-BR",
    "pt_BR": "pt-BR",
    "pt-br": "pt-BR",
}


def normalize_locale(locale: str | None) -> str:
    """
    Normalize locale string to supported format.

    Args:
        locale: Locale string to normalize (e.g., "en", "pt-br", "en_US")
                If None, uses current context locale or default.

    Returns:
        Normalized locale string ("pt-BR" or "en-US")
    """
    if locale is None:
        locale = get_locale() or DEFAULT_LOCALE

    return _LOCALE_MAP.get(locale, locale)


__all__ = [
    "Translator",
    "get_translator",
    "translate",
    "normalize_locale",
    "SUPPORTED_LOCALES",
    "DEFAULT_LOCALE",
    "format_date",
    "format_time",
    "format_datetime",
    "format_number",
    "format_currency",
    "format_percentage",
    "format_degree",
]
