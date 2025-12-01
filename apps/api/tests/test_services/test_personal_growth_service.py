"""
Tests for PersonalGrowthService.

Tests the chart pattern analysis and ensure the service structure is correct.
Note: AI generation tests are mocked to avoid OpenAI API calls.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.personal_growth_service import PersonalGrowthService


class TestAnalyzeChartPatterns:
    """Tests for analyze_chart_patterns method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.service = PersonalGrowthService(language="en-US")
        self.sample_chart_data = {
            "planets": [
                {
                    "name": "Sun",
                    "sign": "Aries",
                    "house": 10,
                    "retrograde": False,
                    "dignities": {"exalted": True},
                },
                {
                    "name": "Moon",
                    "sign": "Cancer",
                    "house": 1,
                    "retrograde": False,
                    "dignities": {"ruler": True},
                },
                {
                    "name": "Mercury",
                    "sign": "Pisces",
                    "house": 9,
                    "retrograde": True,
                    "dignities": {"fall": True},
                },
                {
                    "name": "Venus",
                    "sign": "Taurus",
                    "house": 11,
                    "retrograde": False,
                    "dignities": {"ruler": True},
                },
                {
                    "name": "Mars",
                    "sign": "Aries",
                    "house": 10,
                    "retrograde": False,
                    "dignities": {"ruler": True},
                },
                {
                    "name": "Jupiter",
                    "sign": "Aries",
                    "house": 10,
                    "retrograde": False,
                    "dignities": {},
                },
                {
                    "name": "Saturn",
                    "sign": "Capricorn",
                    "house": 7,
                    "retrograde": True,
                    "dignities": {"ruler": True},
                },
            ],
            "aspects": [
                {
                    "planet1": "Sun",
                    "planet2": "Moon",
                    "aspect": "square",
                    "orb": 3.5,
                    "applying": True,
                },
                {
                    "planet1": "Venus",
                    "planet2": "Jupiter",
                    "aspect": "trine",
                    "orb": 2.0,
                    "applying": False,
                },
                {
                    "planet1": "Mars",
                    "planet2": "Saturn",
                    "aspect": "opposition",
                    "orb": 4.0,
                    "applying": True,
                },
                {
                    "planet1": "Sun",
                    "planet2": "Mars",
                    "aspect": "conjunction",
                    "orb": 1.5,
                    "applying": False,
                },
            ],
            "ascendant": 120.0,  # Leo ascendant (120 degrees = Leo)
            "sect": "diurnal",
        }

    def test_extracts_big_three(self) -> None:
        """Test that Big Three (Sun, Moon, Ascendant) is correctly extracted."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)

        assert "big_three" in patterns
        assert patterns["big_three"]["sun"]["sign"] == "Aries"
        assert patterns["big_three"]["sun"]["house"] == 10
        assert patterns["big_three"]["moon"]["sign"] == "Cancer"
        assert patterns["big_three"]["moon"]["house"] == 1
        assert patterns["big_three"]["ascendant"]["sign"] == "Leo"

    def test_categorizes_difficult_aspects(self) -> None:
        """Test that squares and oppositions are categorized as difficult."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)

        assert len(patterns["difficult_aspects"]) == 2
        aspect_names = [a["planets"] for a in patterns["difficult_aspects"]]
        assert "Sun square Moon" in aspect_names
        assert "Mars opposition Saturn" in aspect_names

    def test_categorizes_harmonious_aspects(self) -> None:
        """Test that trines, sextiles, conjunctions are categorized as harmonious."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)

        assert len(patterns["harmonious_aspects"]) == 2
        aspect_names = [a["planets"] for a in patterns["harmonious_aspects"]]
        assert "Venus trine Jupiter" in aspect_names
        assert "Sun conjunction Mars" in aspect_names

    def test_identifies_retrograde_planets(self) -> None:
        """Test that retrograde planets are correctly identified."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)

        assert len(patterns["retrogrades"]) == 2
        retro_names = [r["planet"] for r in patterns["retrogrades"]]
        assert "Mercury" in retro_names
        assert "Saturn" in retro_names

    def test_identifies_strong_dignities(self) -> None:
        """Test that planets in domicile or exaltation are identified."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)

        assert len(patterns["strong_dignities"]) >= 3
        strong_planets = [d["planet"] for d in patterns["strong_dignities"]]
        assert "Sun" in strong_planets  # Exalted in Aries
        assert "Moon" in strong_planets  # Ruler of Cancer
        assert "Venus" in strong_planets  # Ruler of Taurus

    def test_identifies_weak_dignities(self) -> None:
        """Test that planets in detriment or fall are identified."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)

        assert len(patterns["weak_dignities"]) >= 1
        weak_planets = [d["planet"] for d in patterns["weak_dignities"]]
        assert "Mercury" in weak_planets  # Fall in Pisces

    def test_detects_stelliums(self) -> None:
        """Test that stelliums (3+ planets in same sign) are detected."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)

        # Sun, Mars, Jupiter are all in Aries
        assert len(patterns["stelliums"]) == 1
        assert patterns["stelliums"][0]["sign"] == "Aries"
        assert len(patterns["stelliums"][0]["planets"]) == 3

    def test_includes_sect(self) -> None:
        """Test that sect information is included."""
        patterns = self.service.analyze_chart_patterns(self.sample_chart_data)
        assert patterns["sect"] == "diurnal"


class TestLanguageInstruction:
    """Tests for language instruction generation."""

    def test_english_instruction(self) -> None:
        """Test English language instruction."""
        service = PersonalGrowthService(language="en-US")
        instruction = service._get_language_instruction()

        assert "English" in instruction
        assert "en-US" in instruction

    def test_portuguese_instruction(self) -> None:
        """Test Portuguese language instruction."""
        service = PersonalGrowthService(language="pt-BR")
        instruction = service._get_language_instruction()

        assert "Português" in instruction
        assert "pt-BR" in instruction


class TestBuildChartSummary:
    """Tests for chart summary building."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.service = PersonalGrowthService(language="en-US")

    def test_includes_big_three_in_summary(self) -> None:
        """Test that Big Three is included in chart summary."""
        chart_data = {
            "planets": [
                {"name": "Sun", "sign": "Leo", "house": 1, "retrograde": False},
                {"name": "Moon", "sign": "Pisces", "house": 6, "retrograde": False},
            ],
            "aspects": [],
            "ascendant": 0.0,  # Aries
            "sect": "diurnal",
        }
        patterns = self.service.analyze_chart_patterns(chart_data)
        summary = self.service._build_chart_summary(chart_data, patterns)

        assert "Sun in Leo" in summary
        assert "Moon in Pisces" in summary
        assert "Ascendant in Aries" in summary

    def test_includes_retrograde_info(self) -> None:
        """Test that retrograde planets are noted in summary."""
        chart_data = {
            "planets": [
                {"name": "Mercury", "sign": "Virgo", "house": 3, "retrograde": True},
            ],
            "aspects": [],
            "ascendant": 0.0,
            "sect": "diurnal",
        }
        patterns = self.service.analyze_chart_patterns(chart_data)
        summary = self.service._build_chart_summary(chart_data, patterns)

        assert "Mercury" in summary
        assert "(R)" in summary or "Retrograde" in summary


class TestGenerateGrowthSuggestions:
    """Tests for the main generate_growth_suggestions method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.service = PersonalGrowthService(language="en-US")
        self.sample_chart_data = {
            "planets": [
                {"name": "Sun", "sign": "Aries", "house": 1, "retrograde": False, "dignities": {}},
                {
                    "name": "Moon",
                    "sign": "Cancer",
                    "house": 4,
                    "retrograde": False,
                    "dignities": {},
                },
            ],
            "aspects": [
                {
                    "planet1": "Sun",
                    "planet2": "Moon",
                    "aspect": "square",
                    "orb": 3.0,
                    "applying": True,
                },
            ],
            "ascendant": 0.0,
            "sect": "diurnal",
        }

    @pytest.mark.asyncio
    async def test_generates_all_sections(self) -> None:
        """Test that all suggestion sections are generated."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"growth_points": []}'))]

        with patch.object(
            self.service.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            suggestions = await self.service.generate_growth_suggestions(self.sample_chart_data)

        assert "growth_points" in suggestions
        assert "challenges" in suggestions
        assert "opportunities" in suggestions
        assert "purpose" in suggestions
        assert "metadata" in suggestions

    @pytest.mark.asyncio
    async def test_includes_metadata(self) -> None:
        """Test that metadata is included in response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"growth_points": []}'))]

        with patch.object(
            self.service.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            suggestions = await self.service.generate_growth_suggestions(self.sample_chart_data)

        assert suggestions["metadata"]["language"] == "en-US"
        assert suggestions["metadata"]["model"] == "gpt-4o-mini"
        assert "patterns_analyzed" in suggestions["metadata"]


class TestSchemaValidation:
    """Test that Pydantic schemas work correctly."""

    def test_growth_response_schema(self) -> None:
        """Test GrowthSuggestionsResponse schema."""
        from app.schemas.growth import GrowthSuggestionsResponse

        # Test with minimal data
        response = GrowthSuggestionsResponse(
            growth_points=[],
            challenges=[],
            opportunities=[],
        )
        assert response.growth_points == []
        assert response.purpose is None

    def test_growth_point_schema(self) -> None:
        """Test GrowthPoint schema."""
        from app.schemas.growth import GrowthPoint

        point = GrowthPoint(
            area="Communication",
            indicator="Mercury retrograde in Pisces",
            explanation="Mercury retrograde can indicate challenges with clear communication.",
            practical_actions=["Practice journaling", "Think before speaking"],
            mindset_shift="My intuition is a valid form of intelligence",
        )
        assert point.area == "Communication"
        assert len(point.practical_actions) == 2

    def test_challenge_schema(self) -> None:
        """Test Challenge schema."""
        from app.schemas.growth import Challenge

        challenge = Challenge(
            name="Self-Criticism Pattern",
            pattern="Sun square Saturn",
            manifestation="Tendency to be overly critical of oneself",
            strategy="Practice self-compassion",
            practices=["Daily affirmations", "Celebrate small wins"],
        )
        assert challenge.name == "Self-Criticism Pattern"
        assert len(challenge.practices) == 2

    def test_purpose_schema(self) -> None:
        """Test Purpose schema."""
        from app.schemas.growth import Purpose

        purpose = Purpose(
            soul_direction="Evolution through creative expression",
            vocation="Leadership and innovation",
            contribution="Inspiring others to take action",
            integration="Balance independence with collaboration",
            next_steps=["Start a creative project", "Join a community"],
        )
        assert purpose.vocation == "Leadership and innovation"
        assert len(purpose.next_steps) == 2

    def test_metadata_with_focus_areas(self) -> None:
        """Test GrowthMetadata with focus areas."""
        from app.schemas.growth import GrowthMetadata, PatternsAnalyzed

        metadata = GrowthMetadata(
            language="en-US",
            model="gpt-4o-mini",
            patterns_analyzed=PatternsAnalyzed(
                difficult_aspects=2,
                harmonious_aspects=3,
                retrogrades=1,
                stelliums=1,
            ),
            focus_areas=["career", "relationships"],
            cached=True,
        )
        assert metadata.focus_areas == ["career", "relationships"]
        assert metadata.cached is True


class TestFocusAreasInstruction:
    """Tests for focus areas instruction generation."""

    def test_english_focus_areas(self) -> None:
        """Test focus areas instruction in English."""
        service = PersonalGrowthService(language="en-US")
        instruction = service._get_focus_areas_instruction(["career", "relationships"])

        assert "FOCUS AREAS" in instruction
        assert "career" in instruction
        assert "relationships" in instruction

    def test_portuguese_focus_areas(self) -> None:
        """Test focus areas instruction in Portuguese."""
        service = PersonalGrowthService(language="pt-BR")
        instruction = service._get_focus_areas_instruction(["carreira", "relacionamentos"])

        assert "ÁREAS DE FOCO" in instruction
        assert "carreira" in instruction
        assert "relacionamentos" in instruction

    def test_no_focus_areas(self) -> None:
        """Test that no instruction is returned when focus_areas is None."""
        service = PersonalGrowthService(language="en-US")
        instruction = service._get_focus_areas_instruction(None)

        assert instruction == ""

    def test_empty_focus_areas(self) -> None:
        """Test that no instruction is returned when focus_areas is empty."""
        service = PersonalGrowthService(language="en-US")
        instruction = service._get_focus_areas_instruction([])

        assert instruction == ""


class TestServiceWithoutCache:
    """Test service works correctly without database/cache."""

    def test_service_initializes_without_db(self) -> None:
        """Test service can be initialized without database session."""
        service = PersonalGrowthService(language="en-US")

        assert service.db is None
        assert service.cache_service is None
        assert service.language == "en-US"
        assert service.model == "gpt-4o-mini"
