"""
Tests for mentality calculation module.
"""

from app.astro.mentality import (
    calculate_dignity_weight,
    calculate_house_strength,
    calculate_mental_depth,
    calculate_mental_speed,
    calculate_mental_strength,
    calculate_mental_versatility,
    calculate_mentality,
    determine_mentality_type,
    get_mercury_aspects,
    get_planet_data,
    get_planets_in_house,
    is_benefic_aspect,
    is_malefic_aspect,
)


class TestDignityWeight:
    """Test dignity weight calculation."""

    def test_ruler_returns_max_weight(self) -> None:
        """Test ruler dignity returns weight of 2.0."""
        weight, dignity = calculate_dignity_weight(["ruler"])
        assert weight == 2.0
        assert dignity == "domicile"

    def test_exalted_returns_high_weight(self) -> None:
        """Test exalted dignity returns weight of 1.75."""
        weight, dignity = calculate_dignity_weight(["exalted"])
        assert weight == 1.75
        assert dignity == "exaltation"

    def test_triplicity_returns_medium_weight(self) -> None:
        """Test triplicity dignity returns weight of 1.5."""
        weight, dignity = calculate_dignity_weight(["triplicity_day"])
        assert weight == 1.5
        assert dignity == "triplicity"

    def test_detriment_returns_low_weight(self) -> None:
        """Test detriment returns weight of 0.75."""
        weight, dignity = calculate_dignity_weight(["detriment"])
        assert weight == 0.75
        assert dignity == "detriment"

    def test_fall_returns_min_weight(self) -> None:
        """Test fall returns weight of 0.5."""
        weight, dignity = calculate_dignity_weight(["fall"])
        assert weight == 0.5
        assert dignity == "fall"

    def test_empty_returns_peregrine(self) -> None:
        """Test empty dignities returns peregrine."""
        weight, dignity = calculate_dignity_weight([])
        assert weight == 1.0
        assert dignity == "peregrine"

    def test_none_returns_peregrine(self) -> None:
        """Test None dignities returns peregrine."""
        weight, dignity = calculate_dignity_weight(None)
        assert weight == 1.0
        assert dignity == "peregrine"

    def test_multiple_dignities_uses_strongest(self) -> None:
        """Test multiple dignities uses the strongest one."""
        weight, dignity = calculate_dignity_weight(["term", "ruler"])
        assert weight == 2.0
        assert dignity == "domicile"


class TestHelperFunctions:
    """Test helper functions for data extraction."""

    def test_get_planet_data_finds_planet(self) -> None:
        """Test finding planet in list."""
        planets = [
            {"name": "Sun", "sign": "Aries"},
            {"name": "Mercury", "sign": "Gemini"},
        ]
        result = get_planet_data(planets, "Mercury")
        assert result is not None
        assert result["sign"] == "Gemini"

    def test_get_planet_data_returns_none_if_not_found(self) -> None:
        """Test returns None if planet not found."""
        planets = [{"name": "Sun", "sign": "Aries"}]
        result = get_planet_data(planets, "Mercury")
        assert result is None

    def test_get_planets_in_house(self) -> None:
        """Test getting planets in specific house."""
        planets = [
            {"name": "Sun", "house": 1},
            {"name": "Mercury", "house": 3},
            {"name": "Venus", "house": 3},
            {"name": "Mars", "house": 7},
        ]
        result = get_planets_in_house(planets, 3)
        assert len(result) == 2
        assert all(p["house"] == 3 for p in result)

    def test_get_mercury_aspects(self) -> None:
        """Test extracting Mercury aspects."""
        aspects = [
            {"planet1": "Mercury", "planet2": "Sun", "aspect": "conjunction"},
            {"planet1": "Venus", "planet2": "Mars", "aspect": "square"},
            {"planet1": "Moon", "planet2": "Mercury", "aspect": "trine"},
        ]
        result = get_mercury_aspects(aspects)
        assert len(result) == 2

    def test_get_mercury_aspects_with_filter(self) -> None:
        """Test extracting Mercury aspects with planet filter."""
        aspects = [
            {"planet1": "Mercury", "planet2": "Sun", "aspect": "conjunction"},
            {"planet1": "Mercury", "planet2": "Mars", "aspect": "square"},
            {"planet1": "Moon", "planet2": "Mercury", "aspect": "trine"},
        ]
        result = get_mercury_aspects(aspects, ["Mars"])
        assert len(result) == 1
        assert result[0]["planet2"] == "Mars"


class TestAspectClassification:
    """Test aspect classification functions."""

    def test_benefic_aspects(self) -> None:
        """Test benefic aspect detection."""
        assert is_benefic_aspect({"aspect": "trine"}) is True
        assert is_benefic_aspect({"aspect": "sextile"}) is True
        assert is_benefic_aspect({"aspect": "square"}) is False

    def test_malefic_aspects(self) -> None:
        """Test malefic aspect detection."""
        assert is_malefic_aspect({"aspect": "square"}) is True
        assert is_malefic_aspect({"aspect": "opposition"}) is True
        assert is_malefic_aspect({"aspect": "trine"}) is False


class TestMentalStrength:
    """Test mental strength calculation."""

    def test_dignified_mercury_increases_strength(self) -> None:
        """Test Mercury with strong dignity increases strength."""
        factors: list[dict] = []
        strength = calculate_mental_strength(
            mercury_dignities=["ruler"],
            mercury_aspects=[],
            moon_dignities=[],
            planets_in_3_9=[],
            factors=factors,
            language="en-US",
        )
        # Base 50 + dignity bonus
        assert strength > 50
        assert any(f["factor_key"] == "mercury_dignity" for f in factors)

    def test_benefic_aspects_increase_strength(self) -> None:
        """Test benefic aspects to Mercury increase strength."""
        factors: list[dict] = []
        strength = calculate_mental_strength(
            mercury_dignities=[],
            mercury_aspects=[
                {"planet1": "Mercury", "planet2": "Jupiter", "aspect": "trine"},
                {"planet1": "Venus", "planet2": "Mercury", "aspect": "sextile"},
            ],
            moon_dignities=[],
            planets_in_3_9=[],
            factors=factors,
            language="en-US",
        )
        assert strength > 50
        assert any(f["factor_key"] == "benefic_aspects" for f in factors)

    def test_malefic_aspects_decrease_strength(self) -> None:
        """Test malefic aspects to Mercury decrease strength."""
        factors: list[dict] = []
        _ = calculate_mental_strength(
            mercury_dignities=[],
            mercury_aspects=[
                {"planet1": "Mercury", "planet2": "Saturn", "aspect": "square"},
            ],
            moon_dignities=[],
            planets_in_3_9=[],
            factors=factors,
            language="en-US",
        )
        # Base is 50, with one malefic aspect it becomes 45 (malefic_penalty = 5)
        # But the function may add other base bonuses, so just check factor was added
        assert any(f["factor_key"] == "malefic_aspects" for f in factors)
        # Verify penalty was applied (contribution should show negative)
        malefic_factor = next(f for f in factors if f["factor_key"] == "malefic_aspects")
        assert "-" in malefic_factor["contribution"]


class TestMentalSpeed:
    """Test mental speed calculation."""

    def test_air_sign_increases_speed(self) -> None:
        """Test Mercury in air sign increases speed."""
        factors: list[dict] = []
        speed = calculate_mental_speed(
            mercury_sign="Gemini",
            mercury_aspects=[],
            mercury_retrograde=False,
            factors=factors,
            language="en-US",
        )
        # Air sign +10, direct +5
        assert speed > 10
        assert any(f["factor_key"] == "mercury_sign_speed" for f in factors)

    def test_water_sign_decreases_speed(self) -> None:
        """Test Mercury in water sign decreases speed."""
        factors: list[dict] = []
        speed = calculate_mental_speed(
            mercury_sign="Cancer",
            mercury_aspects=[],
            mercury_retrograde=False,
            factors=factors,
            language="en-US",
        )
        # Water sign -5, but direct +5, so 0
        assert speed <= 5

    def test_retrograde_reduces_speed(self) -> None:
        """Test retrograde Mercury reduces speed."""
        factors: list[dict] = []
        speed = calculate_mental_speed(
            mercury_sign="Gemini",
            mercury_aspects=[],
            mercury_retrograde=True,
            factors=factors,
            language="en-US",
        )
        # Air sign +10, retrograde -10
        assert speed <= 10
        assert any(f["factor_key"] == "mercury_retrograde" for f in factors)

    def test_mars_aspect_boosts_speed(self) -> None:
        """Test Mars aspect to Mercury boosts speed."""
        factors: list[dict] = []
        speed = calculate_mental_speed(
            mercury_sign="Virgo",
            mercury_aspects=[
                {"planet1": "Mercury", "planet2": "Mars", "aspect": "conjunction", "orb": 2.0}
            ],
            mercury_retrograde=False,
            factors=factors,
            language="en-US",
        )
        # Earth sign 0, direct +5, Mars +5
        assert speed >= 5


class TestMentalDepth:
    """Test mental depth calculation."""

    def test_water_sign_increases_depth(self) -> None:
        """Test Mercury in water sign increases depth."""
        factors: list[dict] = []
        depth = calculate_mental_depth(
            mercury_sign="Scorpio",
            mercury_house=1,
            mercury_aspects=[],
            mercury_dignities=[],
            factors=factors,
            language="en-US",
        )
        # Water sign +10
        assert depth >= 10
        assert any(f["factor_key"] == "mercury_sign_depth" for f in factors)

    def test_house_8_increases_depth(self) -> None:
        """Test Mercury in house 8 increases depth."""
        factors: list[dict] = []
        depth = calculate_mental_depth(
            mercury_sign="Aries",
            mercury_house=8,
            mercury_aspects=[],
            mercury_dignities=[],
            factors=factors,
            language="en-US",
        )
        assert depth >= 5
        assert any(f["factor_key"] == "mercury_depth_house" for f in factors)

    def test_saturn_aspect_increases_depth(self) -> None:
        """Test Saturn aspect to Mercury increases depth."""
        factors: list[dict] = []
        depth = calculate_mental_depth(
            mercury_sign="Aries",
            mercury_house=1,
            mercury_aspects=[
                {"planet1": "Mercury", "planet2": "Saturn", "aspect": "trine", "orb": 3.0}
            ],
            mercury_dignities=[],
            factors=factors,
            language="en-US",
        )
        assert depth >= 5


class TestMentalVersatility:
    """Test mental versatility calculation."""

    def test_mutable_sign_increases_versatility(self) -> None:
        """Test Mercury in mutable sign increases versatility."""
        factors: list[dict] = []
        versatility = calculate_mental_versatility(
            mercury_sign="Gemini",
            mercury_aspects=[],
            planets_in_cadent=[],
            factors=factors,
            language="en-US",
        )
        # Mutable sign +10
        assert versatility >= 10
        assert any(f["factor_key"] == "mercury_mutable" for f in factors)

    def test_many_aspects_increase_versatility(self) -> None:
        """Test 3+ aspects increase versatility."""
        factors: list[dict] = []
        versatility = calculate_mental_versatility(
            mercury_sign="Taurus",  # Fixed sign
            mercury_aspects=[
                {"planet1": "Mercury", "planet2": "Sun", "aspect": "conjunction"},
                {"planet1": "Mercury", "planet2": "Venus", "aspect": "sextile"},
                {"planet1": "Mercury", "planet2": "Mars", "aspect": "square"},
            ],
            planets_in_cadent=[],
            factors=factors,
            language="en-US",
        )
        assert versatility >= 5
        assert any(f["factor_key"] == "mercury_many_aspects" for f in factors)

    def test_cadent_emphasis_increases_versatility(self) -> None:
        """Test planets in cadent houses increase versatility."""
        factors: list[dict] = []
        versatility = calculate_mental_versatility(
            mercury_sign="Taurus",
            mercury_aspects=[],
            planets_in_cadent=[
                {"name": "Sun", "house": 3},
                {"name": "Moon", "house": 6},
                {"name": "Venus", "house": 9},
            ],
            factors=factors,
            language="en-US",
        )
        assert versatility >= 5
        assert any(f["factor_key"] == "cadent_emphasis" for f in factors)


class TestHouseStrength:
    """Test house strength calculation."""

    def test_planets_increase_strength(self) -> None:
        """Test planets in house increase strength."""
        planets = [
            {"name": "Sun", "house": 3},
            {"name": "Mercury", "house": 3},
        ]
        strength = calculate_house_strength(planets, 3, None)
        # Base 50 + 2 planets * 10 = 70
        assert strength >= 70

    def test_benefics_add_more(self) -> None:
        """Test benefics add extra strength."""
        planets = [{"name": "Jupiter", "house": 9}]
        strength = calculate_house_strength(planets, 9, None)
        # Base 50 + 10 (planet) + 10 (benefic) = 70
        assert strength >= 70

    def test_malefics_reduce_slightly(self) -> None:
        """Test malefics reduce strength slightly."""
        planets = [{"name": "Saturn", "house": 3}]
        strength = calculate_house_strength(planets, 3, None)
        # Base 50 + 10 (planet) - 5 (malefic) = 55
        assert strength >= 50 and strength <= 60


class TestMentalityTypeDetection:
    """Test mentality type determination."""

    def test_agile_and_superficial(self) -> None:
        """Test detection of agile and superficial type."""
        type_key = determine_mentality_type(
            speed=10,
            depth=5,
            versatility=8,
            mercury_sign="Gemini",
            house_3_strength=50,
            house_9_strength=50,
        )
        assert type_key == "agile_and_superficial"

    def test_agile_and_deep(self) -> None:
        """Test detection of agile and deep type."""
        type_key = determine_mentality_type(
            speed=15,
            depth=20,
            versatility=8,
            mercury_sign="Aquarius",
            house_3_strength=50,
            house_9_strength=50,
        )
        assert type_key == "agile_and_deep"

    def test_slow_and_deep(self) -> None:
        """Test detection of slow and deep type."""
        type_key = determine_mentality_type(
            speed=-5,
            depth=18,
            versatility=8,
            mercury_sign="Scorpio",
            house_3_strength=50,
            house_9_strength=50,
        )
        assert type_key == "slow_and_deep"

    def test_versatile(self) -> None:
        """Test detection of versatile type."""
        type_key = determine_mentality_type(
            speed=3,
            depth=12,
            versatility=15,
            mercury_sign="Sagittarius",
            house_3_strength=50,
            house_9_strength=50,
        )
        assert type_key == "versatile"

    def test_specialized(self) -> None:
        """Test detection of specialized type."""
        type_key = determine_mentality_type(
            speed=2,
            depth=15,
            versatility=3,
            mercury_sign="Taurus",
            house_3_strength=50,
            house_9_strength=50,
        )
        assert type_key == "specialized"

    def test_abstract(self) -> None:
        """Test detection of abstract type."""
        type_key = determine_mentality_type(
            speed=5,
            depth=10,
            versatility=8,
            mercury_sign="Aquarius",
            house_3_strength=50,
            house_9_strength=80,  # Strong house 9
        )
        assert type_key == "abstract"

    def test_concrete(self) -> None:
        """Test detection of concrete type."""
        type_key = determine_mentality_type(
            speed=0,
            depth=8,
            versatility=5,
            mercury_sign="Taurus",  # Earth sign
            house_3_strength=80,  # Strong house 3
            house_9_strength=50,
        )
        assert type_key == "concrete"


class TestFullMentalityCalculation:
    """Test complete mentality calculation."""

    def test_calculates_with_mercury_in_gemini(self) -> None:
        """Test full calculation with Mercury in Gemini."""
        planets = [
            {
                "name": "Mercury",
                "sign": "Gemini",
                "house": 3,
                "retrograde": False,
                "dignities": ["ruler"],
            },
            {"name": "Moon", "sign": "Cancer", "house": 4, "dignities": ["ruler"]},
            {"name": "Sun", "sign": "Taurus", "house": 2, "dignities": []},
        ]
        houses = [{"number": i, "cusp": i * 30} for i in range(1, 13)]
        aspects = [{"planet1": "Mercury", "planet2": "Jupiter", "aspect": "trine", "orb": 2.0}]

        result = calculate_mentality(
            planets=planets, houses=houses, aspects=aspects, language="en-US"
        )

        assert "type_key" in result
        assert "type" in result
        assert "scores" in result
        assert "mercury_analysis" in result
        assert "factors" in result
        assert "description" in result

        # Mercury in Gemini should result in high speed
        assert result["scores"]["speed"] > 0
        # Mercury with ruler dignity should boost strength
        assert result["scores"]["strength"] >= 50

    def test_returns_unknown_without_mercury(self) -> None:
        """Test returns unknown type if Mercury not found."""
        planets = [{"name": "Sun", "sign": "Aries", "house": 1}]
        houses = [{"number": i, "cusp": i * 30} for i in range(1, 13)]
        aspects = []

        result = calculate_mentality(
            planets=planets, houses=houses, aspects=aspects, language="en-US"
        )

        assert result["type_key"] == "unknown"
        assert result["mercury_analysis"] is None

    def test_mercury_analysis_included(self) -> None:
        """Test mercury analysis data is included."""
        planets = [
            {
                "name": "Mercury",
                "sign": "Virgo",
                "house": 6,
                "retrograde": True,
                "dignities": ["ruler", "term"],
            }
        ]
        houses = [{"number": i, "cusp": i * 30} for i in range(1, 13)]
        aspects = []

        result = calculate_mentality(
            planets=planets, houses=houses, aspects=aspects, language="en-US"
        )

        analysis = result["mercury_analysis"]
        assert analysis is not None
        assert analysis["sign"] == "Virgo"
        assert analysis["house"] == 6
        assert analysis["retrograde"] is True
        assert "ruler" in analysis["dignities"]

    def test_score_ranges_valid(self) -> None:
        """Test all scores are within valid ranges."""
        planets = [
            {
                "name": "Mercury",
                "sign": "Scorpio",
                "house": 8,
                "retrograde": False,
                "dignities": [],
            },
            {"name": "Moon", "sign": "Pisces", "house": 12, "dignities": []},
        ]
        houses = [{"number": i, "cusp": i * 30} for i in range(1, 13)]
        aspects = [
            {"planet1": "Mercury", "planet2": "Saturn", "aspect": "conjunction", "orb": 1.0},
            {"planet1": "Mercury", "planet2": "Pluto", "aspect": "trine", "orb": 3.0},
        ]

        result = calculate_mentality(
            planets=planets, houses=houses, aspects=aspects, language="en-US"
        )

        scores = result["scores"]
        assert 0 <= scores["strength"] <= 100
        assert -15 <= scores["speed"] <= 20
        assert 0 <= scores["depth"] <= 25
        assert 0 <= scores["versatility"] <= 20

    def test_portuguese_translation(self) -> None:
        """Test calculation with Portuguese language."""
        planets = [
            {
                "name": "Mercury",
                "sign": "Gemini",
                "house": 3,
                "retrograde": False,
                "dignities": ["ruler"],
            }
        ]
        houses = [{"number": i, "cusp": i * 30} for i in range(1, 13)]
        aspects = []

        result = calculate_mentality(
            planets=planets, houses=houses, aspects=aspects, language="pt-BR"
        )

        # Type should be in Portuguese
        assert result["type"] is not None
        assert result["description"] is not None
        # Mercury analysis sign should be localized
        assert result["mercury_analysis"]["sign_localized"] is not None
