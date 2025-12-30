"""
Saturn Return calculation module.

Calculates when transiting Saturn returns to its natal position,
identifying all passes including retrograde crossings.

Saturn Return occurs approximately every 29.457 years (sidereal period).
Due to retrograde motion, Saturn typically crosses the natal position
3 times during each return:
1. First pass (direct motion)
2. Second pass (retrograde motion)
3. Third pass (direct motion again)
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import swisseph as swe

from app.translations import DEFAULT_LANGUAGE, get_translation

# Saturn's sidereal period
SATURN_SIDEREAL_PERIOD_DAYS = 10759.22
SATURN_SIDEREAL_PERIOD_YEARS = 29.457

# Swiss Ephemeris planet ID
SATURN = swe.SATURN

# Search parameters
SEARCH_WINDOW_DAYS = 200  # ±200 days around estimated return
PRECISION_DEGREES = 0.001  # Precision for binary search (0.001°)
MAX_ITERATIONS = 100  # Maximum iterations for binary search
MIN_PASS_SEPARATION_DAYS = 30  # Minimum days between passes to avoid duplicates

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
class SaturnReturnPass:
    """A single pass of Saturn over the natal position."""

    date: datetime
    longitude: float
    is_retrograde: bool
    pass_number: int  # 1, 2, or 3


@dataclass
class SaturnReturn:
    """A complete Saturn Return event (all passes)."""

    return_number: int  # 1st, 2nd, 3rd return
    passes: list[SaturnReturnPass]
    start_date: datetime  # First pass
    end_date: datetime  # Last pass
    age_at_return: float  # Age at first pass


@dataclass
class SaturnReturnAnalysis:
    """Complete Saturn Return analysis."""

    natal_saturn_longitude: float
    natal_saturn_sign: str
    natal_saturn_house: int
    current_saturn_longitude: float
    current_saturn_sign: str
    cycle_progress_percent: float
    days_until_next_return: int | None
    past_returns: list[SaturnReturn]
    current_return: SaturnReturn | None
    next_return: SaturnReturn | None


def get_sign_from_longitude(longitude: float) -> str:
    """Get zodiac sign from ecliptic longitude."""
    sign_index = int(longitude / 30) % 12
    return SIGNS[sign_index]


def get_degree_in_sign(longitude: float) -> float:
    """Get degree within the sign (0-30)."""
    return longitude % 30


def get_saturn_position(jd: float) -> tuple[float, float, bool]:
    """
    Get Saturn's position at a given Julian Day.

    Args:
        jd: Julian Day number

    Returns:
        Tuple of (longitude, speed, is_retrograde)
    """
    result = swe.calc_ut(jd, SATURN, swe.FLG_MOSEPH | swe.FLG_SPEED)
    longitude = result[0][0]  # Ecliptic longitude
    speed = result[0][3]  # Speed in longitude
    is_retrograde = speed < 0
    return longitude, speed, is_retrograde


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


def find_exact_crossing(
    target_longitude: float,
    start_jd: float,
    end_jd: float,
) -> float | None:
    """
    Find the exact Julian Day when Saturn crosses the target longitude.

    Uses binary search for precision.

    Args:
        target_longitude: The target ecliptic longitude
        start_jd: Start of search window (Julian Day)
        end_jd: End of search window (Julian Day)

    Returns:
        Julian Day of crossing, or None if not found
    """
    target = normalize_longitude(target_longitude)

    # Get starting positions
    start_lon, _, _ = get_saturn_position(start_jd)
    end_lon, _, _ = get_saturn_position(end_jd)

    start_diff = longitude_diff(start_lon, target)
    end_diff = longitude_diff(end_lon, target)

    # Check if there's a crossing in this interval
    # A crossing occurs if the signs of the differences are different
    # OR if one of them is very close to zero
    if abs(start_diff) < PRECISION_DEGREES:
        return start_jd
    if abs(end_diff) < PRECISION_DEGREES:
        return end_jd

    # If both have the same sign and neither is close, no crossing
    if start_diff * end_diff > 0:
        return None

    # Binary search
    for _ in range(MAX_ITERATIONS):
        mid_jd = (start_jd + end_jd) / 2
        mid_lon, _, _ = get_saturn_position(mid_jd)
        mid_diff = longitude_diff(mid_lon, target)

        if abs(mid_diff) < PRECISION_DEGREES:
            return mid_jd

        # Determine which half contains the crossing
        if start_diff * mid_diff <= 0:
            end_jd = mid_jd
            end_diff = mid_diff
        else:
            start_jd = mid_jd
            start_diff = mid_diff

        # Check if interval is small enough
        if abs(end_jd - start_jd) < 0.0001:  # About 8 seconds precision
            return mid_jd

    return (start_jd + end_jd) / 2


def find_saturn_return_passes(
    target_longitude: float,
    approximate_jd: float,
    search_window_days: int = SEARCH_WINDOW_DAYS,
) -> list[SaturnReturnPass]:
    """
    Find all passes of a Saturn Return.

    Saturn typically makes 3 passes over the natal position during a return
    due to retrograde motion.

    Args:
        target_longitude: Natal Saturn longitude
        approximate_jd: Approximate Julian Day of return
        search_window_days: Days to search before/after approximate date

    Returns:
        List of SaturnReturnPass objects (1-3 passes)
    """
    passes: list[SaturnReturnPass] = []
    target = normalize_longitude(target_longitude)

    # Search window
    start_jd = approximate_jd - search_window_days
    end_jd = approximate_jd + search_window_days

    # Scan through the window in small steps to find all crossings
    step_days = 1.0  # 1 day steps
    current_jd = start_jd

    prev_lon, _, _ = get_saturn_position(current_jd)
    prev_diff = longitude_diff(prev_lon, target)

    while current_jd < end_jd:
        next_jd = current_jd + step_days
        curr_lon, _, _ = get_saturn_position(next_jd)
        curr_diff = longitude_diff(curr_lon, target)

        # Check for crossing (sign change or very close)
        if prev_diff * curr_diff < 0 or abs(curr_diff) < PRECISION_DEGREES:
            # Found potential crossing, refine with binary search
            exact_jd = find_exact_crossing(target, current_jd, next_jd)
            if exact_jd:
                exact_lon, _, is_retro = get_saturn_position(exact_jd)

                # Avoid duplicate passes (within MIN_PASS_SEPARATION_DAYS of each other)
                is_duplicate = False
                for existing_pass in passes:
                    existing_jd = datetime_to_jd(existing_pass.date)
                    if abs(exact_jd - existing_jd) < MIN_PASS_SEPARATION_DAYS:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    passes.append(
                        SaturnReturnPass(
                            date=jd_to_datetime(exact_jd),
                            longitude=round(exact_lon, 4),
                            is_retrograde=is_retro,
                            pass_number=len(passes) + 1,
                        )
                    )

        prev_diff = curr_diff
        current_jd = next_jd

    # Sort passes by date
    passes.sort(key=lambda p: p.date)

    # Renumber passes
    for i, p in enumerate(passes):
        p.pass_number = i + 1

    return passes


def calculate_saturn_returns(
    birth_jd: float,
    natal_saturn_longitude: float,
    current_jd: float | None = None,
    num_returns: int = 3,
) -> tuple[list[SaturnReturn], SaturnReturn | None, SaturnReturn | None]:
    """
    Calculate all Saturn Returns for a chart.

    Args:
        birth_jd: Julian Day of birth
        natal_saturn_longitude: Natal Saturn longitude
        current_jd: Current Julian Day (defaults to now)
        num_returns: Number of returns to calculate (default 3)

    Returns:
        Tuple of (past_returns, current_return, next_return)
    """
    if current_jd is None:
        current_jd = datetime_to_jd(datetime.now(UTC))

    past_returns: list[SaturnReturn] = []
    current_return: SaturnReturn | None = None
    next_return: SaturnReturn | None = None

    for return_num in range(1, num_returns + 1):
        # Estimate approximate return date
        approximate_jd = birth_jd + (return_num * SATURN_SIDEREAL_PERIOD_DAYS)

        # Find all passes for this return
        passes = find_saturn_return_passes(natal_saturn_longitude, approximate_jd)

        if not passes:
            continue

        # Calculate age at return
        age_at_return = (passes[0].date.timestamp() - jd_to_datetime(birth_jd).timestamp()) / (
            365.25 * 24 * 3600
        )

        saturn_return = SaturnReturn(
            return_number=return_num,
            passes=passes,
            start_date=passes[0].date,
            end_date=passes[-1].date,
            age_at_return=round(age_at_return, 1),
        )

        # Categorize as past, current, or next
        first_pass_jd = datetime_to_jd(passes[0].date)
        last_pass_jd = datetime_to_jd(passes[-1].date)

        if last_pass_jd < current_jd:
            # Completely in the past
            past_returns.append(saturn_return)
        elif first_pass_jd <= current_jd <= last_pass_jd:
            # Currently happening
            current_return = saturn_return
        elif first_pass_jd > current_jd and next_return is None:
            # First future return
            next_return = saturn_return

    return past_returns, current_return, next_return


def calculate_cycle_progress(
    birth_jd: float,
    natal_saturn_longitude: float,
    current_jd: float | None = None,
) -> tuple[float, int | None]:
    """
    Calculate the progress through the current Saturn cycle.

    Args:
        birth_jd: Julian Day of birth
        natal_saturn_longitude: Natal Saturn longitude
        current_jd: Current Julian Day (defaults to now)

    Returns:
        Tuple of (cycle_progress_percent, days_until_next_return)
    """
    if current_jd is None:
        current_jd = datetime_to_jd(datetime.now(UTC))

    # Find the most recent return (or birth if no return yet)
    last_return_jd = birth_jd

    for return_num in range(1, 4):  # Check up to 3 returns
        approximate_jd = birth_jd + (return_num * SATURN_SIDEREAL_PERIOD_DAYS)
        passes = find_saturn_return_passes(natal_saturn_longitude, approximate_jd)

        if passes:
            last_pass_jd = datetime_to_jd(passes[-1].date)
            if last_pass_jd < current_jd:
                last_return_jd = last_pass_jd
            else:
                break

    # Calculate progress through current cycle
    days_since_last = current_jd - last_return_jd
    progress = (days_since_last / SATURN_SIDEREAL_PERIOD_DAYS) * 100
    progress = min(100, max(0, progress))  # Clamp to 0-100

    # Calculate days until next return
    next_return_jd = last_return_jd + SATURN_SIDEREAL_PERIOD_DAYS
    days_until_next = int(next_return_jd - current_jd)

    if days_until_next < 0:
        days_until_next = None

    return round(progress, 1), days_until_next


def calculate_saturn_return_analysis(
    birth_jd: float,
    natal_saturn_longitude: float,
    natal_saturn_house: int,
    current_jd: float | None = None,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Calculate complete Saturn Return analysis.

    Args:
        birth_jd: Julian Day of birth
        natal_saturn_longitude: Natal Saturn longitude
        natal_saturn_house: House where natal Saturn is placed
        current_jd: Current Julian Day (defaults to now)
        language: Language for translations

    Returns:
        Dictionary with complete Saturn Return analysis
    """
    if current_jd is None:
        current_jd = datetime_to_jd(datetime.now(UTC))

    # Get current Saturn position
    current_saturn_lon, _, _ = get_saturn_position(current_jd)
    current_saturn_sign = get_sign_from_longitude(current_saturn_lon)

    # Get natal Saturn sign
    natal_saturn_sign = get_sign_from_longitude(natal_saturn_longitude)

    # Calculate returns
    past_returns, current_return, next_return = calculate_saturn_returns(
        birth_jd, natal_saturn_longitude, current_jd
    )

    # Calculate cycle progress
    cycle_progress, days_until_next = calculate_cycle_progress(
        birth_jd, natal_saturn_longitude, current_jd
    )

    # Convert to serializable format
    def serialize_pass(p: SaturnReturnPass) -> dict[str, Any]:
        return {
            "date": p.date.isoformat(),
            "longitude": p.longitude,
            "is_retrograde": p.is_retrograde,
            "pass_number": p.pass_number,
        }

    def serialize_return(r: SaturnReturn) -> dict[str, Any]:
        return {
            "return_number": r.return_number,
            "passes": [serialize_pass(p) for p in r.passes],
            "start_date": r.start_date.isoformat(),
            "end_date": r.end_date.isoformat(),
            "age_at_return": r.age_at_return,
        }

    return {
        "natal_saturn_longitude": round(natal_saturn_longitude, 4),
        "natal_saturn_sign": natal_saturn_sign,
        "natal_saturn_house": natal_saturn_house,
        "natal_saturn_degree": round(get_degree_in_sign(natal_saturn_longitude), 2),
        "current_saturn_longitude": round(current_saturn_lon, 4),
        "current_saturn_sign": current_saturn_sign,
        "cycle_progress_percent": cycle_progress,
        "days_until_next_return": days_until_next,
        "past_returns": [serialize_return(r) for r in past_returns],
        "current_return": serialize_return(current_return) if current_return else None,
        "next_return": serialize_return(next_return) if next_return else None,
    }


def get_saturn_return_interpretation(
    natal_saturn_sign: str,
    natal_saturn_house: int,
    return_number: int | None = None,
    current_phase: str | None = None,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Get Saturn Return interpretation based on sign and house.

    Args:
        natal_saturn_sign: Zodiac sign of natal Saturn
        natal_saturn_house: House of natal Saturn
        return_number: Which return (1, 2, or 3)
        current_phase: Current phase (approaching, first_pass, retrograde_pass, final_pass, post_return)
        language: Language for translations

    Returns:
        Dictionary with interpretations
    """
    sign_key = natal_saturn_sign.lower()
    house_key = str(natal_saturn_house)

    # Get translations
    title = get_translation("saturn_return.title", language)
    general_intro = get_translation("saturn_return.general.intro", language)

    # Get return-specific interpretation
    if return_number == 1:
        return_key = "first_return"
    elif return_number == 2:
        return_key = "second_return"
    elif return_number == 3:
        return_key = "third_return"
    else:
        return_key = "general"

    general_interpretation = get_translation(f"saturn_return.general.{return_key}", language)

    # Get sign interpretation
    sign_interpretation = get_translation(f"saturn_return.signs.{sign_key}", language)

    # Get house interpretation
    house_interpretation = get_translation(f"saturn_return.houses.{house_key}", language)

    # Get phase interpretation if applicable
    phase_interpretation = None
    if current_phase:
        phase_interpretation = get_translation(f"saturn_return.phases.{current_phase}", language)

    return {
        "title": title,
        "natal_saturn_sign": natal_saturn_sign,
        "natal_saturn_house": natal_saturn_house,
        "general_introduction": general_intro,
        "general_interpretation": general_interpretation,
        "sign_interpretation": sign_interpretation,
        "house_interpretation": house_interpretation,
        "current_phase_interpretation": phase_interpretation,
    }
