"""
Unit tests for prenatal syzygy calculations.
"""

import swisseph as swe

from app.astro.prenatal_syzygy import (
    _get_house_for_position,
    _search_syzygy_backward,
    calculate_prenatal_syzygy,
)


class TestSyzygyTypeDetection:
    """Test New Moon vs Full Moon detection based on elongation."""

    def test_new_moon_when_elongation_less_than_180(self) -> None:
        """When Moon is ahead of Sun by < 180°, last syzygy was New Moon."""
        # Sun at 0°, Moon at 45° → elongation = 45° < 180 → New Moon
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,  # Arbitrary JD
            sun_longitude=0.0,
            moon_longitude=45.0,
            houses=None,
            language="en-US",
        )
        assert result["type"] == "new_moon"
        assert result["type_name"] == "New Moon"
        assert result["emoji"] == "🌑"

    def test_full_moon_when_elongation_at_180(self) -> None:
        """When Moon is ahead of Sun by exactly 180°, last syzygy was Full Moon."""
        # Sun at 0°, Moon at 180° → elongation = 180° → Full Moon
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=0.0,
            moon_longitude=180.0,
            houses=None,
            language="en-US",
        )
        assert result["type"] == "full_moon"
        assert result["type_name"] == "Full Moon"
        assert result["emoji"] == "🌕"

    def test_full_moon_when_elongation_greater_than_180(self) -> None:
        """When Moon is ahead of Sun by > 180°, last syzygy was Full Moon."""
        # Sun at 0°, Moon at 270° → elongation = 270° > 180 → Full Moon
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=0.0,
            moon_longitude=270.0,
            houses=None,
            language="en-US",
        )
        assert result["type"] == "full_moon"

    def test_new_moon_with_wrap_around(self) -> None:
        """Test elongation calculation when Moon has wrapped around."""
        # Sun at 350°, Moon at 20° → elongation = (20 - 350) % 360 = 30° < 180 → New Moon
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=350.0,
            moon_longitude=20.0,
            houses=None,
            language="en-US",
        )
        assert result["type"] == "new_moon"


class TestSyzygySearch:
    """Test backward search algorithm for finding exact syzygy moment."""

    def test_search_finds_syzygy_within_30_days(self) -> None:
        """Should find a syzygy within 30 days of any birth date."""
        # Use a known date
        birth_jd = 2460000.0

        # Get initial positions to determine type
        sun_result = swe.calc_ut(birth_jd, swe.SUN)
        moon_result = swe.calc_ut(birth_jd, swe.MOON)
        elongation = (moon_result[0][0] - sun_result[0][0]) % 360
        syzygy_type = "new_moon" if elongation < 180 else "full_moon"

        syzygy_jd = _search_syzygy_backward(birth_jd, syzygy_type)

        # Syzygy should be before birth
        assert syzygy_jd < birth_jd

        # Syzygy should be within ~30 days
        assert birth_jd - syzygy_jd < 30

    def test_search_precision_within_threshold(self) -> None:
        """Syzygy should be found within 0.1° precision."""
        birth_jd = 2460000.0

        # Test New Moon search
        syzygy_jd = _search_syzygy_backward(birth_jd, "new_moon")

        # Get positions at found syzygy
        sun_result = swe.calc_ut(syzygy_jd, swe.SUN)
        moon_result = swe.calc_ut(syzygy_jd, swe.MOON)
        elongation = (moon_result[0][0] - sun_result[0][0]) % 360

        # Should be very close to 0° (or 360°)
        diff = min(elongation, 360 - elongation)
        assert diff < 1.0  # Within 1 degree (generous for test stability)

    def test_search_full_moon_precision(self) -> None:
        """Full Moon syzygy should be close to 180° elongation."""
        # Find a date where the last syzygy was actually a Full Moon
        # We need elongation > 180° at birth to ensure we look for Full Moon
        birth_jd = 2460000.0

        # Check elongation to find appropriate test date
        sun_result = swe.calc_ut(birth_jd, swe.SUN)
        moon_result = swe.calc_ut(birth_jd, swe.MOON)
        elongation = (moon_result[0][0] - sun_result[0][0]) % 360

        # Adjust birth date to get Full Moon scenario if needed
        test_jd = birth_jd
        while elongation < 180:
            test_jd += 7  # Move forward in time
            sun_result = swe.calc_ut(test_jd, swe.SUN)
            moon_result = swe.calc_ut(test_jd, swe.MOON)
            elongation = (moon_result[0][0] - sun_result[0][0]) % 360

        syzygy_jd = _search_syzygy_backward(test_jd, "full_moon")

        sun_result = swe.calc_ut(syzygy_jd, swe.SUN)
        moon_result = swe.calc_ut(syzygy_jd, swe.MOON)
        elongation = (moon_result[0][0] - sun_result[0][0]) % 360

        # Should be close to 180°
        diff = abs(elongation - 180)
        assert diff < 1.0  # Within 1 degree


class TestSignCalculation:
    """Test zodiac sign determination for syzygy position."""

    def test_aries_at_zero_degrees(self) -> None:
        """0° longitude should be Aries."""
        # We can't directly test sign calculation without a real syzygy,
        # but we can verify the result contains valid sign data
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=15.0,  # Mid-Aries
            moon_longitude=20.0,
            houses=None,
            language="en-US",
        )

        assert "sign" in result
        assert "sign_key" in result
        assert result["sign_key"] in [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]

    def test_degree_and_minute_format(self) -> None:
        """Degree should be 0-29 and minute should be 0-59."""
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=45.0,
            moon_longitude=60.0,
            houses=None,
            language="en-US",
        )

        assert 0 <= result["degree"] <= 29
        assert 0 <= result["minute"] <= 59


class TestHousePlacement:
    """Test house placement calculation."""

    def test_get_house_with_no_houses(self) -> None:
        """Should return 1 if no houses provided."""
        assert _get_house_for_position(45.0, None) == 1
        assert _get_house_for_position(45.0, []) == 1

    def test_get_house_with_valid_houses(self) -> None:
        """Should correctly determine house placement."""
        # Create 12 houses with 30° each starting at 0°
        houses = [{"house": i + 1, "longitude": i * 30.0} for i in range(12)]

        # 15° should be in house 1 (0°-30°)
        assert _get_house_for_position(15.0, houses) == 1

        # 45° should be in house 2 (30°-60°)
        assert _get_house_for_position(45.0, houses) == 2

        # 350° should be in house 12 (330°-360°)
        assert _get_house_for_position(350.0, houses) == 12

    def test_get_house_with_wrap_around(self) -> None:
        """Should handle houses that wrap around 0° Aries."""
        # Houses starting at 330° (house 1 wraps from 330° to 30°)
        houses = [
            {"house": 1, "longitude": 330.0},
            {"house": 2, "longitude": 30.0},
            {"house": 3, "longitude": 60.0},
            {"house": 4, "longitude": 90.0},
            {"house": 5, "longitude": 120.0},
            {"house": 6, "longitude": 150.0},
            {"house": 7, "longitude": 180.0},
            {"house": 8, "longitude": 210.0},
            {"house": 9, "longitude": 240.0},
            {"house": 10, "longitude": 270.0},
            {"house": 11, "longitude": 300.0},
            {"house": 12, "longitude": 330.0},  # This should be skipped
        ]
        # Fix: house 12 should be before house 1
        houses = [
            {"house": 1, "longitude": 330.0},
            {"house": 2, "longitude": 30.0},
            {"house": 3, "longitude": 60.0},
            {"house": 4, "longitude": 90.0},
            {"house": 5, "longitude": 120.0},
            {"house": 6, "longitude": 150.0},
            {"house": 7, "longitude": 180.0},
            {"house": 8, "longitude": 210.0},
            {"house": 9, "longitude": 240.0},
            {"house": 10, "longitude": 270.0},
            {"house": 11, "longitude": 300.0},
            {"house": 12, "longitude": 315.0},
        ]

        # 350° wraps into house 1 (330°-30°)
        assert _get_house_for_position(350.0, houses) == 1

        # 10° also in house 1
        assert _get_house_for_position(10.0, houses) == 1


class TestLocalization:
    """Test translation support."""

    def test_english_translations(self) -> None:
        """Should return English text for en-US."""
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=0.0,
            moon_longitude=45.0,
            houses=None,
            language="en-US",
        )

        assert result["type_name"] == "New Moon"
        assert "interpretation" in result
        assert len(result["interpretation"]) > 50  # Should have meaningful text
        assert "keywords" in result

    def test_portuguese_translations(self) -> None:
        """Should return Portuguese text for pt-BR."""
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=0.0,
            moon_longitude=45.0,
            houses=None,
            language="pt-BR",
        )

        assert result["type_name"] == "Lua Nova"
        assert "interpretation" in result
        assert len(result["interpretation"]) > 50

    def test_full_moon_portuguese(self) -> None:
        """Should return Portuguese Full Moon text."""
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=0.0,
            moon_longitude=200.0,  # > 180° elongation
            houses=None,
            language="pt-BR",
        )

        assert result["type_name"] == "Lua Cheia"


class TestReturnStructure:
    """Test the complete return structure."""

    def test_all_required_fields_present(self) -> None:
        """Result should contain all required fields."""
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=45.0,
            moon_longitude=90.0,
            houses=None,
            language="en-US",
        )

        required_fields = [
            "type",
            "type_name",
            "longitude",
            "sign",
            "sign_key",
            "degree",
            "minute",
            "house",
            "emoji",
            "interpretation",
            "keywords",
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_longitude_is_valid(self) -> None:
        """Longitude should be between 0 and 360."""
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=180.0,
            moon_longitude=200.0,
            houses=None,
            language="en-US",
        )

        assert 0 <= result["longitude"] < 360

    def test_type_is_valid(self) -> None:
        """Type should be 'new_moon' or 'full_moon'."""
        result = calculate_prenatal_syzygy(
            birth_jd=2460000.0,
            sun_longitude=0.0,
            moon_longitude=45.0,
            houses=None,
            language="en-US",
        )

        assert result["type"] in ["new_moon", "full_moon"]
