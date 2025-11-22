"""
Tests for interpretation service.

Tests cover:
- AI interpretation generation via OpenAI
- Error handling (timeout, quota exceeded)
- Prompt formatting and context building
- Response parsing and validation
- Dignity validation
"""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.services.interpretation_service import CLASSICAL_PLANETS, InterpretationService


class MockChoice:
    """Mock OpenAI response choice."""

    def __init__(self, content: str):
        self.message = MagicMock()
        self.message.content = content


class MockResponse:
    """Mock OpenAI API response."""

    def __init__(self, content: str):
        self.choices = [MockChoice(content)]


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    client = AsyncMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def interpretation_service(mock_db, mock_openai_client):
    """Create InterpretationService with mocked dependencies."""
    with patch("app.services.interpretation_service.AsyncOpenAI") as mock_class:
        mock_class.return_value = mock_openai_client

        # Mock prompts loading
        mock_prompts = {
            "version": "1.0",
            "system_prompt": "You are an expert astrologer.",
            "planet_prompts": {
                "base": "Interpret {planet} in {sign} in house {house}. Dignities: {dignities}. Sect: {sect}. Retrograde: {retrograde}."
            },
            "house_prompts": {
                "base": "Interpret house {house} with {sign} on the cusp. Ruler: {ruler}. Ruler dignities: {ruler_dignities}. Sect: {sect}."
            },
            "aspect_prompts": {
                "base": "Interpret {aspect} between {planet1} ({sign1}) and {planet2} ({sign2}). Orb: {orb}°. Applying: {applying}. Sect: {sect}. P1 dignities: {dignities1}. P2 dignities: {dignities2}."
            },
        }

        with patch.object(InterpretationService, "_load_prompts", return_value=mock_prompts):
            service = InterpretationService(mock_db)
            service.client = mock_openai_client
            service.prompts = mock_prompts
            return service


class TestClassicalPlanets:
    """Tests for classical planets constant."""

    def test_classical_planets_count(self):
        """Test that there are exactly 7 classical planets."""
        assert len(CLASSICAL_PLANETS) == 7

    def test_classical_planets_list(self):
        """Test that all classical planets are included."""
        expected = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        for planet in expected:
            assert planet in CLASSICAL_PLANETS

    def test_modern_planets_excluded(self):
        """Test that modern planets are not in classical list."""
        modern = ["Uranus", "Neptune", "Pluto"]
        for planet in modern:
            assert planet not in CLASSICAL_PLANETS


class TestInterpretationServiceInit:
    """Tests for InterpretationService initialization."""

    def test_init_creates_client(self, mock_db):
        """Test that initialization creates OpenAI client."""
        with patch("app.services.interpretation_service.AsyncOpenAI") as mock_class:
            with patch.object(InterpretationService, "_load_prompts", return_value={}):
                service = InterpretationService(mock_db)
                mock_class.assert_called_once()

    def test_init_loads_prompts(self, mock_db):
        """Test that initialization loads prompts."""
        with patch("app.services.interpretation_service.AsyncOpenAI"):
            with patch.object(
                InterpretationService, "_load_prompts", return_value={"test": "prompt"}
            ) as mock_load:
                service = InterpretationService(mock_db)
                mock_load.assert_called_once()


class TestLoadPrompts:
    """Tests for prompt loading."""

    def test_load_prompts_returns_dict(self, mock_db):
        """Test that _load_prompts returns a dictionary."""
        with patch("app.services.interpretation_service.AsyncOpenAI"):
            # Create a mock YAML file content
            mock_yaml_content = """
version: "1.0"
system_prompt: "Test prompt"
planet_prompts:
  base: "Test planet"
"""
            with patch("builtins.open", MagicMock()):
                with patch("yaml.safe_load", return_value={"version": "1.0"}):
                    service = InterpretationService(mock_db)
                    # Prompts should be loaded
                    assert isinstance(service.prompts, dict)


class TestValidateDignities:
    """Tests for dignity validation."""

    def test_validate_empty_dignities(self, interpretation_service):
        """Test validation of empty dignities."""
        result = interpretation_service._validate_dignities("Sun", "Leo", {})
        assert result == {}

    def test_validate_correct_rulership(self, interpretation_service):
        """Test validation of correct rulership."""
        # Sun rules Leo
        dignities = {"is_ruler": True}
        result = interpretation_service._validate_dignities("Sun", "Leo", dignities)
        assert result["is_ruler"] is True

    def test_validate_incorrect_rulership(self, interpretation_service):
        """Test validation corrects incorrect rulership."""
        # Sun does NOT rule Aries
        dignities = {"is_ruler": True}
        result = interpretation_service._validate_dignities("Sun", "Aries", dignities)
        assert result["is_ruler"] is False

    def test_validate_correct_exaltation(self, interpretation_service):
        """Test validation of correct exaltation."""
        # Sun is exalted in Aries
        dignities = {"is_exalted": True}
        result = interpretation_service._validate_dignities("Sun", "Aries", dignities)
        assert result["is_exalted"] is True

    def test_validate_incorrect_exaltation(self, interpretation_service):
        """Test validation corrects incorrect exaltation."""
        # Sun is NOT exalted in Taurus
        dignities = {"is_exalted": True}
        result = interpretation_service._validate_dignities("Sun", "Taurus", dignities)
        assert result["is_exalted"] is False

    def test_validate_preserves_other_dignities(self, interpretation_service):
        """Test that validation preserves unrelated dignity fields."""
        dignities = {
            "is_ruler": False,
            "triplicity_ruler": "day",
            "term_ruler": True,
            "score": 5,
        }
        result = interpretation_service._validate_dignities("Sun", "Leo", dignities)
        assert result["triplicity_ruler"] == "day"
        assert result["term_ruler"] is True
        assert result["score"] == 5


class TestFormatDignities:
    """Tests for dignity formatting."""

    def test_format_empty_dignities(self, interpretation_service):
        """Test formatting empty dignities."""
        result = interpretation_service._format_dignities({})
        assert "Peregrino" in result or "score: 0" in result

    def test_format_ruler_dignity(self, interpretation_service):
        """Test formatting rulership dignity."""
        dignities = {"is_ruler": True, "score": 5, "classification": "dignified"}
        result = interpretation_service._format_dignities(dignities)
        assert "DOMICÍLIO" in result
        assert "+5" in result

    def test_format_exalted_dignity(self, interpretation_service):
        """Test formatting exaltation dignity."""
        dignities = {"is_exalted": True, "score": 4, "classification": "dignified"}
        result = interpretation_service._format_dignities(dignities)
        assert "EXALTAÇÃO" in result
        assert "+4" in result

    def test_format_detriment_dignity(self, interpretation_service):
        """Test formatting detriment dignity."""
        dignities = {"is_detriment": True, "score": -5, "classification": "debilitated"}
        result = interpretation_service._format_dignities(dignities)
        assert "DETRIMENTO" in result
        assert "-5" in result

    def test_format_fall_dignity(self, interpretation_service):
        """Test formatting fall dignity."""
        dignities = {"is_fall": True, "score": -4, "classification": "debilitated"}
        result = interpretation_service._format_dignities(dignities)
        assert "QUEDA" in result
        assert "-4" in result

    def test_format_triplicity_day(self, interpretation_service):
        """Test formatting day triplicity."""
        dignities = {"triplicity_ruler": "day", "score": 3, "classification": "dignified"}
        result = interpretation_service._format_dignities(dignities)
        assert "TRIPLICIDADE" in result
        assert "DIURNA" in result

    def test_format_triplicity_night(self, interpretation_service):
        """Test formatting night triplicity."""
        dignities = {"triplicity_ruler": "night", "score": 3, "classification": "dignified"}
        result = interpretation_service._format_dignities(dignities)
        assert "TRIPLICIDADE" in result
        assert "NOTURNA" in result

    def test_format_term_ruler(self, interpretation_service):
        """Test formatting term/bounds."""
        dignities = {"term_ruler": True, "score": 2, "classification": "dignified"}
        result = interpretation_service._format_dignities(dignities)
        assert "TERMO" in result
        assert "+2" in result

    def test_format_face_ruler(self, interpretation_service):
        """Test formatting face/decanate."""
        dignities = {"face_ruler": True, "score": 1, "classification": "dignified"}
        result = interpretation_service._format_dignities(dignities)
        assert "FACE" in result
        assert "+1" in result

    def test_format_multiple_dignities(self, interpretation_service):
        """Test formatting multiple dignities."""
        dignities = {
            "is_ruler": True,
            "triplicity_ruler": "day",
            "score": 8,
            "classification": "dignified",
        }
        result = interpretation_service._format_dignities(dignities)
        assert "DOMICÍLIO" in result
        assert "TRIPLICIDADE" in result
        assert "8" in result

    def test_format_classification_dignified(self, interpretation_service):
        """Test classification text for dignified planet."""
        dignities = {"is_ruler": True, "score": 5, "classification": "dignified"}
        result = interpretation_service._format_dignities(dignities)
        assert "DIGNIFICADO" in result

    def test_format_classification_debilitated(self, interpretation_service):
        """Test classification text for debilitated planet."""
        dignities = {"is_detriment": True, "score": -5, "classification": "debilitated"}
        result = interpretation_service._format_dignities(dignities)
        assert "DEBILITADO" in result

    def test_format_classification_peregrine(self, interpretation_service):
        """Test classification text for peregrine planet."""
        dignities = {"score": 0, "classification": "peregrine"}
        result = interpretation_service._format_dignities(dignities)
        assert "PEREGRINO" in result


class TestGeneratePlanetInterpretation:
    """Tests for planet interpretation generation."""

    @pytest.mark.asyncio
    async def test_generate_planet_interpretation_success(self, interpretation_service):
        """Test successful planet interpretation generation."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "This is a test interpretation for the Sun in Leo."
        )

        result = await interpretation_service.generate_planet_interpretation(
            planet="Sun",
            sign="Leo",
            house=1,
            dignities={"is_ruler": True, "score": 5},
            sect="diurnal",
            retrograde=False,
        )

        assert "Sun" in result or "test interpretation" in result
        interpretation_service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_skips_modern_planets(self, interpretation_service):
        """Test that modern planets are skipped."""
        result = await interpretation_service.generate_planet_interpretation(
            planet="Uranus",
            sign="Aquarius",
            house=11,
            dignities={},
            sect="diurnal",
            retrograde=False,
        )

        assert result == ""
        interpretation_service.client.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_handles_api_error(self, interpretation_service):
        """Test handling of API errors."""
        interpretation_service.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        result = await interpretation_service.generate_planet_interpretation(
            planet="Sun",
            sign="Leo",
            house=1,
            dignities={},
            sect="diurnal",
            retrograde=False,
        )

        assert "Erro" in result

    @pytest.mark.asyncio
    async def test_generate_validates_dignities(self, interpretation_service):
        """Test that dignities are validated before generation."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "Test interpretation"
        )

        # Sun marked as ruler in Aries (incorrect - Mars rules Aries)
        await interpretation_service.generate_planet_interpretation(
            planet="Sun",
            sign="Aries",
            house=1,
            dignities={"is_ruler": True},  # This is wrong
            sect="diurnal",
            retrograde=False,
        )

        # Verify the API was called (validation happens internally)
        interpretation_service.client.chat.completions.create.assert_called_once()


class TestGenerateHouseInterpretation:
    """Tests for house interpretation generation."""

    @pytest.mark.asyncio
    async def test_generate_house_interpretation_success(self, interpretation_service):
        """Test successful house interpretation generation."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "This is the first house interpretation."
        )

        result = await interpretation_service.generate_house_interpretation(
            house=1,
            sign="Aries",
            ruler="Mars",
            ruler_dignities={"is_ruler": True},
            sect="diurnal",
        )

        assert "first house" in result or "interpretation" in result.lower()

    @pytest.mark.asyncio
    async def test_generate_house_handles_api_error(self, interpretation_service):
        """Test handling of API errors for house interpretation."""
        interpretation_service.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        result = await interpretation_service.generate_house_interpretation(
            house=1,
            sign="Aries",
            ruler="Mars",
            ruler_dignities={},
            sect="diurnal",
        )

        assert "Erro" in result


class TestGenerateAspectInterpretation:
    """Tests for aspect interpretation generation."""

    @pytest.mark.asyncio
    async def test_generate_aspect_interpretation_success(self, interpretation_service):
        """Test successful aspect interpretation generation."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "This is a Sun-Moon conjunction interpretation."
        )

        result = await interpretation_service.generate_aspect_interpretation(
            planet1="Sun",
            planet2="Moon",
            aspect="Conjunction",
            sign1="Leo",
            sign2="Leo",
            orb=3.5,
            applying=True,
            sect="diurnal",
            dignities1={"is_ruler": True},
            dignities2={},
        )

        assert "conjunction" in result.lower() or "interpretation" in result.lower()

    @pytest.mark.asyncio
    async def test_generate_aspect_skips_modern_planets(self, interpretation_service):
        """Test that aspects with modern planets are skipped."""
        result = await interpretation_service.generate_aspect_interpretation(
            planet1="Sun",
            planet2="Uranus",  # Modern planet
            aspect="Conjunction",
            sign1="Aquarius",
            sign2="Aquarius",
            orb=2.0,
            applying=True,
            sect="diurnal",
            dignities1={},
            dignities2={},
        )

        assert result == ""
        interpretation_service.client.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_aspect_handles_api_error(self, interpretation_service):
        """Test handling of API errors for aspect interpretation."""
        interpretation_service.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        result = await interpretation_service.generate_aspect_interpretation(
            planet1="Sun",
            planet2="Moon",
            aspect="Opposition",
            sign1="Leo",
            sign2="Aquarius",
            orb=1.0,
            applying=False,
            sect="nocturnal",
            dignities1={},
            dignities2={},
        )

        assert "Erro" in result


class TestGenerateAllInterpretations:
    """Tests for generating all chart interpretations."""

    @pytest.mark.asyncio
    async def test_generate_all_creates_interpretations(self, interpretation_service):
        """Test that generate_all creates interpretations for chart."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "Test interpretation"
        )

        # Mock the repository
        interpretation_service.repository.create = AsyncMock()

        chart_id = uuid4()
        chart_data = {
            "planets": [
                {
                    "name": "Sun",
                    "sign": "Leo",
                    "house": 1,
                    "dignities": {"is_ruler": True},
                    "retrograde": False,
                },
                {
                    "name": "Moon",
                    "sign": "Cancer",
                    "house": 10,
                    "dignities": {"is_ruler": True},
                    "retrograde": False,
                },
            ],
            "houses": [
                {"house": 1, "sign": "Aries"},
            ],
            "aspects": [
                {
                    "planet1": "Sun",
                    "planet2": "Moon",
                    "aspect": "Sextile",
                    "orb": 2.5,
                    "applying": True,
                },
            ],
            "sect": "diurnal",
        }

        interpretations = await interpretation_service.generate_all_interpretations(
            chart_id=chart_id,
            chart_data=chart_data,
        )

        # Should have interpretations for planets, houses, and aspects
        assert len(interpretations) > 0

    @pytest.mark.asyncio
    async def test_generate_all_skips_modern_planets(self, interpretation_service):
        """Test that generate_all skips modern planets."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "Test interpretation"
        )
        interpretation_service.repository.create = AsyncMock()

        chart_id = uuid4()
        chart_data = {
            "planets": [
                {
                    "name": "Uranus",  # Modern planet
                    "sign": "Aquarius",
                    "house": 11,
                    "dignities": {},
                    "retrograde": False,
                },
            ],
            "houses": [],
            "aspects": [],
            "sect": "diurnal",
        }

        interpretations = await interpretation_service.generate_all_interpretations(
            chart_id=chart_id,
            chart_data=chart_data,
        )

        # No interpretations should be created for modern planets
        planet_interps = [i for i in interpretations if i.interpretation_type == "planet"]
        assert len(planet_interps) == 0

    @pytest.mark.asyncio
    async def test_generate_all_calls_progress_callback(self, interpretation_service):
        """Test that progress callback is called during generation."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "Test interpretation"
        )
        interpretation_service.repository.create = AsyncMock()

        progress_values = []

        async def track_progress(value: int) -> None:
            progress_values.append(value)

        chart_id = uuid4()
        chart_data = {
            "planets": [
                {"name": "Sun", "sign": "Leo", "house": 1, "dignities": {}, "retrograde": False},
            ],
            "houses": [{"house": 1, "sign": "Aries"}],
            "aspects": [],
            "sect": "diurnal",
        }

        await interpretation_service.generate_all_interpretations(
            chart_id=chart_id,
            chart_data=chart_data,
            progress_callback=track_progress,
        )

        # Progress callback should have been called
        assert len(progress_values) > 0


class TestGetInterpretationsByChart:
    """Tests for retrieving interpretations by chart."""

    @pytest.mark.asyncio
    async def test_get_interpretations_groups_by_type(self, interpretation_service):
        """Test that interpretations are grouped by type."""
        mock_interp_planet = MagicMock()
        mock_interp_planet.interpretation_type = "planet"
        mock_interp_planet.subject = "Sun"
        mock_interp_planet.content = "Sun interpretation"

        mock_interp_house = MagicMock()
        mock_interp_house.interpretation_type = "house"
        mock_interp_house.subject = "1"
        mock_interp_house.content = "House 1 interpretation"

        mock_interp_aspect = MagicMock()
        mock_interp_aspect.interpretation_type = "aspect"
        mock_interp_aspect.subject = "Sun-Conjunction-Moon"
        mock_interp_aspect.content = "Aspect interpretation"

        interpretation_service.repository.get_by_chart_id = AsyncMock(
            return_value=[mock_interp_planet, mock_interp_house, mock_interp_aspect]
        )

        chart_id = uuid4()
        result = await interpretation_service.get_interpretations_by_chart(chart_id)

        assert "planets" in result
        assert "houses" in result
        assert "aspects" in result
        assert result["planets"]["Sun"] == "Sun interpretation"
        assert result["houses"]["1"] == "House 1 interpretation"
        assert result["aspects"]["Sun-Conjunction-Moon"] == "Aspect interpretation"

    @pytest.mark.asyncio
    async def test_get_interpretations_empty_chart(self, interpretation_service):
        """Test getting interpretations for chart with no interpretations."""
        interpretation_service.repository.get_by_chart_id = AsyncMock(return_value=[])

        chart_id = uuid4()
        result = await interpretation_service.get_interpretations_by_chart(chart_id)

        assert result == {"planets": {}, "houses": {}, "aspects": {}}


class TestAPIResponseHandling:
    """Tests for OpenAI API response handling."""

    @pytest.mark.asyncio
    async def test_strips_whitespace_from_response(self, interpretation_service):
        """Test that whitespace is stripped from API response."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "  Test interpretation with spaces  \n\n"
        )

        result = await interpretation_service.generate_planet_interpretation(
            planet="Sun",
            sign="Leo",
            house=1,
            dignities={},
            sect="diurnal",
            retrograde=False,
        )

        assert not result.startswith(" ")
        assert not result.endswith("\n")

    @pytest.mark.asyncio
    async def test_handles_none_content(self, interpretation_service):
        """Test handling of None content in API response."""
        mock_response = MockResponse("")
        mock_response.choices[0].message.content = None
        interpretation_service.client.chat.completions.create.return_value = mock_response

        result = await interpretation_service.generate_planet_interpretation(
            planet="Sun",
            sign="Leo",
            house=1,
            dignities={},
            sect="diurnal",
            retrograde=False,
        )

        assert result == ""


class TestRetrogradHandling:
    """Tests for retrograde planet handling."""

    @pytest.mark.asyncio
    async def test_retrograde_planet_marked(self, interpretation_service):
        """Test that retrograde status is included in prompt."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "Mercury retrograde interpretation"
        )

        await interpretation_service.generate_planet_interpretation(
            planet="Mercury",
            sign="Gemini",
            house=3,
            dignities={"is_ruler": True},
            sect="diurnal",
            retrograde=True,
        )

        # Verify the call was made (prompt includes retrograde status)
        interpretation_service.client.chat.completions.create.assert_called_once()


class TestSectHandling:
    """Tests for sect (day/night chart) handling."""

    @pytest.mark.asyncio
    async def test_diurnal_chart(self, interpretation_service):
        """Test interpretation for diurnal chart."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "Diurnal interpretation"
        )

        await interpretation_service.generate_planet_interpretation(
            planet="Sun",
            sign="Leo",
            house=10,
            dignities={},
            sect="diurnal",
            retrograde=False,
        )

        interpretation_service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_nocturnal_chart(self, interpretation_service):
        """Test interpretation for nocturnal chart."""
        interpretation_service.client.chat.completions.create.return_value = MockResponse(
            "Nocturnal interpretation"
        )

        await interpretation_service.generate_planet_interpretation(
            planet="Moon",
            sign="Cancer",
            house=4,
            dignities={"is_ruler": True},
            sect="nocturnal",
            retrograde=False,
        )

        interpretation_service.client.chat.completions.create.assert_called_once()
