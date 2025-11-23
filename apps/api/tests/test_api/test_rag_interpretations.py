"""Tests for RAG interpretation endpoints (Admin only)."""
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import BirthChart
from app.models.user import User


@pytest.fixture
def test_chart_data() -> dict:
    """Sample chart calculation result for testing."""
    return {
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
            },
        ],
        "houses": [
            {"number": 1, "cusp": 123.456, "sign": "Leo"},
            {"number": 2, "cusp": 153.456, "sign": "Virgo"},
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
        "ascendant": 123.456,
        "mc": 234.567,
    }


@pytest.fixture
async def test_chart(
    db_session: AsyncSession,
    test_admin_user: User,
    test_chart_data: dict,
) -> BirthChart:
    """Create a test chart for the admin user."""
    chart = BirthChart(
        id=uuid4(),
        user_id=test_admin_user.id,
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
async def mock_rag_services():
    """Mock RAG services for interpretation."""
    with patch('app.api.v1.endpoints.interpretations.InterpretationServiceRAG') as mock_rag_class:
        mock_instance = AsyncMock()
        mock_rag_class.return_value = mock_instance

        # Mock methods
        mock_instance._retrieve_context = AsyncMock(return_value=[
            {
                "payload": {
                    "content": "Test astrological content about Sun in Taurus",
                    "title": "Traditional Astrology",
                    "metadata": {"source": "Test Source", "page": 42},
                },
                "score": 0.95,
            }
        ])
        mock_instance._format_rag_context = AsyncMock(
            return_value="Contexto Astrológico Relevante:\nTest astrological context..."
        )
        mock_instance.generate_planet_interpretation = AsyncMock(
            return_value="RAG-enhanced interpretation for Sun in Taurus..."
        )
        mock_instance.generate_aspect_interpretation = AsyncMock(
            return_value="RAG-enhanced interpretation for Sun trine Moon..."
        )

        yield mock_instance


class TestRAGInterpretationsEndpoints:
    """Tests for RAG interpretation endpoints."""

    @pytest.mark.asyncio
    async def test_get_rag_interpretations_admin_success(
        self,
        client: AsyncClient,
        test_admin_user: User,
        admin_auth_headers: dict[str, str],
        test_chart: BirthChart,
        mock_rag_services,
    ):
        """Test admin can get RAG interpretations."""
        response = await client.get(
            f"/api/v1/charts/{test_chart.id}/interpretations/rag",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert data["source"] == "rag"
        assert "planets" in data
        assert "houses" in data
        assert "aspects" in data
        assert "documents_used" in data

        # Check planet interpretations
        assert "Sun" in data["planets"]
        assert data["planets"]["Sun"]["source"] == "rag"
        assert "content" in data["planets"]["Sun"]

    @pytest.mark.asyncio
    async def test_get_rag_interpretations_non_admin_forbidden(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        test_chart_data: dict,
    ):
        """Test non-admin users cannot access RAG interpretations."""
        # Create chart for regular user
        chart = BirthChart(
            id=uuid4(),
            user_id=test_user.id,
            person_name="Regular User Chart",
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

        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations/rag",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_rag_interpretations_unauthorized(
        self,
        client: AsyncClient,
        test_chart: BirthChart,
    ):
        """Test unauthorized access to RAG interpretations."""
        response = await client.get(
            f"/api/v1/charts/{test_chart.id}/interpretations/rag",
        )

        # 403 is returned by require_admin when no token is provided
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_rag_interpretations_chart_not_found(
        self,
        client: AsyncClient,
        admin_auth_headers: dict[str, str],
    ):
        """Test RAG interpretations for non-existent chart."""
        fake_chart_id = uuid4()

        response = await client.get(
            f"/api/v1/charts/{fake_chart_id}/interpretations/rag",
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_regenerate_rag_interpretations_admin_success(
        self,
        client: AsyncClient,
        test_admin_user: User,
        admin_auth_headers: dict[str, str],
        test_chart: BirthChart,
        mock_rag_services,
    ):
        """Test admin can regenerate RAG interpretations."""
        response = await client.post(
            f"/api/v1/charts/{test_chart.id}/interpretations/rag/regenerate",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["source"] == "rag"
        assert "planets" in data
        assert "documents_used" in data

    @pytest.mark.asyncio
    async def test_regenerate_rag_interpretations_non_admin_forbidden(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        test_chart_data: dict,
    ):
        """Test non-admin cannot regenerate RAG interpretations."""
        # Create chart for regular user
        chart = BirthChart(
            id=uuid4(),
            user_id=test_user.id,
            person_name="Regular User Chart",
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

        response = await client.post(
            f"/api/v1/charts/{chart.id}/interpretations/rag/regenerate",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_rag_interpretations_chart_processing(
        self,
        client: AsyncClient,
        test_admin_user: User,
        admin_auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test RAG interpretations for chart still processing."""
        # Create chart without chart_data (still processing)
        chart = BirthChart(
            id=uuid4(),
            user_id=test_admin_user.id,
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
            f"/api/v1/charts/{chart.id}/interpretations/rag",
            headers=admin_auth_headers,
        )

        assert response.status_code == 400
        assert "still processing" in response.json()["detail"]
