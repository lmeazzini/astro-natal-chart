"""
Hyleg (Giver of Life) calculation for traditional astrology.

The Hyleg (from Arabic "haylāj", from Persian "hīlāg") is the planet or point
that serves as the "Giver of Life" in a chart. It represents:
- The native's vital force and physical constitution
- The primary significator for longevity calculations
- A key point for medical astrology and health analysis

This module implements the Ptolemaic method for Hyleg determination.

References
----------
Primary Source (Implemented):
    Ptolemy, Claudius. Tetrabiblos, Book III, Chapters 10-11.
    "Of the Prorogatory Places" and "Of the Hylegical Places"

Secondary Sources:
    - Vettius Valens. Anthology (2nd century CE)
    - Dorotheus of Sidon. Carmen Astrologicum (1st century CE)
    - Robert Schmidt. "Prenatal Concerns" (Project Hindsight)

Ptolemaic Method (Implemented):
    - Hylegical Places: Houses 1, 7, 9, 10, 11 (or 5° below ASC in 12th)
    - Day charts: Sun → Moon → Ascendant → Part of Fortune → Prenatal Syzygy
    - Night charts: Moon → Sun → Ascendant → Part of Fortune → Prenatal Syzygy
    - Qualification: Must be aspected by domicile lord OR prorogatory planet

Alternative Method (NOT Implemented):
    William Lilly. Christian Astrology (1647), Book III.
    - Hylegical Places: Houses 1, 7, 10, 11 (excludes 9th house)
    - Different triplicity system
    - More practical/horary approach
"""

from typing import Any

import swisseph as swe

from app.astro.dignities import RULERSHIPS
from app.translations import get_translation

# Hylegical places - houses where Hyleg can exist
HYLEGICAL_HOUSES = {1, 7, 9, 10, 11}

# Degrees below ASC in 12th house that are considered hylegical
HYLEGICAL_12TH_HOUSE_DEGREES = 5.0

# Prorogatory planets - can qualify Hyleg via aspect
PROROGATORY_PLANETS = {"Saturn", "Jupiter", "Mars", "Venus", "Mercury"}

# Major aspects for Hyleg qualification
HYLEG_ASPECTS = {
    "Conjunction": {"angle": 0, "orb": 8},
    "Sextile": {"angle": 60, "orb": 6},
    "Square": {"angle": 90, "orb": 7},
    "Trine": {"angle": 120, "orb": 8},
    "Opposition": {"angle": 180, "orb": 8},
}

# Classical planets only (no Uranus, Neptune, Pluto)
CLASSICAL_PLANETS = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}


def calculate_prenatal_syzygy(
    birth_jd: float,
    sun_longitude: float,
    moon_longitude: float,
) -> dict[str, Any]:
    """
    Calculate the prenatal syzygy (last New Moon or Full Moon before birth).

    Uses Swiss Ephemeris to search backwards from birth date.

    Args:
        birth_jd: Julian Day of birth
        sun_longitude: Sun's longitude at birth
        moon_longitude: Moon's longitude at birth

    Returns:
        Dictionary with:
        - type: "new_moon" or "full_moon"
        - longitude: Longitude of the syzygy point
        - jd: Julian Day of the syzygy
        - sign: Zodiac sign of the syzygy
        - degree: Degree within the sign
    """
    from app.services.astro_service import SIGNS

    # Search backwards for the last lunation
    # New Moon: Sun-Moon conjunction (0°)
    # Full Moon: Sun-Moon opposition (180°)

    # Calculate current Sun-Moon elongation
    elongation = (moon_longitude - sun_longitude) % 360

    # If elongation < 180, last syzygy was a New Moon
    # If elongation >= 180, last syzygy was a Full Moon
    if elongation < 180:
        # Find previous New Moon (conjunction)
        syzygy_type = "new_moon"
    else:
        # Find previous Full Moon (opposition)
        syzygy_type = "full_moon"

    # Use Swiss Ephemeris to find the previous lunation
    # We'll iterate backwards by small steps to find when the elongation crossed our target
    jd = birth_jd
    step = 0.5  # Half day steps
    max_iterations = 60  # About 30 days back (enough for any lunar phase)

    prev_elongation = elongation
    for _ in range(max_iterations):
        jd -= step

        # Get Sun position
        sun_result = swe.calc_ut(jd, swe.SUN)
        sun_lon = sun_result[0][0]

        # Get Moon position
        moon_result = swe.calc_ut(jd, swe.MOON)
        moon_lon = moon_result[0][0]

        current_elongation = (moon_lon - sun_lon) % 360

        # Check if we crossed the target elongation
        if syzygy_type == "new_moon":
            # Crossing from small positive to large (near 360)
            if prev_elongation < 30 and current_elongation > 330:
                # Found it, now refine
                break
        else:
            # Crossing from below 180 to above 180
            if prev_elongation >= 180 and current_elongation < 180:
                # Went too far, go back a step
                jd += step
                break
            if prev_elongation < 180 and current_elongation >= 180:
                # Found it
                break

        prev_elongation = current_elongation

    # Refine the search with smaller steps
    step = 0.01  # About 15 minutes
    for _ in range(100):
        sun_result = swe.calc_ut(jd, swe.SUN)
        sun_lon = sun_result[0][0]
        moon_result = swe.calc_ut(jd, swe.MOON)
        moon_lon = moon_result[0][0]

        current_elongation = (moon_lon - sun_lon) % 360

        # Check if close enough to target
        if syzygy_type == "new_moon":
            diff = min(current_elongation, 360 - current_elongation)
        else:
            diff = abs(current_elongation - 180)

        if diff < 0.1:  # Within 0.1 degree
            break

        # Adjust direction
        if syzygy_type == "new_moon":
            if current_elongation < 180:
                jd -= step
            else:
                jd += step
        else:
            if current_elongation < 180:
                jd += step
            else:
                jd -= step

    # Get final position
    sun_result = swe.calc_ut(jd, swe.SUN)
    syzygy_longitude = sun_result[0][0]

    # Calculate sign and degree
    sign_index = int(syzygy_longitude / 30)
    sign = SIGNS[sign_index]
    degree = syzygy_longitude % 30

    return {
        "type": syzygy_type,
        "longitude": syzygy_longitude,
        "jd": jd,
        "sign": sign,
        "degree": degree,
    }


def _translate_qualification_reason(reason: str, language: str) -> str:
    """
    Translate a qualification reason string.

    Handles cases like:
    - "no_aspects" → translated text
    - "aspected_by_prorogatory:Saturn" → translated base + planet name

    Args:
        reason: The raw reason string (may contain :planet_name)
        language: Language code for translation

    Returns:
        Translated reason string
    """
    from app.translations import get_translation

    if ":" in reason:
        # Split into base reason and planet name
        base_reason, planet_name = reason.split(":", 1)
        # Translate the base part
        translated_base = get_translation(f"hyleg.qualification.{base_reason}", language)
        # Append planet name (planet names could also be translated)
        planet_translation = get_translation(f"planets.{planet_name}", language)
        if planet_translation != f"planets.{planet_name}":
            planet_name = planet_translation
        return f"{translated_base} ({planet_name})"
    else:
        return get_translation(f"hyleg.qualification.{reason}", language)


def is_in_hylegical_place(
    house: int,
    longitude: float,
    ascendant: float,
) -> bool:
    """
    Check if a position is in a hylegical place.

    Hylegical places according to Ptolemy: houses 1, 7, 9, 10, 11
    Some traditions also include 5° below the Ascendant (in 12th house but rising).

    Args:
        house: House number (1-12)
        longitude: Longitude of the position (0-360)
        ascendant: Longitude of the Ascendant

    Returns:
        True if the position is in a hylegical place
    """
    # Direct hylegical houses
    if house in HYLEGICAL_HOUSES:
        return True

    # 5° below ASC rule (in 12th house but about to rise)
    if house == 12:
        degrees_from_asc = (ascendant - longitude) % 360
        if degrees_from_asc <= HYLEGICAL_12TH_HOUSE_DEGREES:
            return True

    return False


def find_aspecting_planets(
    target_longitude: float,
    planets: list[dict[str, Any]],
    orb: float = 8.0,
) -> list[dict[str, Any]]:
    """
    Find planets that aspect a given longitude.

    Args:
        target_longitude: The longitude to check aspects to
        planets: List of planet data dictionaries
        orb: Maximum orb for aspects (default 8°)

    Returns:
        List of aspecting planets with aspect details
    """
    aspecting = []

    for planet in planets:
        if planet["name"] not in CLASSICAL_PLANETS:
            continue

        planet_lon = planet["longitude"]

        # Calculate angle between planet and target
        angle_diff = abs(planet_lon - target_longitude)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # Check each aspect type
        for aspect_name, aspect_data in HYLEG_ASPECTS.items():
            aspect_angle = aspect_data["angle"]
            aspect_orb = min(orb, aspect_data["orb"])

            orb_diff = abs(angle_diff - aspect_angle)

            if orb_diff <= aspect_orb:
                aspecting.append(
                    {
                        "planet": planet["name"],
                        "aspect": aspect_name,
                        "orb": round(orb_diff, 2),
                        "angle": round(angle_diff, 2),
                    }
                )
                break  # Only one aspect per planet

    return aspecting


def is_hyleg_qualified(
    candidate_name: str,
    candidate_longitude: float,
    candidate_sign: str,
    planets: list[dict[str, Any]],
) -> tuple[bool, str, list[str]]:
    """
    Check if a Hyleg candidate is qualified by aspect.

    According to Ptolemy, the Hyleg must be aspected by:
    1. Its domicile lord (ruler of the sign it's in), OR
    2. A prorogatory planet (Saturn, Jupiter, Mars, Venus, Mercury)

    Args:
        candidate_name: Name of the candidate (e.g., "Sun", "Moon", "Ascendant")
        candidate_longitude: Longitude of the candidate
        candidate_sign: Sign the candidate is in
        planets: List of all planets

    Returns:
        Tuple of (is_qualified, reason, list_of_aspecting_planets)
    """
    # Get domicile lord of the candidate's sign
    domicile_lord = RULERSHIPS.get(candidate_sign)

    # Find all planets aspecting the candidate
    aspecting = find_aspecting_planets(candidate_longitude, planets)
    aspecting_names = [a["planet"] for a in aspecting]

    # Check if domicile lord aspects the candidate
    if domicile_lord and domicile_lord in aspecting_names:
        return (
            True,
            f"aspected_by_domicile_lord:{domicile_lord}",
            aspecting_names,
        )

    # Check if any prorogatory planet aspects the candidate
    for planet_name in aspecting_names:
        if planet_name in PROROGATORY_PLANETS:
            return (
                True,
                f"aspected_by_prorogatory:{planet_name}",
                aspecting_names,
            )

    # Not qualified
    if not aspecting_names:
        return (False, "no_aspects", [])
    else:
        return (
            False,
            "no_qualifying_aspects",
            aspecting_names,
        )


def get_planet_by_name(
    planets: list[dict[str, Any]],
    name: str,
) -> dict[str, Any] | None:
    """Get a planet dictionary by name."""
    for planet in planets:
        if planet["name"] == name:
            return planet
    return None


def get_house_for_position(
    longitude: float,
    house_cusps: list[dict[str, Any]],
) -> int:
    """
    Determine which house a position falls in.

    Args:
        longitude: The longitude to check (0-360)
        house_cusps: List of house cusp data

    Returns:
        House number (1-12)
    """

    # Sort cusps by house number (handle both "number" and "house" keys)
    def get_house_num(h: dict) -> int:
        return h.get("number", h.get("house", 0))

    def get_cusp_lon(h: dict) -> float:
        return h.get("cusp", h.get("longitude", 0.0))

    cusps = sorted(house_cusps, key=get_house_num)

    for i, cusp in enumerate(cusps):
        next_cusp = cusps[(i + 1) % 12]
        cusp_lon = get_cusp_lon(cusp)
        next_cusp_lon = get_cusp_lon(next_cusp)

        # Handle wrap-around at 360°
        if next_cusp_lon < cusp_lon:
            # Cusp spans 0°
            if longitude >= cusp_lon or longitude < next_cusp_lon:
                return get_house_num(cusp)
        else:
            if cusp_lon <= longitude < next_cusp_lon:
                return get_house_num(cusp)

    return 1  # Default to 1st house


def calculate_hyleg(
    planets: list[dict[str, Any]],
    houses: list[dict[str, Any]],
    aspects: list[dict[str, Any]],
    ascendant: float,
    arabic_parts: list[dict[str, Any]],
    sect: str,
    birth_jd: float,
    method: str = "ptolemaic",
    language: str = "en-US",
) -> dict[str, Any] | None:
    """
    Determine the Hyleg (Giver of Life) for a natal chart.

    Follows the Ptolemaic method:
    1. For day charts: Check Sun first, then Moon
    2. For night charts: Check Moon first, then Sun
    3. Candidate must be in a hylegical place (houses 1, 7, 9, 10, 11 or 5° below ASC)
    4. Candidate must be aspected by domicile lord or prorogatory planet
    5. Fall back to Ascendant, Part of Fortune, Prenatal Syzygy

    Args:
        planets: List of planet data with positions and dignities
        houses: List of house cusp data
        aspects: List of aspect data between planets
        ascendant: Longitude of the Ascendant
        arabic_parts: List of Arabic Parts (Part of Fortune is first)
        sect: Chart sect - "diurnal" or "nocturnal"
        birth_jd: Julian Day of birth
        method: Calculation method (currently only "ptolemaic" supported)
        language: Language for translated strings

    Returns:
        Hyleg data dictionary or None if no Hyleg found
    """
    from app.astro.dignities import calculate_essential_dignities
    from app.services.astro_service import SIGNS

    # Determine luminary order based on sect
    is_day_chart = sect == "diurnal"
    if is_day_chart:
        primary_luminary = "Sun"
        secondary_luminary = "Moon"
    else:
        primary_luminary = "Moon"
        secondary_luminary = "Sun"

    candidates_evaluated: list[dict[str, Any]] = []

    # Helper to evaluate a candidate
    def evaluate_candidate(
        name: str,
        longitude: float,
        sign: str,
        house: int,
        is_point: bool = False,
    ) -> dict[str, Any] | None:
        """Evaluate a single Hyleg candidate."""
        in_hylegical = is_in_hylegical_place(house, longitude, ascendant)
        qualified, reason, aspecting = is_hyleg_qualified(name, longitude, sign, planets)

        evaluation = {
            "candidate": name,
            "longitude": round(longitude, 4),
            "sign": sign,
            "house": house,
            "in_hylegical_place": in_hylegical,
            "is_qualified": in_hylegical and qualified,
            "qualification_reason": reason if in_hylegical else "not_in_hylegical_place",
            "aspecting_planets": aspecting,
        }
        candidates_evaluated.append(evaluation)

        if in_hylegical and qualified:
            # Calculate dignities for the candidate (if it's a planet)
            if not is_point:
                degree = longitude % 30
                dignity_data = calculate_essential_dignities(name, sign, degree, sect)
            else:
                dignity_data = None

            return {
                "hyleg": name,
                "hyleg_longitude": round(longitude, 4),
                "hyleg_sign": sign,
                "hyleg_house": house,
                "is_day_chart": is_day_chart,
                "method": method,
                "qualification_reason": _translate_qualification_reason(reason, language),
                "hyleg_dignity": dignity_data,
                "aspecting_planets": aspecting,
                "domicile_lord": RULERSHIPS.get(sign),
                "candidates_evaluated": candidates_evaluated,
            }
        return None

    # Step 1: Check primary luminary
    primary = get_planet_by_name(planets, primary_luminary)
    if primary:
        result = evaluate_candidate(
            primary["name"],
            primary["longitude"],
            primary["sign"],
            primary["house"],
        )
        if result:
            return result

    # Step 2: Check secondary luminary
    secondary = get_planet_by_name(planets, secondary_luminary)
    if secondary:
        result = evaluate_candidate(
            secondary["name"],
            secondary["longitude"],
            secondary["sign"],
            secondary["house"],
        )
        if result:
            return result

    # Step 3: Check Ascendant
    asc_sign_index = int(ascendant / 30)
    asc_sign = SIGNS[asc_sign_index]
    result = evaluate_candidate(
        "Ascendant",
        ascendant,
        asc_sign,
        1,  # Ascendant is always in 1st house
        is_point=True,
    )
    if result:
        return result

    # Step 4: Check Part of Fortune
    if arabic_parts:
        # Handle both dict format (from calculate_arabic_parts) and list format
        if isinstance(arabic_parts, dict):
            fortune = arabic_parts.get("fortune", {})
        elif isinstance(arabic_parts, list) and len(arabic_parts) > 0:
            fortune = arabic_parts[0]
        else:
            fortune = {}
        fortune_lon = fortune.get("longitude", 0) if fortune else 0
        if fortune_lon > 0:  # Only evaluate if we have valid fortune data
            fortune_sign_index = int(fortune_lon / 30)
            fortune_sign = SIGNS[fortune_sign_index]
            fortune_house = get_house_for_position(fortune_lon, houses)

            result = evaluate_candidate(
                "Part of Fortune",
                fortune_lon,
                fortune_sign,
                fortune_house,
                is_point=True,
            )
            if result:
                return result

    # Step 5: Check Prenatal Syzygy
    sun = get_planet_by_name(planets, "Sun")
    moon = get_planet_by_name(planets, "Moon")
    if sun and moon:
        syzygy = calculate_prenatal_syzygy(birth_jd, sun["longitude"], moon["longitude"])
        syzygy_house = get_house_for_position(syzygy["longitude"], houses)

        result = evaluate_candidate(
            f"Prenatal Syzygy ({syzygy['type'].replace('_', ' ').title()})",
            syzygy["longitude"],
            syzygy["sign"],
            syzygy_house,
            is_point=True,
        )
        if result:
            return result

    # No Hyleg found
    return {
        "hyleg": None,
        "hyleg_longitude": None,
        "hyleg_sign": None,
        "hyleg_house": None,
        "is_day_chart": is_day_chart,
        "method": method,
        "qualification_reason": get_translation("hyleg.no_hyleg_found", language),
        "hyleg_dignity": None,
        "aspecting_planets": [],
        "domicile_lord": None,
        "candidates_evaluated": candidates_evaluated,
    }
