"""
Tests for Longevity API endpoints (Hyleg + Alcochoden).

These endpoints are premium-only features that require:
- Authentication (401 if not authenticated)
- Premium access (403 if free user)

The endpoints:
- GET /api/v1/charts/{chart_id}/hyleg - Calculate Hyleg (Giver of Life)
- GET /api/v1/charts/{chart_id}/alcochoden - Calculate Alcochoden (Giver of Years)
- GET /api/v1/charts/{chart_id}/longevity - Full longevity analysis
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.chart import BirthChart
from app.models.enums import UserRole
from app.models.user import User

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def free_user(db_session: AsyncSession) -> User:
    """Create a user with FREE role."""
    user = User(
        id=uuid4(),
        email="free@example.com",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Free User",
        email_verified=True,
        is_active=True,
        is_superuser=False,
        role=UserRole.FREE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def free_user_headers(free_user: User) -> dict[str, str]:
    """Get auth headers for free user."""
    access_token = create_access_token(data={"sub": str(free_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def premium_user(db_session: AsyncSession) -> User:
    """Create a user with PREMIUM role."""
    user = User(
        id=uuid4(),
        email="premium@example.com",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Premium User",
        email_verified=True,
        is_active=True,
        is_superuser=False,
        role=UserRole.PREMIUM.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def premium_user_headers(premium_user: User) -> dict[str, str]:
    """Get auth headers for premium user."""
    access_token = create_access_token(data={"sub": str(premium_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create a user with ADMIN role."""
    user = User(
        id=uuid4(),
        email="admin@realastrology.ai",
        password_hash=get_password_hash("Admin123!@#"),
        full_name="Admin User",
        email_verified=True,
        is_active=True,
        is_superuser=True,
        role=UserRole.ADMIN.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user_headers(admin_user: User) -> dict[str, str]:
    """Get auth headers for admin user."""
    access_token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def chart_data_with_longevity() -> dict:
    """Sample chart data that includes longevity analysis (language-first format).

    Field names must match the Pydantic schemas in app/schemas/longevity.py:
    - HylegResponse, AlcochodenResponse, LongevitySummary
    """
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
            {
                "name": "Saturn",
                "longitude": 280.0,
                "latitude": 0.5,
                "speed": 0.05,
                "retrograde": False,
                "sign": "Capricorn",
                "degree": 10.0,
                "house": 7,
            },
            {
                "name": "Jupiter",
                "longitude": 120.0,
                "latitude": 1.0,
                "speed": 0.1,
                "retrograde": False,
                "sign": "Leo",
                "degree": 0.0,
                "house": 1,
            },
        ],
        "houses": [
            {"number": 1, "cusp": 120.0, "sign": "Leo", "longitude": 120.0},
            {"number": 2, "cusp": 150.0, "sign": "Virgo", "longitude": 150.0},
            {"number": 3, "cusp": 180.0, "sign": "Libra", "longitude": 180.0},
            {"number": 4, "cusp": 210.0, "sign": "Scorpio", "longitude": 210.0},
            {"number": 5, "cusp": 240.0, "sign": "Sagittarius", "longitude": 240.0},
            {"number": 6, "cusp": 270.0, "sign": "Capricorn", "longitude": 270.0},
            {"number": 7, "cusp": 300.0, "sign": "Aquarius", "longitude": 300.0},
            {"number": 8, "cusp": 330.0, "sign": "Pisces", "longitude": 330.0},
            {"number": 9, "cusp": 0.0, "sign": "Aries", "longitude": 0.0},
            {"number": 10, "cusp": 30.0, "sign": "Taurus", "longitude": 30.0},
            {"number": 11, "cusp": 60.0, "sign": "Gemini", "longitude": 60.0},
            {"number": 12, "cusp": 90.0, "sign": "Cancer", "longitude": 90.0},
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "aspect": "trine",
                "angle": 120.0,
                "orb": 2.3,
                "applying": True,
            },
            {
                "planet1": "Sun",
                "planet2": "Saturn",
                "aspect": "trine",
                "angle": 120.0,
                "orb": 5.0,
                "applying": False,
            },
        ],
        "ascendant": 120.0,
        "midheaven": 30.0,
        "sect": "diurnal",
        "arabic_parts": {
            "fortune": {"longitude": 200.0, "sign": "Libra", "degree": 20.0, "house": 4},
        },
        "longevity": {
            "hyleg": {
                "hyleg": "Sun",
                "hyleg_longitude": 45.123,
                "hyleg_sign": "Taurus",
                "hyleg_house": 10,
                "is_day_chart": True,
                "method": "ptolemaic",
                "qualification_reason": "Sun in hylegical house 10, aspected by Saturn (domicile lord)",
                "hyleg_dignity": {
                    "score": 0,
                    "dignities": [],
                    "is_ruler": False,
                    "is_exalted": False,
                    "is_detriment": False,
                    "is_fall": False,
                    "classification": "peregrine",
                },
                "aspecting_planets": ["Saturn"],
                "domicile_lord": "Venus",
                "candidates_evaluated": [],
            },
            "alcochoden": {
                "alcochoden": "Saturn",
                "alcochoden_longitude": 280.0,
                "alcochoden_sign": "Capricorn",
                "alcochoden_house": 7,
                "hyleg_degree": 15.123,
                "hyleg_sign": "Taurus",
                "dignity_at_hyleg": {"type": "term", "points": 2},
                "aspect_to_hyleg": {"type": "Trine", "orb": 5.0, "applying": False},
                "alcochoden_condition": {
                    "essential_dignity": "domicile",
                    "accidental_dignity": "succedent",
                    "is_retrograde": False,
                    "is_combust": False,
                    "is_debilitated": False,
                    "benefic_aspects": [],
                    "malefic_aspects": [],
                },
                "years": {"minor": 30, "middle": 43.5, "major": 57},
                "year_type_selected": "major",
                "base_years": 57,
                "modifications": [
                    {
                        "reason": "Succedent house placement",
                        "adjustment": 1,
                        "type": "house_position",
                    }
                ],
                "final_years": 58,
                "candidates_evaluated": [],
                "no_alcochoden_reason": None,
            },
            "summary": {
                "vital_force": "strong",
                "vital_force_description": "Sun in angular house provides strong vital force",
                "potential_years": 58,
                "years_confidence": "high",
                "hyleg_found": True,
                "alcochoden_found": True,
                "method": "ptolemaic",
            },
            "educational_disclaimer": "This analysis is for educational purposes only.",
        },
    }
    return {
        "en-US": base_data,
        "pt-BR": base_data,
    }


@pytest.fixture
async def premium_chart_with_longevity(
    db_session: AsyncSession,
    premium_user: User,
    chart_data_with_longevity: dict,
) -> BirthChart:
    """Create a chart owned by premium user with longevity data."""
    chart = BirthChart(
        id=uuid4(),
        user_id=premium_user.id,
        person_name="Premium User Chart",
        birth_datetime=datetime(1990, 6, 15, 14, 30, tzinfo=UTC),
        birth_timezone="America/New_York",
        latitude=40.7128,
        longitude=-74.0060,
        city="New York",
        country="USA",
        chart_data=chart_data_with_longevity,
        house_system="placidus",
        status="completed",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(chart)
    await db_session.commit()
    await db_session.refresh(chart)
    return chart


@pytest.fixture
async def free_chart_with_longevity(
    db_session: AsyncSession,
    free_user: User,
    chart_data_with_longevity: dict,
) -> BirthChart:
    """Create a chart owned by free user with longevity data."""
    chart = BirthChart(
        id=uuid4(),
        user_id=free_user.id,
        person_name="Free User Chart",
        birth_datetime=datetime(1985, 3, 20, 10, 0, tzinfo=UTC),
        birth_timezone="Europe/London",
        latitude=51.5074,
        longitude=-0.1278,
        city="London",
        country="UK",
        chart_data=chart_data_with_longevity,
        house_system="placidus",
        status="completed",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(chart)
    await db_session.commit()
    await db_session.refresh(chart)
    return chart


@pytest.fixture
async def admin_chart_with_longevity(
    db_session: AsyncSession,
    admin_user: User,
    chart_data_with_longevity: dict,
) -> BirthChart:
    """Create a chart owned by admin user with longevity data."""
    chart = BirthChart(
        id=uuid4(),
        user_id=admin_user.id,
        person_name="Admin User Chart",
        birth_datetime=datetime(1980, 12, 25, 8, 30, tzinfo=UTC),
        birth_timezone="America/Los_Angeles",
        latitude=34.0522,
        longitude=-118.2437,
        city="Los Angeles",
        country="USA",
        chart_data=chart_data_with_longevity,
        house_system="placidus",
        status="completed",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(chart)
    await db_session.commit()
    await db_session.refresh(chart)
    return chart


# =============================================================================
# Authentication Tests
# =============================================================================


class TestLongevityAuthentication:
    """Test that longevity endpoints require authentication."""

    @pytest.mark.asyncio
    async def test_hyleg_requires_authentication(
        self,
        client: AsyncClient,
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """GET /hyleg without auth should return 401."""
        response = await client.get(f"/api/v1/charts/{premium_chart_with_longevity.id}/hyleg")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_alcochoden_requires_authentication(
        self,
        client: AsyncClient,
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """GET /alcochoden without auth should return 401."""
        response = await client.get(f"/api/v1/charts/{premium_chart_with_longevity.id}/alcochoden")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_longevity_requires_authentication(
        self,
        client: AsyncClient,
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """GET /longevity without auth should return 401."""
        response = await client.get(f"/api/v1/charts/{premium_chart_with_longevity.id}/longevity")
        assert response.status_code == 401


# =============================================================================
# Premium Access Tests
# =============================================================================


class TestLongevityPremiumAccess:
    """Test that longevity endpoints require premium access."""

    @pytest.mark.asyncio
    async def test_hyleg_blocks_free_user(
        self,
        client: AsyncClient,
        free_user_headers: dict[str, str],
        free_chart_with_longevity: BirthChart,
    ) -> None:
        """Free users should get 403 when accessing hyleg."""
        response = await client.get(
            f"/api/v1/charts/{free_chart_with_longevity.id}/hyleg",
            headers=free_user_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "premium_required"

    @pytest.mark.asyncio
    async def test_alcochoden_blocks_free_user(
        self,
        client: AsyncClient,
        free_user_headers: dict[str, str],
        free_chart_with_longevity: BirthChart,
    ) -> None:
        """Free users should get 403 when accessing alcochoden."""
        response = await client.get(
            f"/api/v1/charts/{free_chart_with_longevity.id}/alcochoden",
            headers=free_user_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "premium_required"

    @pytest.mark.asyncio
    async def test_longevity_blocks_free_user(
        self,
        client: AsyncClient,
        free_user_headers: dict[str, str],
        free_chart_with_longevity: BirthChart,
    ) -> None:
        """Free users should get 403 when accessing longevity."""
        response = await client.get(
            f"/api/v1/charts/{free_chart_with_longevity.id}/longevity",
            headers=free_user_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "premium_required"

    @pytest.mark.asyncio
    async def test_hyleg_allows_premium_user(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Premium users should be able to access hyleg."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/hyleg",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "hyleg" in data
        assert data["hyleg"] == "Sun"

    @pytest.mark.asyncio
    async def test_alcochoden_allows_premium_user(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Premium users should be able to access alcochoden."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/alcochoden",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "alcochoden" in data
        assert data["alcochoden"] == "Saturn"

    @pytest.mark.asyncio
    async def test_longevity_allows_premium_user(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Premium users should be able to access full longevity analysis."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/longevity",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "hyleg" in data
        assert "alcochoden" in data
        assert "summary" in data
        assert "educational_disclaimer" in data

    @pytest.mark.asyncio
    async def test_hyleg_allows_admin_user(
        self,
        client: AsyncClient,
        admin_user_headers: dict[str, str],
        admin_chart_with_longevity: BirthChart,
    ) -> None:
        """Admin users should be able to access hyleg on their own charts."""
        response = await client.get(
            f"/api/v1/charts/{admin_chart_with_longevity.id}/hyleg",
            headers=admin_user_headers,
        )
        assert response.status_code == 200


# =============================================================================
# Response Format Tests
# =============================================================================


class TestLongevityResponseFormat:
    """Test the response format of longevity endpoints."""

    @pytest.mark.asyncio
    async def test_hyleg_response_structure(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Test that hyleg response has correct structure."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/hyleg",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "hyleg" in data
        assert "hyleg_longitude" in data
        assert "hyleg_sign" in data
        assert "hyleg_house" in data
        assert "is_day_chart" in data
        assert "method" in data
        assert "qualification_reason" in data

    @pytest.mark.asyncio
    async def test_alcochoden_response_structure(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Test that alcochoden response has correct structure."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/alcochoden",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Check required fields (matches AlcochodenResponse schema)
        assert "alcochoden" in data
        assert "years" in data or "no_alcochoden_reason" in data
        if data["alcochoden"]:
            assert "alcochoden_longitude" in data
            assert "alcochoden_sign" in data
            assert "alcochoden_house" in data
            assert "year_type_selected" in data
            assert "base_years" in data
            assert "final_years" in data

    @pytest.mark.asyncio
    async def test_longevity_response_structure(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Test that full longevity response has correct structure."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/longevity",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Check top-level structure
        assert "hyleg" in data
        assert "alcochoden" in data
        assert "summary" in data
        assert "educational_disclaimer" in data

        # Check summary structure (matches LongevitySummary schema)
        summary = data["summary"]
        assert "vital_force" in summary
        assert "potential_years" in summary
        assert "years_confidence" in summary
        assert "hyleg_found" in summary
        assert "alcochoden_found" in summary


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestLongevityErrorHandling:
    """Test error handling for longevity endpoints."""

    @pytest.mark.asyncio
    async def test_hyleg_chart_not_found(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
    ) -> None:
        """Non-existent chart should return 404."""
        fake_chart_id = uuid4()
        response = await client.get(
            f"/api/v1/charts/{fake_chart_id}/hyleg",
            headers=premium_user_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_alcochoden_chart_not_found(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
    ) -> None:
        """Non-existent chart should return 404."""
        fake_chart_id = uuid4()
        response = await client.get(
            f"/api/v1/charts/{fake_chart_id}/alcochoden",
            headers=premium_user_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_longevity_chart_not_found(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
    ) -> None:
        """Non-existent chart should return 404."""
        fake_chart_id = uuid4()
        response = await client.get(
            f"/api/v1/charts/{fake_chart_id}/longevity",
            headers=premium_user_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_hyleg_unauthorized_chart_access(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        free_chart_with_longevity: BirthChart,
    ) -> None:
        """Accessing another user's chart should return 403 or 404."""
        response = await client.get(
            f"/api/v1/charts/{free_chart_with_longevity.id}/hyleg",
            headers=premium_user_headers,
        )
        # Should be 404 (chart not found for this user) or 403 (forbidden)
        assert response.status_code in [403, 404]


# =============================================================================
# Method Parameter Tests
# =============================================================================


class TestLongevityMethodParameter:
    """Test the method parameter for longevity calculations."""

    @pytest.mark.asyncio
    async def test_hyleg_default_method(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Default method should be ptolemaic."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/hyleg",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "ptolemaic"

    @pytest.mark.asyncio
    async def test_hyleg_explicit_ptolemaic_method(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Explicit ptolemaic method should work."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/hyleg?method=ptolemaic",
            headers=premium_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "ptolemaic"

    @pytest.mark.asyncio
    async def test_hyleg_invalid_method(
        self,
        client: AsyncClient,
        premium_user_headers: dict[str, str],
        premium_chart_with_longevity: BirthChart,
    ) -> None:
        """Invalid method should return 422 (validation error)."""
        response = await client.get(
            f"/api/v1/charts/{premium_chart_with_longevity.id}/hyleg?method=invalid",
            headers=premium_user_headers,
        )
        assert response.status_code == 422
