"""
Unit tests for planetary terms (bounds) calculations.

Tests all four term systems:
- Egyptian Terms (most widely used in Hellenistic astrology)
- Ptolemaic Terms (Ptolemy's refined system)
- Chaldean Terms (regular 8-7-6-5-4 pattern)
- Dorothean Terms (Dorotheus of Sidon)
"""

import pytest

from app.astro.terms import (
    CHALDEAN_TERMS,
    DOROTHEAN_TERMS,
    EGYPTIAN_TERMS,
    PTOLEMAIC_TERMS,
    TermSystem,
    get_all_term_rulers,
    get_term_ruler,
    get_terms_table,
)

# =============================================================================
# Test Term System Constants
# =============================================================================


class TestTermSystemConstants:
    """Test that all term system constants are properly defined."""

    @pytest.mark.parametrize(
        "terms_dict",
        [EGYPTIAN_TERMS, PTOLEMAIC_TERMS, CHALDEAN_TERMS, DOROTHEAN_TERMS],
    )
    def test_all_twelve_signs_present(self, terms_dict: dict) -> None:
        """Each term system should have all 12 zodiac signs."""
        expected_signs = {
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
        }
        assert set(terms_dict.keys()) == expected_signs

    @pytest.mark.parametrize(
        "terms_dict",
        [EGYPTIAN_TERMS, PTOLEMAIC_TERMS, CHALDEAN_TERMS, DOROTHEAN_TERMS],
    )
    def test_each_sign_has_five_terms(self, terms_dict: dict) -> None:
        """Each sign should have exactly 5 terms."""
        for sign, terms in terms_dict.items():
            assert len(terms) == 5, f"{sign} should have 5 terms, got {len(terms)}"

    @pytest.mark.parametrize(
        "terms_dict",
        [EGYPTIAN_TERMS, PTOLEMAIC_TERMS, CHALDEAN_TERMS, DOROTHEAN_TERMS],
    )
    def test_terms_cover_full_30_degrees(self, terms_dict: dict) -> None:
        """Terms in each sign should cover 0-30 degrees without gaps."""
        for sign, terms in terms_dict.items():
            # First term should start at 0
            assert terms[0][0] == 0, f"{sign} first term should start at 0"
            # Last term should end at 30
            assert terms[-1][1] == 30, f"{sign} last term should end at 30"
            # Terms should be contiguous (end of one = start of next)
            for i in range(len(terms) - 1):
                assert terms[i][1] == terms[i + 1][0], (
                    f"{sign} term {i} end ({terms[i][1]}) should equal "
                    f"term {i + 1} start ({terms[i + 1][0]})"
                )

    @pytest.mark.parametrize(
        "terms_dict",
        [EGYPTIAN_TERMS, PTOLEMAIC_TERMS, CHALDEAN_TERMS, DOROTHEAN_TERMS],
    )
    def test_only_five_planets_rule_terms(self, terms_dict: dict) -> None:
        """Only Saturn, Jupiter, Mars, Venus, Mercury should rule terms (no luminaries)."""
        valid_planets = {"Saturn", "Jupiter", "Mars", "Venus", "Mercury"}
        for sign, terms in terms_dict.items():
            for _start, _end, planet in terms:
                assert planet in valid_planets, (
                    f"{sign} has invalid planet '{planet}' - "
                    "only Saturn, Jupiter, Mars, Venus, Mercury can rule terms"
                )


# =============================================================================
# Test Egyptian Terms
# =============================================================================


class TestEgyptianTerms:
    """Test Egyptian term system (most widely used)."""

    def test_aries_terms(self) -> None:
        """Test Aries Egyptian terms."""
        expected = [
            (0, 6, "Jupiter"),
            (6, 14, "Venus"),
            (14, 21, "Mercury"),
            (21, 26, "Mars"),
            (26, 30, "Saturn"),
        ]
        assert EGYPTIAN_TERMS["Aries"] == expected

    def test_taurus_terms(self) -> None:
        """Test Taurus Egyptian terms."""
        expected = [
            (0, 8, "Venus"),
            (8, 15, "Mercury"),
            (15, 22, "Jupiter"),
            (22, 27, "Saturn"),
            (27, 30, "Mars"),
        ]
        assert EGYPTIAN_TERMS["Taurus"] == expected


# =============================================================================
# Test Ptolemaic Terms
# =============================================================================


class TestPtolemaicTerms:
    """Test Ptolemaic term system (Ptolemy's refined system)."""

    def test_aries_terms(self) -> None:
        """Test Aries Ptolemaic terms - slightly different from Egyptian."""
        expected = [
            (0, 6, "Jupiter"),
            (6, 14, "Venus"),
            (14, 21, "Mercury"),
            (21, 26, "Mars"),
            (26, 30, "Saturn"),
        ]
        assert PTOLEMAIC_TERMS["Aries"] == expected

    def test_cancer_differs_from_egyptian(self) -> None:
        """Cancer Ptolemaic terms differ from Egyptian (Jupiter before Venus)."""
        # Egyptian Cancer: Mars 0-7, Venus 7-13, Mercury 13-19, Jupiter 19-26, Saturn 26-30
        # Ptolemaic Cancer: Mars 0-6, Jupiter 6-13, Mercury 13-20, Venus 20-27, Saturn 27-30
        ptolemaic_cancer = PTOLEMAIC_TERMS["Cancer"]
        egyptian_cancer = EGYPTIAN_TERMS["Cancer"]
        assert ptolemaic_cancer != egyptian_cancer


# =============================================================================
# Test Chaldean Terms
# =============================================================================


class TestChaldeanTerms:
    """Test Chaldean term system (regular 8-7-6-5-4 pattern)."""

    def test_regular_8_7_6_5_4_pattern(self) -> None:
        """Chaldean terms should follow the 8-7-6-5-4 degree pattern."""
        for sign, terms in CHALDEAN_TERMS.items():
            degrees = [end - start for start, end, _ in terms]
            assert degrees == [
                8,
                7,
                6,
                5,
                4,
            ], f"{sign} should have 8-7-6-5-4 degree pattern, got {degrees}"

    def test_fire_signs_jupiter_first(self) -> None:
        """Fire signs (Aries, Leo, Sagittarius) should have Jupiter first."""
        for sign in ["Aries", "Leo", "Sagittarius"]:
            first_ruler = CHALDEAN_TERMS[sign][0][2]
            assert (
                first_ruler == "Jupiter"
            ), f"{sign} (fire sign) should have Jupiter first, got {first_ruler}"

    def test_earth_signs_venus_first(self) -> None:
        """Earth signs (Taurus, Virgo, Capricorn) should have Venus first."""
        for sign in ["Taurus", "Virgo", "Capricorn"]:
            first_ruler = CHALDEAN_TERMS[sign][0][2]
            assert (
                first_ruler == "Venus"
            ), f"{sign} (earth sign) should have Venus first, got {first_ruler}"

    def test_air_signs_pattern(self) -> None:
        """Air signs should follow the Chaldean air triplicity pattern."""
        # Gemini: Mercury first (triplicity ruler)
        # Libra: Saturn first (triplicity ruler)
        # Aquarius: Saturn first (triplicity ruler)
        assert CHALDEAN_TERMS["Gemini"][0][2] == "Mercury"
        assert CHALDEAN_TERMS["Libra"][0][2] == "Saturn"
        assert CHALDEAN_TERMS["Aquarius"][0][2] == "Saturn"

    def test_water_signs_mars_first(self) -> None:
        """Water signs (Cancer, Scorpio, Pisces) should have Mars first."""
        for sign in ["Cancer", "Scorpio"]:
            first_ruler = CHALDEAN_TERMS[sign][0][2]
            assert (
                first_ruler == "Mars"
            ), f"{sign} (water sign) should have Mars first, got {first_ruler}"
        # Pisces is an exception - Venus first
        assert CHALDEAN_TERMS["Pisces"][0][2] == "Venus"


# =============================================================================
# Test get_term_ruler() Function
# =============================================================================


class TestGetTermRuler:
    """Test get_term_ruler() function for looking up term rulers."""

    def test_aries_0_degrees_egyptian(self) -> None:
        """0° Aries should be in Jupiter's term (Egyptian)."""
        result = get_term_ruler(0.0, TermSystem.EGYPTIAN)
        assert result["term_ruler"] == "Jupiter"
        assert result["sign"] == "Aries"
        assert result["term_start"] == 0
        assert result["term_end"] == 6

    def test_aries_5_degrees_egyptian(self) -> None:
        """5° Aries should still be in Jupiter's term (Egyptian)."""
        result = get_term_ruler(5.0, TermSystem.EGYPTIAN)
        assert result["term_ruler"] == "Jupiter"

    def test_aries_6_degrees_changes_term(self) -> None:
        """6° Aries should be in Venus's term (boundary condition)."""
        result = get_term_ruler(6.0, TermSystem.EGYPTIAN)
        assert result["term_ruler"] == "Venus"
        assert result["term_start"] == 6
        assert result["term_end"] == 14

    def test_taurus_15_degrees_egyptian(self) -> None:
        """15° Taurus (45° longitude) should be in Jupiter's term (Egyptian)."""
        result = get_term_ruler(45.0, TermSystem.EGYPTIAN)
        assert result["term_ruler"] == "Jupiter"
        assert result["sign"] == "Taurus"
        assert result["degree_in_sign"] == 15.0

    def test_longitude_conversion(self) -> None:
        """Test longitude to sign/degree conversion."""
        # 90° = 0° Cancer
        result = get_term_ruler(90.0, TermSystem.EGYPTIAN)
        assert result["sign"] == "Cancer"
        assert result["degree_in_sign"] == 0.0
        assert result["term_ruler"] == "Mars"

    def test_ptolemaic_system(self) -> None:
        """Test Ptolemaic term lookup."""
        # 96° = 6° Cancer - should be Jupiter in Ptolemaic (not Venus as in Egyptian)
        result = get_term_ruler(96.0, TermSystem.PTOLEMAIC)
        assert result["sign"] == "Cancer"
        assert result["term_system"] == TermSystem.PTOLEMAIC
        assert result["term_ruler"] == "Jupiter"

    def test_chaldean_system(self) -> None:
        """Test Chaldean term lookup."""
        # 0° Aries - should be Jupiter with 8-degree term
        result = get_term_ruler(0.0, TermSystem.CHALDEAN)
        assert result["term_ruler"] == "Jupiter"
        assert result["term_end"] == 8  # Chaldean has 8° first term

    def test_end_of_sign_boundary(self) -> None:
        """Test 29.99° (end of sign)."""
        result = get_term_ruler(29.99, TermSystem.EGYPTIAN)
        assert result["sign"] == "Aries"
        assert result["term_ruler"] == "Saturn"  # Last term in Aries

    def test_pisces_last_degrees(self) -> None:
        """Test last degrees of Pisces (359°)."""
        result = get_term_ruler(359.0, TermSystem.EGYPTIAN)
        assert result["sign"] == "Pisces"
        assert result["degree_in_sign"] == 29.0
        assert result["term_ruler"] == "Saturn"  # Last term in Pisces

    def test_invalid_longitude_negative(self) -> None:
        """Negative longitude should raise ValueError."""
        with pytest.raises(ValueError):
            get_term_ruler(-1.0, TermSystem.EGYPTIAN)

    def test_invalid_longitude_too_high(self) -> None:
        """Longitude >= 360 should raise ValueError."""
        with pytest.raises(ValueError):
            get_term_ruler(360.0, TermSystem.EGYPTIAN)


# =============================================================================
# Test get_all_term_rulers() Function
# =============================================================================


class TestGetAllTermRulers:
    """Test get_all_term_rulers() function for chart-wide term analysis."""

    @pytest.fixture
    def sample_planets(self) -> list[dict]:
        """Sample planet positions for testing."""
        return [
            {"name": "Sun", "longitude": 45.0, "sign": "Taurus"},  # 15° Taurus
            {"name": "Moon", "longitude": 120.0, "sign": "Leo"},  # 0° Leo
            {"name": "Mercury", "longitude": 65.0, "sign": "Gemini"},  # 5° Gemini
            {"name": "Venus", "longitude": 35.0, "sign": "Taurus"},  # 5° Taurus
            {"name": "Mars", "longitude": 200.0, "sign": "Libra"},  # 20° Libra
            {"name": "Jupiter", "longitude": 270.0, "sign": "Capricorn"},  # 0° Cap
            {"name": "Saturn", "longitude": 310.0, "sign": "Aquarius"},  # 10° Aqua
        ]

    def test_returns_all_planets(self, sample_planets: list[dict]) -> None:
        """Should return term info for all planets."""
        result = get_all_term_rulers(sample_planets, TermSystem.EGYPTIAN)
        assert len(result["planets"]) == 7
        planet_names = [p["planet"] for p in result["planets"]]
        assert "Sun" in planet_names
        assert "Moon" in planet_names
        assert "Saturn" in planet_names

    def test_identifies_planets_in_own_term(self, sample_planets: list[dict]) -> None:
        """Should identify when a planet is in its own term."""
        result = get_all_term_rulers(sample_planets, TermSystem.EGYPTIAN)

        # Venus at 5° Taurus is in Venus's term (0-8° Taurus)
        venus_info = next(p for p in result["planets"] if p["planet"] == "Venus")
        assert venus_info["in_own_term"] is True
        assert venus_info["term_ruler"] == "Venus"

    def test_summary_planets_in_own_term(self, sample_planets: list[dict]) -> None:
        """Summary should list planets in their own term."""
        result = get_all_term_rulers(sample_planets, TermSystem.EGYPTIAN)
        assert "Venus" in result["summary"]["planets_in_own_term"]

    def test_summary_term_ruler_frequency(self, sample_planets: list[dict]) -> None:
        """Summary should count term ruler frequency."""
        result = get_all_term_rulers(sample_planets, TermSystem.EGYPTIAN)
        freq = result["summary"]["term_ruler_frequency"]
        assert isinstance(freq, dict)
        # All values should be positive integers
        for _planet, count in freq.items():
            assert isinstance(count, int)
            assert count > 0

    def test_system_in_response(self, sample_planets: list[dict]) -> None:
        """Response should include the term system used."""
        result = get_all_term_rulers(sample_planets, TermSystem.PTOLEMAIC)
        assert result["system"] == TermSystem.PTOLEMAIC

    def test_empty_planets_list(self) -> None:
        """Should handle empty planets list."""
        result = get_all_term_rulers([], TermSystem.EGYPTIAN)
        assert result["planets"] == []
        assert result["summary"]["planets_in_own_term"] == []


# =============================================================================
# Test get_terms_table() Function
# =============================================================================


class TestGetTermsTable:
    """Test get_terms_table() function for reference display."""

    def test_returns_all_signs(self) -> None:
        """Should return terms for all 12 signs."""
        result = get_terms_table(TermSystem.EGYPTIAN)
        assert len(result["signs"]) == 12

    def test_each_sign_has_five_entries(self) -> None:
        """Each sign should have 5 term entries."""
        result = get_terms_table(TermSystem.EGYPTIAN)
        for sign, terms in result["signs"].items():
            assert len(terms) == 5, f"{sign} should have 5 terms"

    def test_term_entry_structure(self) -> None:
        """Each term entry should have ruler, start, and end."""
        result = get_terms_table(TermSystem.EGYPTIAN)
        aries_terms = result["signs"]["Aries"]
        for term in aries_terms:
            assert "ruler" in term
            assert "start" in term
            assert "end" in term

    def test_includes_system_in_response(self) -> None:
        """Response should include the term system."""
        result = get_terms_table(TermSystem.CHALDEAN)
        assert result["system"] == TermSystem.CHALDEAN

    def test_different_systems_return_different_data(self) -> None:
        """Different term systems should return different data."""
        egyptian = get_terms_table(TermSystem.EGYPTIAN)
        ptolemaic = get_terms_table(TermSystem.PTOLEMAIC)
        chaldean = get_terms_table(TermSystem.CHALDEAN)

        # Cancer differs between Egyptian and Ptolemaic
        assert egyptian["signs"]["Cancer"] != ptolemaic["signs"]["Cancer"]

        # Chaldean has regular 8-7-6-5-4 pattern, others don't
        aries_chaldean = chaldean["signs"]["Aries"]
        degrees = [t["end"] - t["start"] for t in aries_chaldean]
        assert degrees == [8, 7, 6, 5, 4]


# =============================================================================
# Test TermSystem Enum
# =============================================================================


class TestTermSystemEnum:
    """Test TermSystem enumeration."""

    def test_all_systems_defined(self) -> None:
        """All four term systems should be defined."""
        assert TermSystem.EGYPTIAN.value == "egyptian"
        assert TermSystem.PTOLEMAIC.value == "ptolemaic"
        assert TermSystem.CHALDEAN.value == "chaldean"
        assert TermSystem.DOROTHEAN.value == "dorothean"

    def test_enum_is_string_enum(self) -> None:
        """TermSystem should be a string enum for JSON serialization."""
        assert isinstance(TermSystem.EGYPTIAN.value, str)
        assert str(TermSystem.EGYPTIAN) == "TermSystem.EGYPTIAN"
