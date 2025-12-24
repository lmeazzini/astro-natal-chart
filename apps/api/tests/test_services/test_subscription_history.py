"""Tests for subscription history tracking."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SubscriptionChangeType, SubscriptionStatus, UserRole
from app.models.subscription import Subscription
from app.models.user import User
from app.repositories.subscription_history_repository import SubscriptionHistoryRepository
from app.services import subscription_service


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user for testing subscription operations."""
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_session)
    admin = User(
        id=uuid4(),
        email="admin_history@test.com",
        password_hash="hashed",
        full_name="Admin User History",
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
    """Create user with premium subscription for testing."""
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db_session)
    user = User(
        id=uuid4(),
        email="premium_history@test.com",
        password_hash="hashed",
        full_name="Premium User History",
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


class TestSubscriptionHistoryCreation:
    """Tests for subscription history record creation."""

    async def test_grant_creates_history_record(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test granting subscription creates history record."""
        history_repo = SubscriptionHistoryRepository(db_session)

        # Grant subscription
        subscription = await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            days=30,
            admin_user=admin_user,
        )

        # Verify history record exists
        history = await history_repo.get_by_user_id(test_user.id)
        assert len(history) == 1

        # Verify history record details
        record = history[0]
        assert record.subscription_id == subscription.id
        assert record.user_id == test_user.id
        assert record.status == SubscriptionStatus.ACTIVE.value
        assert record.change_type == SubscriptionChangeType.GRANTED.value
        assert record.changed_by_user_id == admin_user.id
        assert record.expires_at is not None

    async def test_revoke_creates_history_record(
        self,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
    ):
        """Test revoking subscription creates history record."""
        history_repo = SubscriptionHistoryRepository(db_session)

        # Revoke subscription
        await subscription_service.revoke_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            admin_user=admin_user,
        )

        # Verify history record exists
        history = await history_repo.get_by_user_id(premium_user.id)
        assert len(history) == 1

        # Verify history record details
        record = history[0]
        assert record.subscription_id == active_subscription.id
        assert record.user_id == premium_user.id
        assert record.status == SubscriptionStatus.CANCELLED.value
        assert record.change_type == SubscriptionChangeType.REVOKED.value
        assert record.changed_by_user_id == admin_user.id

    async def test_extend_creates_history_record(
        self,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
    ):
        """Test extending subscription creates history record."""
        history_repo = SubscriptionHistoryRepository(db_session)

        # Extend subscription
        await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            extend_days=30,
            admin_user=admin_user,
        )

        # Verify history record exists
        history = await history_repo.get_by_user_id(premium_user.id)
        assert len(history) == 1

        # Verify history record details
        record = history[0]
        assert record.subscription_id == active_subscription.id
        assert record.user_id == premium_user.id
        assert record.status == SubscriptionStatus.ACTIVE.value
        assert record.change_type == SubscriptionChangeType.EXTENDED.value
        assert record.changed_by_user_id == admin_user.id

    async def test_expire_creates_history_record(self, db_session: AsyncSession):
        """Test auto-expiration creates history record with no changed_by_user_id."""
        from app.repositories.subscription_repository import SubscriptionRepository
        from app.repositories.user_repository import UserRepository

        subscription_repo = SubscriptionRepository(db_session)
        user_repo = UserRepository(db_session)
        history_repo = SubscriptionHistoryRepository(db_session)

        # Create user with expired subscription
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email="expired_history@test.com",
            password_hash="hashed",
            full_name="Expired User History",
            role=UserRole.PREMIUM.value,
            email_verified=True,
            is_active=True,
        )
        created_user = await user_repo.create(user)

        subscription = Subscription(
            id=uuid4(),
            user_id=created_user.id,
            status=SubscriptionStatus.ACTIVE.value,
            started_at=now - timedelta(days=60),
            expires_at=now - timedelta(days=1),  # Expired yesterday
        )
        await subscription_repo.create(subscription)
        await db_session.commit()

        # Run expiration check
        await subscription_service.check_and_expire_subscriptions(db_session)

        # Verify history record exists
        history = await history_repo.get_by_user_id(created_user.id)
        assert len(history) == 1

        # Verify history record details
        record = history[0]
        assert record.subscription_id == subscription.id
        assert record.user_id == created_user.id
        assert record.status == SubscriptionStatus.EXPIRED.value
        assert record.change_type == SubscriptionChangeType.EXPIRED.value
        assert record.changed_by_user_id is None  # System auto-expired


class TestSubscriptionHistoryQuery:
    """Tests for querying subscription history."""

    async def test_get_history_by_user_id(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test getting history for a user."""
        history_repo = SubscriptionHistoryRepository(db_session)

        # Grant, then extend, then revoke
        await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            days=30,
            admin_user=admin_user,
        )
        await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            extend_days=30,
            admin_user=admin_user,
        )
        await subscription_service.revoke_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            admin_user=admin_user,
        )

        # Get history
        history = await history_repo.get_by_user_id(test_user.id)
        assert len(history) == 3

        # Verify order (most recent first)
        assert history[0].change_type == SubscriptionChangeType.REVOKED.value
        assert history[1].change_type == SubscriptionChangeType.EXTENDED.value
        assert history[2].change_type == SubscriptionChangeType.GRANTED.value

    async def test_get_history_pagination(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test history pagination."""
        history_repo = SubscriptionHistoryRepository(db_session)

        # Grant subscription
        await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            days=30,
            admin_user=admin_user,
        )

        # Extend multiple times to create history records
        for _ in range(5):
            await subscription_service.extend_premium_subscription(
                db=db_session,
                user_id=test_user.id,
                extend_days=10,
                admin_user=admin_user,
            )

        # Get paginated history
        first_page = await history_repo.get_by_user_id(test_user.id, skip=0, limit=3)
        assert len(first_page) == 3

        second_page = await history_repo.get_by_user_id(test_user.id, skip=3, limit=3)
        assert len(second_page) == 3

        # Verify no overlap
        first_ids = {r.id for r in first_page}
        second_ids = {r.id for r in second_page}
        assert first_ids.isdisjoint(second_ids)

    async def test_get_empty_history(self, db_session: AsyncSession, test_user: User):
        """Test getting history for user with no subscription history."""
        history_repo = SubscriptionHistoryRepository(db_session)

        history = await history_repo.get_by_user_id(test_user.id)
        assert len(history) == 0


class TestGetSubscriptionHistoryService:
    """Tests for the get_subscription_history service function."""

    async def test_get_subscription_history(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test service function to get subscription history."""
        # Grant and extend
        await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            days=30,
            admin_user=admin_user,
        )
        await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            extend_days=30,
            admin_user=admin_user,
        )

        # Get history via service function
        history = await subscription_service.get_subscription_history(
            db=db_session,
            user_id=test_user.id,
        )

        assert len(history) == 2
        assert history[0].change_type == SubscriptionChangeType.EXTENDED.value
        assert history[1].change_type == SubscriptionChangeType.GRANTED.value
