"""
Solar Phase calculation based on Sun sign.

This module calculates the solar phase at birth based on the zodiac sign
where the Sun is positioned. The 12 signs are divided into 4 phases of 3 signs each,
corresponding to the 4 traditional temperaments.
"""

from typing import Any

from app.translations import DEFAULT_LANGUAGE, get_translation

# Phase keys and their associated signs
PHASE_KEYS = ["first", "second", "third", "fourth"]

# Map signs to phase key
SIGN_TO_PHASE_KEY = {
    # Phase 1: Sanguine (Hot & Moist)
    "Aries": "first",
    "Taurus": "first",
    "Gemini": "first",
    # Phase 2: Choleric (Hot & Dry)
    "Cancer": "second",
    "Leo": "second",
    "Virgo": "second",
    # Phase 3: Melancholic (Cold & Dry)
    "Libra": "third",
    "Scorpio": "third",
    "Sagittarius": "third",
    # Phase 4: Phlegmatic (Cold & Moist)
    "Capricorn": "fourth",
    "Aquarius": "fourth",
    "Pisces": "fourth",
}

# Phase number mapping
PHASE_KEY_TO_NUMBER = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
}


def calculate_solar_phase(sun_sign: str, language: str = DEFAULT_LANGUAGE) -> dict[str, Any]:
    """
    Calculate the solar phase based on the Sun's zodiac sign.

    The 12 signs are divided into 4 phases:
    - Phase 1 (Signs 1-3): Aries, Taurus, Gemini -> Sanguine (Hot & Moist)
    - Phase 2 (Signs 4-6): Cancer, Leo, Virgo -> Choleric (Hot & Dry)
    - Phase 3 (Signs 7-9): Libra, Scorpio, Sagittarius -> Melancholic (Cold & Dry)
    - Phase 4 (Signs 10-12): Capricorn, Aquarius, Pisces -> Phlegmatic (Cold & Moist)

    Args:
        sun_sign: Name of the zodiac sign (e.g., "Aries", "Taurus")
        language: Language for translations ('en-US' or 'pt-BR')

    Returns:
        Dictionary containing:
        - phase_key: Internal key for the phase (e.g., "first")
        - phase_number: Number of the phase (1-4)
        - phase_name: Localized name of the phase
        - temperament: Localized temperament name
        - qualities: Localized qualities (Hot/Cold and Dry/Moist)
        - signs: List of localized sign names in this phase
        - description: Localized interpretation

    Example:
        >>> calculate_solar_phase("Aries", "en-US")
        {
            "phase_key": "first",
            "phase_number": 1,
            "phase_name": "1st Solar Phase",
            "temperament": "Sanguine",
            "qualities": "Hot & Moist",
            "signs": ["Aries", "Taurus", "Gemini"],
            "description": "...",
        }
    """
    phase_key = SIGN_TO_PHASE_KEY.get(sun_sign)

    if phase_key is None:
        return {
            "phase_key": "unknown",
            "phase_number": 0,
            "phase_name": get_translation("solar_phases.unknown.name", language) or "Unknown",
            "temperament": get_translation("temperaments.unknown.name", language) or "Unknown",
            "qualities": "Unknown",
            "signs": [],
            "description": "Solar phase not found for this sign.",
        }

    phase_number = PHASE_KEY_TO_NUMBER[phase_key]

    # Get translations
    phase_name = get_translation(f"solar_phases.{phase_key}.name", language)
    temperament = get_translation(f"solar_phases.{phase_key}.temperament", language)
    qualities = get_translation(f"solar_phases.{phase_key}.qualities", language)
    description = get_translation(f"solar_phases.{phase_key}.description", language)

    # Get localized sign names
    signs_data = get_translation(f"solar_phases.{phase_key}.signs", language)
    signs: list[str] = signs_data if isinstance(signs_data, list) else []

    return {
        "phase_key": phase_key,
        "phase_number": phase_number,
        "phase_name": phase_name,
        "temperament": temperament,
        "qualities": qualities,
        "signs": signs,
        "description": description,
    }
