"""
Internationalization (i18n) module for the API.

Provides translation services for error messages and user-facing strings,
as well as locale-aware formatting for dates, numbers, and currencies.
"""

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

__all__ = [
    "Translator",
    "get_translator",
    "translate",
    "format_date",
    "format_time",
    "format_datetime",
    "format_number",
    "format_currency",
    "format_percentage",
    "format_degree",
]
