"""
Tests for the require_verified_email dependency.

This dependency ensures that only users with verified emails can access
premium features like AI interpretations and PDF exports.
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


@pytest.fixture
async def unverified_user(db_session: AsyncSession) -> User:
    """Create a user with unverified email."""
    user = User(
        id=uuid4(),
        email="unverified@example.com",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Unverified User",
        email_verified=False,  # Email NOT verified
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
async def unverified_user_headers(unverified_user: User) -> dict[str, str]:
    """Get auth headers for unverified user."""
    access_token = create_access_token(data={"sub": str(unverified_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def verified_user(db_session: AsyncSession) -> User:
    """Create a user with verified email."""
    user = User(
        id=uuid4(),
        email="verified@example.com",
        password_hash=get_password_hash("Test123!@#"),
        full_name="Verified User",
        email_verified=True,  # Email verified
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
async def verified_user_headers(verified_user: User) -> dict[str, str]:
    """Get auth headers for verified user."""
    access_token = create_access_token(data={"sub": str(verified_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def admin_unverified_user(db_session: AsyncSession) -> User:
    """Create an admin user with unverified email (admin bypass test)."""
    user = User(
        id=uuid4(),
        email="admin-unverified@example.com",
        password_hash=get_password_hash("Admin123!@#"),
        full_name="Admin Unverified",
        email_verified=False,  # Email NOT verified
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
async def admin_unverified_headers(admin_unverified_user: User) -> dict[str, str]:
    """Get auth headers for unverified admin user."""
    access_token = create_access_token(data={"sub": str(admin_unverified_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


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
        ],
        "houses": [
            {"house": 1, "cusp": 123.456, "sign": "Leo"},
        ],
        "aspects": [],
        "arabic_parts": {},
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
async def chart_for_unverified_user(
    db_session: AsyncSession,
    unverified_user: User,
    test_chart_data: dict,
) -> BirthChart:
    """Create a chart for the unverified user."""
    chart = BirthChart(
        id=uuid4(),
        user_id=unverified_user.id,
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
async def chart_for_verified_user(
    db_session: AsyncSession,
    verified_user: User,
    test_chart_data: dict,
) -> BirthChart:
    """Create a chart for the verified user."""
    chart = BirthChart(
        id=uuid4(),
        user_id=verified_user.id,
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
async def chart_for_admin_unverified(
    db_session: AsyncSession,
    admin_unverified_user: User,
    test_chart_data: dict,
) -> BirthChart:
    """Create a chart for the unverified admin user."""
    chart = BirthChart(
        id=uuid4(),
        user_id=admin_unverified_user.id,
        person_name="Admin Chart",
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


class TestRequireVerifiedEmailDependency:
    """Tests for the require_verified_email dependency on interpretation endpoints."""

    @pytest.mark.asyncio
    async def test_unverified_user_gets_403(
        self,
        client: AsyncClient,
        unverified_user_headers: dict[str, str],
        chart_for_unverified_user: BirthChart,
    ):
        """Test that unverified users get 403 with correct error structure."""
        response = await client.get(
            f"/api/v1/charts/{chart_for_unverified_user.id}/interpretations",
            headers=unverified_user_headers,
        )

        assert response.status_code == 403
        data = response.json()

        # Check error structure
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "email_not_verified"
        assert "message" in detail
        assert "user_email" in detail
        assert detail["user_email"] == "unverified@example.com"

    @pytest.mark.asyncio
    async def test_unverified_user_regenerate_gets_403(
        self,
        client: AsyncClient,
        unverified_user_headers: dict[str, str],
        chart_for_unverified_user: BirthChart,
    ):
        """Test that unverified users cannot regenerate interpretations."""
        response = await client.post(
            f"/api/v1/charts/{chart_for_unverified_user.id}/interpretations/regenerate",
            headers=unverified_user_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "email_not_verified"

    @pytest.mark.asyncio
    async def test_verified_user_can_access(
        self,
        client: AsyncClient,
        verified_user_headers: dict[str, str],
        chart_for_verified_user: BirthChart,
    ):
        """Test that verified users can access interpretations endpoint."""
        # This should not return 403 - it may return 200 or generate interpretations
        # The key assertion is that it doesn't fail with email verification error
        response = await client.get(
            f"/api/v1/charts/{chart_for_verified_user.id}/interpretations",
            headers=verified_user_headers,
        )

        # Should not be a 403 email verification error
        assert response.status_code != 403 or (
            response.status_code == 403
            and response.json().get("detail", {}).get("error") != "email_not_verified"
        )

    @pytest.mark.asyncio
    async def test_admin_bypass_email_verification(
        self,
        client: AsyncClient,
        admin_unverified_headers: dict[str, str],
        chart_for_admin_unverified: BirthChart,
    ):
        """Test that admin users bypass email verification requirement."""
        response = await client.get(
            f"/api/v1/charts/{chart_for_admin_unverified.id}/interpretations",
            headers=admin_unverified_headers,
        )

        # Admin should NOT get 403 email verification error
        # They may get 200 (success) or other errors (like OpenAI not configured)
        # but NOT the email_not_verified error
        if response.status_code == 403:
            data = response.json()
            # If 403, it should NOT be due to email verification
            assert data.get("detail", {}).get("error") != "email_not_verified"

    @pytest.mark.asyncio
    async def test_no_token_returns_401(
        self,
        client: AsyncClient,
        chart_for_verified_user: BirthChart,
    ):
        """Test that requests without token return 401."""
        response = await client.get(
            f"/api/v1/charts/{chart_for_verified_user.id}/interpretations",
        )

        # FastAPI HTTPBearer returns 401 when no Bearer token is provided
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_error_message_is_translated(
        self,
        client: AsyncClient,
        unverified_user_headers: dict[str, str],
        chart_for_unverified_user: BirthChart,
    ):
        """Test that error message is properly formatted."""
        response = await client.get(
            f"/api/v1/charts/{chart_for_unverified_user.id}/interpretations",
            headers=unverified_user_headers,
        )

        assert response.status_code == 403
        data = response.json()

        # Message should be a non-empty string
        message = data["detail"]["message"]
        assert isinstance(message, str)
        assert len(message) > 0
        # Should contain something about email verification
        assert "email" in message.lower() or "verif" in message.lower()
