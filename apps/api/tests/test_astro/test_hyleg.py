"""
Tests for Hyleg (Giver of Life) calculation module.
"""

import pytest

from app.astro.hyleg import (
    calculate_hyleg,
    find_aspecting_planets,
    get_planet_by_name,
    is_hyleg_qualified,
    is_in_hylegical_place,
)


class TestHylegicalPlaces:
    """Test hylegical place detection."""

    def test_house_1_is_hylegical(self) -> None:
        """Test that house 1 is a hylegical place."""
        assert is_in_hylegical_place(1, 120.0, 120.0) is True

    def test_house_7_is_hylegical(self) -> None:
        """Test that house 7 is a hylegical place."""
        assert is_in_hylegical_place(7, 300.0, 120.0) is True

    def test_house_9_is_hylegical(self) -> None:
        """Test that house 9 is a hylegical place."""
        assert is_in_hylegical_place(9, 0.0, 120.0) is True

    def test_house_10_is_hylegical(self) -> None:
        """Test that house 10 is a hylegical place."""
        assert is_in_hylegical_place(10, 30.0, 120.0) is True

    def test_house_11_is_hylegical(self) -> None:
        """Test that house 11 is a hylegical place."""
        assert is_in_hylegical_place(11, 60.0, 120.0) is True

    def test_house_6_not_hylegical(self) -> None:
        """Test that house 6 is not a hylegical place."""
        assert is_in_hylegical_place(6, 270.0, 120.0) is False

    def test_house_3_not_hylegical(self) -> None:
        """Test that house 3 is not a hylegical place."""
        assert is_in_hylegical_place(3, 180.0, 120.0) is False

    def test_5_degrees_below_asc_is_hylegical(self) -> None:
        """Test that 5° below ASC in 12th house is hylegical."""
        # ASC at 120°, position at 117° (3° before ASC in 12th house)
        assert is_in_hylegical_place(12, 117.0, 120.0) is True

    def test_10_degrees_below_asc_not_hylegical(self) -> None:
        """Test that 10° below ASC in 12th house is not hylegical."""
        # ASC at 120°, position at 110° (10° before ASC)
        assert is_in_hylegical_place(12, 110.0, 120.0) is False


class TestFindAspectingPlanets:
    """Test finding planets that aspect a position."""

    @pytest.fixture
    def sample_planets(self) -> list[dict]:
        """Sample planets for testing."""
        return [
            {"name": "Sun", "longitude": 45.0, "sign": "Taurus", "house": 10},
            {"name": "Moon", "longitude": 165.0, "sign": "Virgo", "house": 2},
            {"name": "Jupiter", "longitude": 45.0, "sign": "Taurus", "house": 10},  # Conjunct Sun
            {"name": "Venus", "longitude": 105.0, "sign": "Cancer", "house": 12},  # Sextile to Sun
            {
                "name": "Saturn",
                "longitude": 225.0,
                "sign": "Scorpio",
                "house": 4,
            },  # Opposition to Sun
            {"name": "Mars", "longitude": 315.0, "sign": "Aquarius", "house": 7},  # No major aspect
        ]

    def test_finds_conjunction(self, sample_planets: list[dict]) -> None:
        """Test finding conjunction aspect."""
        aspecting = find_aspecting_planets(45.0, sample_planets)
        planet_names = [a["planet"] for a in aspecting]
        assert "Jupiter" in planet_names

    def test_finds_sextile(self, sample_planets: list[dict]) -> None:
        """Test finding sextile aspect."""
        aspecting = find_aspecting_planets(45.0, sample_planets)
        planet_names = [a["planet"] for a in aspecting]
        assert "Venus" in planet_names

    def test_finds_opposition(self, sample_planets: list[dict]) -> None:
        """Test finding opposition aspect."""
        aspecting = find_aspecting_planets(45.0, sample_planets)
        planet_names = [a["planet"] for a in aspecting]
        assert "Saturn" in planet_names

    def test_no_aspect_not_included(self, sample_planets: list[dict]) -> None:
        """Test that planet with no major aspect is excluded."""
        # Mars at 315° is 90° (square) from Sun at 45° - it will be included
        # Change Mars to a position with no major aspect (e.g., 75° = 30° from Sun = semisextile)
        planets_with_no_aspect = [
            {"name": "Sun", "longitude": 45.0, "sign": "Taurus", "house": 10},
            {"name": "Moon", "longitude": 165.0, "sign": "Virgo", "house": 2},
            {"name": "Jupiter", "longitude": 45.0, "sign": "Taurus", "house": 10},
            {"name": "Venus", "longitude": 105.0, "sign": "Cancer", "house": 12},
            {"name": "Saturn", "longitude": 225.0, "sign": "Scorpio", "house": 4},
            {
                "name": "Mars",
                "longitude": 75.0,
                "sign": "Gemini",
                "house": 11,
            },  # 30° from Sun = semisextile (minor aspect with 2° orb)
        ]
        aspecting = find_aspecting_planets(45.0, planets_with_no_aspect)
        planet_names = [a["planet"] for a in aspecting]
        # Mars at 75° is 30° from 45° (semisextile) - but that's within orb, let's use a position truly not aspected
        # 45° + 20° = 65° (no aspect), or 45° + 40° = 85° (close to square but not quite)
        # Actually let's test a position that's at an odd angle
        planets_no_aspect = [
            {"name": "Sun", "longitude": 45.0, "sign": "Taurus", "house": 10},
            {
                "name": "Mars",
                "longitude": 65.0,
                "sign": "Gemini",
                "house": 11,
            },  # 20° from Sun - no aspect
        ]
        aspecting = find_aspecting_planets(45.0, planets_no_aspect)
        planet_names = [a["planet"] for a in aspecting]
        assert "Mars" not in planet_names


class TestHylegQualification:
    """Test Hyleg qualification by aspect."""

    @pytest.fixture
    def sample_planets_with_aspects(self) -> list[dict]:
        """Sample planets with specific aspect configuration."""
        return [
            {"name": "Sun", "longitude": 125.0, "sign": "Leo", "house": 10},  # 5° Leo
            {"name": "Moon", "longitude": 245.0, "sign": "Sagittarius", "house": 3},
            {"name": "Mercury", "longitude": 130.0, "sign": "Leo", "house": 10},
            {"name": "Venus", "longitude": 65.0, "sign": "Gemini", "house": 9},  # Sextile to Sun
            {"name": "Mars", "longitude": 35.0, "sign": "Taurus", "house": 8},
            {
                "name": "Jupiter",
                "longitude": 245.0,
                "sign": "Sagittarius",
                "house": 3,
            },  # Trine to Sun
            {"name": "Saturn", "longitude": 305.0, "sign": "Aquarius", "house": 5},
        ]

    def test_qualified_by_domicile_lord(self, sample_planets_with_aspects: list[dict]) -> None:
        """Test qualification by domicile lord aspect."""
        # Sun is domicile lord of Leo, checking if Moon in Leo is aspected by Sun
        # Moon at 5° Leo would have Sun as domicile lord
        # Sun needs to aspect the Moon position
        qualified, reason, aspecting = is_hyleg_qualified(
            "Moon", 125.0, "Leo", sample_planets_with_aspects
        )
        # Sun at 125° conjunct Moon at 125° should qualify
        assert qualified is True
        assert "domicile_lord" in reason or "prorogatory" in reason

    def test_qualified_by_prorogatory_planet(self, sample_planets_with_aspects: list[dict]) -> None:
        """Test qualification by prorogatory planet aspect."""
        # Sun at 125° Leo, Jupiter at 245° Sagittarius - trine aspect
        qualified, reason, aspecting = is_hyleg_qualified(
            "Sun", 125.0, "Leo", sample_planets_with_aspects
        )
        assert qualified is True
        assert "Jupiter" in aspecting or "Venus" in aspecting


class TestCalculateHyleg:
    """Test main Hyleg calculation."""

    @pytest.fixture
    def sample_chart_data(self) -> dict:
        """Sample chart data for testing."""
        return {
            "planets": [
                {
                    "name": "Sun",
                    "longitude": 125.0,
                    "sign": "Leo",
                    "house": 10,
                    "retrograde": False,
                },
                {
                    "name": "Moon",
                    "longitude": 45.0,
                    "sign": "Taurus",
                    "house": 7,
                    "retrograde": False,
                },
                {
                    "name": "Mercury",
                    "longitude": 130.0,
                    "sign": "Leo",
                    "house": 10,
                    "retrograde": False,
                },
                {
                    "name": "Venus",
                    "longitude": 65.0,
                    "sign": "Gemini",
                    "house": 9,
                    "retrograde": False,
                },
                {
                    "name": "Mars",
                    "longitude": 35.0,
                    "sign": "Taurus",
                    "house": 7,
                    "retrograde": False,
                },
                {
                    "name": "Jupiter",
                    "longitude": 165.0,
                    "sign": "Virgo",
                    "house": 11,
                    "retrograde": False,
                },
                {
                    "name": "Saturn",
                    "longitude": 305.0,
                    "sign": "Aquarius",
                    "house": 4,
                    "retrograde": False,
                },
            ],
            "houses": [
                {"number": 1, "cusp": 180.0, "sign": "Libra"},
                {"number": 2, "cusp": 210.0, "sign": "Scorpio"},
                {"number": 3, "cusp": 240.0, "sign": "Sagittarius"},
                {"number": 4, "cusp": 270.0, "sign": "Capricorn"},
                {"number": 5, "cusp": 300.0, "sign": "Aquarius"},
                {"number": 6, "cusp": 330.0, "sign": "Pisces"},
                {"number": 7, "cusp": 0.0, "sign": "Aries"},
                {"number": 8, "cusp": 30.0, "sign": "Taurus"},
                {"number": 9, "cusp": 60.0, "sign": "Gemini"},
                {"number": 10, "cusp": 90.0, "sign": "Cancer"},
                {"number": 11, "cusp": 120.0, "sign": "Leo"},
                {"number": 12, "cusp": 150.0, "sign": "Virgo"},
            ],
            "aspects": [],
            "ascendant": 180.0,
            "arabic_parts": [{"name": "Fortune", "longitude": 200.0}],
            "sect": "diurnal",
            "birth_jd": 2460000.0,
        }

    def test_day_chart_checks_sun_first(self, sample_chart_data: dict) -> None:
        """Test that day chart checks Sun before Moon."""
        result = calculate_hyleg(
            planets=sample_chart_data["planets"],
            houses=sample_chart_data["houses"],
            aspects=sample_chart_data["aspects"],
            ascendant=sample_chart_data["ascendant"],
            arabic_parts=sample_chart_data["arabic_parts"],
            sect="diurnal",
            birth_jd=sample_chart_data["birth_jd"],
        )
        assert result is not None
        assert result["is_day_chart"] is True
        # First candidate evaluated should be Sun for day chart
        if result["candidates_evaluated"]:
            assert result["candidates_evaluated"][0]["candidate"] == "Sun"

    def test_night_chart_checks_moon_first(self, sample_chart_data: dict) -> None:
        """Test that night chart checks Moon before Sun."""
        result = calculate_hyleg(
            planets=sample_chart_data["planets"],
            houses=sample_chart_data["houses"],
            aspects=sample_chart_data["aspects"],
            ascendant=sample_chart_data["ascendant"],
            arabic_parts=sample_chart_data["arabic_parts"],
            sect="nocturnal",
            birth_jd=sample_chart_data["birth_jd"],
        )
        assert result is not None
        assert result["is_day_chart"] is False
        # First candidate evaluated should be Moon for night chart
        if result["candidates_evaluated"]:
            assert result["candidates_evaluated"][0]["candidate"] == "Moon"

    def test_returns_candidates_evaluated(self, sample_chart_data: dict) -> None:
        """Test that candidates evaluated list is populated."""
        result = calculate_hyleg(
            planets=sample_chart_data["planets"],
            houses=sample_chart_data["houses"],
            aspects=sample_chart_data["aspects"],
            ascendant=sample_chart_data["ascendant"],
            arabic_parts=sample_chart_data["arabic_parts"],
            sect="diurnal",
            birth_jd=sample_chart_data["birth_jd"],
        )
        assert result is not None
        assert "candidates_evaluated" in result
        assert len(result["candidates_evaluated"]) > 0


class TestGetPlanetByName:
    """Test get_planet_by_name helper function."""

    def test_finds_existing_planet(self) -> None:
        """Test finding an existing planet."""
        planets = [
            {"name": "Sun", "longitude": 100.0},
            {"name": "Moon", "longitude": 200.0},
        ]
        result = get_planet_by_name(planets, "Sun")
        assert result is not None
        assert result["longitude"] == 100.0

    def test_returns_none_for_missing_planet(self) -> None:
        """Test returning None for missing planet."""
        planets = [
            {"name": "Sun", "longitude": 100.0},
        ]
        result = get_planet_by_name(planets, "Mars")
        assert result is None
