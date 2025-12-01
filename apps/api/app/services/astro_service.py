"""
Astrological calculation service using Swiss Ephemeris (PySwisseph).
"""

from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from app.astro.dignities import calculate_essential_dignities, find_lord_of_nativity, get_sign_ruler
from app.astro.lunar_phase import calculate_lunar_phase
from app.astro.solar_phase import calculate_solar_phase
from app.astro.temperament import calculate_temperament
from app.schemas.chart import AspectData, HousePosition, PlanetPosition

# Set ephemeris path to None to use built-in Moshier ephemeris (lower precision but no files needed)
# For production, download Swiss Ephemeris files for higher precision
swe.set_ephe_path(None)

# Planet constants from Swiss Ephemeris
# Note: Using Moshier ephemeris (built-in) which supports main planets and nodes
# Chiron and other asteroids require external ephemeris files
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "North Node": swe.TRUE_NODE,
    # "Chiron": swe.CHIRON,  # Requires external ephemeris files
}

# Zodiac signs
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

# House systems
HOUSE_SYSTEMS = {
    "placidus": b"P",
    "koch": b"K",
    "equal": b"E",
    "whole_sign": b"W",
    "campanus": b"C",
    "regiomontanus": b"R",
}

# Major aspects with their angles and orbs
ASPECTS = {
    "Conjunction": {"angle": 0, "orb": 8},
    "Opposition": {"angle": 180, "orb": 8},
    "Trine": {"angle": 120, "orb": 8},
    "Square": {"angle": 90, "orb": 7},
    "Sextile": {"angle": 60, "orb": 6},
    "Quincunx": {"angle": 150, "orb": 3},
    "Semisextile": {"angle": 30, "orb": 2},
    "Semisquare": {"angle": 45, "orb": 2},
    "Sesquiquadrate": {"angle": 135, "orb": 2},
}

# Sect constants (Hellenistic astrology)
# Diurnal planets work better in day charts, nocturnal planets in night charts
DIURNAL_PLANETS = ["Sun", "Jupiter", "Saturn"]
NOCTURNAL_PLANETS = ["Moon", "Venus", "Mars"]
NEUTRAL_PLANETS = ["Mercury"]

# Planet factions
BENEFIC_PLANETS = ["Jupiter", "Venus"]
MALEFIC_PLANETS = ["Saturn", "Mars"]
LUMINARY_PLANETS = ["Sun", "Moon"]

# Modern/outer planets to skip in traditional sect analysis
MODERN_PLANETS = ["Uranus", "Neptune", "Pluto", "North Node", "Chiron"]

# Classical planet order (traditional sorting)
CLASSICAL_PLANET_ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def convert_to_julian_day(dt: datetime, timezone: str, latitude: float, longitude: float) -> float:
    """
    Convert datetime to Julian Day for Swiss Ephemeris calculations.

    Args:
        dt: Birth datetime (can be timezone-aware UTC or naive local time)
        timezone: Timezone string (e.g., 'America/Sao_Paulo') - used only if dt is naive
        latitude: Geographic latitude (unused, kept for API compatibility)
        longitude: Geographic longitude (unused, kept for API compatibility)

    Returns:
        Julian Day number
    """
    # Handle timezone conversion properly
    # Case 1: datetime already has timezone info (e.g., from database with UTC)
    # Case 2: naive datetime that should be interpreted in the given timezone
    if dt.tzinfo is not None:
        # Already timezone-aware - convert directly to UTC
        dt_utc = dt.astimezone(ZoneInfo("UTC"))
    else:
        # Naive datetime - interpret it in the given timezone, then convert to UTC
        tz = ZoneInfo(timezone)
        dt_aware = dt.replace(tzinfo=tz)
        dt_utc = dt_aware.astimezone(ZoneInfo("UTC"))

    # Calculate Julian Day
    jd: float = swe.julday(  # type: ignore[no-any-return]
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
    )

    return jd


def get_sign_and_position(longitude: float) -> dict[str, Any]:
    """
    Get zodiac sign and precise position from longitude.

    Args:
        longitude: Ecliptic longitude (0-360 degrees)

    Returns:
        Dict with sign, degree, minute, second
    """
    sign_num = int(longitude / 30)
    sign = SIGNS[sign_num]

    # Position within sign (0-30 degrees)
    pos_in_sign = longitude - (sign_num * 30)
    degree = int(pos_in_sign)
    minute_float = (pos_in_sign - degree) * 60
    minute = int(minute_float)
    second = int((minute_float - minute) * 60)

    return {
        "sign": sign,
        "degree": degree,
        "minute": minute,
        "second": second,
    }


def calculate_planets(jd: float, house_cusps: list[float]) -> list[PlanetPosition]:
    """
    Calculate positions of all planets.

    Args:
        jd: Julian Day
        house_cusps: List of house cusp longitudes

    Returns:
        List of planet positions
    """
    planets = []

    for name, planet_id in PLANETS.items():
        # Calculate planet position
        # flags: SEFLG_MOSEPH (Moshier ephemeris, built-in) + SEFLG_SPEED (get speed)
        result, flags_ret = swe.calc_ut(jd, planet_id, swe.FLG_MOSEPH | swe.FLG_SPEED)

        longitude = result[0]
        latitude = result[1]
        speed = result[3]

        # Get sign and position
        sign_data = get_sign_and_position(longitude)

        # Determine house
        house = get_house_for_planet(longitude, house_cusps)

        # Check if retrograde (speed < 0)
        retrograde = speed < 0

        planets.append(
            PlanetPosition(
                name=name,
                longitude=longitude,
                latitude=latitude,
                speed=speed,
                sign=sign_data["sign"],
                degree=sign_data["degree"],
                minute=sign_data["minute"],
                second=sign_data["second"],
                house=house,
                retrograde=retrograde,
            )
        )

    return planets


def get_house_for_planet(planet_longitude: float, house_cusps: list[float]) -> int:
    """
    Determine which house a planet is in.

    Args:
        planet_longitude: Planet's ecliptic longitude
        house_cusps: List of 12 house cusp longitudes

    Returns:
        House number (1-12)
    """
    for i in range(12):
        cusp = house_cusps[i]
        next_cusp = house_cusps[(i + 1) % 12]

        # Handle wrap-around at 360/0 degrees
        if next_cusp < cusp:
            if planet_longitude >= cusp or planet_longitude < next_cusp:
                return i + 1
        else:
            if cusp <= planet_longitude < next_cusp:
                return i + 1

    return 1  # Fallback to house 1


def calculate_houses(
    jd: float, latitude: float, longitude: float, house_system: str = "placidus"
) -> tuple[list[HousePosition], float, float]:
    """
    Calculate house cusps and angles.

    Args:
        jd: Julian Day
        latitude: Geographic latitude
        longitude: Geographic longitude
        house_system: House system to use (default: placidus)

    Returns:
        Tuple of (house positions, ascendant, midheaven)
    """
    hsys = HOUSE_SYSTEMS.get(house_system, b"P")

    # Calculate houses
    cusps, ascmc = swe.houses(jd, latitude, longitude, hsys)

    # cusps[0:12] are houses 1-12 (indices 0-11)
    # ascmc[0] = Ascendant, ascmc[1] = MC (Midheaven)
    ascendant = ascmc[0]
    midheaven = ascmc[1]

    houses = []
    for i in range(12):
        cusp_longitude = cusps[i]
        sign_data = get_sign_and_position(cusp_longitude)

        houses.append(
            HousePosition(
                house=i + 1,  # Houses are numbered 1-12, but index is 0-11
                longitude=cusp_longitude,
                sign=sign_data["sign"],
                degree=sign_data["degree"],
                minute=sign_data["minute"],
                second=sign_data["second"],
            )
        )

    return houses, ascendant, midheaven


def calculate_aspects(planets: list[PlanetPosition]) -> list[AspectData]:
    """
    Calculate aspects between planets.

    Args:
        planets: List of planet positions

    Returns:
        List of significant aspects
    """
    aspects = []

    # Compare each planet with every other planet
    for i, planet1 in enumerate(planets):
        for planet2 in planets[i + 1 :]:
            # Calculate angle between planets
            angle_diff = abs(planet1.longitude - planet2.longitude)

            # Normalize to 0-180 degrees
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            # Check each aspect type
            for aspect_name, aspect_data in ASPECTS.items():
                aspect_angle = aspect_data["angle"]
                orb = aspect_data["orb"]

                # Calculate orb (difference from exact aspect)
                orb_diff = abs(angle_diff - aspect_angle)

                # If within orb, it's a valid aspect
                if orb_diff <= orb:
                    # Determine if applying or separating
                    applying = is_aspect_applying(
                        planet1.longitude,
                        planet2.longitude,
                        planet1.speed,
                        planet2.speed,
                        aspect_angle,
                    )

                    aspects.append(
                        AspectData(
                            planet1=planet1.name,
                            planet2=planet2.name,
                            aspect=aspect_name,
                            angle=angle_diff,
                            orb=orb_diff,
                            applying=applying,
                        )
                    )

    return aspects


def is_aspect_applying(
    lon1: float, lon2: float, speed1: float, speed2: float, aspect_angle: float
) -> bool:
    """
    Determine if an aspect is applying or separating.

    Args:
        lon1: Planet 1 longitude
        lon2: Planet 2 longitude
        speed1: Planet 1 daily speed
        speed2: Planet 2 daily speed
        aspect_angle: Target aspect angle

    Returns:
        True if applying, False if separating
    """
    # Calculate relative speed
    relative_speed = speed1 - speed2

    # Calculate current angle
    current_angle = abs(lon1 - lon2)
    if current_angle > 180:
        current_angle = 360 - current_angle

    # If faster planet is catching up, aspect is applying
    return (relative_speed > 0 and current_angle < aspect_angle) or (
        relative_speed < 0 and current_angle > aspect_angle
    )


def calculate_sect(ascendant: float, sun_longitude: float) -> str:
    """
    Calculate chart sect (day chart vs night chart).

    In traditional astrology, sect determines whether a chart is diurnal or nocturnal:
    - Diurnal (day chart): Sun is above the horizon (houses 7-12)
    - Nocturnal (night chart): Sun is below the horizon (houses 1-6)

    The horizon is defined by the ASC-DSC axis:
    - Sun between ASC and DSC (going through IC, increasing degrees) = BELOW horizon
    - Sun between DSC and ASC (going through MC, decreasing/wrapping degrees) = ABOVE horizon

    Edge cases:
    - Sun exactly on ASC (sunrise): counted as diurnal (start of day)
    - Sun exactly on DSC (sunset): counted as nocturnal (start of night)

    Args:
        ascendant: Ascendant degree (0-360)
        sun_longitude: Sun's ecliptic longitude (0-360)

    Returns:
        "diurnal" if day chart, "nocturnal" if night chart
    """
    # Calculate descendant (opposite of ascendant)
    descendant = (ascendant + 180) % 360

    # Normalize sun longitude
    sun_lon = sun_longitude % 360

    # Determine if Sun is BELOW the horizon (between ASC and DSC going through IC)
    # If Sun is below horizon, it's a night chart; otherwise it's a day chart
    if ascendant < descendant:
        # Normal case: ASC is at smaller degree than DSC
        # Sun between ASC and DSC (exclusive of DSC) = below horizon = nocturnal
        sun_below_horizon = ascendant <= sun_lon < descendant
    else:
        # Wrapped case: ASC crosses 0° (e.g., ASC=350, DSC=170)
        # Sun is below horizon if it's >= ASC (going to 360) OR < DSC (from 0)
        sun_below_horizon = sun_lon >= ascendant or sun_lon < descendant

    return "nocturnal" if sun_below_horizon else "diurnal"


def get_planet_sect_status(planet_name: str, chart_sect: str) -> dict[str, Any]:
    """
    Get planet's sect status and performance based on traditional astrology.

    In Hellenistic astrology:
    - Diurnal planets (Sun, Jupiter, Saturn) work better in day charts
    - Nocturnal planets (Moon, Venus, Mars) work better in night charts
    - Mercury is neutral and adapts to either sect

    Args:
        planet_name: Name of planet
        chart_sect: 'diurnal' or 'nocturnal'

    Returns:
        Dictionary with sect analysis for the planet
    """
    # Determine planet's natural sect using module constants
    if planet_name in DIURNAL_PLANETS:
        planet_sect = "diurnal"
    elif planet_name in NOCTURNAL_PLANETS:
        planet_sect = "nocturnal"
    else:
        planet_sect = "neutral"

    # Check if in sect
    in_sect = (planet_sect == chart_sect) or (planet_sect == "neutral")

    # Determine faction using module constants
    if planet_name in BENEFIC_PLANETS:
        faction = "benefic"
    elif planet_name in MALEFIC_PLANETS:
        faction = "malefic"
    elif planet_name in LUMINARY_PLANETS:
        faction = "luminary"
    else:
        faction = "neutral"

    # Determine performance based on faction and sect status
    if faction == "benefic":
        performance = "optimal" if in_sect else "moderate"
    elif faction == "malefic":
        performance = "moderate" if in_sect else "challenging"
    else:
        performance = "optimal"  # Luminaries and Mercury

    return {
        "planet_sect": planet_sect,
        "in_sect": in_sect,
        "faction": faction,
        "performance": performance,
    }


def calculate_sect_analysis(planets: list[dict[str, Any]], chart_sect: str) -> dict[str, Any]:
    """
    Complete sect analysis of the chart.

    Analyzes all planets' relationship with the chart's sect, categorizing them
    as in-sect, out-of-sect, or neutral, and identifying benefics/malefics.

    Args:
        planets: List of planet dictionaries with name, sign, house
        chart_sect: 'diurnal' or 'nocturnal'

    Returns:
        Complete sect analysis dictionary
    """
    planets_in_sect: list[dict[str, Any]] = []
    planets_out_of_sect: list[dict[str, Any]] = []
    planets_neutral: list[dict[str, Any]] = []

    benefics: dict[str, dict[str, Any] | None] = {"in_sect": None, "out_of_sect": None}
    malefics: dict[str, dict[str, Any] | None] = {"in_sect": None, "out_of_sect": None}

    for planet in planets:
        planet_name = planet.get("name", "")
        # Skip modern planets using module constant
        if planet_name in MODERN_PLANETS:
            continue

        status = get_planet_sect_status(planet_name, chart_sect)

        planet_data = {
            "name": planet_name,
            "sign": planet.get("sign", ""),
            "house": planet.get("house", 0),
            "degree": planet.get("degree", 0),
            **status,
        }

        # Categorize by sect status
        if status["planet_sect"] == "neutral":
            planets_neutral.append(planet_data)
        elif status["in_sect"]:
            planets_in_sect.append(planet_data)
            if status["faction"] == "benefic":
                benefics["in_sect"] = planet_data
            elif status["faction"] == "malefic":
                malefics["in_sect"] = planet_data
        else:
            planets_out_of_sect.append(planet_data)
            if status["faction"] == "benefic":
                benefics["out_of_sect"] = planet_data
            elif status["faction"] == "malefic":
                malefics["out_of_sect"] = planet_data

    # Get Sun's house for display
    sun_house = 1
    for planet in planets:
        if planet.get("name") == "Sun":
            sun_house = planet.get("house", 1)
            break

    return {
        "sect": chart_sect,
        "sun_house": sun_house,
        "planets_by_sect": {
            "in_sect": planets_in_sect,
            "out_of_sect": planets_out_of_sect,
            "neutral": planets_neutral,
        },
        "benefics": benefics,
        "malefics": malefics,
    }


def get_house_for_position(longitude: float, house_cusps: list[float]) -> int:
    """
    Determine which house a given position falls into.

    Args:
        longitude: Ecliptic longitude (0-360)
        house_cusps: List of 12 house cusp longitudes

    Returns:
        House number (1-12)
    """
    lon = longitude % 360

    for i in range(len(house_cusps)):
        cusp = house_cusps[i]
        next_cusp = house_cusps[(i + 1) % 12]

        if cusp < next_cusp:
            # Normal case
            if cusp <= lon < next_cusp:
                return i + 1
        else:
            # Wrapped case (crosses 0° Aries)
            if lon >= cusp or lon < next_cusp:
                return i + 1

    return 1  # Fallback to first house


def calculate_arabic_parts(
    ascendant: float,
    sun_longitude: float,
    moon_longitude: float,
    planets: list[PlanetPosition],
    house_cusps: list[float],
    sect: str,
) -> dict[str, Any]:
    """
    Calculate Arabic Parts (Lots) according to Hellenistic tradition.

    Formula: Part = Ascendant + Planet1 - Planet2 (all modulo 360)
    Formulas differ between diurnal and nocturnal charts.

    Args:
        ascendant: Ascendant degree (0-360)
        sun_longitude: Sun's ecliptic longitude (0-360)
        moon_longitude: Moon's ecliptic longitude (0-360)
        planets: List of planet positions
        house_cusps: List of house cusp longitudes
        sect: "diurnal" or "nocturnal"

    Returns:
        Dictionary with calculated Arabic Parts
    """
    is_diurnal = sect == "diurnal"

    # Helper to get planet longitude
    def get_planet_long(name: str) -> float:
        for planet in planets:
            if planet.name == name:
                return planet.longitude
        return 0.0

    # Helper to get sign from longitude
    def get_sign(lon: float) -> str:
        sign_index = int((lon % 360) // 30)
        return SIGNS[sign_index]

    parts = {}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Arabic Parts (Lots) - Traditional Hellenistic Astrology
    # ═══════════════════════════════════════════════════════════════════════════════
    # All parts use the formula: ASC + Planet1 - Planet2 (modulo 360)
    # Most reverse by sect (day/night), except Part of Exaltation (fixed formula)
    #
    # CORE PARTS (Phase 1):
    #   1. Fortune:   Day: ASC + Moon - Sun      | Night: ASC + Sun - Moon
    #   2. Spirit:    Day: ASC + Sun - Moon      | Night: ASC + Moon - Sun
    #   3. Eros:      Day: ASC + Venus - Spirit  | Night: ASC + Spirit - Venus
    #   4. Necessity: Day: ASC + Fortune - Mercury | Night: ASC + Mercury - Fortune
    #
    # EXTENDED PARTS (Phase 2 - Issue #110):
    #   5. Marriage:   Day: ASC + Venus - Saturn  | Night: ASC + Saturn - Venus
    #   6. Victory:    Day: ASC + Jupiter - Fortune | Night: ASC + Fortune - Jupiter
    #   7. Father:     Day: ASC + Sun - Saturn    | Night: ASC + Saturn - Sun
    #   8. Mother:     Day: ASC + Moon - Venus    | Night: ASC + Venus - Moon
    #   9. Children:   Day: ASC + Jupiter - Moon  | Night: ASC + Moon - Jupiter
    #  10. Exaltation: ASC + 19° (Sun's exaltation) - Sun  [FIXED - no reversal]
    #  11. Illness:    Day: ASC + Mars - Saturn   | Night: ASC + Saturn - Mars
    #  12. Courage:    Day: ASC + Fortune - Mars  | Night: ASC + Mars - Fortune
    #  13. Reputation: Day: ASC + Fortune - Spirit | Night: ASC + Spirit - Fortune
    #
    # References:
    #   - Vettius Valens, Anthology
    #   - Firmicus Maternus, Mathesis
    #   - Al-Biruni, Book of Instruction
    # ═══════════════════════════════════════════════════════════════════════════════

    # 1. Part of Fortune (Lote da Fortuna)
    # Most important Arabic Part - body, health, material wealth
    # Diurnal: Asc + Moon - Sun
    # Nocturnal: Asc + Sun - Moon
    if is_diurnal:
        fortune_lon = (ascendant + moon_longitude - sun_longitude) % 360
    else:
        fortune_lon = (ascendant + sun_longitude - moon_longitude) % 360

    parts["fortune"] = {
        "longitude": fortune_lon,
        "sign": get_sign(fortune_lon),
        "degree": fortune_lon % 30,
        "house": get_house_for_position(fortune_lon, house_cusps),
    }

    # 2. Part of Spirit (Lote do Espírito)
    # Mind, action, initiative - inverse of Fortune
    # Diurnal: Asc + Sun - Moon
    # Nocturnal: Asc + Moon - Sun
    if is_diurnal:
        spirit_lon = (ascendant + sun_longitude - moon_longitude) % 360
    else:
        spirit_lon = (ascendant + moon_longitude - sun_longitude) % 360

    parts["spirit"] = {
        "longitude": spirit_lon,
        "sign": get_sign(spirit_lon),
        "degree": spirit_lon % 30,
        "house": get_house_for_position(spirit_lon, house_cusps),
    }

    # 3. Part of Eros (Lote de Eros)
    # Love, desire, passion
    # Diurnal: Asc + Venus - Spirit
    # Nocturnal: Asc + Spirit - Venus
    venus_lon = get_planet_long("Venus")
    if is_diurnal:
        eros_lon = (ascendant + venus_lon - spirit_lon) % 360
    else:
        eros_lon = (ascendant + spirit_lon - venus_lon) % 360

    parts["eros"] = {
        "longitude": eros_lon,
        "sign": get_sign(eros_lon),
        "degree": eros_lon % 30,
        "house": get_house_for_position(eros_lon, house_cusps),
    }

    # 4. Part of Necessity (Lote da Necessidade)
    # Restrictions, karma, destiny
    # Diurnal: Asc + Fortune - Mercury
    # Nocturnal: Asc + Mercury - Fortune
    mercury_lon = get_planet_long("Mercury")
    if is_diurnal:
        necessity_lon = (ascendant + fortune_lon - mercury_lon) % 360
    else:
        necessity_lon = (ascendant + mercury_lon - fortune_lon) % 360

    parts["necessity"] = {
        "longitude": necessity_lon,
        "sign": get_sign(necessity_lon),
        "degree": necessity_lon % 30,
        "house": get_house_for_position(necessity_lon, house_cusps),
    }

    # Additional Arabic Parts (Issue #110 - Phase 2)
    # Get additional planet longitudes
    saturn_lon = get_planet_long("Saturn")
    mars_lon = get_planet_long("Mars")
    jupiter_lon = get_planet_long("Jupiter")

    # 5. Part of Marriage (Lote do Casamento)
    # Relationships, partnerships, matrimony
    # Diurnal: Asc + Venus - Saturn
    # Nocturnal: Asc + Saturn - Venus
    if is_diurnal:
        marriage_lon = (ascendant + venus_lon - saturn_lon) % 360
    else:
        marriage_lon = (ascendant + saturn_lon - venus_lon) % 360

    parts["marriage"] = {
        "longitude": marriage_lon,
        "sign": get_sign(marriage_lon),
        "degree": marriage_lon % 30,
        "house": get_house_for_position(marriage_lon, house_cusps),
    }

    # 6. Part of Victory (Lote da Vitória)
    # Success, triumph, achievement
    # Diurnal: Asc + Jupiter - Fortune
    # Nocturnal: Asc + Fortune - Jupiter
    if is_diurnal:
        victory_lon = (ascendant + jupiter_lon - fortune_lon) % 360
    else:
        victory_lon = (ascendant + fortune_lon - jupiter_lon) % 360

    parts["victory"] = {
        "longitude": victory_lon,
        "sign": get_sign(victory_lon),
        "degree": victory_lon % 30,
        "house": get_house_for_position(victory_lon, house_cusps),
    }

    # 7. Part of Father (Lote do Pai)
    # Paternal figure, authority, guidance
    # Diurnal: Asc + Sun - Saturn
    # Nocturnal: Asc + Saturn - Sun
    if is_diurnal:
        father_lon = (ascendant + sun_longitude - saturn_lon) % 360
    else:
        father_lon = (ascendant + saturn_lon - sun_longitude) % 360

    parts["father"] = {
        "longitude": father_lon,
        "sign": get_sign(father_lon),
        "degree": father_lon % 30,
        "house": get_house_for_position(father_lon, house_cusps),
    }

    # 8. Part of Mother (Lote da Mãe)
    # Maternal figure, nurturing, roots
    # Diurnal: Asc + Moon - Venus
    # Nocturnal: Asc + Venus - Moon
    if is_diurnal:
        mother_lon = (ascendant + moon_longitude - venus_lon) % 360
    else:
        mother_lon = (ascendant + venus_lon - moon_longitude) % 360

    parts["mother"] = {
        "longitude": mother_lon,
        "sign": get_sign(mother_lon),
        "degree": mother_lon % 30,
        "house": get_house_for_position(mother_lon, house_cusps),
    }

    # 9. Part of Children (Lote dos Filhos)
    # Offspring, creativity, fertility
    # Diurnal: Asc + Jupiter - Moon
    # Nocturnal: Asc + Moon - Jupiter
    if is_diurnal:
        children_lon = (ascendant + jupiter_lon - moon_longitude) % 360
    else:
        children_lon = (ascendant + moon_longitude - jupiter_lon) % 360

    parts["children"] = {
        "longitude": children_lon,
        "sign": get_sign(children_lon),
        "degree": children_lon % 30,
        "house": get_house_for_position(children_lon, house_cusps),
    }

    # 10. Part of Exaltation (Lote da Exaltação)
    # Honor, recognition, elevation
    # FIXED FORMULA (does not reverse by sect): Asc + 19° Aries - Sun
    # 19° Aries = Sun's exaltation degree (absolute longitude 19.0)
    SUN_EXALTATION_DEGREE = 19.0
    exaltation_lon = (ascendant + SUN_EXALTATION_DEGREE - sun_longitude) % 360

    parts["exaltation"] = {
        "longitude": exaltation_lon,
        "sign": get_sign(exaltation_lon),
        "degree": exaltation_lon % 30,
        "house": get_house_for_position(exaltation_lon, house_cusps),
    }

    # 11. Part of Illness (Lote da Doença)
    # Health challenges, vulnerabilities
    # Diurnal: Asc + Mars - Saturn
    # Nocturnal: Asc + Saturn - Mars
    if is_diurnal:
        illness_lon = (ascendant + mars_lon - saturn_lon) % 360
    else:
        illness_lon = (ascendant + saturn_lon - mars_lon) % 360

    parts["illness"] = {
        "longitude": illness_lon,
        "sign": get_sign(illness_lon),
        "degree": illness_lon % 30,
        "house": get_house_for_position(illness_lon, house_cusps),
    }

    # 12. Part of Courage (Lote da Coragem)
    # Bravery, boldness, initiative
    # Diurnal: Asc + Fortune - Mars
    # Nocturnal: Asc + Mars - Fortune
    if is_diurnal:
        courage_lon = (ascendant + fortune_lon - mars_lon) % 360
    else:
        courage_lon = (ascendant + mars_lon - fortune_lon) % 360

    parts["courage"] = {
        "longitude": courage_lon,
        "sign": get_sign(courage_lon),
        "degree": courage_lon % 30,
        "house": get_house_for_position(courage_lon, house_cusps),
    }

    # 13. Part of Reputation (Lote da Reputação)
    # Fame, public image, social standing
    # Diurnal: Asc + Fortune - Spirit
    # Nocturnal: Asc + Spirit - Fortune
    if is_diurnal:
        reputation_lon = (ascendant + fortune_lon - spirit_lon) % 360
    else:
        reputation_lon = (ascendant + spirit_lon - fortune_lon) % 360

    parts["reputation"] = {
        "longitude": reputation_lon,
        "sign": get_sign(reputation_lon),
        "degree": reputation_lon % 30,
        "house": get_house_for_position(reputation_lon, house_cusps),
    }

    return parts


def calculate_birth_chart(
    birth_datetime: datetime,
    timezone: str,
    latitude: float,
    longitude: float,
    house_system: str = "placidus",
    language: str = "pt-BR",
) -> dict[str, Any]:
    """
    Calculate complete birth chart.

    Args:
        birth_datetime: Birth date and time
        timezone: Timezone string
        latitude: Geographic latitude
        longitude: Geographic longitude
        house_system: House system to use
        language: Language for interpretations ('pt-BR' or 'en-US')

    Returns:
        Complete chart data dictionary
    """
    # Convert to Julian Day
    jd = convert_to_julian_day(birth_datetime, timezone, latitude, longitude)

    # Calculate houses and angles
    houses, ascendant, midheaven = calculate_houses(jd, latitude, longitude, house_system)

    # Get house cusps for planet calculations
    house_cusps = [h.longitude for h in houses]

    # Calculate planet positions
    planets = calculate_planets(jd, house_cusps)

    # Find Sun and Moon for sect, lunar phase and solar phase
    sun_longitude = 0.0
    sun_sign = ""
    moon_longitude = 0.0
    for planet in planets:
        if planet.name == "Sun":
            sun_longitude = planet.longitude
            sun_sign = planet.sign
        elif planet.name == "Moon":
            moon_longitude = planet.longitude

    # Calculate sect (day/night chart)
    sect = calculate_sect(ascendant, sun_longitude)

    # Calculate lunar phase
    lunar_phase = calculate_lunar_phase(sun_longitude, moon_longitude, language)

    # Calculate solar phase
    solar_phase = calculate_solar_phase(sun_sign, language)

    # Add essential dignities to each planet
    planets_with_dignities = []
    for planet in planets:
        planet_dict = planet.model_dump()
        # Only calculate dignities for classical 7 planets
        if planet.name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            dignities = calculate_essential_dignities(planet.name, planet.sign, planet.degree, sect)
            planet_dict["dignities"] = dignities
        planets_with_dignities.append(planet_dict)

    # Calculate aspects
    aspects = calculate_aspects(planets)

    # Find Lord of Nativity (planet with highest essential dignity score)
    lord_of_nativity = find_lord_of_nativity(planets_with_dignities, language)

    # Calculate Temperament based on 5 traditional factors
    # Get ascendant sign
    ascendant_sign_data = get_sign_and_position(ascendant)
    ascendant_sign = ascendant_sign_data["sign"]

    # Get ascendant ruler, its sign, and dignities
    ascendant_ruler_name = get_sign_ruler(ascendant_sign) or "Sun"
    ascendant_ruler_data = next(
        (p for p in planets_with_dignities if p.get("name") == ascendant_ruler_name), None
    )
    ascendant_ruler_sign = (
        ascendant_ruler_data.get("sign", ascendant_sign) if ascendant_ruler_data else ascendant_sign
    )
    ascendant_ruler_dignities = (
        ascendant_ruler_data.get("dignities", {}).get("dignities")
        if ascendant_ruler_data and ascendant_ruler_data.get("dignities")
        else None
    )

    # Get lord of nativity, its sign, and dignities
    lord_of_nativity_name = lord_of_nativity["planet_key"] if lord_of_nativity else "Sun"
    lord_of_nativity_data = next(
        (p for p in planets_with_dignities if p.get("name") == lord_of_nativity_name), None
    )
    lord_of_nativity_sign = (
        lord_of_nativity_data.get("sign", "Aries") if lord_of_nativity_data else "Aries"
    )
    lord_of_nativity_dignities = (
        lord_of_nativity_data.get("dignities", {}).get("dignities")
        if lord_of_nativity_data and lord_of_nativity_data.get("dignities")
        else None
    )

    temperament = calculate_temperament(
        ascendant_sign=ascendant_sign,
        ascendant_ruler_name=ascendant_ruler_name,
        ascendant_ruler_sign=ascendant_ruler_sign,
        sun_sign=sun_sign,
        sun_longitude=sun_longitude,
        moon_longitude=moon_longitude,
        lord_of_nativity_name=lord_of_nativity_name,
        lord_of_nativity_sign=lord_of_nativity_sign,
        ascendant_ruler_dignities=ascendant_ruler_dignities,
        lord_of_nativity_dignities=lord_of_nativity_dignities,
        language=language,
    )

    # Calculate Arabic Parts (Lots)
    arabic_parts = calculate_arabic_parts(
        ascendant=ascendant,
        sun_longitude=sun_longitude,
        moon_longitude=moon_longitude,
        planets=planets,
        house_cusps=house_cusps,
        sect=sect,
    )

    # Calculate complete sect analysis with planet classifications
    sect_analysis = calculate_sect_analysis(planets_with_dignities, sect)

    return {
        "planets": planets_with_dignities,
        "houses": [h.model_dump() for h in houses],
        "aspects": [a.model_dump() for a in aspects],
        "ascendant": ascendant,
        "midheaven": midheaven,
        "sect": sect,
        "sect_analysis": sect_analysis,
        "lunar_phase": lunar_phase,
        "solar_phase": solar_phase,
        "lord_of_nativity": lord_of_nativity,
        "temperament": temperament,
        "arabic_parts": arabic_parts,
        "calculation_timestamp": datetime.now(UTC).isoformat(),
    }
