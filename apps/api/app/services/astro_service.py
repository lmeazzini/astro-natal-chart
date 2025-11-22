"""
Astrological calculation service using Swiss Ephemeris (PySwisseph).
"""

from datetime import datetime
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

    # Check if Sun is between Ascendant and Descendant (going through MC)
    # This determines if Sun is above horizon (day chart)
    if ascendant < descendant:
        # Normal case: ASC is at smaller degree than DSC
        is_day_chart = ascendant <= sun_lon <= descendant
    else:
        # Wrapped case: ASC crosses 0° Aries
        is_day_chart = sun_lon >= ascendant or sun_lon <= descendant

    return "diurnal" if is_day_chart else "nocturnal"


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

    return parts


def calculate_birth_chart(
    birth_datetime: datetime,
    timezone: str,
    latitude: float,
    longitude: float,
    house_system: str = "placidus",
) -> dict[str, Any]:
    """
    Calculate complete birth chart.

    Args:
        birth_datetime: Birth date and time
        timezone: Timezone string
        latitude: Geographic latitude
        longitude: Geographic longitude
        house_system: House system to use

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
    lunar_phase = calculate_lunar_phase(sun_longitude, moon_longitude)

    # Calculate solar phase
    solar_phase = calculate_solar_phase(sun_sign)

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
    lord_of_nativity = find_lord_of_nativity(planets_with_dignities)

    # Calculate Temperament based on 5 traditional factors
    # Get ascendant sign
    ascendant_sign_data = get_sign_and_position(ascendant)
    ascendant_sign = ascendant_sign_data["sign"]

    # Get ascendant ruler and its sign
    ascendant_ruler_name = get_sign_ruler(ascendant_sign) or "Sun"
    ascendant_ruler_planet = next((p for p in planets if p.name == ascendant_ruler_name), None)
    ascendant_ruler_sign = ascendant_ruler_planet.sign if ascendant_ruler_planet else ascendant_sign

    # Get lord of nativity sign
    lord_of_nativity_name = lord_of_nativity["planet"] if lord_of_nativity else "Sun"
    lord_of_nativity_planet = next((p for p in planets if p.name == lord_of_nativity_name), None)
    lord_of_nativity_sign = lord_of_nativity_planet.sign if lord_of_nativity_planet else "Aries"

    temperament = calculate_temperament(
        ascendant_sign=ascendant_sign,
        ascendant_ruler_name=ascendant_ruler_name,
        ascendant_ruler_sign=ascendant_ruler_sign,
        sun_sign=sun_sign,
        sun_longitude=sun_longitude,
        moon_longitude=moon_longitude,
        lord_of_nativity_name=lord_of_nativity_name,
        lord_of_nativity_sign=lord_of_nativity_sign,
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

    return {
        "planets": planets_with_dignities,
        "houses": [h.model_dump() for h in houses],
        "aspects": [a.model_dump() for a in aspects],
        "ascendant": ascendant,
        "midheaven": midheaven,
        "sect": sect,
        "lunar_phase": lunar_phase,
        "solar_phase": solar_phase,
        "lord_of_nativity": lord_of_nativity,
        "temperament": temperament,
        "arabic_parts": arabic_parts,
        "calculation_timestamp": datetime.utcnow().isoformat(),
    }
