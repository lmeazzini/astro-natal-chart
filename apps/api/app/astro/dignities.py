"""
Essential dignities calculation for traditional astrology.

This module implements the traditional system of essential dignities used in
Hellenistic and Medieval astrology, including:
- Rulership (Domicile)
- Exaltation
- Triplicity (by sect)
- Term (Bounds) - Egyptian system (default, other systems available in terms.py)
- Face (Decan)
"""

from typing import Any

from app.astro.terms import EGYPTIAN_TERMS
from app.translations import DEFAULT_LANGUAGE, get_translation

# Zodiac signs in order
SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

# Traditional rulerships (domicile)
RULERSHIPS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# Exaltations with specific degrees
EXALTATIONS = {
    "Sun": {"sign": "Aries", "degree": 19},
    "Moon": {"sign": "Taurus", "degree": 3},
    "Mercury": {"sign": "Virgo", "degree": 15},
    "Venus": {"sign": "Pisces", "degree": 27},
    "Mars": {"sign": "Capricorn", "degree": 28},
    "Jupiter": {"sign": "Cancer", "degree": 15},
    "Saturn": {"sign": "Libra", "degree": 21},
}

# Triplicities by element and sect
TRIPLICITIES = {
    "Fire": {  # Aries, Leo, Sagittarius
        "day_ruler": "Sun",
        "night_ruler": "Jupiter",
        "participant": "Saturn",
    },
    "Earth": {  # Taurus, Virgo, Capricorn
        "day_ruler": "Venus",
        "night_ruler": "Moon",
        "participant": "Mars",
    },
    "Air": {  # Gemini, Libra, Aquarius
        "day_ruler": "Saturn",
        "night_ruler": "Mercury",
        "participant": "Jupiter",
    },
    "Water": {  # Cancer, Scorpio, Pisces
        "day_ruler": "Venus",
        "night_ruler": "Mars",
        "participant": "Moon",
    },
}

# Element for each sign
SIGN_ELEMENTS = {
    "Aries": "Fire",
    "Taurus": "Earth",
    "Gemini": "Air",
    "Cancer": "Water",
    "Leo": "Fire",
    "Virgo": "Earth",
    "Libra": "Air",
    "Scorpio": "Water",
    "Sagittarius": "Fire",
    "Capricorn": "Earth",
    "Aquarius": "Air",
    "Pisces": "Water",
}

# Egyptian terms are now imported from app.astro.terms
# For other term systems (Ptolemaic, Chaldean, Dorothean), use app.astro.terms module directly

# Faces (decans) - 10-degree divisions, ruled by planets in Chaldean order
# Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon (repeated)
CHALDEAN_ORDER = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]

# Faces for each sign (3 decans of 10 degrees each)
FACES = {
    "Aries": [(0, 10, "Mars"), (10, 20, "Sun"), (20, 30, "Venus")],
    "Taurus": [(0, 10, "Mercury"), (10, 20, "Moon"), (20, 30, "Saturn")],
    "Gemini": [(0, 10, "Jupiter"), (10, 20, "Mars"), (20, 30, "Sun")],
    "Cancer": [(0, 10, "Venus"), (10, 20, "Mercury"), (20, 30, "Moon")],
    "Leo": [(0, 10, "Saturn"), (10, 20, "Jupiter"), (20, 30, "Mars")],
    "Virgo": [(0, 10, "Sun"), (10, 20, "Venus"), (20, 30, "Mercury")],
    "Libra": [(0, 10, "Moon"), (10, 20, "Saturn"), (20, 30, "Jupiter")],
    "Scorpio": [(0, 10, "Mars"), (10, 20, "Sun"), (20, 30, "Venus")],
    "Sagittarius": [(0, 10, "Mercury"), (10, 20, "Moon"), (20, 30, "Saturn")],
    "Capricorn": [(0, 10, "Jupiter"), (10, 20, "Mars"), (20, 30, "Sun")],
    "Aquarius": [(0, 10, "Venus"), (10, 20, "Mercury"), (20, 30, "Moon")],
    "Pisces": [(0, 10, "Saturn"), (10, 20, "Jupiter"), (20, 30, "Mars")],
}

# Dignity type to emoji icon mapping
DIGNITY_ICONS = {
    "ruler": "👑",
    "exalted": "⭐",
    "triplicity_day": "☀️",
    "triplicity_night": "🌙",
    "triplicity_participant": "✨",
    "term": "📜",
    "face": "🎭",
    "detriment": "⚠️",
    "fall": "⬇️",
}

# Points for each dignity type
DIGNITY_POINTS = {
    "ruler": 5,
    "exalted": 4,
    "triplicity_day": 3,
    "triplicity_night": 3,
    "triplicity_participant": 3,
    "term": 2,
    "face": 1,
    "detriment": -5,
    "fall": -4,
}


def get_planet_in_term(sign: str, degree: float) -> str | None:
    """
    Get the planet that rules the term (bound) for a given degree in a sign.

    Args:
        sign: Zodiac sign name
        degree: Degree within the sign (0-30)

    Returns:
        Planet name that rules the term, or None if not found
    """
    if sign not in EGYPTIAN_TERMS:
        return None

    for start, end, planet in EGYPTIAN_TERMS[sign]:
        if start <= degree < end:
            return planet
    return None


def get_planet_in_face(sign: str, degree: float) -> str | None:
    """
    Get the planet that rules the face (decan) for a given degree in a sign.

    Args:
        sign: Zodiac sign name
        degree: Degree within the sign (0-30)

    Returns:
        Planet name that rules the face, or None if not found
    """
    if sign not in FACES:
        return None

    for start, end, planet in FACES[sign]:
        if start <= degree < end:
            return planet
    return None


def calculate_essential_dignities(
    planet: str, sign: str, degree: float, sect: str
) -> dict[str, Any]:
    """
    Calculate all essential dignities for a planet.

    This follows the traditional point system:
    - Rulership (Domicile): +5
    - Exaltation: +4
    - Triplicity: +3 (for day/night ruler), +3 (for participant)
    - Term: +2
    - Face: +1
    - Detriment (opposite of rulership): -5
    - Fall (opposite of exaltation): -4

    Args:
        planet: Planet name (e.g., "Sun", "Moon", "Mars")
        sign: Zodiac sign name (e.g., "Aries", "Taurus")
        degree: Degree within the sign (0.0-30.0)
        sect: Chart sect - "diurnal" (day chart) or "nocturnal" (night chart)

    Returns:
        Dictionary containing:
        - score: Total dignity score
        - dignities: List of dignity names
        - is_ruler: Boolean
        - is_exalted: Boolean
        - is_detriment: Boolean
        - is_fall: Boolean
        - triplicity_ruler: str or None
        - term_ruler: str or None
        - face_ruler: str or None
        - classification: "dignified", "peregrine", or "debilitated"
    """
    score = 0
    dignities: list[str] = []

    # Rulership (Domicile) - +5
    is_ruler = RULERSHIPS.get(sign) == planet
    if is_ruler:
        score += 5
        dignities.append("ruler")

    # Detriment (opposite of rulership) - -5
    sign_index = SIGNS.index(sign)
    opposite_sign = SIGNS[(sign_index + 6) % 12]
    is_detriment = RULERSHIPS.get(opposite_sign) == planet
    if is_detriment:
        score -= 5
        dignities.append("detriment")

    # Exaltation - +4
    is_exalted = False
    if planet in EXALTATIONS:
        exalt_data = EXALTATIONS[planet]
        is_exalted = exalt_data["sign"] == sign
        if is_exalted:
            score += 4
            dignities.append("exalted")

    # Fall (opposite of exaltation) - -4
    is_fall = False
    if planet in EXALTATIONS:
        exalt_data = EXALTATIONS[planet]
        exalt_sign = str(exalt_data["sign"])  # Type cast for mypy
        exalt_sign_index = SIGNS.index(exalt_sign)
        fall_sign = SIGNS[(exalt_sign_index + 6) % 12]
        is_fall = fall_sign == sign
        if is_fall:
            score -= 4
            dignities.append("fall")

    # Triplicity - +3
    triplicity_ruler: str | None = None
    element = SIGN_ELEMENTS.get(sign)
    if element and element in TRIPLICITIES:
        trip_data = TRIPLICITIES[element]
        if sect == "diurnal":
            if trip_data["day_ruler"] == planet:
                score += 3
                dignities.append("triplicity_day")
                triplicity_ruler = "day"
            elif trip_data["participant"] == planet:
                score += 3
                dignities.append("triplicity_participant")
                triplicity_ruler = "participant"
        else:  # nocturnal
            if trip_data["night_ruler"] == planet:
                score += 3
                dignities.append("triplicity_night")
                triplicity_ruler = "night"
            elif trip_data["participant"] == planet:
                score += 3
                dignities.append("triplicity_participant")
                triplicity_ruler = "participant"

    # Term (Bound) - +2
    term_ruler_planet = get_planet_in_term(sign, degree)
    term_ruler = None
    if term_ruler_planet == planet:
        score += 2
        dignities.append("term")
        term_ruler = planet

    # Face (Decan) - +1
    face_ruler_planet = get_planet_in_face(sign, degree)
    face_ruler = None
    if face_ruler_planet == planet:
        score += 1
        dignities.append("face")
        face_ruler = planet

    # Classification
    if score >= 4:
        classification = "dignified"
    elif score <= -4:
        classification = "debilitated"
    else:
        classification = "peregrine"

    return {
        "score": score,
        "dignities": dignities,
        "is_ruler": is_ruler,
        "is_exalted": is_exalted,
        "is_detriment": is_detriment,
        "is_fall": is_fall,
        "triplicity_ruler": triplicity_ruler,
        "term_ruler": term_ruler,
        "face_ruler": face_ruler,
        "classification": classification,
    }


def get_sign_ruler(sign: str) -> str | None:
    """
    Get the traditional ruler of a zodiac sign.

    Args:
        sign: Zodiac sign name

    Returns:
        Planet name that rules the sign, or None if sign not found
    """
    return RULERSHIPS.get(sign)


def find_lord_of_nativity(
    planets_with_dignities: list[dict[str, Any]],
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any] | None:
    """
    Find the Lord of Nativity - the planet with the highest essential dignity score.

    The Lord of Nativity represents the dominant life force and vital energy
    in the natal chart according to traditional astrology.

    Args:
        planets_with_dignities: List of planet dictionaries with dignity data
        language: Language for translations ('en-US' or 'pt-BR')

    Returns:
        Dictionary containing:
        - planet: Name of the planet (localized)
        - planet_key: Internal planet key (e.g., "Sun", "Moon")
        - score: Total dignity score
        - sign: Zodiac sign where planet is located (localized)
        - sign_key: Internal sign key
        - house: House number
        - dignities: Breakdown of dignity components
        Or None if no planets have dignities

    Tie-breaking priority (if multiple planets have same score):
    1. Sun
    2. Moon
    3. Mercury
    4. Venus
    5. Mars
    6. Jupiter
    7. Saturn
    """
    # Priority order for tie-breaking
    planet_priority = {
        "Sun": 1,
        "Moon": 2,
        "Mercury": 3,
        "Venus": 4,
        "Mars": 5,
        "Jupiter": 6,
        "Saturn": 7,
    }

    # Filter only classical planets with dignities
    classical_planets = [
        p for p in planets_with_dignities if p.get("name") in planet_priority and p.get("dignities")
    ]

    if not classical_planets:
        return None

    # Find planet(s) with highest score
    max_score = max(p["dignities"]["score"] for p in classical_planets)

    # Get all planets with max score
    top_planets = [p for p in classical_planets if p["dignities"]["score"] == max_score]

    # If tie, use priority order (Sun > Moon > Mercury > Venus > Mars > Jupiter > Saturn)
    if len(top_planets) > 1:
        lord = min(top_planets, key=lambda p: planet_priority.get(p["name"], 999))
    else:
        lord = top_planets[0]

    # Build detailed dignity breakdown for display
    dignity_details = []
    dign = lord["dignities"]

    # Map dignity types to their translation keys and icons
    dignity_type_map = [
        ("is_ruler", "ruler", "domicile", 5, DIGNITY_ICONS["ruler"]),
        ("is_exalted", "exalted", "exaltation", 4, DIGNITY_ICONS["exalted"]),
        ("is_detriment", "detriment", "detriment", -5, DIGNITY_ICONS["detriment"]),
        ("is_fall", "fall", "fall", -4, DIGNITY_ICONS["fall"]),
    ]

    for check_key, dignity_key, trans_key, points, icon in dignity_type_map:
        if dign.get(check_key):
            dignity_details.append(
                {
                    "type": dignity_key,
                    "label": get_translation(f"dignities.{trans_key}", language),
                    "points": points,
                    "icon": icon,
                }
            )

    if dign.get("triplicity_ruler"):
        trip_type = dign["triplicity_ruler"]
        trip_key = (
            f"triplicity_{trip_type}" if trip_type != "participant" else "triplicity_participant"
        )
        icon = DIGNITY_ICONS.get(trip_key, "star")
        dignity_details.append(
            {
                "type": "triplicity",
                "label": get_translation(f"dignities.{trip_key}", language),
                "points": 3,
                "icon": icon,
            }
        )

    if dign.get("term_ruler"):
        dignity_details.append(
            {
                "type": "term",
                "label": get_translation("dignities.term", language),
                "points": 2,
                "icon": DIGNITY_ICONS["term"],
            }
        )

    if dign.get("face_ruler"):
        dignity_details.append(
            {
                "type": "face",
                "label": get_translation("dignities.face", language),
                "points": 1,
                "icon": DIGNITY_ICONS["face"],
            }
        )

    # Get localized planet and sign names
    planet_key = lord["name"]
    sign_key = lord["sign"]
    planet_name = get_translation(f"planets.{planet_key}", language)
    sign_name = get_translation(f"signs.{sign_key}", language)

    return {
        "planet": planet_name,
        "planet_key": planet_key,
        "score": dign["score"],
        "sign": sign_name,
        "sign_key": sign_key,
        "house": lord.get("house", 0),
        "classification": dign.get("classification", "peregrine"),
        "dignity_details": dignity_details,
    }
