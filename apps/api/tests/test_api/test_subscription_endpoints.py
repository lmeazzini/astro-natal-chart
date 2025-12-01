"""Tests for subscription API endpoints."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SubscriptionStatus, UserRole
from app.models.subscription import Subscription
from app.models.user import User


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user for testing admin endpoints."""
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_session)
    admin = User(
        id=uuid4(),
        email="admin@test.com",
        password_hash="hashed",
        full_name="Admin User",
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
        email="premium@test.com",
        password_hash="hashed",
        full_name="Premium User",
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


class TestGrantSubscription:
    """Tests for POST /admin/subscriptions/grant endpoint."""

    async def test_grant_subscription_success(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User, admin_headers: dict
    ):
        """Test successfully granting subscription."""
        response = await client.post(
            "/api/v1/admin/subscriptions/grant",
            json={
                "user_id": str(test_user.id),
                "days": 30,
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert data["user_id"] == str(test_user.id)
        assert data["status"] == "active"
        assert data["expires_at"] is not None
        assert data["is_active"] is True

        # Verify user role upgraded
        await db_session.refresh(test_user)
        assert test_user.role == UserRole.PREMIUM.value

    async def test_grant_lifetime_subscription(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User, admin_headers: dict
    ):
        """Test granting lifetime subscription."""
        response = await client.post(
            "/api/v1/admin/subscriptions/grant",
            json={
                "user_id": str(test_user.id),
                "days": None,
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()

        # Verify lifetime subscription
        assert data["expires_at"] is None
        assert data["is_active"] is True
        assert data["days_remaining"] is None

    async def test_grant_subscription_user_not_found(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test granting subscription to non-existent user."""
        fake_user_id = str(uuid4())

        response = await client.post(
            "/api/v1/admin/subscriptions/grant",
            json={
                "user_id": fake_user_id,
                "days": 30,
            },
            headers=admin_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_grant_subscription_requires_admin(
        self, client: AsyncClient, test_user: User, user_headers: dict
    ):
        """Test granting subscription requires admin privileges."""
        response = await client.post(
            "/api/v1/admin/subscriptions/grant",
            json={
                "user_id": str(test_user.id),
                "days": 30,
            },
            headers=user_headers,
        )

        assert response.status_code == 403

    async def test_grant_subscription_requires_auth(self, client: AsyncClient, test_user: User):
        """Test granting subscription requires authentication."""
        response = await client.post(
            "/api/v1/admin/subscriptions/grant",
            json={
                "user_id": str(test_user.id),
                "days": 30,
            },
        )

        assert response.status_code == 401

    async def test_grant_subscription_invalid_days(
        self, client: AsyncClient, test_user: User, admin_headers: dict
    ):
        """Test granting subscription with invalid days value."""
        # Test days < 1
        response = await client.post(
            "/api/v1/admin/subscriptions/grant",
            json={
                "user_id": str(test_user.id),
                "days": 0,
            },
            headers=admin_headers,
        )
        assert response.status_code == 422

        # Test days > 3650 (max)
        response = await client.post(
            "/api/v1/admin/subscriptions/grant",
            json={
                "user_id": str(test_user.id),
                "days": 4000,
            },
            headers=admin_headers,
        )
        assert response.status_code == 422


class TestRevokeSubscription:
    """Tests for POST /admin/subscriptions/revoke endpoint."""

    async def test_revoke_subscription_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_headers: dict,
    ):
        """Test successfully revoking subscription."""
        response = await client.post(
            "/api/v1/admin/subscriptions/revoke",
            json={"user_id": str(premium_user.id)},
            headers=admin_headers,
        )

        assert response.status_code == 204

        # Verify subscription cancelled
        await db_session.refresh(active_subscription)
        assert active_subscription.status == SubscriptionStatus.CANCELLED.value

        # Verify user downgraded
        await db_session.refresh(premium_user)
        assert premium_user.role == UserRole.FREE.value

    async def test_revoke_subscription_user_not_found(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test revoking subscription from non-existent user."""
        fake_user_id = str(uuid4())

        response = await client.post(
            "/api/v1/admin/subscriptions/revoke",
            json={"user_id": fake_user_id},
            headers=admin_headers,
        )

        assert response.status_code == 404

    async def test_revoke_subscription_no_subscription(
        self, client: AsyncClient, test_user: User, admin_headers: dict
    ):
        """Test revoking subscription from user without subscription."""
        response = await client.post(
            "/api/v1/admin/subscriptions/revoke",
            json={"user_id": str(test_user.id)},
            headers=admin_headers,
        )

        assert response.status_code == 404
        assert "subscription not found" in response.json()["detail"].lower()

    async def test_revoke_subscription_requires_admin(
        self,
        client: AsyncClient,
        premium_user: User,
        active_subscription: Subscription,
        user_headers: dict,
    ):
        """Test revoking subscription requires admin privileges."""
        response = await client.post(
            "/api/v1/admin/subscriptions/revoke",
            json={"user_id": str(premium_user.id)},
            headers=user_headers,
        )

        assert response.status_code == 403


class TestExtendSubscription:
    """Tests for PATCH /admin/subscriptions/extend endpoint."""

    async def test_extend_subscription_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_headers: dict,
    ):
        """Test successfully extending subscription."""
        original_started_at = active_subscription.started_at
        original_expires_at = active_subscription.expires_at

        response = await client.patch(
            "/api/v1/admin/subscriptions/extend",
            json={
                "user_id": str(premium_user.id),
                "extend_days": 30,
            },
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify started_at NOT changed
        assert (
            datetime.fromisoformat(data["started_at"].replace("Z", "+00:00")) == original_started_at
        )

        # Verify expires_at extended
        new_expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        expected_expires = original_expires_at + timedelta(days=30)
        delta = abs((new_expires_at - expected_expires).total_seconds())
        assert delta < 5

    async def test_extend_expired_subscription_reactivates(
        self, client: AsyncClient, db_session: AsyncSession, premium_user: User, admin_headers: dict
    ):
        """Test extending expired subscription reactivates it."""
        from app.repositories.subscription_repository import SubscriptionRepository

        subscription_repo = SubscriptionRepository(db_session)

        # Create expired subscription
        now = datetime.now(UTC)
        expired_sub = Subscription(
            id=uuid4(),
            user_id=premium_user.id,
            status=SubscriptionStatus.EXPIRED.value,
            started_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=30),
        )
        await subscription_repo.create(expired_sub)
        await db_session.commit()

        # Downgrade user
        premium_user.role = UserRole.FREE.value
        await db_session.commit()

        # Extend subscription
        response = await client.patch(
            "/api/v1/admin/subscriptions/extend",
            json={
                "user_id": str(premium_user.id),
                "extend_days": 30,
            },
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify reactivated
        assert data["status"] == "active"
        assert data["is_active"] is True

        # Verify user upgraded
        await db_session.refresh(premium_user)
        assert premium_user.role == UserRole.PREMIUM.value

    async def test_extend_lifetime_subscription_fails(
        self, client: AsyncClient, db_session: AsyncSession, premium_user: User, admin_headers: dict
    ):
        """Test extending lifetime subscription returns error."""
        from app.repositories.subscription_repository import SubscriptionRepository

        subscription_repo = SubscriptionRepository(db_session)

        # Create lifetime subscription
        lifetime_sub = Subscription(
            id=uuid4(),
            user_id=premium_user.id,
            status=SubscriptionStatus.ACTIVE.value,
            started_at=datetime.now(UTC),
            expires_at=None,  # Lifetime
        )
        await subscription_repo.create(lifetime_sub)
        await db_session.commit()

        # Try to extend
        response = await client.patch(
            "/api/v1/admin/subscriptions/extend",
            json={
                "user_id": str(premium_user.id),
                "extend_days": 30,
            },
            headers=admin_headers,
        )

        assert response.status_code == 400
        assert "lifetime" in response.json()["detail"].lower()

    async def test_extend_nonexistent_subscription_fails(
        self, client: AsyncClient, test_user: User, admin_headers: dict
    ):
        """Test extending non-existent subscription returns error."""
        response = await client.patch(
            "/api/v1/admin/subscriptions/extend",
            json={
                "user_id": str(test_user.id),
                "extend_days": 30,
            },
            headers=admin_headers,
        )

        # The error message says "Use grant instead", which is a 400 Bad Request (not 404)
        # because the user exists but has no subscription
        assert response.status_code == 400
        assert (
            "not found" in response.json()["detail"].lower()
            or "grant" in response.json()["detail"].lower()
        )

    async def test_extend_subscription_invalid_days(
        self,
        client: AsyncClient,
        premium_user: User,
        active_subscription: Subscription,
        admin_headers: dict,
    ):
        """Test extending subscription with invalid days value."""
        # Test days < 1
        response = await client.patch(
            "/api/v1/admin/subscriptions/extend",
            json={
                "user_id": str(premium_user.id),
                "extend_days": 0,
            },
            headers=admin_headers,
        )
        assert response.status_code == 422

        # Test days > 3650 (max)
        response = await client.patch(
            "/api/v1/admin/subscriptions/extend",
            json={
                "user_id": str(premium_user.id),
                "extend_days": 4000,
            },
            headers=admin_headers,
        )
        assert response.status_code == 422

    async def test_extend_subscription_requires_admin(
        self,
        client: AsyncClient,
        premium_user: User,
        active_subscription: Subscription,
        user_headers: dict,
    ):
        """Test extending subscription requires admin privileges."""
        response = await client.patch(
            "/api/v1/admin/subscriptions/extend",
            json={
                "user_id": str(premium_user.id),
                "extend_days": 30,
            },
            headers=user_headers,
        )

        assert response.status_code == 403


class TestListSubscriptions:
    """Tests for GET /admin/subscriptions endpoint."""

    async def test_list_subscriptions_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        active_subscription: Subscription,
        admin_headers: dict,
    ):
        """Test successfully listing subscriptions."""
        response = await client.get(
            "/api/v1/admin/subscriptions",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify list structure
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verify subscription in list
        sub_ids = [sub["id"] for sub in data]
        assert str(active_subscription.id) in sub_ids

    async def test_list_subscriptions_pagination(
        self, client: AsyncClient, db_session: AsyncSession, admin_headers: dict
    ):
        """Test subscription list pagination."""
        from app.repositories.subscription_repository import SubscriptionRepository
        from app.repositories.user_repository import UserRepository

        subscription_repo = SubscriptionRepository(db_session)
        user_repo = UserRepository(db_session)

        # Create 5 subscriptions
        now = datetime.now(UTC)
        for i in range(5):
            user = User(
                id=uuid4(),
                email=f"user{i}@test.com",
                password_hash="hashed",
                full_name=f"User {i}",
                role=UserRole.PREMIUM.value,
                email_verified=True,
                is_active=True,
            )
            created_user = await user_repo.create(user)

            subscription = Subscription(
                id=uuid4(),
                user_id=created_user.id,
                status=SubscriptionStatus.ACTIVE.value,
                started_at=now,
                expires_at=now + timedelta(days=30),
            )
            await subscription_repo.create(subscription)

        await db_session.commit()

        # Test first page
        response = await client.get(
            "/api/v1/admin/subscriptions?skip=0&limit=3",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Test second page
        response = await client.get(
            "/api/v1/admin/subscriptions?skip=3&limit=3",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2  # At least 2 more from our 5

    async def test_list_subscriptions_requires_admin(
        self, client: AsyncClient, active_subscription: Subscription, user_headers: dict
    ):
        """Test listing subscriptions requires admin privileges."""
        response = await client.get(
            "/api/v1/admin/subscriptions",
            headers=user_headers,
        )

        assert response.status_code == 403


class TestGetUserSubscription:
    """Tests for GET /users/me/subscription endpoint."""

    async def test_get_user_subscription_with_active_subscription(
        self, client: AsyncClient, premium_user: User, active_subscription: Subscription
    ):
        """Test getting user's own subscription when active."""
        from app.core.security import create_access_token

        access_token = create_access_token(data={"sub": str(premium_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get(
            "/api/v1/users/me/subscription",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["has_subscription"] is True
        assert data["is_premium"] is True
        assert data["subscription"] is not None
        assert data["subscription"]["id"] == str(active_subscription.id)
        assert data["subscription"]["is_active"] is True

    async def test_get_user_subscription_without_subscription(
        self, client: AsyncClient, test_user: User, user_headers: dict
    ):
        """Test getting user's own subscription when none exists."""
        response = await client.get(
            "/api/v1/users/me/subscription",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["has_subscription"] is False
        assert data["is_premium"] is False
        assert data["subscription"] is None

    async def test_get_user_subscription_with_expired_subscription(
        self, client: AsyncClient, db_session: AsyncSession, premium_user: User
    ):
        """Test getting user's subscription when expired."""
        from app.core.security import create_access_token
        from app.repositories.subscription_repository import SubscriptionRepository

        subscription_repo = SubscriptionRepository(db_session)

        # Create expired subscription
        now = datetime.now(UTC)
        expired_sub = Subscription(
            id=uuid4(),
            user_id=premium_user.id,
            status=SubscriptionStatus.EXPIRED.value,
            started_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=1),
        )
        await subscription_repo.create(expired_sub)

        # Downgrade user role since subscription is expired
        premium_user.role = UserRole.FREE.value

        await db_session.commit()

        access_token = create_access_token(data={"sub": str(premium_user.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get(
            "/api/v1/users/me/subscription",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response shows expired state
        assert data["has_subscription"] is True
        assert data["is_premium"] is False  # Not active
        assert data["subscription"]["is_active"] is False
        assert data["subscription"]["is_expired"] is True

    async def test_get_user_subscription_requires_auth(self, client: AsyncClient):
        """Test getting subscription requires authentication."""
        response = await client.get("/api/v1/users/me/subscription")

        assert response.status_code == 401
