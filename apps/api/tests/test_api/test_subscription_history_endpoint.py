"""Tests for subscription history API endpoint."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SubscriptionStatus, UserRole
from app.models.subscription import Subscription
from app.models.user import User
from app.services import subscription_service


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user for testing admin endpoints."""
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_session)
    admin = User(
        id=uuid4(),
        email="admin_history_api@test.com",
        password_hash="hashed",
        full_name="Admin User History API",
        role=UserRole.ADMIN.value,
        is_superuser=True,
        email_verified=True,
        is_active=True,
    )
    created_admin = await user_repo.create(admin)
    await db_session.commit()
    return created_admin


@pytest.fixture
async def premium_user(db_session: AsyncSession) -> User:
    """Create premium user for testing."""
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_session)
    user = User(
        id=uuid4(),
        email="premium_history_api@test.com",
        password_hash="hashed",
        full_name="Premium User History API",
        role=UserRole.PREMIUM.value,
        email_verified=True,
        is_active=True,
    )
    created_user = await user_repo.create(user)
    await db_session.commit()
    return created_user


@pytest.fixture
async def active_subscription(db_session: AsyncSession, premium_user: User) -> Subscription:
    """Create active subscription for testing."""
    from app.repositories.subscription_repository import SubscriptionRepository

    subscription_repo = SubscriptionRepository(db_session)
    now = datetime.now(UTC)
    subscription = Subscription(
        id=uuid4(),
        user_id=premium_user.id,
        status=SubscriptionStatus.ACTIVE.value,
        started_at=now,
        expires_at=now + timedelta(days=30),
    )
    created_sub = await subscription_repo.create(subscription)
    await db_session.commit()
    return created_sub


@pytest.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    """Generate authentication headers for admin user."""
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def user_headers(test_user: User) -> dict[str, str]:
    """Generate authentication headers for regular user."""
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


class TestGetSubscriptionHistoryEndpoint:
    """Tests for GET /admin/subscriptions/{user_id}/history endpoint."""

    async def test_get_history_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
        admin_headers: dict,
    ):
        """Test successfully getting subscription history."""
        # Create some history by extending subscription
        await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            extend_days=30,
            admin_user=admin_user,
        )

        # Call endpoint
        response = await client.get(
            f"/api/v1/admin/subscriptions/{premium_user.id}/history",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["change_type"] == "extended"
        assert data[0]["user_id"] == str(premium_user.id)
        assert data[0]["changed_by_user_id"] == str(admin_user.id)

    async def test_get_history_empty(
        self,
        client: AsyncClient,
        test_user: User,
        admin_headers: dict,
    ):
        """Test getting empty history for user with no subscription."""
        response = await client.get(
            f"/api/v1/admin/subscriptions/{test_user.id}/history",
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_history_user_not_found(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ):
        """Test getting history for non-existent user."""
        fake_user_id = uuid4()
        response = await client.get(
            f"/api/v1/admin/subscriptions/{fake_user_id}/history",
            headers=admin_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_history_non_admin_forbidden(
        self,
        client: AsyncClient,
        premium_user: User,
        user_headers: dict,
    ):
        """Test non-admin user cannot access history endpoint."""
        response = await client.get(
            f"/api/v1/admin/subscriptions/{premium_user.id}/history",
            headers=user_headers,
        )

        assert response.status_code == 403

    async def test_get_history_unauthenticated(
        self,
        client: AsyncClient,
        premium_user: User,
    ):
        """Test unauthenticated user cannot access history endpoint."""
        response = await client.get(
            f"/api/v1/admin/subscriptions/{premium_user.id}/history",
        )

        assert response.status_code == 401

    async def test_get_history_pagination(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
        admin_headers: dict,
    ):
        """Test history pagination works correctly."""
        # Create multiple history records
        for _ in range(5):
            await subscription_service.extend_premium_subscription(
                db=db_session,
                user_id=premium_user.id,
                extend_days=10,
                admin_user=admin_user,
            )

        # Get first page
        response = await client.get(
            f"/api/v1/admin/subscriptions/{premium_user.id}/history",
            headers=admin_headers,
            params={"skip": 0, "limit": 2},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get second page
        response = await client.get(
            f"/api/v1/admin/subscriptions/{premium_user.id}/history",
            headers=admin_headers,
            params={"skip": 2, "limit": 2},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
