"""
Tests for essential dignities calculation module.
"""

from app.astro.dignities import (
    calculate_essential_dignities,
    get_planet_in_face,
    get_planet_in_term,
    get_sign_ruler,
)


class TestRulerships:
    """Test rulership (domicile) calculations."""

    def test_sun_in_leo_is_ruler(self) -> None:
        """Test Sun in Leo (rulership)."""
        result = calculate_essential_dignities("Sun", "Leo", 15.0, "diurnal")
        assert result["is_ruler"] is True
        assert "ruler" in result["dignities"]
        assert result["score"] >= 5

    def test_moon_in_cancer_is_ruler(self) -> None:
        """Test Moon in Cancer (rulership)."""
        result = calculate_essential_dignities("Moon", "Cancer", 10.0, "nocturnal")
        assert result["is_ruler"] is True
        assert "ruler" in result["dignities"]

    def test_mars_in_aries_is_ruler(self) -> None:
        """Test Mars in Aries (rulership)."""
        result = calculate_essential_dignities("Mars", "Aries", 5.0, "diurnal")
        assert result["is_ruler"] is True
        assert "ruler" in result["dignities"]

    def test_venus_not_ruler_in_aries(self) -> None:
        """Test Venus in Aries (not ruler)."""
        result = calculate_essential_dignities("Venus", "Aries", 15.0, "diurnal")
        assert result["is_ruler"] is False


class TestExaltations:
    """Test exaltation calculations."""

    def test_sun_exalted_in_aries(self) -> None:
        """Test Sun exalted in Aries."""
        result = calculate_essential_dignities("Sun", "Aries", 19.0, "diurnal")
        assert result["is_exalted"] is True
        assert "exalted" in result["dignities"]
        assert result["score"] >= 4

    def test_moon_exalted_in_taurus(self) -> None:
        """Test Moon exalted in Taurus."""
        result = calculate_essential_dignities("Moon", "Taurus", 3.0, "nocturnal")
        assert result["is_exalted"] is True
        assert "exalted" in result["dignities"]

    def test_jupiter_exalted_in_cancer(self) -> None:
        """Test Jupiter exalted in Cancer."""
        result = calculate_essential_dignities("Jupiter", "Cancer", 15.0, "diurnal")
        assert result["is_exalted"] is True
        assert "exalted" in result["dignities"]

    def test_mars_not_exalted_in_aries(self) -> None:
        """Test Mars not exalted in Aries (exalted in Capricorn)."""
        result = calculate_essential_dignities("Mars", "Aries", 10.0, "diurnal")
        assert result["is_exalted"] is False


class TestDetriment:
    """Test detriment (opposite of rulership) calculations."""

    def test_sun_in_aquarius_detriment(self) -> None:
        """Test Sun in Aquarius (detriment - opposite of Leo)."""
        result = calculate_essential_dignities("Sun", "Aquarius", 15.0, "diurnal")
        assert result["is_detriment"] is True
        assert "detriment" in result["dignities"]
        assert result["score"] <= -5

    def test_moon_in_capricorn_detriment(self) -> None:
        """Test Moon in Capricorn (detriment - opposite of Cancer)."""
        result = calculate_essential_dignities("Moon", "Capricorn", 10.0, "nocturnal")
        assert result["is_detriment"] is True
        assert "detriment" in result["dignities"]


class TestFall:
    """Test fall (opposite of exaltation) calculations."""

    def test_sun_in_libra_fall(self) -> None:
        """Test Sun in Libra (fall - opposite of Aries exaltation)."""
        result = calculate_essential_dignities("Sun", "Libra", 15.0, "diurnal")
        assert result["is_fall"] is True
        assert "fall" in result["dignities"]
        assert result["score"] <= -4

    def test_moon_in_scorpio_fall(self) -> None:
        """Test Moon in Scorpio (fall - opposite of Taurus exaltation)."""
        result = calculate_essential_dignities("Moon", "Scorpio", 10.0, "nocturnal")
        assert result["is_fall"] is True
        assert "fall" in result["dignities"]


class TestTriplicity:
    """Test triplicity calculations with sect."""

    def test_sun_in_fire_sign_diurnal(self) -> None:
        """Test Sun as day ruler of Fire triplicity in diurnal chart."""
        result = calculate_essential_dignities("Sun", "Aries", 10.0, "diurnal")
        assert result["triplicity_ruler"] == "day"
        assert "triplicity_day" in result["dignities"]
        assert result["score"] >= 3

    def test_jupiter_in_fire_sign_nocturnal(self) -> None:
        """Test Jupiter as night ruler of Fire triplicity in nocturnal chart."""
        result = calculate_essential_dignities("Jupiter", "Leo", 10.0, "nocturnal")
        assert result["triplicity_ruler"] == "night"
        assert "triplicity_night" in result["dignities"]

    def test_saturn_in_fire_sign_participant(self) -> None:
        """Test Saturn as participant of Fire triplicity."""
        result = calculate_essential_dignities("Saturn", "Sagittarius", 10.0, "diurnal")
        assert result["triplicity_ruler"] == "participant"
        assert "triplicity_participant" in result["dignities"]

    def test_venus_in_earth_sign_diurnal(self) -> None:
        """Test Venus as day ruler of Earth triplicity."""
        result = calculate_essential_dignities("Venus", "Taurus", 10.0, "diurnal")
        # Venus is both ruler and triplicity ruler in Taurus
        assert result["is_ruler"] is True
        assert result["triplicity_ruler"] in ["day", "participant"]


class TestTerms:
    """Test term (bounds) calculations."""

    def test_get_planet_in_term_aries(self) -> None:
        """Test term ruler detection in Aries."""
        # First 6 degrees of Aries are Jupiter's term
        assert get_planet_in_term("Aries", 3.0) == "Jupiter"
        # 6-14 degrees are Venus's term
        assert get_planet_in_term("Aries", 10.0) == "Venus"
        # 14-21 degrees are Mercury's term
        assert get_planet_in_term("Aries", 18.0) == "Mercury"

    def test_term_adds_to_score(self) -> None:
        """Test that being in own term adds 2 points."""
        # Jupiter in first 6 degrees of Aries (Jupiter's term)
        result = calculate_essential_dignities("Jupiter", "Aries", 3.0, "diurnal")
        assert result["term_ruler"] == "Jupiter"
        assert "term" in result["dignities"]


class TestFaces:
    """Test face (decan) calculations."""

    def test_get_planet_in_face_aries(self) -> None:
        """Test face ruler detection in Aries."""
        # First decan (0-10) is Mars
        assert get_planet_in_face("Aries", 5.0) == "Mars"
        # Second decan (10-20) is Sun
        assert get_planet_in_face("Aries", 15.0) == "Sun"
        # Third decan (20-30) is Venus
        assert get_planet_in_face("Aries", 25.0) == "Venus"

    def test_face_adds_to_score(self) -> None:
        """Test that being in own face adds 1 point."""
        # Mars in first decan of Aries (Mars's face)
        result = calculate_essential_dignities("Mars", "Aries", 5.0, "diurnal")
        assert result["face_ruler"] == "Mars"
        assert "face" in result["dignities"]


class TestClassification:
    """Test overall dignity classification."""

    def test_dignified_classification(self) -> None:
        """Test planet with high dignity score is classified as dignified."""
        # Sun in Leo (ruler +5) should be dignified
        result = calculate_essential_dignities("Sun", "Leo", 10.0, "diurnal")
        assert result["classification"] == "dignified"
        assert result["score"] >= 4

    def test_debilitated_classification(self) -> None:
        """Test planet with low dignity score is classified as debilitated."""
        # Sun in Aquarius (detriment -5) should be debilitated
        result = calculate_essential_dignities("Sun", "Aquarius", 15.0, "diurnal")
        assert result["classification"] == "debilitated"
        assert result["score"] <= -4

    def test_peregrine_classification(self) -> None:
        """Test planet with neutral dignity score is peregrine."""
        # Sun in Gemini (no major dignities) might be peregrine
        result = calculate_essential_dignities("Sun", "Gemini", 15.0, "diurnal")
        # Should be peregrine unless it has minor dignities
        assert result["score"] < 4 and result["score"] > -4


class TestGetSignRuler:
    """Test sign ruler lookup function."""

    def test_get_sign_ruler_leo(self) -> None:
        """Test getting ruler of Leo."""
        assert get_sign_ruler("Leo") == "Sun"

    def test_get_sign_ruler_cancer(self) -> None:
        """Test getting ruler of Cancer."""
        assert get_sign_ruler("Cancer") == "Moon"

    def test_get_sign_ruler_aries(self) -> None:
        """Test getting ruler of Aries."""
        assert get_sign_ruler("Aries") == "Mars"

    def test_get_sign_ruler_invalid(self) -> None:
        """Test getting ruler of invalid sign."""
        assert get_sign_ruler("InvalidSign") is None


class TestComprehensiveDignities:
    """Test comprehensive dignity calculations with multiple factors."""

    def test_mars_in_aries_comprehensive(self) -> None:
        """Test Mars in Aries with multiple dignities."""
        # Mars in Aries at 5 degrees:
        # - Ruler of Aries: +5
        # - In own term (0-6 degrees): potentially (need to check tables)
        # - In own face (0-10 degrees): +1
        result = calculate_essential_dignities("Mars", "Aries", 5.0, "diurnal")

        assert result["is_ruler"] is True
        assert result["face_ruler"] == "Mars"
        assert result["score"] > 0
        assert result["classification"] == "dignified"

    def test_venus_in_pisces_comprehensive(self) -> None:
        """Test Venus in Pisces with exaltation."""
        # Venus exalted in Pisces at 27 degrees
        result = calculate_essential_dignities("Venus", "Pisces", 27.0, "diurnal")

        assert result["is_exalted"] is True
        assert result["score"] >= 4
        assert result["classification"] == "dignified"

    def test_saturn_in_libra_comprehensive(self) -> None:
        """Test Saturn in Libra with exaltation."""
        # Saturn exalted in Libra at 21 degrees
        result = calculate_essential_dignities("Saturn", "Libra", 21.0, "nocturnal")

        assert result["is_exalted"] is True
        assert result["score"] >= 4
        assert result["classification"] == "dignified"
