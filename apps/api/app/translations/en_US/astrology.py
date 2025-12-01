"""
English translations for core astrological terms.
"""

from typing import Any

translations: dict[str, Any] = {
    "planets": {
        "Sun": "Sun",
        "Moon": "Moon",
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Mars": "Mars",
        "Jupiter": "Jupiter",
        "Saturn": "Saturn",
        "Uranus": "Uranus",
        "Neptune": "Neptune",
        "Pluto": "Pluto",
        "North Node": "North Node",
        "South Node": "South Node",
    },
    "signs": {
        "Aries": "Aries",
        "Taurus": "Taurus",
        "Gemini": "Gemini",
        "Cancer": "Cancer",
        "Leo": "Leo",
        "Virgo": "Virgo",
        "Libra": "Libra",
        "Scorpio": "Scorpio",
        "Sagittarius": "Sagittarius",
        "Capricorn": "Capricorn",
        "Aquarius": "Aquarius",
        "Pisces": "Pisces",
    },
    "elements": {
        "Fire": "Fire",
        "Earth": "Earth",
        "Air": "Air",
        "Water": "Water",
    },
    "qualities": {
        "hot": "Hot",
        "cold": "Cold",
        "wet": "Moist",
        "dry": "Dry",
    },
    "factors": {
        "ascendant": "Ascendant",
        "ascendant_ruler": "Ascendant Ruler",
        "solar_phase": "Solar Phase",
        "lunar_phase": "Lunar Phase",
        "lord_of_nativity": "Lord of Nativity",
    },
    "aspects": {
        "conjunction": "Conjunction",
        "opposition": "Opposition",
        "trine": "Trine",
        "square": "Square",
        "sextile": "Sextile",
        "quincunx": "Quincunx",
        "semisextile": "Semisextile",
        "semisquare": "Semisquare",
        "sesquiquadrate": "Sesquiquadrate",
    },
    "common": {
        "planet_in_sign": "{planet} in {sign}",
    },
}
