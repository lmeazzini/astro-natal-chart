"""
Essential dignities calculation for traditional astrology.

This module implements the traditional system of essential dignities used in
Hellenistic and Medieval astrology, including:
- Rulership (Domicile)
- Exaltation
- Triplicity (by sect)
- Term (Bounds) - Egyptian system
- Face (Decan)
"""

from typing import Any

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

# Egyptian terms (bounds) - each planet rules specific degree ranges in each sign
# Format: {sign: [(start_degree, end_degree, planet), ...]}
EGYPTIAN_TERMS = {
    "Aries": [
        (0, 6, "Jupiter"),
        (6, 14, "Venus"),
        (14, 21, "Mercury"),
        (21, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
    "Taurus": [
        (0, 8, "Venus"),
        (8, 15, "Mercury"),
        (15, 22, "Jupiter"),
        (22, 27, "Saturn"),
        (27, 30, "Mars"),
    ],
    "Gemini": [
        (0, 7, "Mercury"),
        (7, 14, "Jupiter"),
        (14, 21, "Venus"),
        (21, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
    "Cancer": [
        (0, 7, "Mars"),
        (7, 13, "Venus"),
        (13, 19, "Mercury"),
        (19, 26, "Jupiter"),
        (26, 30, "Saturn"),
    ],
    "Leo": [
        (0, 6, "Jupiter"),
        (6, 13, "Venus"),
        (13, 19, "Mercury"),
        (19, 25, "Saturn"),
        (25, 30, "Mars"),
    ],
    "Virgo": [
        (0, 7, "Mercury"),
        (7, 13, "Venus"),
        (13, 18, "Jupiter"),
        (18, 24, "Mars"),
        (24, 30, "Saturn"),
    ],
    "Libra": [
        (0, 6, "Saturn"),
        (6, 11, "Venus"),
        (11, 19, "Jupiter"),
        (19, 24, "Mercury"),
        (24, 30, "Mars"),
    ],
    "Scorpio": [
        (0, 6, "Mars"),
        (6, 14, "Venus"),
        (14, 21, "Mercury"),
        (21, 27, "Jupiter"),
        (27, 30, "Saturn"),
    ],
    "Sagittarius": [
        (0, 8, "Jupiter"),
        (8, 14, "Venus"),
        (14, 19, "Mercury"),
        (19, 25, "Saturn"),
        (25, 30, "Mars"),
    ],
    "Capricorn": [
        (0, 6, "Venus"),
        (6, 12, "Mercury"),
        (12, 19, "Jupiter"),
        (19, 25, "Mars"),
        (25, 30, "Saturn"),
    ],
    "Aquarius": [
        (0, 6, "Saturn"),
        (6, 12, "Mercury"),
        (12, 20, "Venus"),
        (20, 25, "Jupiter"),
        (25, 30, "Mars"),
    ],
    "Pisces": [
        (0, 8, "Venus"),
        (8, 14, "Jupiter"),
        (14, 20, "Mercury"),
        (20, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
}

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
    term_ruler = get_planet_in_term(sign, degree)
    if term_ruler == planet:
        score += 2
        dignities.append("term")

    # Face (Decan) - +1
    face_ruler = get_planet_in_face(sign, degree)
    if face_ruler == planet:
        score += 1
        dignities.append("face")

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
