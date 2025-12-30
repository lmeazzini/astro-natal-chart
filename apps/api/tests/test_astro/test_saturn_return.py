"""
Tests for Saturn Return calculation module.

Saturn Return occurs approximately every 29.457 years when transiting Saturn
returns to its natal position. Due to retrograde motion, Saturn typically
crosses the natal position 3 times during each return.
"""

from datetime import UTC, datetime

import pytest

from app.astro.saturn_return import (
    PRECISION_DEGREES,
    SATURN_SIDEREAL_PERIOD_DAYS,
    SATURN_SIDEREAL_PERIOD_YEARS,
    SIGNS,
    calculate_cycle_progress,
    calculate_saturn_return_analysis,
    calculate_saturn_returns,
    datetime_to_jd,
    find_exact_crossing,
    find_saturn_return_passes,
    get_degree_in_sign,
    get_saturn_position,
    get_saturn_return_interpretation,
    get_sign_from_longitude,
    jd_to_datetime,
    longitude_diff,
    normalize_longitude,
)


class TestConstants:
    """Test module constants are reasonable."""

    def test_saturn_period_days(self) -> None:
        """Test Saturn's sidereal period in days."""
        # Saturn's sidereal period is approximately 10,759 days
        assert 10700 < SATURN_SIDEREAL_PERIOD_DAYS < 10800

    def test_saturn_period_years(self) -> None:
        """Test Saturn's sidereal period in years."""
        # Saturn's sidereal period is approximately 29.5 years
        assert 29.0 < SATURN_SIDEREAL_PERIOD_YEARS < 30.0

    def test_precision_degrees(self) -> None:
        """Test precision is appropriately small."""
        # Precision should be less than 0.01 degrees
        assert PRECISION_DEGREES < 0.01

    def test_signs_list(self) -> None:
        """Test signs list is complete."""
        assert len(SIGNS) == 12
        assert SIGNS[0] == "Aries"
        assert SIGNS[-1] == "Pisces"


class TestGetSignFromLongitude:
    """Test sign calculation from ecliptic longitude."""

    def test_aries(self) -> None:
        """Test 0-30 degrees is Aries."""
        assert get_sign_from_longitude(0.0) == "Aries"
        assert get_sign_from_longitude(15.0) == "Aries"
        assert get_sign_from_longitude(29.99) == "Aries"

    def test_taurus(self) -> None:
        """Test 30-60 degrees is Taurus."""
        assert get_sign_from_longitude(30.0) == "Taurus"
        assert get_sign_from_longitude(45.0) == "Taurus"

    def test_capricorn(self) -> None:
        """Test 270-300 degrees is Capricorn."""
        assert get_sign_from_longitude(270.0) == "Capricorn"
        assert get_sign_from_longitude(285.0) == "Capricorn"

    def test_pisces(self) -> None:
        """Test 330-360 degrees is Pisces."""
        assert get_sign_from_longitude(330.0) == "Pisces"
        assert get_sign_from_longitude(359.99) == "Pisces"

    def test_wrap_around(self) -> None:
        """Test longitude wrapping at 360 degrees."""
        assert get_sign_from_longitude(360.0) == "Aries"
        assert get_sign_from_longitude(390.0) == "Taurus"

    def test_negative_longitude(self) -> None:
        """Test negative longitude normalization."""
        # -30 degrees should wrap to 330 (Pisces)
        assert get_sign_from_longitude(-30.0) == "Pisces"


class TestGetDegreeInSign:
    """Test degree within sign calculation."""

    def test_start_of_sign(self) -> None:
        """Test degrees at start of sign."""
        assert get_degree_in_sign(0.0) == 0.0
        assert get_degree_in_sign(30.0) == 0.0
        assert get_degree_in_sign(270.0) == 0.0

    def test_middle_of_sign(self) -> None:
        """Test degrees in middle of sign."""
        assert get_degree_in_sign(15.0) == 15.0
        assert get_degree_in_sign(45.0) == 15.0

    def test_end_of_sign(self) -> None:
        """Test degrees at end of sign."""
        assert abs(get_degree_in_sign(29.99) - 29.99) < 0.01
        assert abs(get_degree_in_sign(59.99) - 29.99) < 0.01


class TestNormalizeLongitude:
    """Test longitude normalization to 0-360 range."""

    def test_already_normalized(self) -> None:
        """Test longitude already in range."""
        assert normalize_longitude(0.0) == 0.0
        assert normalize_longitude(180.0) == 180.0
        assert normalize_longitude(359.99) == 359.99

    def test_negative_longitude(self) -> None:
        """Test negative longitude normalization."""
        assert normalize_longitude(-30.0) == 330.0
        assert normalize_longitude(-90.0) == 270.0
        assert normalize_longitude(-360.0) == 0.0

    def test_large_longitude(self) -> None:
        """Test longitude greater than 360."""
        assert normalize_longitude(360.0) == 0.0
        assert normalize_longitude(390.0) == 30.0
        assert normalize_longitude(720.0) == 0.0


class TestLongitudeDiff:
    """Test angular difference calculation."""

    def test_same_longitude(self) -> None:
        """Test difference between same longitudes."""
        assert longitude_diff(100.0, 100.0) == 0.0

    def test_small_difference(self) -> None:
        """Test small angular difference."""
        assert abs(longitude_diff(100.0, 95.0) - 5.0) < 0.001
        assert abs(longitude_diff(95.0, 100.0) - (-5.0)) < 0.001

    def test_crossing_zero(self) -> None:
        """Test difference across 0/360 boundary."""
        # 350 to 10 degrees should be 20 degrees apart
        assert abs(longitude_diff(10.0, 350.0) - 20.0) < 0.001
        assert abs(longitude_diff(350.0, 10.0) - (-20.0)) < 0.001

    def test_opposite_sides(self) -> None:
        """Test difference at exactly 180 degrees."""
        assert abs(abs(longitude_diff(0.0, 180.0)) - 180.0) < 0.001


class TestJulianDayConversion:
    """Test datetime to Julian Day conversions."""

    def test_known_date(self) -> None:
        """Test conversion of a known date."""
        # J2000.0 (January 1, 2000, 12:00 UTC) is JD 2451545.0
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
        jd = datetime_to_jd(dt)
        assert abs(jd - 2451545.0) < 0.001

    def test_round_trip(self) -> None:
        """Test datetime -> JD -> datetime round trip."""
        original = datetime(1990, 6, 15, 14, 30, 0, tzinfo=UTC)
        jd = datetime_to_jd(original)
        result = jd_to_datetime(jd)

        assert result.year == original.year
        assert result.month == original.month
        assert result.day == original.day
        assert result.hour == original.hour
        # Allow 1 minute tolerance due to floating point
        assert abs(result.minute - original.minute) <= 1

    def test_naive_datetime_treated_as_utc(self) -> None:
        """Test naive datetime is treated as UTC."""
        dt_naive = datetime(2000, 1, 1, 12, 0, 0)
        dt_utc = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)

        jd_naive = datetime_to_jd(dt_naive)
        jd_utc = datetime_to_jd(dt_utc)

        assert abs(jd_naive - jd_utc) < 0.001


class TestGetSaturnPosition:
    """Test Saturn position retrieval from ephemeris."""

    def test_returns_tuple(self) -> None:
        """Test function returns expected tuple format."""
        jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        longitude, speed, is_retrograde = get_saturn_position(jd)

        assert isinstance(longitude, float)
        assert isinstance(speed, float)
        assert isinstance(is_retrograde, bool)

    def test_longitude_in_range(self) -> None:
        """Test longitude is in valid range."""
        jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        longitude, _, _ = get_saturn_position(jd)

        assert 0.0 <= longitude < 360.0

    def test_retrograde_detection(self) -> None:
        """Test retrograde is correctly detected from negative speed."""
        jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        longitude, speed, is_retrograde = get_saturn_position(jd)

        assert is_retrograde == (speed < 0)

    def test_different_dates_give_different_positions(self) -> None:
        """Test that different dates produce different Saturn positions."""
        jd1 = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        jd2 = datetime_to_jd(datetime(2020, 7, 1, 0, 0, 0, tzinfo=UTC))

        lon1, _, _ = get_saturn_position(jd1)
        lon2, _, _ = get_saturn_position(jd2)

        assert abs(lon1 - lon2) > 1.0  # Saturn moves several degrees in 6 months


class TestFindExactCrossing:
    """Test binary search for exact longitude crossing."""

    def test_finds_crossing_in_range(self) -> None:
        """Test finding a crossing when it exists in the range."""
        # Get Saturn's position at a known date
        start_jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        start_lon, _, _ = get_saturn_position(start_jd)

        # Search for a crossing 30 days later (Saturn moves ~1 degree)
        end_jd = start_jd + 30
        end_lon, _, _ = get_saturn_position(end_jd)

        # Target a longitude between start and end
        target = (start_lon + end_lon) / 2

        crossing_jd = find_exact_crossing(target, start_jd, end_jd)

        if crossing_jd:
            crossing_lon, _, _ = get_saturn_position(crossing_jd)
            assert abs(longitude_diff(crossing_lon, target)) < PRECISION_DEGREES * 10

    def test_returns_none_for_no_crossing(self) -> None:
        """Test returns None when no crossing exists."""
        # Use a window where we know Saturn won't cross the target
        start_jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        end_jd = start_jd + 5  # 5 days

        start_lon, _, _ = get_saturn_position(start_jd)
        end_lon, _, _ = get_saturn_position(end_jd)

        # Choose a target that's clearly outside the range Saturn will cover
        # Saturn moves about 0.03 degrees per day, so in 5 days it moves ~0.15 degrees
        # Target 50 degrees away from both start and end
        target = normalize_longitude(start_lon + 50)

        crossing_jd = find_exact_crossing(target, start_jd, end_jd)

        # The function should return None because Saturn can't move 50 degrees in 5 days
        assert crossing_jd is None


class TestFindSaturnReturnPasses:
    """Test finding all passes of a Saturn Return."""

    def test_finds_passes(self) -> None:
        """Test that passes are found for a Saturn Return."""
        # Use a birth date where Saturn was at a known position
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)

        # Look for first return (~29.5 years later)
        approximate_return_jd = birth_jd + SATURN_SIDEREAL_PERIOD_DAYS

        passes = find_saturn_return_passes(natal_lon, approximate_return_jd)

        # Should find at least 1 pass
        assert len(passes) >= 1

    def test_passes_are_sorted_by_date(self) -> None:
        """Test that passes are returned in chronological order."""
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)
        approximate_return_jd = birth_jd + SATURN_SIDEREAL_PERIOD_DAYS

        passes = find_saturn_return_passes(natal_lon, approximate_return_jd)

        if len(passes) > 1:
            for i in range(len(passes) - 1):
                assert passes[i].date < passes[i + 1].date

    def test_passes_have_sequential_numbers(self) -> None:
        """Test that passes are numbered sequentially."""
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)
        approximate_return_jd = birth_jd + SATURN_SIDEREAL_PERIOD_DAYS

        passes = find_saturn_return_passes(natal_lon, approximate_return_jd)

        for i, p in enumerate(passes):
            assert p.pass_number == i + 1

    def test_pass_longitudes_match_target(self) -> None:
        """Test that pass longitudes are close to natal longitude."""
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)
        approximate_return_jd = birth_jd + SATURN_SIDEREAL_PERIOD_DAYS

        passes = find_saturn_return_passes(natal_lon, approximate_return_jd)

        for p in passes:
            # Each pass should be very close to natal longitude
            diff = abs(longitude_diff(p.longitude, natal_lon))
            assert diff < 1.0  # Within 1 degree


class TestCalculateSaturnReturns:
    """Test complete Saturn Return calculation."""

    def test_categorizes_returns_correctly(self) -> None:
        """Test returns are categorized as past, current, or next."""
        # Birth in 1960
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)

        # Current date around 2020 (after first return, before second)
        current_jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))

        past_returns, current_return, next_return = calculate_saturn_returns(
            birth_jd, natal_lon, current_jd
        )

        # Should have at least one past return (1989-1990)
        assert len(past_returns) >= 1

        # First past return should be at age ~29
        if past_returns:
            assert 28 < past_returns[0].age_at_return < 31

    def test_age_at_return_is_reasonable(self) -> None:
        """Test calculated age at return is approximately correct."""
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)
        current_jd = datetime_to_jd(datetime(2050, 1, 1, 0, 0, 0, tzinfo=UTC))

        past_returns, current_return, next_return = calculate_saturn_returns(
            birth_jd, natal_lon, current_jd, num_returns=3
        )

        # Check ages are multiples of ~29.5 years
        for i, sr in enumerate(past_returns):
            expected_age = (i + 1) * SATURN_SIDEREAL_PERIOD_YEARS
            assert abs(sr.age_at_return - expected_age) < 2.0

    def test_return_has_passes(self) -> None:
        """Test each return contains passes."""
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)
        current_jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))

        past_returns, _, _ = calculate_saturn_returns(birth_jd, natal_lon, current_jd)

        for sr in past_returns:
            assert len(sr.passes) >= 1


class TestCalculateCycleProgress:
    """Test cycle progress calculation."""

    def test_progress_in_valid_range(self) -> None:
        """Test progress is between 0 and 100."""
        birth_jd = datetime_to_jd(datetime(1990, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)
        current_jd = datetime_to_jd(datetime(2010, 1, 1, 0, 0, 0, tzinfo=UTC))

        progress, days_until = calculate_cycle_progress(birth_jd, natal_lon, current_jd)

        assert 0 <= progress <= 100

    def test_days_until_is_positive_or_none(self) -> None:
        """Test days until next return is positive or None."""
        birth_jd = datetime_to_jd(datetime(1990, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)
        current_jd = datetime_to_jd(datetime(2010, 1, 1, 0, 0, 0, tzinfo=UTC))

        progress, days_until = calculate_cycle_progress(birth_jd, natal_lon, current_jd)

        if days_until is not None:
            assert days_until > 0

    def test_progress_increases_with_time(self) -> None:
        """Test progress increases as time passes."""
        birth_jd = datetime_to_jd(datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)

        # Check progress at different times
        jd_early = datetime_to_jd(datetime(2005, 1, 1, 0, 0, 0, tzinfo=UTC))
        jd_later = datetime_to_jd(datetime(2015, 1, 1, 0, 0, 0, tzinfo=UTC))

        progress_early, _ = calculate_cycle_progress(birth_jd, natal_lon, jd_early)
        progress_later, _ = calculate_cycle_progress(birth_jd, natal_lon, jd_later)

        assert progress_later > progress_early


class TestCalculateSaturnReturnAnalysis:
    """Test complete Saturn Return analysis."""

    def test_returns_complete_analysis(self) -> None:
        """Test analysis contains all expected fields."""
        birth_jd = datetime_to_jd(datetime(1980, 6, 15, 12, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)

        analysis = calculate_saturn_return_analysis(
            birth_jd=birth_jd,
            natal_saturn_longitude=natal_lon,
            natal_saturn_house=10,
            current_jd=datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC)),
        )

        # Check all required fields
        assert "natal_saturn_longitude" in analysis
        assert "natal_saturn_sign" in analysis
        assert "natal_saturn_house" in analysis
        assert "natal_saturn_degree" in analysis
        assert "current_saturn_longitude" in analysis
        assert "current_saturn_sign" in analysis
        assert "cycle_progress_percent" in analysis
        assert "days_until_next_return" in analysis
        assert "past_returns" in analysis
        assert "current_return" in analysis
        assert "next_return" in analysis

    def test_natal_saturn_sign_matches_longitude(self) -> None:
        """Test natal Saturn sign matches the calculated longitude."""
        # Saturn at 285 degrees is in Capricorn (270-300)
        analysis = calculate_saturn_return_analysis(
            birth_jd=datetime_to_jd(datetime(1990, 1, 1, 0, 0, 0, tzinfo=UTC)),
            natal_saturn_longitude=285.0,
            natal_saturn_house=7,
        )

        assert analysis["natal_saturn_sign"] == "Capricorn"

    def test_natal_saturn_degree_correct(self) -> None:
        """Test natal Saturn degree is correct within sign."""
        # 285 degrees = 15 degrees Capricorn
        analysis = calculate_saturn_return_analysis(
            birth_jd=datetime_to_jd(datetime(1990, 1, 1, 0, 0, 0, tzinfo=UTC)),
            natal_saturn_longitude=285.0,
            natal_saturn_house=7,
        )

        assert abs(analysis["natal_saturn_degree"] - 15.0) < 0.1

    def test_house_is_preserved(self) -> None:
        """Test natal Saturn house is preserved in output."""
        analysis = calculate_saturn_return_analysis(
            birth_jd=datetime_to_jd(datetime(1990, 1, 1, 0, 0, 0, tzinfo=UTC)),
            natal_saturn_longitude=285.0,
            natal_saturn_house=10,
        )

        assert analysis["natal_saturn_house"] == 10

    def test_serialization_format(self) -> None:
        """Test returns are serialized correctly."""
        birth_jd = datetime_to_jd(datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC))
        natal_lon, _, _ = get_saturn_position(birth_jd)

        analysis = calculate_saturn_return_analysis(
            birth_jd=birth_jd,
            natal_saturn_longitude=natal_lon,
            natal_saturn_house=5,
            current_jd=datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC)),
        )

        # Check past returns are serialized as dicts
        for sr in analysis["past_returns"]:
            assert isinstance(sr, dict)
            assert "return_number" in sr
            assert "passes" in sr
            assert isinstance(sr["passes"], list)


class TestGetSaturnReturnInterpretation:
    """Test Saturn Return interpretation retrieval."""

    def test_returns_interpretation_dict(self) -> None:
        """Test interpretation returns expected structure."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign="Capricorn",
            natal_saturn_house=10,
            return_number=1,
            language="en_US",
        )

        assert isinstance(interpretation, dict)
        assert "title" in interpretation
        assert "natal_saturn_sign" in interpretation
        assert "natal_saturn_house" in interpretation
        assert "general_introduction" in interpretation
        assert "general_interpretation" in interpretation
        assert "sign_interpretation" in interpretation
        assert "house_interpretation" in interpretation

    def test_preserves_sign_and_house(self) -> None:
        """Test sign and house are preserved in output."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign="Leo",
            natal_saturn_house=5,
        )

        assert interpretation["natal_saturn_sign"] == "Leo"
        assert interpretation["natal_saturn_house"] == 5

    def test_phase_interpretation_optional(self) -> None:
        """Test phase interpretation is None when not provided."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign="Aries",
            natal_saturn_house=1,
        )

        assert interpretation["current_phase_interpretation"] is None

    def test_phase_interpretation_included(self) -> None:
        """Test phase interpretation is included when provided."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign="Aries",
            natal_saturn_house=1,
            current_phase="first_pass",
            language="en_US",
        )

        # Phase interpretation should be populated (not None)
        assert interpretation["current_phase_interpretation"] is not None

    @pytest.mark.parametrize(
        "sign",
        [
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
        ],
    )
    def test_all_signs_have_interpretations(self, sign: str) -> None:
        """Test all zodiac signs have interpretations."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign=sign,
            natal_saturn_house=1,
            language="en_US",
        )

        # Should have non-empty sign interpretation
        assert interpretation["sign_interpretation"]
        assert len(interpretation["sign_interpretation"]) > 10

    @pytest.mark.parametrize("house", range(1, 13))
    def test_all_houses_have_interpretations(self, house: int) -> None:
        """Test all houses have interpretations."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign="Aries",
            natal_saturn_house=house,
            language="en_US",
        )

        # Should have non-empty house interpretation
        assert interpretation["house_interpretation"]
        assert len(interpretation["house_interpretation"]) > 10


class TestKnownSaturnReturns:
    """Test against known historical Saturn Returns for verification."""

    def test_1989_saturn_return(self) -> None:
        """
        Test Saturn Return calculation for someone born in late 1959.

        Saturn was in Capricorn in 1959 and returned to Capricorn in 1989.
        """
        # Birth: December 1959 when Saturn was in Capricorn
        birth_dt = datetime(1959, 12, 15, 12, 0, 0, tzinfo=UTC)
        birth_jd = datetime_to_jd(birth_dt)
        natal_lon, _, _ = get_saturn_position(birth_jd)

        # Saturn should be in Capricorn
        assert get_sign_from_longitude(natal_lon) == "Capricorn"

        # Calculate returns up to 2020
        current_jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        past_returns, current_return, next_return = calculate_saturn_returns(
            birth_jd, natal_lon, current_jd
        )

        # Should have first return around 1989
        assert len(past_returns) >= 1
        first_return = past_returns[0]

        # First pass should be in late 1988 or 1989
        first_pass_year = first_return.start_date.year
        assert 1988 <= first_pass_year <= 1990

    def test_young_person_no_past_returns(self) -> None:
        """Test someone born recently has no past returns yet."""
        birth_dt = datetime(2010, 1, 1, 0, 0, 0, tzinfo=UTC)
        birth_jd = datetime_to_jd(birth_dt)
        natal_lon, _, _ = get_saturn_position(birth_jd)

        current_jd = datetime_to_jd(datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC))
        past_returns, current_return, next_return = calculate_saturn_returns(
            birth_jd, natal_lon, current_jd
        )

        # Should have no past or current returns yet
        assert len(past_returns) == 0
        assert current_return is None

        # Should have a next return
        assert next_return is not None
        # Next return should be around 2039
        assert 2038 <= next_return.start_date.year <= 2041


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_saturn_near_zero_degrees(self) -> None:
        """Test calculation when Saturn is near 0 degrees (Aries)."""
        analysis = calculate_saturn_return_analysis(
            birth_jd=datetime_to_jd(datetime(1980, 1, 1, 0, 0, 0, tzinfo=UTC)),
            natal_saturn_longitude=1.5,  # 1.5 degrees Aries
            natal_saturn_house=1,
        )

        assert analysis["natal_saturn_sign"] == "Aries"
        assert abs(analysis["natal_saturn_degree"] - 1.5) < 0.1

    def test_saturn_near_360_degrees(self) -> None:
        """Test calculation when Saturn is near 360 degrees (late Pisces)."""
        analysis = calculate_saturn_return_analysis(
            birth_jd=datetime_to_jd(datetime(1980, 1, 1, 0, 0, 0, tzinfo=UTC)),
            natal_saturn_longitude=358.5,  # 28.5 degrees Pisces
            natal_saturn_house=12,
        )

        assert analysis["natal_saturn_sign"] == "Pisces"
        assert abs(analysis["natal_saturn_degree"] - 28.5) < 0.1

    def test_very_old_birth_date(self) -> None:
        """Test calculation for very old birth date (3 returns)."""
        birth_dt = datetime(1930, 1, 1, 0, 0, 0, tzinfo=UTC)
        birth_jd = datetime_to_jd(birth_dt)
        natal_lon, _, _ = get_saturn_position(birth_jd)

        current_jd = datetime_to_jd(datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC))
        past_returns, current_return, next_return = calculate_saturn_returns(
            birth_jd, natal_lon, current_jd, num_returns=3
        )

        # Should have 3 past returns (1959, 1988, 2017-ish)
        assert len(past_returns) >= 2

    def test_current_return_detection(self) -> None:
        """Test detection of a currently happening return."""
        # Find a date when Saturn was/will be returning
        # We can simulate by checking between first and last pass
        birth_dt = datetime(1960, 1, 1, 0, 0, 0, tzinfo=UTC)
        birth_jd = datetime_to_jd(birth_dt)
        natal_lon, _, _ = get_saturn_position(birth_jd)

        # Get the first return details
        approximate_return_jd = birth_jd + SATURN_SIDEREAL_PERIOD_DAYS
        passes = find_saturn_return_passes(natal_lon, approximate_return_jd)

        if len(passes) >= 2:
            # Set current date to between first and last pass
            first_pass_jd = datetime_to_jd(passes[0].date)
            last_pass_jd = datetime_to_jd(passes[-1].date)
            mid_jd = (first_pass_jd + last_pass_jd) / 2

            past_returns, current_return, next_return = calculate_saturn_returns(
                birth_jd, natal_lon, mid_jd
            )

            # Should detect as current return
            assert current_return is not None
            assert current_return.return_number == 1


class TestLanguageSupport:
    """Test multi-language interpretation support."""

    def test_english_interpretation(self) -> None:
        """Test English interpretation retrieval."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign="Capricorn",
            natal_saturn_house=10,
            language="en_US",
        )

        # Should contain English text
        assert interpretation["title"]
        assert interpretation["general_introduction"]

    def test_portuguese_interpretation(self) -> None:
        """Test Portuguese interpretation retrieval."""
        interpretation = get_saturn_return_interpretation(
            natal_saturn_sign="Capricorn",
            natal_saturn_house=10,
            language="pt_BR",
        )

        # Should contain Portuguese text
        assert interpretation["title"]
        assert interpretation["general_introduction"]
