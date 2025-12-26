"""
Mentality calculation based on traditional astrology.

This module calculates intellectual characteristics (different from Temperament):
- **Temperament**: Physical/emotional constitution
- **Mentality**: Intellectual capacity, thinking style, communication

Key Metrics:
- Strength (0-100): Overall mental power
- Speed (-15 to +20): How fast one thinks
- Depth (0-25): How deeply one analyzes
- Versatility (0-20): Adaptability of thought

Primary Factors:
- Mercury: Sign, house, aspects, dignities, retrograde status
- Moon: Supporting mental functions
- Houses 3 and 9: Concrete vs. abstract thinking
- Aspects: Mercury contacts with other planets

Mentality Types:
1. Agile & Superficial: High speed, low depth
2. Agile & Deep: High speed, high depth (rare)
3. Slow & Deep: Low speed, high depth
4. Slow & Superficial: Low speed, low depth
5. Versatile: High versatility
6. Specialized: Low versatility, focused
7. Abstract: Strong House 9, Mercury in Air
8. Concrete: Strong House 3, Mercury in Earth
"""

from typing import Any

from app.translations import DEFAULT_LANGUAGE, get_translation

# Dignity weight scale (same as temperament.py)
DIGNITY_WEIGHTS = {
    "domicile": 2.0,
    "ruler": 2.0,
    "exalted": 1.75,
    "triplicity": 1.5,
    "triplicity_day": 1.5,
    "triplicity_night": 1.5,
    "triplicity_participant": 1.5,
    "term": 1.25,
    "face": 1.1,
    "peregrine": 1.0,
    "detriment": 0.75,
    "fall": 0.5,
}

# Sign element mappings for mental characteristics
SIGN_ELEMENTS = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

# Sign modality mappings
SIGN_MODALITIES = {
    "Aries": "cardinal",
    "Cancer": "cardinal",
    "Libra": "cardinal",
    "Capricorn": "cardinal",
    "Taurus": "fixed",
    "Leo": "fixed",
    "Scorpio": "fixed",
    "Aquarius": "fixed",
    "Gemini": "mutable",
    "Virgo": "mutable",
    "Sagittarius": "mutable",
    "Pisces": "mutable",
}

# Mercury sign modifiers for Speed
MERCURY_SPEED_BY_ELEMENT = {
    "air": 10,  # Air signs: fast thinking
    "fire": 8,  # Fire signs: quick but impulsive
    "earth": 0,  # Earth signs: methodical
    "water": -5,  # Water signs: intuitive but slower
}

# Mercury sign modifiers for Depth
MERCURY_DEPTH_BY_ELEMENT = {
    "water": 10,  # Water signs: deep and intuitive
    "earth": 8,  # Earth signs: thorough and practical
    "air": 2,  # Air signs: broad but less deep
    "fire": 0,  # Fire signs: quick but surface-level
}

# Cadent houses (associated with mental activity)
CADENT_HOUSES = [3, 6, 9, 12]

# Mental houses
HOUSE_3 = 3  # Concrete thinking, communication, learning
HOUSE_9 = 9  # Abstract thinking, philosophy, higher learning

# Aspect types and their mental effects
ASPECT_EFFECTS = {
    # Speed boosters
    "mars_speed": 5,  # Mars aspects speed up thinking
    "uranus_speed": 5,  # Uranus adds originality and speed
    # Depth boosters
    "saturn_depth": 5,  # Saturn adds structure and depth
    "pluto_depth": 5,  # Pluto adds intensity and depth
    # Negative effects
    "neptune_confusion": -3,  # Neptune can cloud thinking
}

# Mentality types
MENTALITY_TYPES = [
    "agile_and_superficial",
    "agile_and_deep",
    "slow_and_deep",
    "slow_and_superficial",
    "versatile",
    "specialized",
    "abstract",
    "concrete",
]

# Icons for mentality types
MENTALITY_ICONS = {
    "agile_and_superficial": "\u26a1",  # Lightning bolt
    "agile_and_deep": "\U0001f9e0",  # Brain
    "slow_and_deep": "\U0001f50d",  # Magnifying glass
    "slow_and_superficial": "\U0001f422",  # Turtle
    "versatile": "\U0001f300",  # Cyclone (adaptability)
    "specialized": "\U0001f3af",  # Bullseye (focus)
    "abstract": "\u2601\ufe0f",  # Cloud (ethereal)
    "concrete": "\U0001f9f1",  # Brick (practical)
}


def calculate_dignity_weight(dignities: list[str] | None) -> tuple[float, str]:
    """
    Calculate the weight multiplier based on essential dignities.

    Uses the strongest dignity present to determine weight.

    Args:
        dignities: List of dignity names from calculate_essential_dignities()

    Returns:
        Tuple of (weight, dominant_dignity_name)
    """
    if not dignities:
        return (1.0, "peregrine")

    # Priority order: check strongest dignities first
    if "ruler" in dignities:
        return (DIGNITY_WEIGHTS["ruler"], "domicile")
    if "exalted" in dignities:
        return (DIGNITY_WEIGHTS["exalted"], "exaltation")

    for trip in ["triplicity_day", "triplicity_night", "triplicity_participant"]:
        if trip in dignities:
            return (DIGNITY_WEIGHTS[trip], "triplicity")

    if "term" in dignities:
        return (DIGNITY_WEIGHTS["term"], "term")
    if "face" in dignities:
        return (DIGNITY_WEIGHTS["face"], "face")

    # Debilities
    if "detriment" in dignities:
        return (DIGNITY_WEIGHTS["detriment"], "detriment")
    if "fall" in dignities:
        return (DIGNITY_WEIGHTS["fall"], "fall")

    return (1.0, "peregrine")


def get_planet_data(planets: list[dict], planet_name: str) -> dict | None:
    """Find a planet in the planets list by name."""
    for planet in planets:
        if planet.get("name") == planet_name:
            return planet
    return None


def get_planets_in_house(planets: list[dict], house_number: int) -> list[dict]:
    """Get all planets in a specific house."""
    return [p for p in planets if p.get("house") == house_number]


def get_planets_in_houses(planets: list[dict], house_numbers: list[int]) -> list[dict]:
    """Get all planets in specified houses."""
    return [p for p in planets if p.get("house") in house_numbers]


def get_mercury_aspects(aspects: list[dict], target_planets: list[str] | None = None) -> list[dict]:
    """
    Get all aspects involving Mercury.

    Args:
        aspects: List of aspect dictionaries
        target_planets: Optional filter for specific planets

    Returns:
        List of aspects involving Mercury
    """
    mercury_aspects = []
    for aspect in aspects:
        planet1 = aspect.get("planet1", "")
        planet2 = aspect.get("planet2", "")

        if planet1 == "Mercury" or planet2 == "Mercury":
            if target_planets:
                other = planet2 if planet1 == "Mercury" else planet1
                if other in target_planets:
                    mercury_aspects.append(aspect)
            else:
                mercury_aspects.append(aspect)

    return mercury_aspects


def is_benefic_aspect(aspect: dict) -> bool:
    """Check if an aspect is traditionally benefic (trine, sextile)."""
    aspect_type = aspect.get("aspect", "").lower()
    return aspect_type in ["trine", "sextile"]


def is_malefic_aspect(aspect: dict) -> bool:
    """Check if an aspect is traditionally malefic (square, opposition)."""
    aspect_type = aspect.get("aspect", "").lower()
    return aspect_type in ["square", "opposition"]


def is_conjunction(aspect: dict) -> bool:
    """Check if an aspect is a conjunction."""
    aspect_type = aspect.get("aspect", "").lower()
    return aspect_type == "conjunction"


def calculate_mental_strength(
    mercury_dignities: list[str] | None,
    mercury_aspects: list[dict],
    moon_dignities: list[str] | None,
    planets_in_3_9: list[dict],
    factors: list[dict],
    language: str,
) -> float:
    """
    Calculate overall mental strength (0-100).

    Components:
    - Mercury essential dignity (0-30)
    - Mercury accidental dignity/aspects (0-20)
    - Benefic aspects to Mercury (0-20)
    - Moon strength (0-15)
    - Benefics in houses 3/9 (0-15)
    - Malefic aspects reduce score (0-20)

    Args:
        mercury_dignities: Mercury's essential dignities
        mercury_aspects: All aspects involving Mercury
        moon_dignities: Moon's essential dignities
        planets_in_3_9: Planets in houses 3 and 9
        factors: List to append contributing factors
        language: Language for translations

    Returns:
        Mental strength score (0-100)
    """
    strength = 0.0

    # Mercury essential dignity (0-30)
    merc_weight, merc_dignity = calculate_dignity_weight(mercury_dignities)
    dignity_score = (merc_weight - 0.5) * 20  # Maps 0.5-2.0 to 0-30
    strength += dignity_score

    if dignity_score > 0:
        factors.append(
            {
                "factor_key": "mercury_dignity",
                "factor": get_translation("mentality.factors.mercury_dignity", language),
                "value": get_translation(f"dignities.{merc_dignity}", language),
                "contribution": f"+{dignity_score:.0f} {get_translation('mentality.strength', language)}",
            }
        )

    # Benefic aspects to Mercury (0-20)
    benefic_count = sum(1 for a in mercury_aspects if is_benefic_aspect(a))
    benefic_score = min(benefic_count * 5, 20)
    strength += benefic_score

    if benefic_score > 0:
        factors.append(
            {
                "factor_key": "benefic_aspects",
                "factor": get_translation("mentality.factors.benefic_aspects", language),
                "value": str(benefic_count),
                "contribution": f"+{benefic_score:.0f} {get_translation('mentality.strength', language)}",
            }
        )

    # Malefic aspects to Mercury (reduce score, 0-20)
    malefic_count = sum(1 for a in mercury_aspects if is_malefic_aspect(a))
    malefic_penalty = min(malefic_count * 5, 20)
    strength -= malefic_penalty

    if malefic_penalty > 0:
        factors.append(
            {
                "factor_key": "malefic_aspects",
                "factor": get_translation("mentality.factors.malefic_aspects", language),
                "value": str(malefic_count),
                "contribution": f"-{malefic_penalty:.0f} {get_translation('mentality.strength', language)}",
            }
        )

    # Moon strength (0-15)
    moon_weight, moon_dignity = calculate_dignity_weight(moon_dignities)
    moon_score = (moon_weight - 0.5) * 10  # Maps 0.5-2.0 to 0-15
    strength += moon_score

    if moon_score > 0:
        factors.append(
            {
                "factor_key": "moon_strength",
                "factor": get_translation("mentality.factors.moon_strength", language),
                "value": get_translation(f"dignities.{moon_dignity}", language),
                "contribution": f"+{moon_score:.0f} {get_translation('mentality.strength', language)}",
            }
        )

    # Benefics in houses 3/9 (0-15)
    benefics = ["Venus", "Jupiter"]
    benefics_in_mental_houses = [p for p in planets_in_3_9 if p.get("name") in benefics]
    mental_house_score = len(benefics_in_mental_houses) * 7.5
    mental_house_score = min(mental_house_score, 15)
    strength += mental_house_score

    if mental_house_score > 0:
        planet_names = [p.get("name", "") for p in benefics_in_mental_houses]
        factors.append(
            {
                "factor_key": "benefics_in_mental_houses",
                "factor": get_translation("mentality.factors.benefics_in_mental_houses", language),
                "value": ", ".join(planet_names),
                "contribution": f"+{mental_house_score:.0f} {get_translation('mentality.strength', language)}",
            }
        )

    # Base score adjustment (start from 50)
    strength += 50

    # Clamp to 0-100
    return max(0, min(100, strength))


def calculate_mental_speed(
    mercury_sign: str,
    mercury_aspects: list[dict],
    mercury_retrograde: bool,
    factors: list[dict],
    language: str,
) -> float:
    """
    Calculate mental speed (-15 to +20).

    Components:
    - Mercury sign element (+10 Air/Fire, 0 Earth, -5 Water)
    - Mercury-Mars/Uranus aspects (+5 each)
    - Mercury retrograde (-10)
    - Mercury direct (+5)

    Args:
        mercury_sign: Sign where Mercury is located
        mercury_aspects: Aspects involving Mercury
        mercury_retrograde: Whether Mercury is retrograde
        factors: List to append contributing factors
        language: Language for translations

    Returns:
        Mental speed score (-15 to +20)
    """
    speed = 0.0

    # Mercury sign element
    element = SIGN_ELEMENTS.get(mercury_sign, "earth")
    element_modifier = MERCURY_SPEED_BY_ELEMENT.get(element, 0)
    speed += element_modifier

    if element_modifier != 0:
        sign_name = get_translation(f"signs.{mercury_sign}", language)
        factors.append(
            {
                "factor_key": "mercury_sign_speed",
                "factor": get_translation("mentality.factors.mercury_sign_speed", language),
                "value": sign_name,
                "contribution": f"{element_modifier:+.0f} {get_translation('mentality.speed', language)}",
            }
        )

    # Mercury-Mars/Uranus aspects (speed boosters)
    speed_planets = ["Mars", "Uranus"]
    speed_aspects = get_mercury_aspects(mercury_aspects, speed_planets)

    for aspect in speed_aspects:
        other_planet: str = (
            aspect.get("planet2", "")
            if aspect.get("planet1") == "Mercury"
            else aspect.get("planet1", "")
        )
        if not other_planet:
            continue
        # Conjunction and hard aspects also boost speed (Mars/Uranus are activating)
        if is_benefic_aspect(aspect) or is_conjunction(aspect) or is_malefic_aspect(aspect):
            speed += 5
            planet_name = get_translation(f"planets.{other_planet}", language)
            aspect_name = get_translation(
                f"aspects.{aspect.get('aspect', 'conjunction')}", language
            )
            factors.append(
                {
                    "factor_key": f"mercury_{other_planet.lower()}_aspect",
                    "factor": f"Mercury-{planet_name} {aspect_name}",
                    "value": f"{aspect.get('orb', 0):.1f}\u00b0",
                    "contribution": f"+5 {get_translation('mentality.speed', language)}",
                }
            )

    # Retrograde status
    if mercury_retrograde:
        speed -= 10
        factors.append(
            {
                "factor_key": "mercury_retrograde",
                "factor": get_translation("mentality.factors.mercury_retrograde", language),
                "value": get_translation("common.yes", language),
                "contribution": f"-10 {get_translation('mentality.speed', language)}",
            }
        )
    else:
        speed += 5
        factors.append(
            {
                "factor_key": "mercury_direct",
                "factor": get_translation("mentality.factors.mercury_direct", language),
                "value": get_translation("common.yes", language),
                "contribution": f"+5 {get_translation('mentality.speed', language)}",
            }
        )

    # Clamp to -15 to +20
    return max(-15, min(20, speed))


def calculate_mental_depth(
    mercury_sign: str,
    mercury_house: int,
    mercury_aspects: list[dict],
    mercury_dignities: list[str] | None,
    factors: list[dict],
    language: str,
) -> float:
    """
    Calculate mental depth (0-25).

    Components:
    - Mercury sign element (+10 Water/Earth)
    - Mercury-Saturn/Pluto aspects (+5 each)
    - Mercury in House 8/12 (+5)
    - Essential dignity present (+5-10)

    Args:
        mercury_sign: Sign where Mercury is located
        mercury_house: House where Mercury is located
        mercury_aspects: Aspects involving Mercury
        mercury_dignities: Mercury's essential dignities
        factors: List to append contributing factors
        language: Language for translations

    Returns:
        Mental depth score (0-25)
    """
    depth = 0.0

    # Mercury sign element (Water/Earth = deep)
    element = SIGN_ELEMENTS.get(mercury_sign, "earth")
    element_modifier = MERCURY_DEPTH_BY_ELEMENT.get(element, 0)
    depth += element_modifier

    if element_modifier > 0:
        sign_name = get_translation(f"signs.{mercury_sign}", language)
        factors.append(
            {
                "factor_key": "mercury_sign_depth",
                "factor": get_translation("mentality.factors.mercury_sign_depth", language),
                "value": sign_name,
                "contribution": f"+{element_modifier:.0f} {get_translation('mentality.depth', language)}",
            }
        )

    # Mercury-Saturn/Pluto aspects (depth boosters)
    depth_planets = ["Saturn", "Pluto"]
    depth_aspects = get_mercury_aspects(mercury_aspects, depth_planets)

    for aspect in depth_aspects:
        other_planet: str = (
            aspect.get("planet2", "")
            if aspect.get("planet1") == "Mercury"
            else aspect.get("planet1", "")
        )
        if not other_planet:
            continue
        # Any aspect to Saturn/Pluto adds depth (even hard aspects)
        depth += 5
        planet_name = get_translation(f"planets.{other_planet}", language)
        aspect_name = get_translation(f"aspects.{aspect.get('aspect', 'conjunction')}", language)
        factors.append(
            {
                "factor_key": f"mercury_{other_planet.lower()}_depth",
                "factor": f"Mercury-{planet_name} {aspect_name}",
                "value": f"{aspect.get('orb', 0):.1f}\u00b0",
                "contribution": f"+5 {get_translation('mentality.depth', language)}",
            }
        )

    # Mercury in House 8/12 (depth houses)
    depth_houses = [8, 12]
    if mercury_house in depth_houses:
        depth += 5
        factors.append(
            {
                "factor_key": "mercury_depth_house",
                "factor": get_translation("mentality.factors.mercury_depth_house", language),
                "value": str(mercury_house),
                "contribution": f"+5 {get_translation('mentality.depth', language)}",
            }
        )

    # Essential dignity bonus
    merc_weight, merc_dignity = calculate_dignity_weight(mercury_dignities)
    if merc_weight >= 1.5:  # Triplicity or better
        dignity_bonus = 5 if merc_weight >= 1.75 else 3
        depth += dignity_bonus
        factors.append(
            {
                "factor_key": "mercury_dignity_depth",
                "factor": get_translation("mentality.factors.mercury_dignity_depth", language),
                "value": get_translation(f"dignities.{merc_dignity}", language),
                "contribution": f"+{dignity_bonus:.0f} {get_translation('mentality.depth', language)}",
            }
        )

    # Clamp to 0-25
    return max(0, min(25, depth))


def calculate_mental_versatility(
    mercury_sign: str,
    mercury_aspects: list[dict],
    planets_in_cadent: list[dict],
    factors: list[dict],
    language: str,
) -> float:
    """
    Calculate mental versatility (0-20).

    Components:
    - Mercury in mutable sign (+10)
    - 3+ aspects to Mercury (+5)
    - Planets in cadent houses (+5 if 3+)

    Args:
        mercury_sign: Sign where Mercury is located
        mercury_aspects: Aspects involving Mercury
        planets_in_cadent: Planets in cadent houses (3, 6, 9, 12)
        factors: List to append contributing factors
        language: Language for translations

    Returns:
        Mental versatility score (0-20)
    """
    versatility = 0.0

    # Mercury in mutable sign
    modality = SIGN_MODALITIES.get(mercury_sign, "fixed")
    if modality == "mutable":
        versatility += 10
        sign_name = get_translation(f"signs.{mercury_sign}", language)
        factors.append(
            {
                "factor_key": "mercury_mutable",
                "factor": get_translation("mentality.factors.mercury_mutable", language),
                "value": sign_name,
                "contribution": f"+10 {get_translation('mentality.versatility', language)}",
            }
        )

    # Multiple aspects to Mercury (3+)
    aspect_count = len(mercury_aspects)
    if aspect_count >= 3:
        versatility += 5
        factors.append(
            {
                "factor_key": "mercury_many_aspects",
                "factor": get_translation("mentality.factors.mercury_many_aspects", language),
                "value": str(aspect_count),
                "contribution": f"+5 {get_translation('mentality.versatility', language)}",
            }
        )

    # Planets in cadent houses (3+ planets)
    if len(planets_in_cadent) >= 3:
        versatility += 5
        factors.append(
            {
                "factor_key": "cadent_emphasis",
                "factor": get_translation("mentality.factors.cadent_emphasis", language),
                "value": str(len(planets_in_cadent)),
                "contribution": f"+5 {get_translation('mentality.versatility', language)}",
            }
        )

    # Clamp to 0-20
    return max(0, min(20, versatility))


def calculate_house_strength(
    planets: list[dict], house_number: int, house_ruler_dignities: list[str] | None
) -> float:
    """
    Calculate the strength of a house (0-100).

    Based on:
    - Number of planets in the house
    - Benefics vs. malefics
    - House ruler dignity

    Args:
        planets: All planets in the chart
        house_number: House number to evaluate
        house_ruler_dignities: Dignities of the house ruler

    Returns:
        House strength score (0-100)
    """
    strength = 50.0  # Base

    planets_in_house = get_planets_in_house(planets, house_number)

    # Each planet adds strength
    strength += len(planets_in_house) * 10

    # Benefics add more, malefics less
    benefics = ["Venus", "Jupiter"]
    malefics = ["Mars", "Saturn"]
    for planet in planets_in_house:
        name = planet.get("name", "")
        if name in benefics:
            strength += 10
        elif name in malefics:
            strength -= 5

    # House ruler dignity
    ruler_weight, _ = calculate_dignity_weight(house_ruler_dignities)
    strength += (ruler_weight - 1.0) * 15

    return max(0, min(100, strength))


def determine_mentality_type(
    speed: float,
    depth: float,
    versatility: float,
    mercury_sign: str,
    house_3_strength: float,
    house_9_strength: float,
) -> str:
    """
    Determine the mentality type based on scores.

    Types:
    1. agile_and_superficial: High speed (>5), low depth (<10)
    2. agile_and_deep: High speed (>5), high depth (>15) - rare
    3. slow_and_deep: Low speed (<0), high depth (>15)
    4. slow_and_superficial: Low speed (<0), low depth (<10)
    5. versatile: High versatility (>12)
    6. specialized: Low versatility (<5), moderate/high depth
    7. abstract: Strong House 9 (>70), Mercury in Air sign
    8. concrete: Strong House 3 (>70), Mercury in Earth sign

    Args:
        speed: Mental speed score (-15 to +20)
        depth: Mental depth score (0-25)
        versatility: Mental versatility score (0-20)
        mercury_sign: Sign where Mercury is located
        house_3_strength: Strength of House 3
        house_9_strength: Strength of House 9

    Returns:
        Mentality type key
    """
    element = SIGN_ELEMENTS.get(mercury_sign, "earth")

    # Check for abstract/concrete types first (based on house emphasis)
    if house_9_strength > 70 and element == "air":
        return "abstract"
    if house_3_strength > 70 and element == "earth":
        return "concrete"

    # Check versatility extremes
    if versatility > 12:
        return "versatile"
    if versatility < 5 and depth > 12:
        return "specialized"

    # Speed/depth combinations
    is_fast = speed > 5
    is_slow = speed < 0
    is_deep = depth > 15
    is_shallow = depth < 10

    if is_fast and is_deep:
        return "agile_and_deep"
    if is_fast and is_shallow:
        return "agile_and_superficial"
    if is_slow and is_deep:
        return "slow_and_deep"
    if is_slow and is_shallow:
        return "slow_and_superficial"

    # Default based on dominant characteristic
    if is_fast:
        return "agile_and_superficial"
    if is_deep:
        return "slow_and_deep"

    # Neutral case
    return "versatile"


def calculate_mentality(
    planets: list[dict],
    houses: list[dict],
    aspects: list[dict],
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Calculate mentality analysis based on traditional astrology.

    Main entry point for mentality calculation.

    Args:
        planets: List of planet dictionaries with positions and dignities
        houses: List of house dictionaries with cusps
        aspects: List of aspect dictionaries
        language: Language for translations ('en-US' or 'pt-BR')

    Returns:
        Dictionary with mentality data:
        {
            "type_key": "agile_and_deep",
            "type": "Agile & Deep",
            "icon": "...",
            "scores": {
                "strength": 75,
                "speed": 15,
                "depth": 20,
                "versatility": 12
            },
            "mercury_analysis": {
                "sign": "Gemini",
                "house": 3,
                "retrograde": false,
                "dignities": ["domicile"]
            },
            "factors": [...],
            "description": "..."
        }
    """
    factors: list[dict] = []

    # Get Mercury data
    mercury = get_planet_data(planets, "Mercury")
    if not mercury:
        # Return default if Mercury not found
        return {
            "type_key": "unknown",
            "type": get_translation("mentality.types.unknown.name", language),
            "icon": "\u2753",
            "scores": {"strength": 0, "speed": 0, "depth": 0, "versatility": 0},
            "mercury_analysis": None,
            "factors": [],
            "description": get_translation("mentality.types.unknown.description", language),
        }

    mercury_sign = mercury.get("sign", "Aries")
    mercury_house = mercury.get("house", 1)
    mercury_retrograde = mercury.get("retrograde", False)
    mercury_dignities = mercury.get("dignities", [])

    # Get Moon data
    moon = get_planet_data(planets, "Moon")
    moon_dignities = moon.get("dignities", []) if moon else []

    # Get aspects involving Mercury
    mercury_aspects = get_mercury_aspects(aspects)

    # Get planets in mental houses (3 and 9)
    planets_in_3_9 = get_planets_in_houses(planets, [HOUSE_3, HOUSE_9])

    # Get planets in cadent houses
    planets_in_cadent = get_planets_in_houses(planets, CADENT_HOUSES)

    # Calculate scores
    strength = calculate_mental_strength(
        mercury_dignities=mercury_dignities,
        mercury_aspects=mercury_aspects,
        moon_dignities=moon_dignities,
        planets_in_3_9=planets_in_3_9,
        factors=factors,
        language=language,
    )

    speed = calculate_mental_speed(
        mercury_sign=mercury_sign,
        mercury_aspects=mercury_aspects,
        mercury_retrograde=mercury_retrograde,
        factors=factors,
        language=language,
    )

    depth = calculate_mental_depth(
        mercury_sign=mercury_sign,
        mercury_house=mercury_house,
        mercury_aspects=mercury_aspects,
        mercury_dignities=mercury_dignities,
        factors=factors,
        language=language,
    )

    versatility = calculate_mental_versatility(
        mercury_sign=mercury_sign,
        mercury_aspects=mercury_aspects,
        planets_in_cadent=planets_in_cadent,
        factors=factors,
        language=language,
    )

    # Calculate house strengths for type determination
    # Note: House ruler dignities would require additional lookup
    # For now, use simplified calculation based on planet occupation
    house_3_strength = calculate_house_strength(planets, HOUSE_3, None)
    house_9_strength = calculate_house_strength(planets, HOUSE_9, None)

    # Determine mentality type
    type_key = determine_mentality_type(
        speed=speed,
        depth=depth,
        versatility=versatility,
        mercury_sign=mercury_sign,
        house_3_strength=house_3_strength,
        house_9_strength=house_9_strength,
    )

    # Get localized type name and description
    type_name = get_translation(f"mentality.types.{type_key}.name", language)
    description = get_translation(f"mentality.types.{type_key}.description", language)
    icon = MENTALITY_ICONS.get(type_key, "\U0001f9e0")

    # Build Mercury analysis
    mercury_analysis = {
        "sign": mercury_sign,
        "sign_localized": get_translation(f"signs.{mercury_sign}", language),
        "house": mercury_house,
        "retrograde": mercury_retrograde,
        "dignities": mercury_dignities,
    }

    return {
        "type_key": type_key,
        "type": type_name,
        "icon": icon,
        "scores": {
            "strength": round(strength, 1),
            "speed": round(speed, 1),
            "depth": round(depth, 1),
            "versatility": round(versatility, 1),
        },
        "mercury_analysis": mercury_analysis,
        "factors": factors,
        "description": description,
    }
