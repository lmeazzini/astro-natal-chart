"""
Temperament calculation based on 5 traditional astrology factors.

This module calculates the dominant temperament (Choleric, Sanguine, Melancholic, Phlegmatic)
by analyzing the elemental qualities (Hot, Cold, Moist, Dry) from:
1. Ascendant sign
2. Ascendant ruler planet (weighted by dignity)
3. Solar quadrant (Sun's position relative to angles)
4. Lunar phase (4 divisions)
5. Lord of Nativity (most dignified planet, weighted by dignity)

Dignity-based weighting (Issue #161):
- Domicile (Rulership): 2.0 - Planet at full power
- Exaltation: 1.75 - Planet highly elevated
- Triplicity: 1.5 - Planet supported by element
- Term/Bound: 1.25 - Minor essential dignity
- Face/Decan: 1.1 - Weakest essential dignity
- Peregrine: 1.0 - No dignity (default)
- Detriment: 0.75 - Planet weakened
- Fall: 0.5 - Planet debilitated
"""

from typing import Any

# Dignity weight scale based on traditional essential dignities
# Range: 0.5 (minimum) to 2.0 (maximum)
DIGNITY_WEIGHTS = {
    "domicile": 2.0,      # Planet in its own sign (rulership)
    "ruler": 2.0,         # Alias for domicile
    "exalted": 1.75,      # Planet in exaltation sign
    "triplicity": 1.5,    # Planet as triplicity ruler (day/night/participant)
    "triplicity_day": 1.5,
    "triplicity_night": 1.5,
    "triplicity_participant": 1.5,
    "term": 1.25,         # Planet in own term (bound)
    "face": 1.1,          # Planet in own face (decan)
    "peregrine": 1.0,     # No dignity (default)
    "detriment": 0.75,    # Planet in sign opposite to rulership
    "fall": 0.5,          # Planet in sign opposite to exaltation
}

# Elemental qualities for each zodiac sign
SIGN_QUALITIES = {
    # Fire signs: Hot + Dry
    "Aries": ("hot", "dry"),
    "Leo": ("hot", "dry"),
    "Sagittarius": ("hot", "dry"),
    # Earth signs: Cold + Dry
    "Taurus": ("cold", "dry"),
    "Virgo": ("cold", "dry"),
    "Capricorn": ("cold", "dry"),
    # Air signs: Hot + Moist
    "Gemini": ("hot", "wet"),
    "Libra": ("hot", "wet"),
    "Aquarius": ("hot", "wet"),
    # Water signs: Cold + Moist
    "Cancer": ("cold", "wet"),
    "Scorpio": ("cold", "wet"),
    "Pisces": ("cold", "wet"),
}

# Elemental qualities for each planet
PLANET_QUALITIES = {
    "Sun": ("hot", "dry"),
    "Moon": ("cold", "wet"),
    "Mars": ("hot", "dry"),
    "Venus": ("cold", "wet"),
    "Jupiter": ("hot", "wet"),
    "Saturn": ("cold", "dry"),
    # Mercury is variable - handled separately
}

# Solar phase qualities (based on Sun sign, grouped in 4 phases)
# This follows the same logic as solar_phase.py (Issue #34)
SOLAR_PHASE_QUALITIES = {
    # Phase 1: Aries, Taurus, Gemini - Sanguine (Hot + Moist)
    "Aries": ("hot", "wet"),
    "Taurus": ("hot", "wet"),
    "Gemini": ("hot", "wet"),
    # Phase 2: Cancer, Leo, Virgo - Choleric (Hot + Dry)
    "Cancer": ("hot", "dry"),
    "Leo": ("hot", "dry"),
    "Virgo": ("hot", "dry"),
    # Phase 3: Libra, Scorpio, Sagittarius - Melancholic (Cold + Dry)
    "Libra": ("cold", "dry"),
    "Scorpio": ("cold", "dry"),
    "Sagittarius": ("cold", "dry"),
    # Phase 4: Capricorn, Aquarius, Pisces - Phlegmatic (Cold + Moist)
    "Capricorn": ("cold", "wet"),
    "Aquarius": ("cold", "wet"),
    "Pisces": ("cold", "wet"),
}

# Lunar phase qualities (4 divisions of lunar cycle)
LUNAR_PHASE_QUALITIES = {
    1: ("hot", "wet"),   # New → Waxing (0° - 90°)
    2: ("hot", "dry"),   # Waxing → Full (90° - 180°)
    3: ("cold", "dry"),  # Full → Waning (180° - 270°)
    4: ("cold", "wet"),  # Waning → New (270° - 360°)
}

# Temperament names and descriptions
TEMPERAMENTS = {
    "choleric": {
        "name": "Choleric",
        "name_pt": "Colérico",
        "qualities": ("hot", "dry"),
        "element": "Fire",
        "element_pt": "Fogo",
        "icon": "🔥",
        "description": (
            "O temperamento Colérico é caracterizado por energia, ambição e assertividade. "
            "Pessoas com este temperamento tendem a ser líderes naturais, dinâmicas e orientadas "
            "para a ação. São impulsivas, apaixonadas e têm forte vontade de realizar seus objetivos."
        ),
    },
    "sanguine": {
        "name": "Sanguine",
        "name_pt": "Sanguíneo",
        "qualities": ("hot", "wet"),
        "element": "Air",
        "element_pt": "Ar",
        "icon": "🌬️",
        "description": (
            "O temperamento Sanguíneo é marcado por otimismo, sociabilidade e entusiasmo. "
            "Pessoas sanguíneas são comunicativas, adaptáveis e gostam de variedade. "
            "Têm facilidade para se relacionar, são alegres e mantêm uma perspectiva positiva da vida."
        ),
    },
    "melancholic": {
        "name": "Melancholic",
        "name_pt": "Melancólico",
        "qualities": ("cold", "dry"),
        "element": "Earth",
        "element_pt": "Terra",
        "icon": "🌍",
        "description": (
            "O temperamento Melancólico é caracterizado por profundidade, reflexão e sensibilidade. "
            "Pessoas melancólicas são analíticas, perfeccionistas e introspectivas. "
            "Valorizam a qualidade, têm pensamento crítico desenvolvido e buscam significado genuíno."
        ),
    },
    "phlegmatic": {
        "name": "Phlegmatic",
        "name_pt": "Fleumático",
        "qualities": ("cold", "wet"),
        "element": "Water",
        "element_pt": "Água",
        "icon": "💧",
        "description": (
            "O temperamento Fleumático é marcado por calma, receptividade e diplomacia. "
            "Pessoas fleumáticas são pacientes, empáticas e buscam harmonia. "
            "São adaptáveis, compassivas e orientadas para o bem-estar coletivo."
        ),
    },
}


def calculate_dignity_weight(dignities: list[str] | None) -> tuple[float, str]:
    """
    Calculate the weight multiplier based on essential dignities.

    Uses the strongest dignity present to determine weight.
    If multiple dignities exist, the highest-weighted one is used.
    Debilities (detriment, fall) reduce the weight below 1.0.

    Args:
        dignities: List of dignity names from calculate_essential_dignities()
                   e.g., ["ruler", "term"] or ["detriment"] or None

    Returns:
        Tuple of (weight, dominant_dignity_name)
        - weight: Float between 0.5 and 2.0
        - dominant_dignity_name: Name of the dignity used (for display)

    Examples:
        >>> calculate_dignity_weight(["ruler", "term"])
        (2.0, "domicile")
        >>> calculate_dignity_weight(["triplicity_day", "face"])
        (1.5, "triplicity")
        >>> calculate_dignity_weight(["detriment"])
        (0.75, "detriment")
        >>> calculate_dignity_weight(None)
        (1.0, "peregrine")
    """
    if not dignities:
        return (1.0, "peregrine")

    # Priority order: check strongest dignities first
    # Positive dignities (ordered by strength)
    if "ruler" in dignities:
        return (DIGNITY_WEIGHTS["ruler"], "domicile")
    if "exalted" in dignities:
        return (DIGNITY_WEIGHTS["exalted"], "exaltation")

    # Check triplicities
    for trip in ["triplicity_day", "triplicity_night", "triplicity_participant"]:
        if trip in dignities:
            return (DIGNITY_WEIGHTS[trip], "triplicity")

    if "term" in dignities:
        return (DIGNITY_WEIGHTS["term"], "term")
    if "face" in dignities:
        return (DIGNITY_WEIGHTS["face"], "face")

    # Negative dignities (debilities)
    if "detriment" in dignities:
        return (DIGNITY_WEIGHTS["detriment"], "detriment")
    if "fall" in dignities:
        return (DIGNITY_WEIGHTS["fall"], "fall")

    # Default: peregrine (no dignity)
    return (1.0, "peregrine")


def get_mercury_qualities(mercury_sign: str) -> tuple[str, str]:
    """
    Get elemental qualities for Mercury based on its sign.

    Mercury is variable and adapts to the element of its sign:
    - Fire/Air signs: Hot + Dry
    - Earth/Water signs: Cold + Wet

    Args:
        mercury_sign: Sign where Mercury is located

    Returns:
        Tuple of (quality1, quality2)
    """
    fire_air_signs = ["Aries", "Leo", "Sagittarius", "Gemini", "Libra", "Aquarius"]

    if mercury_sign in fire_air_signs:
        return ("hot", "dry")
    else:
        return ("cold", "wet")


def get_solar_phase_qualities(sun_sign: str) -> tuple[str, str]:
    """
    Get elemental qualities for the solar phase based on Sun's sign.

    This uses the same grouping as solar_phase.py (Issue #34):
    - Phase 1 (Aries, Taurus, Gemini): Sanguine - Hot + Moist
    - Phase 2 (Cancer, Leo, Virgo): Choleric - Hot + Dry
    - Phase 3 (Libra, Scorpio, Sagittarius): Melancholic - Cold + Dry
    - Phase 4 (Capricorn, Aquarius, Pisces): Phlegmatic - Cold + Moist

    Args:
        sun_sign: Zodiac sign where Sun is located

    Returns:
        Tuple of (quality1, quality2)
    """
    return SOLAR_PHASE_QUALITIES.get(sun_sign, ("hot", "dry"))


def get_lunar_temperament_phase(sun_longitude: float, moon_longitude: float) -> int:
    """
    Determine lunar phase for temperament calculation (4 divisions).

    This is different from the 8-phase lunar cycle. For temperament,
    we divide the lunar cycle into 4 equal parts:
    1. New → Waxing (0° - 90°): Hot + Moist
    2. Waxing → Full (90° - 180°): Hot + Dry
    3. Full → Waning (180° - 270°): Cold + Dry
    4. Waning → New (270° - 360°): Cold + Moist

    Args:
        sun_longitude: Sun's ecliptic longitude
        moon_longitude: Moon's ecliptic longitude

    Returns:
        Phase number (1-4)
    """
    # Calculate angle from Sun to Moon
    angle = (moon_longitude - sun_longitude) % 360

    if 0 <= angle < 90:
        return 1
    elif 90 <= angle < 180:
        return 2
    elif 180 <= angle < 270:
        return 3
    else:  # 270 <= angle < 360
        return 4


def calculate_temperament(
    ascendant_sign: str,
    ascendant_ruler_name: str,
    ascendant_ruler_sign: str,
    sun_sign: str,
    sun_longitude: float,
    moon_longitude: float,
    lord_of_nativity_name: str,
    lord_of_nativity_sign: str,
    ascendant_ruler_dignities: list[str] | None = None,
    lord_of_nativity_dignities: list[str] | None = None,
) -> dict[str, Any]:
    """
    Calculate the dominant temperament based on 5 traditional factors.

    The temperament is determined by counting the elemental qualities
    (Hot, Cold, Moist, Dry) from:
    1. Ascendant sign (weight: 1.0)
    2. Ascendant ruler planet (weight: based on dignity, 0.5-2.0)
    3. Solar phase (based on Sun sign, weight: 1.0)
    4. Lunar phase (4 divisions, weight: 1.0)
    5. Lord of Nativity planet (weight: based on dignity, 0.5-2.0)

    Dignity-based weighting (Issue #161):
    - Factors 2 and 5 (planetary factors) use dignity-based weights
    - Weight range: 0.5 (fall) to 2.0 (domicile)
    - This makes dignified planets contribute more to the final score

    Args:
        ascendant_sign: Sign on the Ascendant
        ascendant_ruler_name: Planet ruling the Ascendant
        ascendant_ruler_sign: Sign where Ascendant ruler is located
        sun_sign: Zodiac sign where Sun is located
        sun_longitude: Sun's ecliptic longitude
        moon_longitude: Moon's ecliptic longitude
        lord_of_nativity_name: Most dignified planet
        lord_of_nativity_sign: Sign where Lord of Nativity is located
        ascendant_ruler_dignities: List of dignities for ascendant ruler (optional)
        lord_of_nativity_dignities: List of dignities for lord of nativity (optional)

    Returns:
        Dictionary with temperament data:
        {
            "dominant": "sanguine",
            "dominant_pt": "Sanguíneo",
            "scores": {"hot": 3.5, "cold": 2.0, "wet": 3.5, "dry": 2.0},
            "factors": [...],  # Now includes weight and dignity fields
            "description": "...",
            ...
        }
    """
    # Initialize quality scores (now using floats for weighted calculations)
    scores: dict[str, float] = {"hot": 0.0, "cold": 0.0, "wet": 0.0, "dry": 0.0}
    factors = []

    # Factor 1: Ascendant sign (no weighting - it's a sign, not a planet)
    asc_qualities = SIGN_QUALITIES[ascendant_sign]
    weight = 1.0
    scores[asc_qualities[0]] += weight
    scores[asc_qualities[1]] += weight
    factors.append(
        {
            "factor": "Ascendant",
            "factor_pt": "Ascendente",
            "value": ascendant_sign,
            "qualities": list(asc_qualities),
            "weight": weight,
            "dignity": None,
        }
    )

    # Factor 2: Ascendant ruler (with dignity-based weighting)
    if ascendant_ruler_name == "Mercury":
        ruler_qualities = get_mercury_qualities(ascendant_ruler_sign)
    else:
        ruler_qualities = PLANET_QUALITIES.get(ascendant_ruler_name, ("hot", "dry"))

    # Calculate weight from dignities
    ruler_weight, ruler_dignity = calculate_dignity_weight(ascendant_ruler_dignities)

    scores[ruler_qualities[0]] += ruler_weight
    scores[ruler_qualities[1]] += ruler_weight
    factors.append(
        {
            "factor": "Ascendant Ruler",
            "factor_pt": "Regente do Ascendente",
            "value": f"{ascendant_ruler_name} in {ascendant_ruler_sign}",
            "value_pt": f"{ascendant_ruler_name} em {ascendant_ruler_sign}",
            "qualities": list(ruler_qualities),
            "weight": ruler_weight,
            "dignity": ruler_dignity,
        }
    )

    # Factor 3: Solar phase (based on Sun sign - same as Issue #34)
    # No weighting - it's based on the Sun's seasonal position, not its dignity
    solar_qualities = get_solar_phase_qualities(sun_sign)
    solar_weight = 1.0
    scores[solar_qualities[0]] += solar_weight
    scores[solar_qualities[1]] += solar_weight

    # Determine which phase the Sun is in
    phase_groups = {
        1: (["Aries", "Taurus", "Gemini"], "1ª Fase (Sanguíneo)", "1st Phase (Sanguine)"),
        2: (["Cancer", "Leo", "Virgo"], "2ª Fase (Colérico)", "2nd Phase (Choleric)"),
        3: (["Libra", "Scorpio", "Sagittarius"], "3ª Fase (Melancólico)", "3rd Phase (Melancholic)"),
        4: (["Capricorn", "Aquarius", "Pisces"], "4ª Fase (Fleumático)", "4th Phase (Phlegmatic)"),
    }

    solar_phase_name_pt = ""
    solar_phase_name_en = ""
    for _phase_num, (signs, name_pt, name_en) in phase_groups.items():
        if sun_sign in signs:
            solar_phase_name_pt = name_pt
            solar_phase_name_en = name_en
            break

    factors.append(
        {
            "factor": "Solar Phase",
            "factor_pt": "Fase Solar",
            "value": f"{sun_sign} - {solar_phase_name_en}",
            "value_pt": f"{sun_sign} - {solar_phase_name_pt}",
            "qualities": list(solar_qualities),
            "weight": solar_weight,
            "dignity": None,
        }
    )

    # Factor 4: Lunar phase (4 divisions)
    # No weighting - it's based on the Moon's phase position, not its dignity
    lunar_phase = get_lunar_temperament_phase(sun_longitude, moon_longitude)
    lunar_qualities = LUNAR_PHASE_QUALITIES[lunar_phase]
    lunar_weight = 1.0
    scores[lunar_qualities[0]] += lunar_weight
    scores[lunar_qualities[1]] += lunar_weight

    lunar_angle = (moon_longitude - sun_longitude) % 360
    phase_names = {
        1: f"New Moon → Waxing ({lunar_angle:.1f}°)",
        2: f"Waxing → Full Moon ({lunar_angle:.1f}°)",
        3: f"Full Moon → Waning ({lunar_angle:.1f}°)",
        4: f"Waning → New Moon ({lunar_angle:.1f}°)",
    }
    phase_names_pt = {
        1: f"Lua Nova → Crescente ({lunar_angle:.1f}°)",
        2: f"Crescente → Lua Cheia ({lunar_angle:.1f}°)",
        3: f"Lua Cheia → Minguante ({lunar_angle:.1f}°)",
        4: f"Minguante → Lua Nova ({lunar_angle:.1f}°)",
    }

    factors.append(
        {
            "factor": "Lunar Phase",
            "factor_pt": "Fase Lunar",
            "value": phase_names[lunar_phase],
            "value_pt": phase_names_pt[lunar_phase],
            "qualities": list(lunar_qualities),
            "weight": lunar_weight,
            "dignity": None,
        }
    )

    # Factor 5: Lord of Nativity (with dignity-based weighting)
    if lord_of_nativity_name == "Mercury":
        lord_qualities = get_mercury_qualities(lord_of_nativity_sign)
    else:
        lord_qualities = PLANET_QUALITIES.get(lord_of_nativity_name, ("hot", "dry"))

    # Calculate weight from dignities
    lord_weight, lord_dignity = calculate_dignity_weight(lord_of_nativity_dignities)

    scores[lord_qualities[0]] += lord_weight
    scores[lord_qualities[1]] += lord_weight
    factors.append(
        {
            "factor": "Lord of Nativity",
            "factor_pt": "Senhor da Natividade",
            "value": f"{lord_of_nativity_name} in {lord_of_nativity_sign}",
            "value_pt": f"{lord_of_nativity_name} em {lord_of_nativity_sign}",
            "qualities": list(lord_qualities),
            "weight": lord_weight,
            "dignity": lord_dignity,
        }
    )

    # Determine dominant temperament
    # Hot vs Cold
    hot_cold = "hot" if scores["hot"] > scores["cold"] else "cold"
    # Wet vs Dry
    wet_dry = "wet" if scores["wet"] > scores["dry"] else "dry"

    # Map to temperament
    if hot_cold == "hot" and wet_dry == "dry":
        temperament_key = "choleric"
    elif hot_cold == "hot" and wet_dry == "wet":
        temperament_key = "sanguine"
    elif hot_cold == "cold" and wet_dry == "dry":
        temperament_key = "melancholic"
    else:  # cold and wet
        temperament_key = "phlegmatic"

    temperament_data = TEMPERAMENTS[temperament_key]

    return {
        "dominant": temperament_key,
        "dominant_pt": temperament_data["name_pt"],
        "element": temperament_data["element"],
        "element_pt": temperament_data["element_pt"],
        "icon": temperament_data["icon"],
        "scores": scores,
        "factors": factors,
        "description": temperament_data["description"],
    }
