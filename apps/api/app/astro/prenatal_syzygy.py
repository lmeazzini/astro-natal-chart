"""
Prenatal Syzygy - Last New Moon or Full Moon before birth.

The syzygy (from Greek "σύζυγος" = yoked together) is the Sun-Moon alignment:
- New Moon: Sun-Moon conjunction (0°)
- Full Moon: Sun-Moon opposition (180°)

The Prenatal Syzygy is significant because:
1. It's one of the 5 points used for Almuten Figuris calculation
2. The degree of the syzygy is considered sensitive
3. Some rectification techniques use it
4. It indicates prenatal "karmic" conditions

References:
- Ptolemy's Tetrabiblos
- Vettius Valens' Anthology
- Robert Schmidt's "Prenatal Concerns" (Project Hindsight)
"""

from typing import Any

import swisseph as swe

from app.translations import DEFAULT_LANGUAGE, get_translation

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


def calculate_prenatal_syzygy(
    birth_jd: float,
    sun_longitude: float,
    moon_longitude: float,
    houses: list[dict] | None = None,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Calculate the prenatal syzygy (last New Moon or Full Moon before birth).

    Uses Swiss Ephemeris to search backwards from birth date with a two-phase
    search algorithm: coarse search (0.5 day steps) followed by fine search
    (0.01 day steps, ~15 minute precision).

    Args:
        birth_jd: Julian Day of birth
        sun_longitude: Sun's longitude at birth (0-360)
        moon_longitude: Moon's longitude at birth (0-360)
        houses: List of house data for house placement (optional)
        language: Language code for translations ('en-US' or 'pt-BR')

    Returns:
        Dictionary with:
        - type: "new_moon" or "full_moon"
        - type_name: Localized name ("New Moon" / "Lua Nova")
        - longitude: Syzygy longitude (0-360)
        - sign: Localized zodiac sign name
        - sign_key: Sign key in lowercase English
        - degree: Degree within sign (0-29)
        - minute: Arc minutes (0-59)
        - house: House placement (1-12)
        - emoji: Moon phase emoji
        - interpretation: Localized interpretation text
        - keywords: Localized keywords
    """
    # Determine syzygy type from elongation
    # If Moon is ahead of Sun by < 180°, last syzygy was New Moon
    # If Moon is ahead of Sun by >= 180°, last syzygy was Full Moon
    elongation = (moon_longitude - sun_longitude) % 360
    syzygy_type = "new_moon" if elongation < 180 else "full_moon"

    # Search backward for exact syzygy moment
    syzygy_jd = _search_syzygy_backward(birth_jd, syzygy_type)

    # Get Sun position at syzygy (the conjunction/opposition point)
    sun_result = swe.calc_ut(syzygy_jd, swe.SUN)
    syzygy_longitude = sun_result[0][0]

    # For Full Moon, use Moon position (opposition point)
    if syzygy_type == "full_moon":
        moon_result = swe.calc_ut(syzygy_jd, swe.MOON)
        syzygy_longitude = moon_result[0][0]

    # Calculate sign and degree
    sign_index = int(syzygy_longitude // 30)
    degree_in_sign = syzygy_longitude % 30
    sign = ZODIAC_SIGNS[sign_index]

    # Get house placement
    house = _get_house_for_position(syzygy_longitude, houses) if houses else 1

    # Get translations
    type_name = get_translation(f"prenatal_syzygy.types.{syzygy_type}", language)
    sign_name = get_translation(f"signs.{sign.lower()}", language)
    interpretation = get_translation(
        f"prenatal_syzygy.interpretations.{syzygy_type}.{sign.lower()}", language
    )
    keywords = get_translation(f"prenatal_syzygy.keywords.{syzygy_type}", language)

    return {
        "type": syzygy_type,
        "type_name": type_name,
        "longitude": round(syzygy_longitude, 4),
        "sign": sign_name,
        "sign_key": sign.lower(),
        "degree": int(degree_in_sign),
        "minute": int((degree_in_sign % 1) * 60),
        "house": house,
        "emoji": "🌑" if syzygy_type == "new_moon" else "🌕",
        "interpretation": interpretation,
        "keywords": keywords,
    }


def _search_syzygy_backward(start_jd: float, syzygy_type: str) -> float:
    """
    Search backward from birth for exact syzygy moment.

    Uses a two-phase search algorithm:
    1. Coarse search: 0.5 day steps to find approximate crossing
    2. Fine search: 0.01 day steps (~15 min) for 0.1° precision

    Args:
        start_jd: Julian Day to start searching from (birth)
        syzygy_type: "new_moon" or "full_moon"

    Returns:
        Julian Day of the syzygy moment
    """
    jd = start_jd
    step = 0.5  # Half day steps for coarse search
    max_iterations = 60  # About 30 days back (enough for any lunar phase)

    # Get initial elongation
    sun_result = swe.calc_ut(jd, swe.SUN)
    moon_result = swe.calc_ut(jd, swe.MOON)
    prev_elongation = (moon_result[0][0] - sun_result[0][0]) % 360

    # Coarse search phase
    for _ in range(max_iterations):
        jd -= step

        sun_result = swe.calc_ut(jd, swe.SUN)
        moon_result = swe.calc_ut(jd, swe.MOON)
        current_elongation = (moon_result[0][0] - sun_result[0][0]) % 360

        # Check if we crossed the target elongation
        if syzygy_type == "new_moon":
            # New Moon: Looking for elongation crossing 0°
            # When we go from small positive (< 30) to large (> 330), we crossed
            if prev_elongation < 30 and current_elongation > 330:
                break
        else:
            # Full Moon: Looking for elongation crossing 180°
            if prev_elongation >= 180 and current_elongation < 180:
                # Went too far, step back
                jd += step
                break
            if prev_elongation < 180 and current_elongation >= 180:
                break

        prev_elongation = current_elongation

    # Fine search phase
    step = 0.01  # About 15 minutes

    for _ in range(100):
        sun_result = swe.calc_ut(jd, swe.SUN)
        moon_result = swe.calc_ut(jd, swe.MOON)
        current_elongation = (moon_result[0][0] - sun_result[0][0]) % 360

        # Check if close enough to target
        if syzygy_type == "new_moon":
            diff = min(current_elongation, 360 - current_elongation)
        else:
            diff = abs(current_elongation - 180)

        if diff < 0.1:  # Within 0.1 degree precision
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

    return jd


def _get_house_for_position(longitude: float, houses: list[dict] | None) -> int:
    """
    Determine which house a longitude falls in.

    Args:
        longitude: Ecliptic longitude (0-360)
        houses: List of house dictionaries with 'house' and 'longitude' keys

    Returns:
        House number (1-12)
    """
    if not houses or len(houses) < 12:
        return 1

    for i in range(12):
        house = houses[i]
        next_house = houses[(i + 1) % 12]
        cusp = house.get("longitude", 0)
        next_cusp = next_house.get("longitude", 0)

        # Handle wrap-around at 0° Aries
        if next_cusp < cusp:
            if longitude >= cusp or longitude < next_cusp:
                return house.get("house", i + 1)
        else:
            if cusp <= longitude < next_cusp:
                return house.get("house", i + 1)

    return 1
