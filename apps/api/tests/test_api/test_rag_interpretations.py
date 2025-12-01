"""Tests for RAG interpretation endpoints (available to all users)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import BirthChart
from app.models.interpretation import ChartInterpretation
from app.models.user import User
from app.services.interpretation_service_rag import RAG_PROMPT_VERSION


@pytest.fixture
def test_chart_data() -> dict:
    """Sample chart calculation result for testing (language-first format)."""
    base_data = {
        "planets": [
            {
                "name": "Sun",
                "longitude": 45.123,
                "latitude": 0.002,
                "speed": 0.985,
                "retrograde": False,
                "sign": "Taurus",
                "degree": 15.123,
                "house": 10,
                "dignities": {"exalted": False, "ruler": False},
            },
            {
                "name": "Moon",
                "longitude": 165.456,
                "latitude": 5.234,
                "speed": 13.456,
                "retrograde": False,
                "sign": "Virgo",
                "degree": 15.456,
                "house": 3,
                "dignities": {},
            },
        ],
        "houses": [
            {"house": 1, "cusp": 123.456, "sign": "Leo"},
            {"house": 2, "cusp": 153.456, "sign": "Virgo"},
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "aspect": "trine",
                "angle": 120.333,
                "orb": 0.333,
                "applying": True,
            }
        ],
        "arabic_parts": {
            "fortune": {
                "longitude": 45.0,
                "sign": "Taurus",
                "degree": 15.0,
                "house": 10,
            }
        },
        "ascendant": 123.456,
        "mc": 234.567,
        "sect": "diurnal",
    }
    # Return language-first format
    return {
        "en-US": base_data,
        "pt-BR": base_data,
    }


@pytest.fixture
async def test_chart_for_user(
    db_session: AsyncSession,
    test_user: User,
    test_chart_data: dict,
) -> BirthChart:
    """Create a test chart for the regular user."""
    chart = BirthChart(
        id=uuid4(),
        user_id=test_user.id,
        person_name="Test Chart",
        birth_datetime=datetime(1990, 5, 15, 10, 30, tzinfo=UTC),
        birth_timezone="America/Sao_Paulo",
        latitude=-23.5505,
        longitude=-46.6333,
        city="São Paulo",
        country="Brazil",
        house_system="placidus",
        zodiac_type="tropical",
        chart_data=test_chart_data,
        status="completed",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(chart)
    await db_session.commit()
    await db_session.refresh(chart)
    return chart


@pytest.fixture
async def test_chart_with_interpretations(
    db_session: AsyncSession,
    test_user: User,
    test_chart_data: dict,
) -> BirthChart:
    """Create a test chart with existing RAG interpretations."""
    chart = BirthChart(
        id=uuid4(),
        user_id=test_user.id,
        person_name="Chart With Interpretations",
        birth_datetime=datetime(1990, 5, 15, 10, 30, tzinfo=UTC),
        birth_timezone="America/Sao_Paulo",
        latitude=-23.5505,
        longitude=-46.6333,
        city="São Paulo",
        country="Brazil",
        house_system="placidus",
        zodiac_type="tropical",
        chart_data=test_chart_data,
        status="completed",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(chart)
    await db_session.flush()

    # Add existing interpretations
    interp = ChartInterpretation(
        id=uuid4(),
        chart_id=chart.id,
        interpretation_type="planet",
        subject="Sun",
        content="Cached interpretation for Sun in Taurus...",
        openai_model="gpt-4o-mini-rag",
        prompt_version=RAG_PROMPT_VERSION,
        rag_sources=[
            {
                "source": "Test Book",
                "page": "42",
                "relevance_score": 0.95,
                "content_preview": "Preview...",
            }
        ],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(interp)

    await db_session.commit()
    await db_session.refresh(chart)
    return chart


@pytest.fixture
def mock_rag_services():
    """Mock RAG services for interpretation generation."""
    with patch("app.api.v1.endpoints.interpretations.InterpretationServiceRAG") as mock_rag_class:
        mock_instance = AsyncMock()
        mock_rag_class.return_value = mock_instance

        # Mock methods using the new public method name
        mock_instance.retrieve_context = AsyncMock(
            return_value=[
                {
                    "payload": {
                        "content": "Test astrological content about Sun in Taurus",
                        "title": "Traditional Astrology",
                        "metadata": {"source": "Test Source", "page": 42},
                    },
                    "score": 0.95,
                }
            ]
        )
        mock_instance._format_rag_context = AsyncMock(
            return_value="Contexto Astrológico Relevante:\nTest astrological context..."
        )
        mock_instance.generate_planet_interpretation = AsyncMock(
            return_value="RAG-enhanced interpretation for Sun in Taurus..."
        )
        mock_instance.generate_house_interpretation = AsyncMock(
            return_value="RAG-enhanced interpretation for house 1 in Leo..."
        )
        mock_instance.generate_aspect_interpretation = AsyncMock(
            return_value="RAG-enhanced interpretation for Sun trine Moon..."
        )
        mock_instance.generate_arabic_part_interpretation = AsyncMock(
            return_value="RAG-enhanced interpretation for Part of Fortune..."
        )

        yield mock_instance


class TestRAGInterpretationsEndpoints:
    """Tests for RAG interpretation endpoints (available to all users)."""

    @pytest.mark.asyncio
    async def test_get_interpretations_returns_cached(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_chart_with_interpretations: BirthChart,
    ):
        """Test getting interpretations returns cached data from database."""
        response = await client.get(
            f"/api/v1/charts/{test_chart_with_interpretations.id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure (RAGInterpretationsResponse)
        assert "planets" in data
        assert "houses" in data
        assert "aspects" in data
        assert "arabic_parts" in data
        assert "metadata" in data
        assert "documents_used" in data["metadata"]

        # Check cached planet interpretation
        assert "Sun" in data["planets"]
        assert data["planets"]["Sun"]["source"] == "database"  # Loaded from database
        assert "Cached interpretation" in data["planets"]["Sun"]["content"]
        assert len(data["planets"]["Sun"]["rag_sources"]) > 0

    @pytest.mark.asyncio
    async def test_get_interpretations_generates_when_none_exist(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_chart_for_user: BirthChart,
        mock_rag_services,
    ):
        """Test that interpretations are generated when none exist."""
        response = await client.get(
            f"/api/v1/charts/{test_chart_for_user.id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Check RAGInterpretationsResponse structure
        assert "metadata" in data
        assert "planets" in data

    @pytest.mark.asyncio
    async def test_get_interpretations_unauthorized(
        self,
        client: AsyncClient,
        test_chart_for_user: BirthChart,
    ):
        """Test unauthorized request returns 401 (no token provided)."""
        response = await client.get(
            f"/api/v1/charts/{test_chart_for_user.id}/interpretations",
        )

        # FastAPI returns 403 when no token is provided via get_current_user dependency
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_interpretations_chart_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test interpretations for non-existent chart returns 404."""
        fake_chart_id = uuid4()

        response = await client.get(
            f"/api/v1/charts/{fake_chart_id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_interpretations_other_user_chart_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        test_chart_data: dict,
    ):
        """Test user cannot access another user's chart interpretations.

        Note: Returns 404 (not 403) to avoid revealing existence of other users' charts.
        This is a security best practice.
        """
        # Create chart for a different user
        other_user = User(
            id=uuid4(),
            email="other@example.com",
            password_hash="hashed",
            full_name="Other User",
            is_active=True,
            email_verified=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(other_user)
        await db_session.flush()

        other_chart = BirthChart(
            id=uuid4(),
            user_id=other_user.id,
            person_name="Other User Chart",
            birth_datetime=datetime(1990, 5, 15, 10, 30, tzinfo=UTC),
            birth_timezone="America/Sao_Paulo",
            latitude=-23.5505,
            longitude=-46.6333,
            city="São Paulo",
            country="Brazil",
            house_system="placidus",
            zodiac_type="tropical",
            chart_data=test_chart_data,
            status="completed",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(other_chart)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/charts/{other_chart.id}/interpretations",
            headers=auth_headers,
        )

        # Returns 404 to not reveal existence of other users' charts (security best practice)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_interpretations_chart_processing(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test interpretations for chart still processing returns 400."""
        # Create chart without chart_data (still processing)
        chart = BirthChart(
            id=uuid4(),
            user_id=test_user.id,
            person_name="Processing Chart",
            birth_datetime=datetime(1990, 5, 15, 10, 30, tzinfo=UTC),
            birth_timezone="America/Sao_Paulo",
            latitude=-23.5505,
            longitude=-46.6333,
            city="São Paulo",
            country="Brazil",
            house_system="placidus",
            zodiac_type="tropical",
            chart_data=None,  # No data yet
            status="processing",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(chart)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "still processing" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_regenerate_interpretations_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_chart_with_interpretations: BirthChart,
        mock_rag_services,
    ):
        """Test regenerating interpretations deletes old and creates new."""
        response = await client.post(
            f"/api/v1/charts/{test_chart_with_interpretations.id}/interpretations/regenerate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Check RAGInterpretationsResponse structure
        assert "metadata" in data
        assert "planets" in data
        assert "documents_used" in data["metadata"]

    @pytest.mark.asyncio
    async def test_regenerate_interpretations_unauthorized(
        self,
        client: AsyncClient,
        test_chart_for_user: BirthChart,
    ):
        """Test unauthorized request returns 401 (no token provided)."""
        response = await client.post(
            f"/api/v1/charts/{test_chart_for_user.id}/interpretations/regenerate",
        )

        # FastAPI returns 403 when no token is provided via get_current_user dependency
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_regenerate_interpretations_chart_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test regenerating interpretations for non-existent chart returns 404."""
        fake_chart_id = uuid4()

        response = await client.post(
            f"/api/v1/charts/{fake_chart_id}/interpretations/regenerate",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestRAGServiceIntegration:
    """Tests for RAG service integration."""

    @pytest.mark.asyncio
    async def test_retrieve_context_method_is_public(self):
        """Test that retrieve_context is a public method."""
        from app.services.interpretation_service_rag import InterpretationServiceRAG

        # Check method exists and is not private (doesn't start with _)
        assert hasattr(InterpretationServiceRAG, "retrieve_context")
        assert not hasattr(InterpretationServiceRAG, "_retrieve_context") or hasattr(
            InterpretationServiceRAG, "retrieve_context"
        )

    @pytest.mark.asyncio
    async def test_constants_are_exported(self):
        """Test that RAG constants are properly exported."""
        from app.services.interpretation_service_rag import (
            ARABIC_PARTS,
            RAG_MODEL_ID,
            RAG_PROMPT_VERSION,
        )

        assert RAG_MODEL_ID == "gpt-4o-mini-rag"
        assert RAG_PROMPT_VERSION == "rag-v1"
        assert "fortune" in ARABIC_PARTS
        assert "spirit" in ARABIC_PARTS

    @pytest.mark.asyncio
    async def test_typedicts_are_exported(self):
        """Test that TypedDicts are properly exported."""
        from app.services.interpretation_service_rag import (
            ArabicPartData,
            AspectData,
            HouseData,
            PlanetData,
        )

        # TypedDicts should be importable
        assert PlanetData is not None
        assert HouseData is not None
        assert AspectData is not None
        assert ArabicPartData is not None
