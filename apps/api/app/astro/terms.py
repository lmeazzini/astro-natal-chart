"""
Planetary Terms (Bounds) - Traditional Astrology Essential Dignities

Terms divide each zodiac sign into 5 unequal segments, each ruled by one of
the five non-luminary planets (Saturn, Jupiter, Mars, Venus, Mercury).

This module implements four historical term systems:
- Egyptian Terms: Most widely used in Hellenistic astrology
- Ptolemaic Terms: Ptolemy's refined system from Tetrabiblos
- Chaldean Terms: Regular 8-7-6-5-4 degree pattern
- Dorothean Terms: From Dorotheus of Sidon

A planet in its own term receives +2 dignity points.

Sources:
- Ptolemy, Tetrabiblos (Book I, Ch. 20-21)
- Vettius Valens, Anthology
- Dorotheus of Sidon
"""

from enum import Enum

# Zodiac signs in order
ZODIAC_SIGNS = [
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


class TermSystem(str, Enum):
    """Available term systems for planetary bounds."""

    EGYPTIAN = "egyptian"
    PTOLEMAIC = "ptolemaic"
    CHALDEAN = "chaldean"
    DOROTHEAN = "dorothean"


# =============================================================================
# Egyptian Terms (Most widely used in Hellenistic astrology)
# =============================================================================
# Format: {sign: [(start_degree, end_degree, planet), ...]}

EGYPTIAN_TERMS: dict[str, list[tuple[int, int, str]]] = {
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


# =============================================================================
# Ptolemaic Terms (From Ptolemy's Tetrabiblos)
# =============================================================================
# Ptolemy's refined system differs slightly from Egyptian terms.
# Based on considerations of exaltations, triplicities, and houses.

PTOLEMAIC_TERMS: dict[str, list[tuple[int, int, str]]] = {
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
        (22, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Gemini": [
        (0, 7, "Mercury"),
        (7, 14, "Jupiter"),
        (14, 21, "Venus"),
        (21, 25, "Saturn"),
        (25, 30, "Mars"),
    ],
    "Cancer": [
        (0, 6, "Mars"),
        (6, 13, "Jupiter"),
        (13, 20, "Mercury"),
        (20, 27, "Venus"),
        (27, 30, "Saturn"),
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
        (18, 24, "Saturn"),
        (24, 30, "Mars"),
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
        (6, 13, "Jupiter"),
        (13, 21, "Venus"),
        (21, 27, "Mercury"),
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
        (19, 25, "Saturn"),
        (25, 30, "Mars"),
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


# =============================================================================
# Chaldean Terms (Regular 8-7-6-5-4 degree pattern)
# =============================================================================
# The Chaldean system uses a fixed 8-7-6-5-4 degree pattern per sign.
# The triplicity lord receives the first (longest) term.
# Fire triplicity (Aries, Leo, Sag): Jupiter leads
# Earth triplicity (Taurus, Virgo, Cap): Venus leads
# Air triplicity (Gemini, Libra, Aqua): Mercury or Saturn leads
# Water triplicity (Cancer, Scorpio, Pisces): Mars or Venus leads

CHALDEAN_TERMS: dict[str, list[tuple[int, int, str]]] = {
    "Aries": [
        (0, 8, "Jupiter"),
        (8, 15, "Venus"),
        (15, 21, "Mercury"),
        (21, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Taurus": [
        (0, 8, "Venus"),
        (8, 15, "Jupiter"),
        (15, 21, "Mercury"),
        (21, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Gemini": [
        (0, 8, "Mercury"),
        (8, 15, "Jupiter"),
        (15, 21, "Venus"),
        (21, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Cancer": [
        (0, 8, "Mars"),
        (8, 15, "Jupiter"),
        (15, 21, "Venus"),
        (21, 26, "Mercury"),
        (26, 30, "Saturn"),
    ],
    "Leo": [
        (0, 8, "Jupiter"),
        (8, 15, "Venus"),
        (15, 21, "Mercury"),
        (21, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Virgo": [
        (0, 8, "Venus"),
        (8, 15, "Jupiter"),
        (15, 21, "Mercury"),
        (21, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
    "Libra": [
        (0, 8, "Saturn"),
        (8, 15, "Venus"),
        (15, 21, "Jupiter"),
        (21, 26, "Mercury"),
        (26, 30, "Mars"),
    ],
    "Scorpio": [
        (0, 8, "Mars"),
        (8, 15, "Venus"),
        (15, 21, "Jupiter"),
        (21, 26, "Mercury"),
        (26, 30, "Saturn"),
    ],
    "Sagittarius": [
        (0, 8, "Jupiter"),
        (8, 15, "Venus"),
        (15, 21, "Mercury"),
        (21, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Capricorn": [
        (0, 8, "Venus"),
        (8, 15, "Mercury"),
        (15, 21, "Jupiter"),
        (21, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
    "Aquarius": [
        (0, 8, "Saturn"),
        (8, 15, "Mercury"),
        (15, 21, "Venus"),
        (21, 26, "Jupiter"),
        (26, 30, "Mars"),
    ],
    "Pisces": [
        (0, 8, "Venus"),
        (8, 15, "Jupiter"),
        (15, 21, "Mercury"),
        (21, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
}


# =============================================================================
# Dorothean Terms (From Dorotheus of Sidon)
# =============================================================================
# Very similar to Egyptian terms with minor variations.
# Based on Dorotheus of Sidon's Carmen Astrologicum.

DOROTHEAN_TERMS: dict[str, list[tuple[int, int, str]]] = {
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
        (22, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Gemini": [
        (0, 7, "Mercury"),
        (7, 13, "Jupiter"),
        (13, 20, "Venus"),
        (20, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Cancer": [
        (0, 6, "Mars"),
        (6, 13, "Jupiter"),
        (13, 20, "Mercury"),
        (20, 27, "Venus"),
        (27, 30, "Saturn"),
    ],
    "Leo": [
        (0, 6, "Saturn"),
        (6, 13, "Mercury"),
        (13, 18, "Venus"),
        (18, 24, "Jupiter"),
        (24, 30, "Mars"),
    ],
    "Virgo": [
        (0, 7, "Mercury"),
        (7, 13, "Venus"),
        (13, 18, "Jupiter"),
        (18, 24, "Saturn"),
        (24, 30, "Mars"),
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
        (6, 13, "Jupiter"),
        (13, 21, "Venus"),
        (21, 27, "Mercury"),
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


# =============================================================================
# Term System Lookup
# =============================================================================

TERM_SYSTEMS: dict[TermSystem, dict[str, list[tuple[int, int, str]]]] = {
    TermSystem.EGYPTIAN: EGYPTIAN_TERMS,
    TermSystem.PTOLEMAIC: PTOLEMAIC_TERMS,
    TermSystem.CHALDEAN: CHALDEAN_TERMS,
    TermSystem.DOROTHEAN: DOROTHEAN_TERMS,
}


# =============================================================================
# Functions
# =============================================================================


def _longitude_to_sign_and_degree(longitude: float) -> tuple[str, float]:
    """
    Convert ecliptic longitude to zodiac sign and degree within sign.

    Args:
        longitude: Ecliptic longitude in degrees (0-359.999...)

    Returns:
        Tuple of (sign_name, degree_in_sign)
    """
    sign_index = int(longitude / 30)
    degree_in_sign = longitude % 30
    return ZODIAC_SIGNS[sign_index], degree_in_sign


def get_term_ruler(
    longitude: float,
    system: TermSystem = TermSystem.EGYPTIAN,
) -> dict:
    """
    Get the term ruler for a specific ecliptic longitude.

    Args:
        longitude: Ecliptic longitude in degrees (0-359.999...)
        system: Which term system to use (default: Egyptian)

    Returns:
        Dictionary with term information:
        - longitude: Original longitude
        - sign: Zodiac sign name
        - degree_in_sign: Degree within the sign (0-29.999...)
        - term_ruler: Planet ruling this term
        - term_start: Start degree of this term
        - term_end: End degree of this term
        - term_system: Which system was used

    Raises:
        ValueError: If longitude is not in valid range [0, 360)
    """
    if longitude < 0 or longitude >= 360:
        raise ValueError(f"Longitude must be in range [0, 360), got {longitude}")

    sign, degree_in_sign = _longitude_to_sign_and_degree(longitude)
    terms = TERM_SYSTEMS[system][sign]

    for start, end, ruler in terms:
        if start <= degree_in_sign < end:
            return {
                "longitude": longitude,
                "sign": sign,
                "degree_in_sign": degree_in_sign,
                "term_ruler": ruler,
                "term_start": start,
                "term_end": end,
                "term_system": system,
            }

    # Should never reach here if terms are properly defined
    raise ValueError(f"Could not find term for {degree_in_sign}° {sign}")


def get_all_term_rulers(
    planets: list[dict],
    system: TermSystem = TermSystem.EGYPTIAN,
) -> dict:
    """
    Get term rulers for all planets in a chart.

    Args:
        planets: List of planet dictionaries with at least 'name' and 'longitude' keys
        system: Which term system to use (default: Egyptian)

    Returns:
        Dictionary with:
        - system: The term system used
        - planets: List of planet term info dictionaries
        - summary: Analysis summary with planets in own term and frequency

    Example:
        >>> planets = [{"name": "Sun", "longitude": 45.0}, ...]
        >>> result = get_all_term_rulers(planets)
        >>> result["planets"][0]["term_ruler"]
        "Jupiter"
    """
    planet_term_info = []
    planets_in_own_term = []
    term_ruler_counts: dict[str, int] = {}

    for planet in planets:
        name = planet.get("name", "")
        longitude = planet.get("longitude", 0.0)

        try:
            term_info = get_term_ruler(longitude, system)
            term_ruler = term_info["term_ruler"]
            in_own_term = name == term_ruler

            planet_term_info.append(
                {
                    "planet": name,
                    "term_ruler": term_ruler,
                    "in_own_term": in_own_term,
                }
            )

            if in_own_term:
                planets_in_own_term.append(name)

            term_ruler_counts[term_ruler] = term_ruler_counts.get(term_ruler, 0) + 1

        except (ValueError, KeyError):
            # Skip planets with invalid positions
            continue

    return {
        "system": system,
        "planets": planet_term_info,
        "summary": {
            "planets_in_own_term": planets_in_own_term,
            "term_ruler_frequency": term_ruler_counts,
        },
    }


def get_terms_table(system: TermSystem = TermSystem.EGYPTIAN) -> dict:
    """
    Get the complete terms table for a specific system.

    Useful for displaying a reference table of all terms.

    Args:
        system: Which term system to use (default: Egyptian)

    Returns:
        Dictionary with:
        - system: The term system
        - signs: Dictionary mapping sign names to lists of term entries

    Each term entry contains:
        - ruler: Planet ruling this term
        - start: Start degree (0-29)
        - end: End degree (1-30)
    """
    terms_data = TERM_SYSTEMS[system]
    signs_output = {}

    for sign in ZODIAC_SIGNS:
        sign_terms = []
        for start, end, ruler in terms_data[sign]:
            sign_terms.append(
                {
                    "ruler": ruler,
                    "start": start,
                    "end": end,
                }
            )
        signs_output[sign] = sign_terms

    return {
        "system": system,
        "signs": signs_output,
    }


def get_planet_in_term(
    sign: str,
    degree: float,
    system: TermSystem = TermSystem.EGYPTIAN,
) -> str | None:
    """
    Get the planet that rules a specific degree in a sign.

    This is a simplified lookup function for use in dignity calculations.

    Args:
        sign: Zodiac sign name (e.g., "Aries", "Taurus")
        degree: Degree within the sign (0-29.999...)
        system: Which term system to use (default: Egyptian)

    Returns:
        Planet name ruling this term, or None if sign not found
    """
    terms = TERM_SYSTEMS.get(system, {}).get(sign)
    if not terms:
        return None

    for start, end, ruler in terms:
        if start <= degree < end:
            return ruler

    return None
