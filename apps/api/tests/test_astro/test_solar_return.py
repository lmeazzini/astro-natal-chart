"""
Tests for Solar Return calculation module.

Solar Return occurs approximately every year when the transiting Sun
returns to its natal position. Unlike Saturn, the Sun never retrogrades,
so there is always exactly one pass per year.
"""

from datetime import UTC, datetime

import pytest

from app.astro.solar_return import (
    MAX_ITERATIONS,
    PRECISION_DEGREES,
    SEARCH_WINDOW_DAYS,
    SIGNS,
    SUN_TROPICAL_YEAR_DAYS,
    calculate_comparison,
    calculate_multiple_solar_returns,
    calculate_solar_return,
    calculate_sr_to_natal_aspects,
    datetime_to_jd,
    find_sun_return_moment,
    get_degree_in_sign,
    get_planet_house,
    get_sign_from_longitude,
    get_solar_return_interpretation,
    get_sun_position,
    jd_to_datetime,
    longitude_diff,
    normalize_longitude,
)


class TestConstants:
    """Test module constants are reasonable."""

    def test_sun_tropical_year_days(self) -> None:
        """Test Sun's tropical year period in days."""
        # Sun's tropical year is approximately 365.2422 days
        assert 365.0 < SUN_TROPICAL_YEAR_DAYS < 366.0
        assert abs(SUN_TROPICAL_YEAR_DAYS - 365.2422) < 0.001

    def test_precision_degrees(self) -> None:
        """Test precision is appropriately small."""
        # Precision should be less than 0.001 degrees
        assert PRECISION_DEGREES < 0.001

    def test_search_window_days(self) -> None:
        """Test search window is reasonable."""
        # Search window should be a few days around birthday
        assert 2 <= SEARCH_WINDOW_DAYS <= 7

    def test_max_iterations(self) -> None:
        """Test max iterations is sufficient."""
        assert MAX_ITERATIONS >= 50

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


class TestGetSunPosition:
    """Test Sun position retrieval from ephemeris."""

    def test_returns_tuple(self) -> None:
        """Test function returns expected tuple format."""
        jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        longitude, speed = get_sun_position(jd)

        assert isinstance(longitude, float)
        assert isinstance(speed, float)

    def test_longitude_in_range(self) -> None:
        """Test longitude is in valid range."""
        jd = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        longitude, _ = get_sun_position(jd)

        assert 0.0 <= longitude < 360.0

    def test_sun_always_direct(self) -> None:
        """Test Sun always has positive speed (never retrograde)."""
        # Check several dates throughout the year
        for month in range(1, 13):
            jd = datetime_to_jd(datetime(2020, month, 15, 0, 0, 0, tzinfo=UTC))
            _, speed = get_sun_position(jd)
            assert speed > 0  # Sun never goes retrograde

    def test_different_dates_give_different_positions(self) -> None:
        """Test that different dates produce different Sun positions."""
        jd1 = datetime_to_jd(datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC))
        jd2 = datetime_to_jd(datetime(2020, 7, 1, 0, 0, 0, tzinfo=UTC))

        lon1, _ = get_sun_position(jd1)
        lon2, _ = get_sun_position(jd2)

        assert abs(lon1 - lon2) > 90.0  # Sun moves ~180 degrees in 6 months


class TestFindSunReturnMoment:
    """Test finding exact Sun return moment."""

    def test_finds_return_near_birthday(self) -> None:
        """Test return is found near the birthday."""
        # Someone born March 21, 1990 (near spring equinox)
        birth_jd = datetime_to_jd(datetime(1990, 3, 21, 12, 0, 0, tzinfo=UTC))
        natal_lon, _ = get_sun_position(birth_jd)

        # Find 2020 solar return
        return_dt = find_sun_return_moment(natal_lon, 2020, 3, 21)

        # Should be within a few days of March 21, 2020
        assert return_dt.year == 2020
        assert 3 <= return_dt.month <= 3 or return_dt.month == 4  # Could be early April
        if return_dt.month == 3:
            assert 18 <= return_dt.day <= 24

    def test_return_sun_matches_natal(self) -> None:
        """Test that return Sun position matches natal."""
        birth_jd = datetime_to_jd(datetime(1985, 7, 15, 8, 0, 0, tzinfo=UTC))
        natal_lon, _ = get_sun_position(birth_jd)

        return_dt = find_sun_return_moment(natal_lon, 2024, 7, 15)
        return_jd = datetime_to_jd(return_dt)
        return_lon, _ = get_sun_position(return_jd)

        # Should be very close (within precision)
        diff = abs(longitude_diff(return_lon, natal_lon))
        assert diff < 0.01  # Within 0.01 degrees

    def test_handles_leap_year_birthday(self) -> None:
        """Test handling of February 29 birthday in non-leap year."""
        # Someone born February 29, 2000
        birth_jd = datetime_to_jd(datetime(2000, 2, 29, 12, 0, 0, tzinfo=UTC))
        natal_lon, _ = get_sun_position(birth_jd)

        # Find 2023 solar return (non-leap year)
        return_dt = find_sun_return_moment(natal_lon, 2023, 2, 29)

        # Should still find the return (around Feb 28 or Mar 1)
        assert return_dt.year == 2023
        assert return_dt.month in [2, 3]


class TestGetPlanetHouse:
    """Test planet house determination."""

    def test_first_house(self) -> None:
        """Test planet in first house."""
        # Equal houses starting at 0 degrees
        cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        assert get_planet_house(15.0, cusps) == 1
        assert get_planet_house(0.0, cusps) == 1

    def test_tenth_house(self) -> None:
        """Test planet in tenth house."""
        cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        assert get_planet_house(275.0, cusps) == 10

    def test_wrap_around(self) -> None:
        """Test planet house with wrap around."""
        # First house spans from 330 to 30 degrees
        cusps = [330.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0]
        assert get_planet_house(350.0, cusps) == 1
        assert get_planet_house(15.0, cusps) == 2


class TestCalculateSrToNatalAspects:
    """Test Solar Return to natal aspects calculation."""

    def test_finds_conjunction(self) -> None:
        """Test finding a conjunction aspect."""
        sr_planets = [{"name": "Sun", "longitude": 100.0}]
        natal_planets = [{"name": "Moon", "longitude": 102.0}]

        aspects = calculate_sr_to_natal_aspects(sr_planets, natal_planets)

        assert len(aspects) >= 1
        conj = next((a for a in aspects if a["aspect"] == "Conjunction"), None)
        assert conj is not None
        assert conj["sr_planet"] == "Sun"
        assert conj["natal_planet"] == "Moon"
        assert conj["orb"] < 3.0

    def test_finds_opposition(self) -> None:
        """Test finding an opposition aspect."""
        sr_planets = [{"name": "Mars", "longitude": 0.0}]
        natal_planets = [{"name": "Jupiter", "longitude": 178.0}]

        aspects = calculate_sr_to_natal_aspects(sr_planets, natal_planets)

        opp = next((a for a in aspects if a["aspect"] == "Opposition"), None)
        assert opp is not None
        assert opp["orb"] < 3.0

    def test_finds_trine(self) -> None:
        """Test finding a trine aspect."""
        sr_planets = [{"name": "Venus", "longitude": 0.0}]
        natal_planets = [{"name": "Saturn", "longitude": 120.0}]

        aspects = calculate_sr_to_natal_aspects(sr_planets, natal_planets)

        trine = next((a for a in aspects if a["aspect"] == "Trine"), None)
        assert trine is not None
        assert trine["is_major"] is True

    def test_finds_square(self) -> None:
        """Test finding a square aspect."""
        sr_planets = [{"name": "Mercury", "longitude": 0.0}]
        natal_planets = [{"name": "Pluto", "longitude": 90.0}]

        aspects = calculate_sr_to_natal_aspects(sr_planets, natal_planets)

        square = next((a for a in aspects if a["aspect"] == "Square"), None)
        assert square is not None

    def test_aspects_sorted_by_orb(self) -> None:
        """Test aspects are sorted by orb (tightest first)."""
        sr_planets = [{"name": "Sun", "longitude": 100.0}]
        natal_planets = [
            {"name": "Moon", "longitude": 100.0},  # Exact conjunction
            {"name": "Mars", "longitude": 105.0},  # 5 degree orb
        ]

        aspects = calculate_sr_to_natal_aspects(sr_planets, natal_planets)

        if len(aspects) >= 2:
            assert aspects[0]["orb"] <= aspects[1]["orb"]

    def test_skips_nodes(self) -> None:
        """Test that lunar nodes are skipped."""
        sr_planets = [{"name": "North Node", "longitude": 100.0}]
        natal_planets = [{"name": "South Node", "longitude": 100.0}]

        aspects = calculate_sr_to_natal_aspects(sr_planets, natal_planets)

        assert len(aspects) == 0


class TestCalculateSolarReturn:
    """Test complete Solar Return calculation."""

    def test_returns_chart_data(self) -> None:
        """Test SR calculation returns expected structure."""
        sr = calculate_solar_return(
            natal_sun_longitude=100.0,
            birth_datetime=datetime(1990, 7, 15, 12, 0, 0, tzinfo=UTC),
            target_year=2024,
            latitude=40.7128,
            longitude=-74.006,
            timezone="America/New_York",
            city="New York",
            country="USA",
        )

        assert "chart" in sr
        chart = sr["chart"]

        # Check required fields
        assert "return_datetime" in chart
        assert "return_year" in chart
        assert "location" in chart
        assert "planets" in chart
        assert "houses" in chart
        assert "aspects" in chart
        assert "ascendant" in chart
        assert "ascendant_sign" in chart
        assert "midheaven" in chart
        assert "sun_house" in chart

    def test_return_year_matches(self) -> None:
        """Test return year matches requested year."""
        sr = calculate_solar_return(
            natal_sun_longitude=150.0,
            birth_datetime=datetime(1980, 5, 20, 10, 0, 0, tzinfo=UTC),
            target_year=2025,
            latitude=51.5074,
            longitude=-0.1278,
            timezone="Europe/London",
        )

        assert sr["chart"]["return_year"] == 2025

    def test_location_preserved(self) -> None:
        """Test location is preserved in output."""
        sr = calculate_solar_return(
            natal_sun_longitude=200.0,
            birth_datetime=datetime(1985, 10, 10, 8, 0, 0, tzinfo=UTC),
            target_year=2024,
            latitude=-23.5505,
            longitude=-46.6333,
            timezone="America/Sao_Paulo",
            city="São Paulo",
            country="Brazil",
        )

        loc = sr["chart"]["location"]
        assert loc["city"] == "São Paulo"
        assert loc["country"] == "Brazil"
        assert abs(loc["latitude"] - (-23.5505)) < 0.001

    def test_planets_have_required_fields(self) -> None:
        """Test planets have all required fields."""
        sr = calculate_solar_return(
            natal_sun_longitude=50.0,
            birth_datetime=datetime(1975, 4, 5, 6, 0, 0, tzinfo=UTC),
            target_year=2024,
            latitude=48.8566,
            longitude=2.3522,
            timezone="Europe/Paris",
        )

        for planet in sr["chart"]["planets"]:
            assert "name" in planet
            assert "longitude" in planet
            assert "sign" in planet


class TestCalculateComparison:
    """Test Solar Return to natal comparison."""

    def test_returns_comparison_data(self) -> None:
        """Test comparison returns expected structure."""
        sr_chart = {
            "ascendant": 100.0,
            "midheaven": 10.0,
            "planets": [{"name": "Sun", "longitude": 150.0}],
            "houses": [{"longitude": 100.0 + i * 30} for i in range(12)],
        }

        natal_chart = {
            "planets": [{"name": "Moon", "longitude": 200.0}],
            "houses": [{"longitude": 50.0 + i * 30} for i in range(12)],
        }

        comparison = calculate_comparison(sr_chart, natal_chart)

        assert "sr_asc_in_natal_house" in comparison
        assert "sr_mc_in_natal_house" in comparison
        assert "sr_planets_in_natal_houses" in comparison
        assert "natal_planets_in_sr_houses" in comparison
        assert "key_aspects" in comparison

    def test_sr_planets_in_natal_houses(self) -> None:
        """Test SR planets are placed in natal houses correctly."""
        sr_chart = {
            "ascendant": 0.0,
            "midheaven": 270.0,
            "planets": [
                {"name": "Sun", "longitude": 45.0},  # Should be in house 2
                {"name": "Moon", "longitude": 100.0},  # Should be in house 4
            ],
            "houses": [{"longitude": i * 30.0} for i in range(12)],
        }

        natal_chart = {
            "planets": [],
            "houses": [{"longitude": i * 30.0} for i in range(12)],  # Same houses
        }

        comparison = calculate_comparison(sr_chart, natal_chart)

        assert comparison["sr_planets_in_natal_houses"]["Sun"] == 2
        assert comparison["sr_planets_in_natal_houses"]["Moon"] == 4


class TestGetSolarReturnInterpretation:
    """Test Solar Return interpretation retrieval."""

    def test_returns_interpretation_dict(self) -> None:
        """Test interpretation returns expected structure."""
        interpretation = get_solar_return_interpretation(
            sr_ascendant_sign="Leo",
            sr_sun_house=10,
            language="en_US",
        )

        assert isinstance(interpretation, dict)
        assert "title" in interpretation
        assert "sr_ascendant_sign" in interpretation
        assert "sr_sun_house" in interpretation
        assert "general_introduction" in interpretation
        assert "ascendant_interpretation" in interpretation
        assert "sun_house_interpretation" in interpretation

    def test_preserves_sign_and_house(self) -> None:
        """Test sign and house are preserved in output."""
        interpretation = get_solar_return_interpretation(
            sr_ascendant_sign="Scorpio",
            sr_sun_house=7,
        )

        assert interpretation["sr_ascendant_sign"] == "Scorpio"
        assert interpretation["sr_sun_house"] == 7

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
        interpretation = get_solar_return_interpretation(
            sr_ascendant_sign=sign,
            sr_sun_house=1,
            language="en_US",
        )

        # Should have non-empty ascendant interpretation
        assert interpretation["ascendant_interpretation"]
        assert len(interpretation["ascendant_interpretation"]) > 10

    @pytest.mark.parametrize("house", range(1, 13))
    def test_all_houses_have_interpretations(self, house: int) -> None:
        """Test all houses have interpretations."""
        interpretation = get_solar_return_interpretation(
            sr_ascendant_sign="Aries",
            sr_sun_house=house,
            language="en_US",
        )

        # Should have non-empty house interpretation
        assert interpretation["sun_house_interpretation"]
        assert len(interpretation["sun_house_interpretation"]) > 10


class TestCalculateMultipleSolarReturns:
    """Test multiple Solar Returns calculation."""

    def test_returns_correct_count(self) -> None:
        """Test correct number of returns are calculated."""
        returns = calculate_multiple_solar_returns(
            natal_sun_longitude=100.0,
            birth_datetime=datetime(1990, 6, 15, 12, 0, 0, tzinfo=UTC),
            start_year=2020,
            end_year=2022,
            latitude=40.0,
            longitude=-74.0,
            timezone="America/New_York",
        )

        assert len(returns) == 3  # 2020, 2021, 2022

    def test_years_are_sequential(self) -> None:
        """Test returned years are sequential."""
        returns = calculate_multiple_solar_returns(
            natal_sun_longitude=50.0,
            birth_datetime=datetime(1985, 3, 10, 8, 0, 0, tzinfo=UTC),
            start_year=2015,
            end_year=2020,
            latitude=35.0,
            longitude=139.0,
            timezone="Asia/Tokyo",
        )

        years = [r["chart"]["return_year"] for r in returns]
        assert years == [2015, 2016, 2017, 2018, 2019, 2020]


class TestKnownSolarReturns:
    """Test against known Solar Return dates for verification."""

    def test_2024_spring_equinox_return(self) -> None:
        """
        Test Solar Return for someone born at spring equinox.

        The Sun is at 0° Aries at the spring equinox.
        """
        # Birth at spring equinox (approximately)
        birth_dt = datetime(1990, 3, 21, 0, 0, 0, tzinfo=UTC)
        birth_jd = datetime_to_jd(birth_dt)
        natal_lon, _ = get_sun_position(birth_jd)

        # Sun should be near 0° Aries
        assert get_sign_from_longitude(natal_lon) == "Aries"
        assert get_degree_in_sign(natal_lon) < 5.0

        # Calculate 2024 return
        return_dt = find_sun_return_moment(natal_lon, 2024, 3, 21)

        # Should be around March 19-21, 2024
        assert return_dt.year == 2024
        assert return_dt.month == 3
        assert 19 <= return_dt.day <= 21

    def test_2024_summer_solstice_return(self) -> None:
        """
        Test Solar Return for someone born at summer solstice.

        The Sun is at 0° Cancer at the summer solstice.
        """
        # Birth at summer solstice (approximately)
        birth_dt = datetime(1985, 6, 21, 12, 0, 0, tzinfo=UTC)
        birth_jd = datetime_to_jd(birth_dt)
        natal_lon, _ = get_sun_position(birth_jd)

        # Sun should be near 0° Cancer (90°)
        assert get_sign_from_longitude(natal_lon) == "Cancer"

        # Calculate 2024 return
        return_dt = find_sun_return_moment(natal_lon, 2024, 6, 21)

        # Should be around June 20-21, 2024
        assert return_dt.year == 2024
        assert return_dt.month == 6
        assert 19 <= return_dt.day <= 22


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_sun_near_zero_degrees(self) -> None:
        """Test calculation when Sun is near 0 degrees (Aries)."""
        sr = calculate_solar_return(
            natal_sun_longitude=1.5,  # 1.5 degrees Aries
            birth_datetime=datetime(1990, 3, 22, 12, 0, 0, tzinfo=UTC),
            target_year=2024,
            latitude=40.0,
            longitude=-74.0,
            timezone="America/New_York",
        )

        assert sr["chart"]["ascendant_sign"] in SIGNS

    def test_sun_near_360_degrees(self) -> None:
        """Test calculation when Sun is near 360 degrees (late Pisces)."""
        sr = calculate_solar_return(
            natal_sun_longitude=358.5,  # 28.5 degrees Pisces
            birth_datetime=datetime(1990, 3, 20, 12, 0, 0, tzinfo=UTC),
            target_year=2024,
            latitude=40.0,
            longitude=-74.0,
            timezone="America/New_York",
        )

        assert sr["chart"]["ascendant_sign"] in SIGNS

    def test_relocated_solar_return(self) -> None:
        """Test Solar Return with different location than birth."""
        # Born in New York
        birth_dt = datetime(1980, 8, 15, 10, 0, 0, tzinfo=UTC)
        birth_jd = datetime_to_jd(birth_dt)
        natal_lon, _ = get_sun_position(birth_jd)

        # Calculate SR in Tokyo
        sr_tokyo = calculate_solar_return(
            natal_sun_longitude=natal_lon,
            birth_datetime=birth_dt,
            target_year=2024,
            latitude=35.6762,
            longitude=139.6503,
            timezone="Asia/Tokyo",
            city="Tokyo",
            country="Japan",
        )

        # Calculate SR in New York
        sr_nyc = calculate_solar_return(
            natal_sun_longitude=natal_lon,
            birth_datetime=birth_dt,
            target_year=2024,
            latitude=40.7128,
            longitude=-74.006,
            timezone="America/New_York",
            city="New York",
            country="USA",
        )

        # Return datetime should be the same (same Sun position)
        # But houses/ascendant should be different due to different location
        assert sr_tokyo["chart"]["return_year"] == sr_nyc["chart"]["return_year"]
        # Ascendants will likely be different due to different locations
        # (not testing exact values as they depend on time/location)


class TestLanguageSupport:
    """Test multi-language interpretation support."""

    def test_english_interpretation(self) -> None:
        """Test English interpretation retrieval."""
        interpretation = get_solar_return_interpretation(
            sr_ascendant_sign="Capricorn",
            sr_sun_house=10,
            language="en_US",
        )

        # Should contain text
        assert interpretation["title"]
        assert interpretation["general_introduction"]

    def test_portuguese_interpretation(self) -> None:
        """Test Portuguese interpretation retrieval."""
        interpretation = get_solar_return_interpretation(
            sr_ascendant_sign="Capricorn",
            sr_sun_house=10,
            language="pt_BR",
        )

        # Should contain Portuguese text
        assert interpretation["title"]
        assert interpretation["general_introduction"]
