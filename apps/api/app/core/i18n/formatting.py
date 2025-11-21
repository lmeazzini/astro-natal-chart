"""
Regional formatting utilities for dates, times, and numbers.

Provides locale-aware formatting based on the current request context.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from app.core.context import get_locale

if TYPE_CHECKING:
    from decimal import Decimal

# Date format patterns by locale
DATE_FORMATS = {
    "pt-BR": {
        "short": "%d/%m/%Y",
        "medium": "%d de %b de %Y",
        "long": "%d de %B de %Y",
        "full": "%A, %d de %B de %Y",
    },
    "en-US": {
        "short": "%m/%d/%Y",
        "medium": "%b %d, %Y",
        "long": "%B %d, %Y",
        "full": "%A, %B %d, %Y",
    },
}

# Time format patterns by locale
TIME_FORMATS = {
    "pt-BR": {
        "short": "%H:%M",
        "medium": "%H:%M:%S",
        "long": "%H:%M:%S %Z",
    },
    "en-US": {
        "short": "%I:%M %p",
        "medium": "%I:%M:%S %p",
        "long": "%I:%M:%S %p %Z",
    },
}

# Datetime format patterns by locale
DATETIME_FORMATS = {
    "pt-BR": {
        "short": "%d/%m/%Y %H:%M",
        "medium": "%d de %b de %Y às %H:%M",
        "long": "%d de %B de %Y às %H:%M:%S",
        "full": "%A, %d de %B de %Y às %H:%M:%S",
    },
    "en-US": {
        "short": "%m/%d/%Y %I:%M %p",
        "medium": "%b %d, %Y at %I:%M %p",
        "long": "%B %d, %Y at %I:%M:%S %p",
        "full": "%A, %B %d, %Y at %I:%M:%S %p",
    },
}

# Number format settings by locale
NUMBER_FORMATS = {
    "pt-BR": {
        "decimal_sep": ",",
        "thousands_sep": ".",
    },
    "en-US": {
        "decimal_sep": ".",
        "thousands_sep": ",",
    },
}

# Month names for Portuguese (strftime doesn't support pt-BR natively)
PT_BR_MONTHS = {
    "January": "janeiro",
    "February": "fevereiro",
    "March": "março",
    "April": "abril",
    "May": "maio",
    "June": "junho",
    "July": "julho",
    "August": "agosto",
    "September": "setembro",
    "October": "outubro",
    "November": "novembro",
    "December": "dezembro",
    "Jan": "jan",
    "Feb": "fev",
    "Mar": "mar",
    "Apr": "abr",
    "Jun": "jun",
    "Jul": "jul",
    "Aug": "ago",
    "Sep": "set",
    "Oct": "out",
    "Nov": "nov",
    "Dec": "dez",
}

PT_BR_WEEKDAYS = {
    "Monday": "segunda-feira",
    "Tuesday": "terça-feira",
    "Wednesday": "quarta-feira",
    "Thursday": "quinta-feira",
    "Friday": "sexta-feira",
    "Saturday": "sábado",
    "Sunday": "domingo",
    "Mon": "seg",
    "Tue": "ter",
    "Wed": "qua",
    "Thu": "qui",
    "Fri": "sex",
    "Sat": "sáb",
    "Sun": "dom",
}


def _normalize_locale(locale: str | None) -> str:
    """Normalize locale string to supported format."""
    if locale is None:
        locale = get_locale() or "pt-BR"

    locale_map = {
        "en": "en-US",
        "en_US": "en-US",
        "en-us": "en-US",
        "pt": "pt-BR",
        "pt_BR": "pt-BR",
        "pt-br": "pt-BR",
    }
    return locale_map.get(locale, locale)


def _localize_pt_br(text: str) -> str:
    """Replace English month/weekday names with Portuguese equivalents."""
    result = text
    for en, pt in PT_BR_MONTHS.items():
        result = result.replace(en, pt)
    for en, pt in PT_BR_WEEKDAYS.items():
        result = result.replace(en, pt)
    return result


def format_date(
    value: date | datetime,
    style: str = "medium",
    locale: str | None = None,
) -> str:
    """
    Format a date according to locale.

    Args:
        value: Date or datetime to format
        style: Format style - "short", "medium", "long", or "full"
        locale: Locale to use (defaults to context locale)

    Returns:
        Formatted date string
    """
    locale = _normalize_locale(locale)
    formats = DATE_FORMATS.get(locale, DATE_FORMATS["pt-BR"])
    pattern = formats.get(style, formats["medium"])

    result = value.strftime(pattern)

    if locale == "pt-BR":
        result = _localize_pt_br(result)

    return result


def format_time(
    value: datetime,
    style: str = "short",
    locale: str | None = None,
) -> str:
    """
    Format a time according to locale.

    Args:
        value: Datetime to format
        style: Format style - "short", "medium", or "long"
        locale: Locale to use (defaults to context locale)

    Returns:
        Formatted time string
    """
    locale = _normalize_locale(locale)
    formats = TIME_FORMATS.get(locale, TIME_FORMATS["pt-BR"])
    pattern = formats.get(style, formats["short"])

    return value.strftime(pattern)


def format_datetime(
    value: datetime,
    style: str = "medium",
    locale: str | None = None,
) -> str:
    """
    Format a datetime according to locale.

    Args:
        value: Datetime to format
        style: Format style - "short", "medium", "long", or "full"
        locale: Locale to use (defaults to context locale)

    Returns:
        Formatted datetime string
    """
    locale = _normalize_locale(locale)
    formats = DATETIME_FORMATS.get(locale, DATETIME_FORMATS["pt-BR"])
    pattern = formats.get(style, formats["medium"])

    result = value.strftime(pattern)

    if locale == "pt-BR":
        result = _localize_pt_br(result)

    return result


def format_number(
    value: float | int | "Decimal",
    decimals: int = 2,
    locale: str | None = None,
) -> str:
    """
    Format a number according to locale.

    Args:
        value: Number to format
        decimals: Number of decimal places
        locale: Locale to use (defaults to context locale)

    Returns:
        Formatted number string
    """
    locale = _normalize_locale(locale)

    # Format with standard Python formatting first
    formatted = f"{value:,.{decimals}f}"

    # Replace separators based on locale
    if locale == "pt-BR":
        # Python uses , for thousands and . for decimal
        # pt-BR uses . for thousands and , for decimal
        # Replace in steps to avoid conflicts
        formatted = formatted.replace(",", "TEMP")
        formatted = formatted.replace(".", ",")
        formatted = formatted.replace("TEMP", ".")

    return formatted


def format_currency(
    value: float | int | "Decimal",
    currency: str = "BRL",
    locale: str | None = None,
) -> str:
    """
    Format a currency value according to locale.

    Args:
        value: Amount to format
        currency: Currency code (BRL, USD, EUR)
        locale: Locale to use (defaults to context locale)

    Returns:
        Formatted currency string
    """
    locale = _normalize_locale(locale)
    formatted_number = format_number(value, decimals=2, locale=locale)

    currency_symbols = {
        "BRL": "R$",
        "USD": "$",
        "EUR": "€",
    }

    symbol = currency_symbols.get(currency, currency)

    if locale == "pt-BR":
        return f"{symbol} {formatted_number}"
    else:
        return f"{symbol}{formatted_number}"


def format_percentage(
    value: float,
    decimals: int = 1,
    locale: str | None = None,
) -> str:
    """
    Format a percentage value.

    Args:
        value: Value between 0 and 1 (e.g., 0.85 for 85%)
        decimals: Number of decimal places
        locale: Locale to use (defaults to context locale)

    Returns:
        Formatted percentage string (e.g., "85,0%" or "85.0%")
    """
    locale = _normalize_locale(locale)
    percentage = value * 100
    formatted = format_number(percentage, decimals=decimals, locale=locale)
    return f"{formatted}%"


def format_degree(
    value: float,
    decimals: int = 1,
    locale: str | None = None,
) -> str:
    """
    Format a degree value (for astrological positions).

    Args:
        value: Degree value
        decimals: Number of decimal places
        locale: Locale to use (defaults to context locale)

    Returns:
        Formatted degree string (e.g., "15,3°" or "15.3°")
    """
    locale = _normalize_locale(locale)
    formatted = format_number(value, decimals=decimals, locale=locale)
    return f"{formatted}°"
