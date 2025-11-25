"""
Tests for InterpretationServiceRAG.

Tests the RAG-enhanced interpretation service for extended Arabic Parts.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.interpretation_service_rag import (
    ARABIC_PARTS,
    InterpretationServiceRAG,
)


class TestArabicPartsDefinitions:
    """Test Arabic Parts definitions include all extended parts."""

    def test_all_basic_parts_defined(self) -> None:
        """Test that all basic Arabic Parts are defined."""
        basic_parts = ["fortune", "spirit", "eros", "necessity"]
        for part_key in basic_parts:
            assert part_key in ARABIC_PARTS
            assert "name" in ARABIC_PARTS[part_key]
            assert "name_pt" in ARABIC_PARTS[part_key]

    def test_all_extended_parts_defined(self) -> None:
        """Test that all extended Arabic Parts are defined (Issue #195)."""
        extended_parts = [
            "marriage",
            "victory",
            "father",
            "mother",
            "children",
            "exaltation",
            "illness",
            "courage",
            "reputation",
        ]
        for part_key in extended_parts:
            assert part_key in ARABIC_PARTS, f"Missing extended part: {part_key}"
            assert "name" in ARABIC_PARTS[part_key]
            assert "name_pt" in ARABIC_PARTS[part_key]

    def test_part_names_are_correct(self) -> None:
        """Test that part names are correct for extended parts."""
        expected_names = {
            "marriage": ("Part of Marriage", "Lote do Casamento"),
            "victory": ("Part of Victory", "Lote da Vitória"),
            "father": ("Part of Father", "Lote do Pai"),
            "mother": ("Part of Mother", "Lote da Mãe"),
            "children": ("Part of Children", "Lote dos Filhos"),
            "exaltation": ("Part of Exaltation", "Lote da Exaltação"),
            "illness": ("Part of Illness", "Lote da Doença"),
            "courage": ("Part of Courage", "Lote da Coragem"),
            "reputation": ("Part of Reputation", "Lote da Reputação"),
        }
        for part_key, (name_en, name_pt) in expected_names.items():
            assert ARABIC_PARTS[part_key]["name"] == name_en
            assert ARABIC_PARTS[part_key]["name_pt"] == name_pt


class TestGenerateArabicPartInterpretation:
    """Tests for generate_arabic_part_interpretation method."""

    @pytest.fixture
    def mock_openai_client(self) -> MagicMock:
        """Create mock OpenAI client."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Test interpretation for Arabic Part in Aries house 1."
                )
            )
        ]
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        return mock_client

    @pytest.fixture
    def mock_db(self) -> MagicMock:
        """Create mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_rag_service(
        self, mock_openai_client: MagicMock, mock_db: MagicMock
    ) -> InterpretationServiceRAG:
        """Create InterpretationServiceRAG with mocked dependencies."""
        with patch(
            "app.services.interpretation_service_rag.AsyncOpenAI",
            return_value=mock_openai_client,
        ):
            with patch(
                "app.services.interpretation_service_rag.hybrid_search_service"
            ) as mock_hybrid:
                mock_hybrid.hybrid_search = AsyncMock(return_value=[])
                # Disable cache for testing to avoid async db issues
                service = InterpretationServiceRAG(
                    db=mock_db, use_cache=False, language="pt-BR"
                )
                service.client = mock_openai_client
                return service

    @pytest.mark.asyncio
    async def test_generate_basic_arabic_part(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for basic Arabic Part (fortune)."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="fortune",
            sign="Aries",
            house=1,
            degree=15.5,
            sect="diurnal",
        )
        assert result
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_marriage(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of Marriage."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="marriage",
            sign="Libra",
            house=7,
            degree=10.0,
            sect="diurnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_victory(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of Victory."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="victory",
            sign="Sagittarius",
            house=9,
            degree=22.5,
            sect="nocturnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_father(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of the Father."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="father",
            sign="Leo",
            house=10,
            degree=5.0,
            sect="diurnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_mother(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of the Mother."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="mother",
            sign="Cancer",
            house=4,
            degree=18.0,
            sect="nocturnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_children(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of Children."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="children",
            sign="Leo",
            house=5,
            degree=12.0,
            sect="diurnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_exaltation(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of Exaltation."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="exaltation",
            sign="Capricorn",
            house=10,
            degree=28.0,
            sect="diurnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_illness(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of Illness."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="illness",
            sign="Virgo",
            house=6,
            degree=8.0,
            sect="nocturnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_courage(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of Courage."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="courage",
            sign="Aries",
            house=1,
            degree=1.0,
            sect="diurnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_extended_arabic_part_reputation(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test generating interpretation for Part of Reputation."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="reputation",
            sign="Sagittarius",
            house=10,
            degree=15.0,
            sect="diurnal",
        )
        assert result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_invalid_part_key_returns_empty(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test that invalid part key returns empty string."""
        result = await mock_rag_service.generate_arabic_part_interpretation(
            part_key="invalid_part",
            sign="Aries",
            house=1,
            degree=15.0,
            sect="diurnal",
        )
        assert result == ""

    @pytest.mark.asyncio
    async def test_all_extended_parts_can_be_generated(
        self, mock_rag_service: InterpretationServiceRAG
    ) -> None:
        """Test that all extended Arabic Parts can generate interpretations."""
        extended_parts = [
            "marriage",
            "victory",
            "father",
            "mother",
            "children",
            "exaltation",
            "illness",
            "courage",
            "reputation",
        ]

        for part_key in extended_parts:
            result = await mock_rag_service.generate_arabic_part_interpretation(
                part_key=part_key,
                sign="Aries",
                house=1,
                degree=15.0,
                sect="diurnal",
            )
            assert result, f"Failed to generate interpretation for {part_key}"
            assert isinstance(result, str)


class TestCacheHitTracking:
    """Tests for cache hit/miss tracking in Arabic Part interpretations."""

    @pytest.fixture
    def mock_cache_service(self) -> MagicMock:
        """Create mock cache service."""
        cache = MagicMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        return cache

    @pytest.fixture
    def mock_db(self) -> MagicMock:
        """Create mock database session."""
        return MagicMock()

    @pytest.fixture
    def service_with_cache(
        self, mock_cache_service: MagicMock, mock_db: MagicMock
    ) -> InterpretationServiceRAG:
        """Create service with cache service."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Generated interpretation"))
        ]
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch(
            "app.services.interpretation_service_rag.AsyncOpenAI",
            return_value=mock_client,
        ):
            with patch(
                "app.services.interpretation_service_rag.hybrid_search_service"
            ) as mock_hybrid:
                mock_hybrid.hybrid_search = AsyncMock(return_value=[])
                # Create with cache disabled, then manually set mock cache
                service = InterpretationServiceRAG(
                    db=mock_db, use_cache=False, language="pt-BR"
                )
                service.client = mock_client
                service.cache_service = mock_cache_service
                return service

    @pytest.mark.asyncio
    async def test_cache_miss_increments_counter(
        self, service_with_cache: InterpretationServiceRAG
    ) -> None:
        """Test that cache miss increments the counter."""
        initial_misses = service_with_cache._cache_misses

        await service_with_cache.generate_arabic_part_interpretation(
            part_key="marriage",
            sign="Libra",
            house=7,
            degree=10.0,
            sect="diurnal",
        )

        assert service_with_cache._cache_misses == initial_misses + 1

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_value(
        self, service_with_cache: InterpretationServiceRAG,
        mock_cache_service: MagicMock,
    ) -> None:
        """Test that cache hit returns cached value."""
        cached_interpretation = "Cached interpretation for Part of Marriage"
        mock_cache_service.get = AsyncMock(return_value=cached_interpretation)

        result = await service_with_cache.generate_arabic_part_interpretation(
            part_key="marriage",
            sign="Libra",
            house=7,
            degree=10.0,
            sect="diurnal",
        )

        assert result == cached_interpretation
        assert service_with_cache._cache_hits == 1
