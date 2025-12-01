"""
Backend translation infrastructure for i18n support.

This module provides centralized translation management for the astrology API.
"""

from app.translations.loader import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, get_translation

__all__ = ["get_translation", "SUPPORTED_LANGUAGES", "DEFAULT_LANGUAGE"]
