"""
Solar Return calculation module.

Calculates the exact moment when the transiting Sun returns to its natal
position, and generates a complete chart for that moment.

Solar Return occurs approximately every year on or near the birthday.
The chart is calculated for the exact moment the Sun reaches the natal
Sun's degree, minute, and second, and can be relocated to any location.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import swisseph as swe

from app.translations import DEFAULT_LANGUAGE, get_translation

# Sun's tropical year period (time to return to same ecliptic longitude)
SUN_TROPICAL_YEAR_DAYS = 365.2422

# Swiss Ephemeris planet ID
SUN = swe.SUN

# Search parameters
SEARCH_WINDOW_DAYS = 3  # ±3 days around birthday (Sun moves ~1°/day)
PRECISION_DEGREES = 0.0001  # High precision for exact moment
MAX_ITERATIONS = 100  # Maximum iterations for binary search

# Signs in order
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


@dataclass
class SolarReturnChart:
    """A Solar Return chart with all calculated data."""

    return_datetime: datetime
    return_year: int
    location: dict[str, Any]  # {lat, lon, city, country}
    natal_sun_longitude: float
    return_sun_longitude: float
    # Full chart data
    planets: list[dict[str, Any]]
    houses: list[dict[str, Any]]
    aspects: list[dict[str, Any]]
    ascendant: float
    midheaven: float
    # Additional analysis
    ascendant_sign: str
    sun_house: int


@dataclass
class SolarReturnComparison:
    """Comparison of Solar Return chart to natal chart."""

    sr_asc_in_natal_house: int
    sr_mc_in_natal_house: int
    sr_planets_in_natal_houses: dict[str, int]  # {planet_name: natal_house}
    natal_planets_in_sr_houses: dict[str, int]  # {planet_name: sr_house}
    key_aspects: list[dict[str, Any]]  # Aspects between SR and natal planets


def get_sign_from_longitude(longitude: float) -> str:
    """Get zodiac sign from ecliptic longitude."""
    sign_index = int(longitude / 30) % 12
    return SIGNS[sign_index]


def get_degree_in_sign(longitude: float) -> float:
    """Get degree within the sign (0-30)."""
    return longitude % 30


def get_sun_position(jd: float) -> tuple[float, float]:
    """
    Get Sun's position at a given Julian Day.

    Args:
        jd: Julian Day number

    Returns:
        Tuple of (longitude, speed)
    """
    result = swe.calc_ut(jd, SUN, swe.FLG_MOSEPH | swe.FLG_SPEED)
    longitude = result[0][0]  # Ecliptic longitude
    speed = result[0][3]  # Speed in longitude
    return longitude, speed


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day to datetime."""
    year, month, day, hour = swe.revjul(jd)
    # Convert fractional hour to hours, minutes, seconds
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)
    return datetime(year, month, day, hours, minutes, seconds, tzinfo=UTC)


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    # Ensure we have UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)

    # Calculate decimal hour
    hour = dt.hour + dt.minute / 60 + dt.second / 3600

    return swe.julday(dt.year, dt.month, dt.day, hour)


def normalize_longitude(lon: float) -> float:
    """Normalize longitude to 0-360 range."""
    return lon % 360


def longitude_diff(lon1: float, lon2: float) -> float:
    """
    Calculate the shortest angular difference between two longitudes.

    Returns a value in the range [-180, 180].
    """
    diff = normalize_longitude(lon1) - normalize_longitude(lon2)
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    return diff


def find_sun_return_moment(
    natal_sun_longitude: float,
    target_year: int,
    birth_month: int,
    birth_day: int,
) -> datetime:
    """
    Find the exact moment when the Sun returns to its natal position.

    Uses binary search for precision.

    Args:
        natal_sun_longitude: The natal Sun's ecliptic longitude
        target_year: The year to calculate the return for
        birth_month: Birth month (for initial estimate)
        birth_day: Birth day (for initial estimate)

    Returns:
        Datetime of the exact Sun return moment (UTC)
    """
    target = normalize_longitude(natal_sun_longitude)

    # Start search around birthday in target year
    # Handle edge cases for months with different days
    try:
        estimated_date = datetime(target_year, birth_month, birth_day, 12, 0, 0, tzinfo=UTC)
    except ValueError:
        # Handle Feb 29 for non-leap years
        estimated_date = datetime(target_year, birth_month, 28, 12, 0, 0, tzinfo=UTC)

    estimated_jd = datetime_to_jd(estimated_date)

    # Search window
    start_jd = estimated_jd - SEARCH_WINDOW_DAYS
    end_jd = estimated_jd + SEARCH_WINDOW_DAYS

    # Get starting positions
    start_lon, _ = get_sun_position(start_jd)
    end_lon, _ = get_sun_position(end_jd)

    start_diff = longitude_diff(start_lon, target)
    end_diff = longitude_diff(end_lon, target)

    # If target is near 0° Aries, we need special handling
    # because the longitude wraps around
    if abs(start_diff) < PRECISION_DEGREES:
        return jd_to_datetime(start_jd)
    if abs(end_diff) < PRECISION_DEGREES:
        return jd_to_datetime(end_jd)

    # Binary search for exact moment
    for _ in range(MAX_ITERATIONS):
        mid_jd = (start_jd + end_jd) / 2
        mid_lon, _ = get_sun_position(mid_jd)
        mid_diff = longitude_diff(mid_lon, target)

        if abs(mid_diff) < PRECISION_DEGREES:
            return jd_to_datetime(mid_jd)

        # Determine which half contains the crossing
        # Sun always moves forward (never retrograde)
        if start_diff * mid_diff <= 0:
            end_jd = mid_jd
            end_diff = mid_diff
        else:
            start_jd = mid_jd
            start_diff = mid_diff

        # Check if interval is small enough (~1 second precision)
        if abs(end_jd - start_jd) < 0.00001:
            return jd_to_datetime(mid_jd)

    return jd_to_datetime((start_jd + end_jd) / 2)


def get_planet_house(longitude: float, house_cusps: list[float]) -> int:
    """
    Determine which house a planet is in based on its longitude.

    Args:
        longitude: Planet's ecliptic longitude
        house_cusps: List of house cusp longitudes (12 houses)

    Returns:
        House number (1-12)
    """
    lon = normalize_longitude(longitude)

    for i in range(12):
        cusp = normalize_longitude(house_cusps[i])
        next_cusp = normalize_longitude(house_cusps[(i + 1) % 12])

        if cusp <= next_cusp:
            if cusp <= lon < next_cusp:
                return i + 1
        else:
            # Handle wrap-around (e.g., cusp at 350°, next at 20°)
            if lon >= cusp or lon < next_cusp:
                return i + 1

    return 1  # Default to house 1


def calculate_sr_to_natal_aspects(
    sr_planets: list[dict[str, Any]],
    natal_planets: list[dict[str, Any]],
    orb_major: float = 6.0,
    orb_minor: float = 3.0,
) -> list[dict[str, Any]]:
    """
    Calculate aspects between Solar Return planets and natal planets.

    Args:
        sr_planets: List of SR planet dictionaries
        natal_planets: List of natal planet dictionaries
        orb_major: Orb for major aspects
        orb_minor: Orb for minor aspects

    Returns:
        List of aspect dictionaries
    """
    aspects = []

    # Aspect definitions: (name, angle, is_major)
    # Sorted by angle for efficient range checking
    aspect_defs = [
        ("Conjunction", 0, True),
        ("Sextile", 60, True),
        ("Square", 90, True),
        ("Trine", 120, True),
        ("Quincunx", 150, False),
        ("Opposition", 180, True),
    ]

    # Pre-filter planets to skip (more efficient than checking in inner loop)
    skip_points = {"North Node", "South Node"}

    # Pre-calculate max orb for early exit optimization
    max_orb = max(orb_major, orb_minor)

    for sr_planet in sr_planets:
        sr_name = sr_planet.get("name", "")
        if sr_name in skip_points:
            continue

        sr_lon = sr_planet.get("longitude", 0)

        for natal_planet in natal_planets:
            natal_name = natal_planet.get("name", "")
            if natal_name in skip_points:
                continue

            natal_lon = natal_planet.get("longitude", 0)

            # Calculate angular difference once per planet pair
            diff = abs(longitude_diff(sr_lon, natal_lon))

            # Early exit: if diff is far from any aspect angle, skip all checks
            # Valid aspect angles are 0, 60, 90, 120, 150, 180
            # Check if diff is within max_orb of any of these
            if not (
                diff <= max_orb  # Near conjunction (0°)
                or 60 - max_orb <= diff <= 60 + max_orb  # Near sextile
                or 90 - max_orb <= diff <= 90 + max_orb  # Near square
                or 120 - max_orb <= diff <= 120 + max_orb  # Near trine
                or 150 - max_orb <= diff <= 150 + max_orb  # Near quincunx
                or diff >= 180 - max_orb  # Near opposition
            ):
                continue

            # Check each aspect (only reached if diff is potentially valid)
            for aspect_name, aspect_angle, is_major in aspect_defs:
                orb = orb_major if is_major else orb_minor
                orb_diff = abs(diff - aspect_angle)

                if orb_diff <= orb:
                    aspects.append(
                        {
                            "sr_planet": sr_name,
                            "natal_planet": natal_name,
                            "aspect": aspect_name,
                            "angle": aspect_angle,
                            "orb": round(orb_diff, 2),
                            "is_major": is_major,
                        }
                    )

    # Sort by orb (tightest aspects first)
    aspects.sort(key=lambda a: a["orb"])

    return aspects


def calculate_solar_return(
    natal_sun_longitude: float,
    birth_datetime: datetime,
    target_year: int,
    latitude: float,
    longitude: float,
    timezone: str,
    city: str = "",
    country: str = "",
    house_system: str = "placidus",
    natal_chart_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate a complete Solar Return chart.

    Args:
        natal_sun_longitude: Natal Sun's ecliptic longitude
        birth_datetime: Original birth datetime
        target_year: Year to calculate SR for
        latitude: Location latitude for SR chart
        longitude: Location longitude for SR chart
        timezone: Timezone for the location
        city: City name (optional)
        country: Country name (optional)
        house_system: House system to use
        natal_chart_data: Original natal chart data for comparison (optional)

    Returns:
        Complete Solar Return data including chart and comparison
    """
    # Find exact return moment
    return_datetime = find_sun_return_moment(
        natal_sun_longitude,
        target_year,
        birth_datetime.month,
        birth_datetime.day,
    )

    # Import here to avoid circular imports
    from app.services.astro_service import (
        calculate_aspects,
        calculate_houses,
        calculate_planets,
        convert_to_julian_day,
    )

    # Calculate SR chart at the specified location
    sr_jd = convert_to_julian_day(return_datetime, timezone, latitude, longitude)

    # Calculate houses
    houses, ascendant, midheaven = calculate_houses(sr_jd, latitude, longitude, house_system)
    house_cusps = [h.longitude for h in houses]

    # Calculate planets
    planets = calculate_planets(sr_jd, house_cusps)

    # Convert to dictionaries
    planets_data = [p.model_dump() for p in planets]
    houses_data = [h.model_dump() for h in houses]

    # Calculate aspects
    aspects = calculate_aspects(planets)
    aspects_data = [a.model_dump() for a in aspects]

    # Get Sun's house in SR chart
    sun_house = 1
    for planet in planets_data:
        if planet.get("name") == "Sun":
            sun_house = planet.get("house", 1)
            break

    # Get ascendant sign
    ascendant_sign = get_sign_from_longitude(ascendant)

    # Build chart data
    chart_data = {
        "return_datetime": return_datetime.isoformat(),
        "return_year": target_year,
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "country": country,
            "timezone": timezone,
        },
        "natal_sun_longitude": round(natal_sun_longitude, 4),
        "return_sun_longitude": round(natal_sun_longitude, 4),  # Same as natal
        "planets": planets_data,
        "houses": houses_data,
        "aspects": aspects_data,
        "ascendant": round(ascendant, 4),
        "ascendant_sign": ascendant_sign,
        "ascendant_degree": round(get_degree_in_sign(ascendant), 2),
        "midheaven": round(midheaven, 4),
        "midheaven_sign": get_sign_from_longitude(midheaven),
        "midheaven_degree": round(get_degree_in_sign(midheaven), 2),
        "sun_house": sun_house,
    }

    # Calculate comparison if natal chart data is provided
    comparison = None
    if natal_chart_data:
        comparison = calculate_comparison(chart_data, natal_chart_data)

    return {
        "chart": chart_data,
        "comparison": comparison,
    }


def calculate_comparison(
    sr_chart: dict[str, Any],
    natal_chart: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate comparison between Solar Return and natal chart.

    Args:
        sr_chart: Solar Return chart data
        natal_chart: Natal chart data

    Returns:
        Comparison data
    """
    natal_houses = natal_chart.get("houses", [])
    natal_planets = natal_chart.get("planets", [])
    sr_planets = sr_chart.get("planets", [])
    sr_houses = sr_chart.get("houses", [])

    # Get house cusps
    natal_cusps = [h.get("cusp", h.get("longitude", 0)) for h in natal_houses]
    sr_cusps = [h.get("cusp", h.get("longitude", 0)) for h in sr_houses]

    # SR Ascendant in natal house
    sr_asc = sr_chart.get("ascendant", 0)
    sr_asc_in_natal_house = get_planet_house(sr_asc, natal_cusps)

    # SR MC in natal house
    sr_mc = sr_chart.get("midheaven", 0)
    sr_mc_in_natal_house = get_planet_house(sr_mc, natal_cusps)

    # SR planets in natal houses
    sr_planets_in_natal = {}
    for planet in sr_planets:
        name = planet.get("name", "")
        lon = planet.get("longitude", 0)
        if name and name not in ["North Node", "South Node"]:
            sr_planets_in_natal[name] = get_planet_house(lon, natal_cusps)

    # Natal planets in SR houses
    natal_planets_in_sr = {}
    for planet in natal_planets:
        name = planet.get("name", "")
        lon = planet.get("longitude", 0)
        if name and name not in ["North Node", "South Node"]:
            natal_planets_in_sr[name] = get_planet_house(lon, sr_cusps)

    # Calculate cross-chart aspects
    key_aspects = calculate_sr_to_natal_aspects(sr_planets, natal_planets)

    return {
        "sr_asc_in_natal_house": sr_asc_in_natal_house,
        "sr_mc_in_natal_house": sr_mc_in_natal_house,
        "sr_planets_in_natal_houses": sr_planets_in_natal,
        "natal_planets_in_sr_houses": natal_planets_in_sr,
        "key_aspects": key_aspects[:10],  # Top 10 tightest aspects
    }


def get_solar_return_interpretation(
    sr_ascendant_sign: str,
    sr_sun_house: int,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Get Solar Return interpretation based on ascendant sign and Sun house.

    Args:
        sr_ascendant_sign: Solar Return ascendant sign
        sr_sun_house: House where SR Sun is placed
        language: Language for translations

    Returns:
        Dictionary with interpretations
    """
    sign_key = sr_ascendant_sign.lower()
    house_key = str(sr_sun_house)

    # Get translations
    title = get_translation("solar_return.title", language)
    general_intro = get_translation("solar_return.general.intro", language)
    general_interpretation = get_translation("solar_return.general.yearly_themes", language)

    # Get ascendant sign interpretation
    ascendant_interpretation = get_translation(f"solar_return.ascendant.{sign_key}", language)

    # Get Sun house interpretation
    sun_house_interpretation = get_translation(f"solar_return.sun_house.{house_key}", language)

    return {
        "title": title,
        "sr_ascendant_sign": sr_ascendant_sign,
        "sr_sun_house": sr_sun_house,
        "general_introduction": general_intro,
        "general_interpretation": general_interpretation,
        "ascendant_interpretation": ascendant_interpretation,
        "sun_house_interpretation": sun_house_interpretation,
    }


def calculate_multiple_solar_returns(
    natal_sun_longitude: float,
    birth_datetime: datetime,
    start_year: int,
    end_year: int,
    latitude: float,
    longitude: float,
    timezone: str,
    city: str = "",
    country: str = "",
    house_system: str = "placidus",
) -> list[dict[str, Any]]:
    """
    Calculate Solar Returns for multiple years.

    Args:
        natal_sun_longitude: Natal Sun's ecliptic longitude
        birth_datetime: Original birth datetime
        start_year: First year to calculate
        end_year: Last year to calculate
        latitude: Location latitude
        longitude: Location longitude
        timezone: Timezone
        city: City name
        country: Country name
        house_system: House system

    Returns:
        List of Solar Return data for each year
    """
    returns = []

    for year in range(start_year, end_year + 1):
        sr_data = calculate_solar_return(
            natal_sun_longitude=natal_sun_longitude,
            birth_datetime=birth_datetime,
            target_year=year,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            city=city,
            country=country,
            house_system=house_system,
        )
        returns.append(sr_data)

    return returns
