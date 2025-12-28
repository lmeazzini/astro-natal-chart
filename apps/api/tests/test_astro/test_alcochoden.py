"""
Tests for Alcochoden (Giver of Years) calculation module.
"""

import pytest

from app.astro.alcochoden import (
    ANGULAR_HOUSES,
    CADENT_HOUSES,
    PLANETARY_YEARS,
    SUCCEDENT_HOUSES,
    calculate_alcochoden,
    calculate_house_modification,
    determine_year_type,
    find_alcochoden_candidates,
    get_dignities_at_position,
    get_house_type,
    is_combust,
    is_in_detriment,
    is_in_domicile,
    is_in_exaltation,
    is_in_fall,
)


class TestPlanetaryYears:
    """Test planetary years constants."""

    def test_all_classical_planets_have_years(self) -> None:
        """Test that all classical planets have year values."""
        classical_planets = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        for planet in classical_planets:
            assert planet in PLANETARY_YEARS
            assert "minor" in PLANETARY_YEARS[planet]
            assert "middle" in PLANETARY_YEARS[planet]
            assert "major" in PLANETARY_YEARS[planet]

    def test_saturn_years(self) -> None:
        """Test Saturn's years values."""
        assert PLANETARY_YEARS["Saturn"]["minor"] == 30
        assert PLANETARY_YEARS["Saturn"]["middle"] == 43.5
        assert PLANETARY_YEARS["Saturn"]["major"] == 57

    def test_jupiter_years(self) -> None:
        """Test Jupiter's years values."""
        assert PLANETARY_YEARS["Jupiter"]["minor"] == 12
        assert PLANETARY_YEARS["Jupiter"]["middle"] == 45.5
        assert PLANETARY_YEARS["Jupiter"]["major"] == 79


class TestDignityAtPosition:
    """Test finding dignities at a specific position."""

    def test_finds_domicile_ruler(self) -> None:
        """Test finding domicile ruler at position."""
        # 15° Taurus - Venus is domicile ruler
        result = get_dignities_at_position(45.0, "Taurus", 15.0, "diurnal")
        assert result["domicile"] == "Venus"

    def test_finds_exaltation_ruler(self) -> None:
        """Test finding exaltation ruler at position."""
        # 3° Taurus - Moon is exalted here
        result = get_dignities_at_position(33.0, "Taurus", 3.0, "nocturnal")
        assert result["exaltation"] == "Moon"

    def test_finds_term_ruler(self) -> None:
        """Test finding term ruler at position."""
        # 10° Taurus - Mercury rules the term (8-15° Taurus)
        result = get_dignities_at_position(40.0, "Taurus", 10.0, "diurnal")
        assert result["term"] == "Mercury"

    def test_finds_face_ruler(self) -> None:
        """Test finding face ruler at position."""
        # 5° Taurus - Mercury rules the first face (0-10° Taurus)
        result = get_dignities_at_position(35.0, "Taurus", 5.0, "diurnal")
        assert result["face"] == "Mercury"


class TestCombustion:
    """Test combustion detection."""

    def test_planet_conjunct_sun_is_combust(self) -> None:
        """Test planet very close to Sun is combust."""
        assert is_combust(100.0, 103.0, "Venus") is True

    def test_planet_far_from_sun_not_combust(self) -> None:
        """Test planet far from Sun is not combust."""
        assert is_combust(100.0, 200.0, "Venus") is False

    def test_sun_cannot_be_combust(self) -> None:
        """Test Sun cannot be combust by itself."""
        assert is_combust(100.0, 100.0, "Sun") is False

    def test_planet_exactly_8_degrees_is_combust(self) -> None:
        """Test planet at exactly 8° from Sun is combust."""
        assert is_combust(100.0, 108.0, "Mars") is True

    def test_planet_slightly_beyond_8_degrees_not_combust(self) -> None:
        """Test planet at 8.5° from Sun is not combust."""
        assert is_combust(100.0, 108.5, "Mars") is False


class TestDignityConditions:
    """Test dignity condition checks."""

    def test_sun_in_leo_is_domicile(self) -> None:
        """Test Sun in Leo is in domicile."""
        assert is_in_domicile("Sun", "Leo") is True

    def test_sun_in_aries_not_domicile(self) -> None:
        """Test Sun in Aries is not in domicile."""
        assert is_in_domicile("Sun", "Aries") is False

    def test_sun_in_aries_is_exalted(self) -> None:
        """Test Sun in Aries is exalted."""
        assert is_in_exaltation("Sun", "Aries") is True

    def test_sun_in_leo_not_exalted(self) -> None:
        """Test Sun in Leo is not exalted (it's domicile)."""
        assert is_in_exaltation("Sun", "Leo") is False

    def test_sun_in_aquarius_is_detriment(self) -> None:
        """Test Sun in Aquarius is in detriment."""
        assert is_in_detriment("Sun", "Aquarius") is True

    def test_sun_in_libra_is_fall(self) -> None:
        """Test Sun in Libra is in fall."""
        assert is_in_fall("Sun", "Libra") is True

    def test_jupiter_in_capricorn_is_fall(self) -> None:
        """Test Jupiter in Capricorn is in fall."""
        assert is_in_fall("Jupiter", "Capricorn") is True


class TestYearTypeDetermination:
    """Test year type determination based on planet condition."""

    def test_debilitated_planet_gets_minor_years(self) -> None:
        """Test debilitated planet gets minor years."""
        planet = {"name": "Sun", "sign": "Aquarius", "longitude": 315.0}
        year_type = determine_year_type(planet, 200.0)  # Sun far away
        assert year_type == "minor"

    def test_combust_planet_gets_minor_years(self) -> None:
        """Test combust planet gets minor years."""
        planet = {"name": "Venus", "sign": "Taurus", "longitude": 45.0}
        year_type = determine_year_type(planet, 48.0)  # Sun at 48°, Venus combust
        assert year_type == "minor"

    def test_dignified_planet_gets_major_years(self) -> None:
        """Test dignified planet gets major years."""
        planet = {"name": "Sun", "sign": "Leo", "longitude": 125.0}
        year_type = determine_year_type(planet, 125.0)  # Same position as Sun
        # Sun in Leo is dignified
        assert year_type == "major"

    def test_peregrine_planet_gets_middle_years(self) -> None:
        """Test peregrine planet gets middle years."""
        planet = {"name": "Mars", "sign": "Gemini", "longitude": 75.0}
        year_type = determine_year_type(planet, 200.0)  # Sun far away
        # Mars in Gemini is peregrine (no major dignity or debility)
        assert year_type == "middle"


class TestHouseModification:
    """Test house position modifications."""

    def test_angular_house_adds_3(self) -> None:
        """Test angular house adds 3 years."""
        for house in ANGULAR_HOUSES:
            mod, house_type = calculate_house_modification(house)
            assert mod == 3
            assert house_type == "angular"

    def test_succedent_house_adds_1(self) -> None:
        """Test succedent house adds 1 year."""
        for house in SUCCEDENT_HOUSES:
            mod, house_type = calculate_house_modification(house)
            assert mod == 1
            assert house_type == "succedent"

    def test_cadent_house_subtracts_2(self) -> None:
        """Test cadent house subtracts 2 years."""
        for house in CADENT_HOUSES:
            mod, house_type = calculate_house_modification(house)
            assert mod == -2
            assert house_type == "cadent"

    def test_get_house_type(self) -> None:
        """Test house type classification."""
        assert get_house_type(1) == "angular"
        assert get_house_type(2) == "succedent"
        assert get_house_type(3) == "cadent"
        assert get_house_type(10) == "angular"


class TestFindAlcochodenCandidates:
    """Test finding Alcochoden candidates."""

    @pytest.fixture
    def sample_planets(self) -> list[dict]:
        """Sample planets for testing."""
        return [
            {"name": "Sun", "longitude": 125.0, "sign": "Leo", "house": 10, "retrograde": False},
            {"name": "Moon", "longitude": 45.0, "sign": "Taurus", "house": 7, "retrograde": False},
            {"name": "Venus", "longitude": 65.0, "sign": "Gemini", "house": 9, "retrograde": False},
            {
                "name": "Mars",
                "longitude": 285.0,
                "sign": "Capricorn",
                "house": 4,
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
                "longitude": 315.0,
                "sign": "Aquarius",
                "house": 5,
                "retrograde": False,
            },
            {
                "name": "Mercury",
                "longitude": 130.0,
                "sign": "Leo",
                "house": 10,
                "retrograde": False,
            },
        ]

    def test_excludes_hyleg_planet(self, sample_planets: list[dict]) -> None:
        """Test that Hyleg planet is excluded from candidates."""
        # Hyleg is Moon at 45° Taurus
        # Venus is domicile ruler of Taurus
        candidates = find_alcochoden_candidates(
            hyleg_longitude=45.0,
            hyleg_sign="Taurus",
            hyleg_name="Moon",  # Moon is the Hyleg
            planets=sample_planets,
            sect="nocturnal",
        )
        # Moon should not be in candidates
        planet_names = [c["planet"] for c in candidates]
        assert "Moon" not in planet_names

    def test_returns_sorted_by_dignity_points(self, sample_planets: list[dict]) -> None:
        """Test that candidates are sorted by dignity points."""
        candidates = find_alcochoden_candidates(
            hyleg_longitude=45.0,
            hyleg_sign="Taurus",
            hyleg_name="Ascendant",  # Use point so no planet is excluded
            planets=sample_planets,
            sect="diurnal",
        )
        if len(candidates) > 1:
            # Should be sorted descending by total_dignity_points
            for i in range(len(candidates) - 1):
                assert (
                    candidates[i]["total_dignity_points"]
                    >= candidates[i + 1]["total_dignity_points"]
                )


class TestCalculateAlcochoden:
    """Test main Alcochoden calculation."""

    @pytest.fixture
    def sample_hyleg(self) -> dict:
        """Sample Hyleg data."""
        return {
            "hyleg": "Moon",
            "hyleg_longitude": 45.0,
            "hyleg_sign": "Taurus",
            "hyleg_house": 7,
        }

    @pytest.fixture
    def sample_planets(self) -> list[dict]:
        """Sample planets for testing."""
        return [
            {"name": "Sun", "longitude": 125.0, "sign": "Leo", "house": 10, "retrograde": False},
            {"name": "Moon", "longitude": 45.0, "sign": "Taurus", "house": 7, "retrograde": False},
            {
                "name": "Venus",
                "longitude": 105.0,
                "sign": "Cancer",
                "house": 9,
                "retrograde": False,
            },  # Sextile Moon
            {
                "name": "Mars",
                "longitude": 285.0,
                "sign": "Capricorn",
                "house": 4,
                "retrograde": False,
            },
            {
                "name": "Jupiter",
                "longitude": 165.0,
                "sign": "Virgo",
                "house": 11,
                "retrograde": False,
            },  # Trine Moon
            {
                "name": "Saturn",
                "longitude": 315.0,
                "sign": "Aquarius",
                "house": 5,
                "retrograde": False,
            },
            {
                "name": "Mercury",
                "longitude": 130.0,
                "sign": "Leo",
                "house": 10,
                "retrograde": False,
            },
        ]

    @pytest.fixture
    def sample_houses(self) -> list[dict]:
        """Sample house cusps."""
        return [{"number": i, "cusp": (i - 1) * 30.0, "sign": "Aries"} for i in range(1, 13)]

    def test_returns_none_when_no_hyleg(
        self, sample_planets: list[dict], sample_houses: list[dict]
    ) -> None:
        """Test that None fields are returned when no Hyleg."""
        result = calculate_alcochoden(
            hyleg_data=None,
            planets=sample_planets,
            houses=sample_houses,
            aspects=[],
            sun_longitude=125.0,
            sect="diurnal",
        )
        assert result["alcochoden"] is None
        assert result["no_alcochoden_reason"] is not None

    def test_returns_none_when_hyleg_is_none(
        self, sample_planets: list[dict], sample_houses: list[dict]
    ) -> None:
        """Test when Hyleg data has hyleg=None."""
        hyleg_data = {"hyleg": None}
        result = calculate_alcochoden(
            hyleg_data=hyleg_data,
            planets=sample_planets,
            houses=sample_houses,
            aspects=[],
            sun_longitude=125.0,
            sect="diurnal",
        )
        assert result["alcochoden"] is None

    def test_includes_planetary_years(
        self,
        sample_hyleg: dict,
        sample_planets: list[dict],
        sample_houses: list[dict],
    ) -> None:
        """Test that result includes planetary years table."""
        result = calculate_alcochoden(
            hyleg_data=sample_hyleg,
            planets=sample_planets,
            houses=sample_houses,
            aspects=[],
            sun_longitude=125.0,
            sect="diurnal",
        )
        if result["alcochoden"]:
            assert "years" in result
            assert "minor" in result["years"]
            assert "middle" in result["years"]
            assert "major" in result["years"]

    def test_includes_modifications(
        self,
        sample_hyleg: dict,
        sample_planets: list[dict],
        sample_houses: list[dict],
    ) -> None:
        """Test that result includes modifications list."""
        result = calculate_alcochoden(
            hyleg_data=sample_hyleg,
            planets=sample_planets,
            houses=sample_houses,
            aspects=[],
            sun_longitude=125.0,
            sect="diurnal",
        )
        if result["alcochoden"]:
            assert "modifications" in result
            assert isinstance(result["modifications"], list)
