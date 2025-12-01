"""
Lunar Phase calculation and interpretations.

This module calculates the Moon phase at birth based on the angle
between the Sun and Moon, following the 8-phase lunation cycle.
"""

import math
from typing import Any

from app.translations import DEFAULT_LANGUAGE, get_translation

# Phase keys in order by angle range
PHASE_KEYS = [
    "new_moon",  # 0-45°
    "waxing_crescent",  # 45-90°
    "first_quarter",  # 90-135°
    "waxing_gibbous",  # 135-180°
    "full_moon",  # 180-225°
    "waning_gibbous",  # 225-270°
    "last_quarter",  # 270-315°
    "waning_crescent",  # 315-360°
]

# Emoji for each phase
PHASE_EMOJIS = {
    "new_moon": "🌑",
    "waxing_crescent": "🌒",
    "first_quarter": "🌓",
    "waxing_gibbous": "🌔",
    "full_moon": "🌕",
    "waning_gibbous": "🌖",
    "last_quarter": "🌗",
    "waning_crescent": "🌘",
}


def get_phase_key_from_angle(angle: float) -> str:
    """
    Get the phase key based on the Moon-Sun angle.

    Args:
        angle: Angle between Moon and Sun (0-360)

    Returns:
        Phase key string
    """
    if 0 <= angle < 45:
        return "new_moon"
    elif 45 <= angle < 90:
        return "waxing_crescent"
    elif 90 <= angle < 135:
        return "first_quarter"
    elif 135 <= angle < 180:
        return "waxing_gibbous"
    elif 180 <= angle < 225:
        return "full_moon"
    elif 225 <= angle < 270:
        return "waning_gibbous"
    elif 270 <= angle < 315:
        return "last_quarter"
    else:  # 315 <= angle < 360
        return "waning_crescent"


def calculate_lunar_phase(
    sun_longitude: float, moon_longitude: float, language: str = DEFAULT_LANGUAGE
) -> dict[str, Any]:
    """
    Calculate the lunar phase at birth.

    The lunar phase is determined by the angle between the Sun and Moon.
    Formula: (Moon longitude - Sun longitude) % 360

    Args:
        sun_longitude: Sun's ecliptic longitude in degrees (0-360)
        moon_longitude: Moon's ecliptic longitude in degrees (0-360)
        language: Language for translations ('en-US' or 'pt-BR')

    Returns:
        Dictionary containing:
        - phase_key: Internal key for the phase (e.g., "new_moon")
        - phase_name: Localized name of the phase
        - angle: Exact angle between Moon and Sun (0-360)
        - illumination_percentage: Approximate illumination (0-100)
        - emoji: Unicode emoji representing the phase
        - keywords: Key characteristics of the phase (localized)
        - interpretation: Detailed interpretation (localized)
    """
    # Calculate angle (Moon - Sun), normalized to 0-360
    angle = (moon_longitude - sun_longitude) % 360

    # Get phase key from angle
    phase_key = get_phase_key_from_angle(angle)

    # Get translations
    phase_name = get_translation(f"lunar_phases.{phase_key}.name", language)
    keywords = get_translation(f"lunar_phases.{phase_key}.keywords", language)
    interpretation = get_translation(f"lunar_phases.{phase_key}.interpretation", language)
    emoji = PHASE_EMOJIS[phase_key]

    # Calculate approximate illumination percentage
    # Formula: (1 - cos(angle)) / 2 * 100
    # This gives 0% at New Moon (0°) and 100% at Full Moon (180°)
    illumination = (1 - math.cos(math.radians(angle))) / 2 * 100

    return {
        "phase_key": phase_key,
        "phase_name": phase_name,
        "angle": round(angle, 2),
        "illumination_percentage": round(illumination, 1),
        "emoji": emoji,
        "keywords": keywords,
        "interpretation": interpretation,
    }
