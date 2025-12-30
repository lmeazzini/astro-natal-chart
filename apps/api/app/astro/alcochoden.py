"""
Alcochoden (Giver of Years) calculation for traditional astrology.

The Alcochoden (from Arabic "al-kadhkhudāh", from Persian "kadkhudā" = master of the house)
is the planet that determines the "years of life" in traditional astrology. It works in
conjunction with the Hyleg (Giver of Life).

How It Works:
1. Find the Hyleg (Giver of Life) - the vital point in the chart
2. Identify which planet has the most essential dignity at the Hyleg's degree
3. That planet must also aspect the Hyleg to qualify
4. The qualifying planet becomes the Alcochoden
5. The Alcochoden's planetary years indicate potential lifespan
6. Modifications are applied based on the Alcochoden's condition
"""

from typing import Any

from app.astro.dignities import (
    EGYPTIAN_TERMS,
    EXALTATIONS,
    FACES,
    RULERSHIPS,
    SIGN_ELEMENTS,
    SIGNS,
    TRIPLICITIES,
)
from app.translations import get_translation

# Planetary years table (Minor, Middle, Major)
# Based on Ptolemy and traditional sources
PLANETARY_YEARS: dict[str, dict[str, float]] = {
    "Saturn": {"minor": 30, "middle": 43.5, "major": 57},
    "Jupiter": {"minor": 12, "middle": 45.5, "major": 79},
    "Mars": {"minor": 15, "middle": 40.5, "major": 66},
    "Sun": {"minor": 19, "middle": 69.5, "major": 120},
    "Venus": {"minor": 8, "middle": 45, "major": 82},
    "Mercury": {"minor": 20, "middle": 48, "major": 76},
    "Moon": {"minor": 25, "middle": 66.5, "major": 108},
}

# Dignity priority for Alcochoden selection
DIGNITY_PRIORITY: dict[str, int] = {
    "domicile": 5,
    "exaltation": 4,
    "triplicity": 3,
    "term": 2,
    "face": 1,
}

# House type modifiers
HOUSE_MODIFIERS: dict[str, int] = {
    "angular": 3,  # Houses 1, 4, 7, 10
    "succedent": 1,  # Houses 2, 5, 8, 11
    "cadent": -2,  # Houses 3, 6, 9, 12
}

# Angular houses
ANGULAR_HOUSES = {1, 4, 7, 10}
SUCCEDENT_HOUSES = {2, 5, 8, 11}
CADENT_HOUSES = {3, 6, 9, 12}

# Benefic and malefic planets for aspect modifications
BENEFIC_PLANETS = {"Jupiter", "Venus"}
MALEFIC_PLANETS = {"Saturn", "Mars"}

# Combustion orb (degrees from Sun)
COMBUST_ORB = 8.0

# Major aspects for Alcochoden aspecting Hyleg
ALCOCHODEN_ASPECTS = {
    "Conjunction": {"angle": 0, "orb": 8},
    "Sextile": {"angle": 60, "orb": 6},
    "Square": {"angle": 90, "orb": 7},
    "Trine": {"angle": 120, "orb": 8},
    "Opposition": {"angle": 180, "orb": 8},
}

# Classical planets only
CLASSICAL_PLANETS = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}


def get_dignities_at_position(
    longitude: float,
    sign: str,
    degree: float,
    sect: str,
) -> dict[str, str | None]:
    """
    Find which planets have dignity at a specific zodiacal position.

    Args:
        longitude: Ecliptic longitude (0-360)
        sign: Zodiac sign at the position
        degree: Degree within the sign (0-30)
        sect: Chart sect - "diurnal" or "nocturnal"

    Returns:
        Dictionary mapping dignity type to the planet that has it:
        {
            "domicile": "Venus" or None,
            "exaltation": "Moon" or None,
            "triplicity": "Moon" or None,
            "term": "Jupiter" or None,
            "face": "Saturn" or None,
        }
    """
    dignities: dict[str, str | None] = {
        "domicile": None,
        "exaltation": None,
        "triplicity": None,
        "term": None,
        "face": None,
    }

    # Domicile ruler
    dignities["domicile"] = RULERSHIPS.get(sign)

    # Exaltation ruler (check if any planet is exalted in this sign)
    for planet, exalt_data in EXALTATIONS.items():
        if exalt_data["sign"] == sign:
            dignities["exaltation"] = planet
            break

    # Triplicity ruler (based on element and sect)
    element = SIGN_ELEMENTS.get(sign)
    if element and element in TRIPLICITIES:
        trip_data = TRIPLICITIES[element]
        if sect == "diurnal":
            dignities["triplicity"] = trip_data["day_ruler"]
        else:
            dignities["triplicity"] = trip_data["night_ruler"]

    # Term ruler
    if sign in EGYPTIAN_TERMS:
        for start, end, planet in EGYPTIAN_TERMS[sign]:
            if start <= degree < end:
                dignities["term"] = planet
                break

    # Face ruler
    if sign in FACES:
        for start, end, planet in FACES[sign]:
            if start <= degree < end:
                dignities["face"] = planet
                break

    return dignities


def planet_aspects_position(
    planet_longitude: float,
    target_longitude: float,
    orb: float = 8.0,
) -> dict[str, Any] | None:
    """
    Check if a planet aspects a target position.

    Args:
        planet_longitude: Longitude of the planet
        target_longitude: Longitude of the target position
        orb: Maximum orb for aspects

    Returns:
        Aspect data if aspect found, None otherwise
    """
    angle_diff = abs(planet_longitude - target_longitude)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff

    for aspect_name, aspect_data in ALCOCHODEN_ASPECTS.items():
        aspect_angle = aspect_data["angle"]
        aspect_orb = min(orb, aspect_data["orb"])

        orb_diff = abs(angle_diff - aspect_angle)
        if orb_diff <= aspect_orb:
            return {
                "aspect": aspect_name,
                "angle": round(angle_diff, 2),
                "orb": round(orb_diff, 2),
            }

    return None


def find_alcochoden_candidates(
    hyleg_longitude: float,
    hyleg_sign: str,
    hyleg_name: str,
    planets: list[dict[str, Any]],
    sect: str,
) -> list[dict[str, Any]]:
    """
    Find planets that qualify as Alcochoden candidates.

    A planet qualifies if:
    1. It has essential dignity at the Hyleg's degree
    2. It aspects the Hyleg
    3. It is not the Hyleg itself (if Hyleg is a planet)

    Args:
        hyleg_longitude: Longitude of the Hyleg
        hyleg_sign: Sign of the Hyleg
        hyleg_name: Name of the Hyleg (to exclude if it's a planet)
        planets: List of all planets
        sect: Chart sect

    Returns:
        List of candidate dictionaries sorted by dignity strength
    """
    hyleg_degree = hyleg_longitude % 30

    # Get all dignities at Hyleg's position
    dignities_at_hyleg = get_dignities_at_position(hyleg_longitude, hyleg_sign, hyleg_degree, sect)

    candidates = []

    for planet in planets:
        planet_name = planet["name"]

        # Skip if not a classical planet
        if planet_name not in CLASSICAL_PLANETS:
            continue

        # Skip if this planet IS the Hyleg
        if planet_name == hyleg_name:
            continue

        # Check if planet has any dignity at Hyleg's degree
        planet_dignities = []
        total_points = 0

        for dignity_type, dignity_planet in dignities_at_hyleg.items():
            if dignity_planet == planet_name:
                points = DIGNITY_PRIORITY.get(dignity_type, 0)
                planet_dignities.append(
                    {
                        "type": dignity_type,
                        "points": points,
                    }
                )
                total_points += points

        if not planet_dignities:
            continue  # No dignity at Hyleg's degree

        # Check if planet aspects the Hyleg
        aspect_data = planet_aspects_position(planet["longitude"], hyleg_longitude)

        if not aspect_data:
            continue  # No aspect to Hyleg

        # This planet qualifies as a candidate
        candidates.append(
            {
                "planet": planet_name,
                "longitude": planet["longitude"],
                "sign": planet["sign"],
                "house": planet["house"],
                "dignity_at_hyleg": planet_dignities,
                "total_dignity_points": total_points,
                "highest_dignity": max(planet_dignities, key=lambda d: d["points"]),
                "aspect_to_hyleg": aspect_data,
                "is_retrograde": planet.get("retrograde", False),
            }
        )

    # Sort by total dignity points (highest first)
    candidates.sort(key=lambda c: c["total_dignity_points"], reverse=True)

    return candidates


def is_combust(
    planet_longitude: float,
    sun_longitude: float,
    planet_name: str,
) -> bool:
    """
    Check if a planet is combust (too close to the Sun).

    The Sun cannot be combust.
    Combustion weakens the planet significantly.

    Args:
        planet_longitude: Longitude of the planet
        sun_longitude: Longitude of the Sun
        planet_name: Name of the planet

    Returns:
        True if the planet is combust
    """
    if planet_name == "Sun":
        return False

    angle_diff = abs(planet_longitude - sun_longitude)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff

    return angle_diff <= COMBUST_ORB


def is_in_detriment(planet_name: str, sign: str) -> bool:
    """Check if planet is in detriment (opposite sign of rulership)."""
    sign_index = SIGNS.index(sign)
    opposite_sign = SIGNS[(sign_index + 6) % 12]
    return RULERSHIPS.get(opposite_sign) == planet_name


def is_in_fall(planet_name: str, sign: str) -> bool:
    """Check if planet is in fall (opposite sign of exaltation)."""
    if planet_name not in EXALTATIONS:
        return False

    exalt_sign = EXALTATIONS[planet_name]["sign"]
    exalt_sign_index = SIGNS.index(exalt_sign)
    fall_sign = SIGNS[(exalt_sign_index + 6) % 12]

    return sign == fall_sign


def is_in_domicile(planet_name: str, sign: str) -> bool:
    """Check if planet is in its domicile (rulership)."""
    return RULERSHIPS.get(sign) == planet_name


def is_in_exaltation(planet_name: str, sign: str) -> bool:
    """Check if planet is in its exaltation."""
    if planet_name not in EXALTATIONS:
        return False
    return EXALTATIONS[planet_name]["sign"] == sign


def determine_year_type(
    planet: dict[str, Any],
    sun_longitude: float,
) -> str:
    """
    Determine which year type (minor/middle/major) to use.

    Rules:
    - Minor years: Planet is debilitated (detriment/fall) or combust
    - Major years: Planet is essentially dignified (domicile/exaltation)
    - Middle years: Otherwise (peregrine or moderately dignified)

    Args:
        planet: Planet data dictionary
        sun_longitude: Sun's longitude for combustion check

    Returns:
        "minor", "middle", or "major"
    """
    planet_name = planet["name"]
    planet_sign = planet["sign"]
    planet_longitude = planet["longitude"]

    # Check combustion first (always gives minor years)
    if is_combust(planet_longitude, sun_longitude, planet_name):
        return "minor"

    # Check debilitation (detriment or fall)
    if is_in_detriment(planet_name, planet_sign):
        return "minor"
    if is_in_fall(planet_name, planet_sign):
        return "minor"

    # Check strong dignification (domicile or exaltation)
    if is_in_domicile(planet_name, planet_sign):
        return "major"
    if is_in_exaltation(planet_name, planet_sign):
        return "major"

    # Default to middle years
    return "middle"


def get_house_type(house: int) -> str:
    """Get house type (angular, succedent, cadent)."""
    if house in ANGULAR_HOUSES:
        return "angular"
    elif house in SUCCEDENT_HOUSES:
        return "succedent"
    else:
        return "cadent"


def calculate_house_modification(house: int) -> tuple[int, str]:
    """
    Calculate year modification based on house position.

    Returns:
        Tuple of (modification_value, reason)
    """
    house_type = get_house_type(house)
    modification = HOUSE_MODIFIERS[house_type]
    return modification, house_type


def calculate_aspect_modifications(
    planet: dict[str, Any],
    aspects: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Calculate year modifications based on aspects to the Alcochoden.

    - Benefic aspects (from Jupiter/Venus) add +5 years
    - Malefic aspects (from Saturn/Mars) subtract -5 years

    Only considers major aspects (conjunction, trine, sextile for benefics;
    conjunction, square, opposition for malefics).

    Args:
        planet: The Alcochoden planet
        aspects: List of all aspects

    Returns:
        List of modification dictionaries
    """
    planet_name = planet["name"]
    modifications = []

    for aspect in aspects:
        # Check if aspect involves the Alcochoden
        if aspect["planet1"] != planet_name and aspect["planet2"] != planet_name:
            continue

        # Get the other planet
        other_planet = aspect["planet2"] if aspect["planet1"] == planet_name else aspect["planet1"]
        aspect_type = aspect["aspect"]

        # Benefic aspects (Jupiter/Venus trine, sextile, conjunction)
        if other_planet in BENEFIC_PLANETS:
            if aspect_type in ["Trine", "Sextile", "Conjunction"]:
                modifications.append(
                    {
                        "reason": f"{other_planet} {aspect_type.lower()}",
                        "adjustment": 5,
                        "type": "benefic_aspect",
                    }
                )

        # Malefic aspects (Saturn/Mars conjunction, square, opposition)
        if other_planet in MALEFIC_PLANETS:
            if aspect_type in ["Conjunction", "Square", "Opposition"]:
                modifications.append(
                    {
                        "reason": f"{other_planet} {aspect_type.lower()}",
                        "adjustment": -5,
                        "type": "malefic_aspect",
                    }
                )

    return modifications


def calculate_alcochoden(
    hyleg_data: dict[str, Any] | None,
    planets: list[dict[str, Any]],
    houses: list[dict[str, Any]],
    aspects: list[dict[str, Any]],
    sun_longitude: float,
    sect: str,
    language: str = "en-US",
) -> dict[str, Any] | None:
    """
    Calculate the Alcochoden (Giver of Years) based on the Hyleg.

    Args:
        hyleg_data: Hyleg calculation result (None if no Hyleg found)
        planets: List of planet data
        houses: List of house cusp data
        aspects: List of aspect data
        sun_longitude: Sun's longitude for combustion check
        sect: Chart sect
        language: Language for translations

    Returns:
        Alcochoden data dictionary or None if no Alcochoden found
    """
    if hyleg_data is None or hyleg_data.get("hyleg") is None:
        return {
            "alcochoden": None,
            "alcochoden_longitude": None,
            "alcochoden_sign": None,
            "alcochoden_house": None,
            "dignity_at_hyleg": None,
            "aspect_to_hyleg": None,
            "alcochoden_condition": None,
            "years": None,
            "year_type_selected": None,
            "base_years": None,
            "modifications": [],
            "final_years": None,
            "candidates_evaluated": [],
            "no_alcochoden_reason": get_translation("alcochoden.no_hyleg", language),
        }

    hyleg_longitude = hyleg_data["hyleg_longitude"]
    hyleg_sign = hyleg_data["hyleg_sign"]
    hyleg_name = hyleg_data["hyleg"]

    # Find Alcochoden candidates
    candidates = find_alcochoden_candidates(hyleg_longitude, hyleg_sign, hyleg_name, planets, sect)

    # Build candidates evaluated list
    candidates_evaluated = []
    for candidate in candidates:
        candidates_evaluated.append(
            {
                "planet": candidate["planet"],
                "dignity_type": candidate["highest_dignity"]["type"],
                "dignity_points": candidate["total_dignity_points"],
                "aspects_hyleg": True,
                "aspect_type": candidate["aspect_to_hyleg"]["aspect"],
                "selected": False,
            }
        )

    if not candidates:
        return {
            "alcochoden": None,
            "alcochoden_longitude": None,
            "alcochoden_sign": None,
            "alcochoden_house": None,
            "dignity_at_hyleg": None,
            "aspect_to_hyleg": None,
            "alcochoden_condition": None,
            "years": None,
            "year_type_selected": None,
            "base_years": None,
            "modifications": [],
            "final_years": None,
            "candidates_evaluated": candidates_evaluated,
            "no_alcochoden_reason": get_translation("alcochoden.no_candidates", language),
        }

    # Select the best candidate (highest dignity points)
    alcochoden_candidate = candidates[0]
    alcochoden_planet = alcochoden_candidate["planet"]

    # Mark selected in candidates list
    if candidates_evaluated:
        candidates_evaluated[0]["selected"] = True

    # Get planet data
    planet_data = next(p for p in planets if p["name"] == alcochoden_planet)

    # Determine year type
    year_type = determine_year_type(planet_data, sun_longitude)

    # Get planetary years
    years = PLANETARY_YEARS.get(alcochoden_planet, {"minor": 0, "middle": 0, "major": 0})
    base_years = years[year_type]

    # Calculate modifications
    modifications = []

    # House position modification
    house = planet_data["house"]
    house_mod, house_type = calculate_house_modification(house)
    modifications.append(
        {
            "reason": get_translation(f"alcochoden.house_type.{house_type}", language),
            "adjustment": house_mod,
            "type": "house_position",
        }
    )

    # Aspect modifications
    aspect_mods = calculate_aspect_modifications(planet_data, aspects)
    modifications.extend(aspect_mods)

    # Calculate final years
    total_modification = sum(m["adjustment"] for m in modifications)
    final_years = base_years + total_modification

    # Build condition data
    alcochoden_condition = {
        "essential_dignity": None,
        "accidental_dignity": house_type,
        "is_retrograde": planet_data.get("retrograde", False),
        "is_combust": is_combust(planet_data["longitude"], sun_longitude, alcochoden_planet),
        "is_debilitated": is_in_detriment(alcochoden_planet, planet_data["sign"])
        or is_in_fall(alcochoden_planet, planet_data["sign"]),
        "benefic_aspects": [
            m["reason"] for m in modifications if m.get("type") == "benefic_aspect"
        ],
        "malefic_aspects": [
            m["reason"] for m in modifications if m.get("type") == "malefic_aspect"
        ],
    }

    # Determine essential dignity classification
    if is_in_domicile(alcochoden_planet, planet_data["sign"]):
        alcochoden_condition["essential_dignity"] = "domicile"
    elif is_in_exaltation(alcochoden_planet, planet_data["sign"]):
        alcochoden_condition["essential_dignity"] = "exaltation"
    elif is_in_detriment(alcochoden_planet, planet_data["sign"]):
        alcochoden_condition["essential_dignity"] = "detriment"
    elif is_in_fall(alcochoden_planet, planet_data["sign"]):
        alcochoden_condition["essential_dignity"] = "fall"
    else:
        alcochoden_condition["essential_dignity"] = "peregrine"

    return {
        "alcochoden": alcochoden_planet,
        "alcochoden_longitude": round(planet_data["longitude"], 4),
        "alcochoden_sign": planet_data["sign"],
        "alcochoden_house": planet_data["house"],
        "hyleg_degree": round(hyleg_longitude % 30, 4),
        "hyleg_sign": hyleg_sign,
        "dignity_at_hyleg": {
            "type": alcochoden_candidate["highest_dignity"]["type"],
            "points": alcochoden_candidate["total_dignity_points"],
        },
        "aspect_to_hyleg": {
            "type": alcochoden_candidate["aspect_to_hyleg"]["aspect"],
            "orb": alcochoden_candidate["aspect_to_hyleg"]["orb"],
            "applying": None,  # Would need planet speeds to calculate
        },
        "alcochoden_condition": alcochoden_condition,
        "years": {
            "minor": years["minor"],
            "middle": years["middle"],
            "major": years["major"],
        },
        "year_type_selected": year_type,
        "base_years": base_years,
        "modifications": modifications,
        "final_years": round(final_years, 1),
        "candidates_evaluated": candidates_evaluated,
        "no_alcochoden_reason": None,
    }
