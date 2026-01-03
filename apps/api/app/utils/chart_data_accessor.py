"""
Chart Data Accessor Utility

Provides backward-compatible access to chart_data JSONB column.
Handles both legacy flat format and new language-first format.

Formats supported:
- Language-first (new): {"en-US": {...}, "pt-BR": {...}}
- Flat (legacy): {"planets": [...], "houses": [...], "aspects": [...]}
"""

from typing import Any

from loguru import logger

# Supported languages
SUPPORTED_LANGUAGES = {"en-US", "pt-BR"}


def extract_language_data(chart_data: dict[str, Any], language: str = "pt-BR") -> dict[str, Any]:
    """
    Extract language-specific data from chart_data with backward compatibility.

    Handles both formats:
    - Language-first: {"en-US": {...}, "pt-BR": {...}}
    - Flat (legacy): {"planets": [...], "houses": [...]}

    Args:
        chart_data: The chart_data JSONB dict
        language: Target language code (default: "pt-BR")

    Returns:
        Language-specific chart data dict

    Examples:
        >>> # Language-first format
        >>> data = {"en-US": {"planets": [...]}, "pt-BR": {"planets": [...]}}
        >>> extract_language_data(data, "pt-BR")
        {"planets": [...]}

        >>> # Legacy flat format
        >>> data = {"planets": [...], "houses": [...]}
        >>> extract_language_data(data, "pt-BR")
        {"planets": [...], "houses": [...]}
    """
    if not chart_data:
        return {}

    # Check if language-first format (exact match)
    if language in chart_data:
        logger.debug(f"Extracting chart data for language: {language}")
        lang_data: dict[str, Any] = chart_data[language]
        return lang_data

    # Check if another supported language exists (language-first but wrong language)
    available_languages = SUPPORTED_LANGUAGES & set(chart_data.keys())
    if available_languages:
        # Fallback to first available language
        fallback_lang = next(iter(available_languages))
        logger.warning(
            f"Requested language '{language}' not found. Falling back to '{fallback_lang}'"
        )
        fallback_data: dict[str, Any] = chart_data[fallback_lang]
        return fallback_data

    # Legacy flat format - return as-is
    logger.debug("Using legacy flat chart_data format")
    return chart_data


def is_language_first_format(chart_data: dict[str, Any]) -> bool:
    """
    Check if chart_data uses language-first structure.

    Args:
        chart_data: The chart_data JSONB dict

    Returns:
        True if language-first format, False if legacy flat format

    Examples:
        >>> is_language_first_format({"en-US": {...}, "pt-BR": {...}})
        True

        >>> is_language_first_format({"planets": [...], "houses": [...]})
        False
    """
    if not chart_data:
        return False

    # Check if any supported language key exists at top level
    return bool(SUPPORTED_LANGUAGES & set(chart_data.keys()))


def get_available_languages(chart_data: dict[str, Any]) -> list[str]:
    """
    Get list of available languages in chart_data.

    Args:
        chart_data: The chart_data JSONB dict

    Returns:
        List of available language codes (e.g., ["en-US", "pt-BR"])
        Empty list if legacy flat format

    Examples:
        >>> get_available_languages({"en-US": {...}, "pt-BR": {...}})
        ["en-US", "pt-BR"]

        >>> get_available_languages({"planets": [...], "houses": [...]})
        []
    """
    if not chart_data:
        return []

    if is_language_first_format(chart_data):
        return sorted(SUPPORTED_LANGUAGES & set(chart_data.keys()))

    return []


def validate_language_data(chart_data: dict[str, Any], language: str) -> tuple[bool, str]:
    """
    Validate that chart_data has required structure for given language.

    Args:
        chart_data: The chart_data JSONB dict
        language: Target language code

    Returns:
        Tuple of (is_valid, error_message)
        (True, "") if valid, (False, "error message") if invalid

    Examples:
        >>> data = {"en-US": {"planets": [], "houses": []}}
        >>> validate_language_data(data, "en-US")
        (True, "")

        >>> validate_language_data({}, "pt-BR")
        (False, "chart_data is empty")
    """
    if not chart_data:
        return False, "chart_data is empty"

    lang_data = extract_language_data(chart_data, language)

    if not lang_data:
        return False, f"No data found for language '{language}'"

    # Check for essential keys
    required_keys = {"planets", "houses"}
    missing_keys = required_keys - set(lang_data.keys())

    if missing_keys:
        return False, f"Missing required keys: {missing_keys}"

    return True, ""
