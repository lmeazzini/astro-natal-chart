"""Tests for subscription service layer."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SubscriptionStatus, UserRole
from app.models.subscription import Subscription
from app.models.user import User
from app.services import subscription_service


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user for testing subscription operations."""
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
    """Create user with premium subscription for testing."""
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


class TestGrantPremiumSubscription:
    """Tests for granting premium subscriptions."""

    async def test_grant_new_subscription_time_limited(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test granting new time-limited subscription."""
        # Grant 30-day subscription
        subscription = await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            days=30,
            admin_user=admin_user,
        )

        # Verify subscription
        assert subscription.user_id == test_user.id
        assert subscription.status == SubscriptionStatus.ACTIVE.value
        assert subscription.expires_at is not None

        # Verify expiration date is ~30 days in future
        expected_expires = datetime.now(UTC) + timedelta(days=30)
        delta = abs((subscription.expires_at - expected_expires).total_seconds())
        assert delta < 5  # Within 5 seconds

        # Verify user role upgraded
        await db_session.refresh(test_user)
        assert test_user.role == UserRole.PREMIUM.value

    async def test_grant_new_subscription_lifetime(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test granting lifetime subscription."""
        # Grant lifetime subscription
        subscription = await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            days=None,
            admin_user=admin_user,
        )

        # Verify subscription
        assert subscription.user_id == test_user.id
        assert subscription.status == SubscriptionStatus.ACTIVE.value
        assert subscription.expires_at is None  # Lifetime

        # Verify user role upgraded
        await db_session.refresh(test_user)
        assert test_user.role == UserRole.PREMIUM.value

    async def test_grant_updates_existing_subscription(
        self,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
    ):
        """Test granting subscription to user with existing subscription updates it."""
        original_id = active_subscription.id
        original_started_at = active_subscription.started_at

        # Grant new 60-day subscription
        subscription = await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            days=60,
            admin_user=admin_user,
        )

        # Verify subscription was updated (same ID)
        assert subscription.id == original_id
        assert subscription.status == SubscriptionStatus.ACTIVE.value

        # Verify started_at was RESET (grant resets start date)
        assert subscription.started_at > original_started_at

        # Verify new expiration date
        expected_expires = datetime.now(UTC) + timedelta(days=60)
        delta = abs((subscription.expires_at - expected_expires).total_seconds())
        assert delta < 5

    async def test_grant_to_nonexistent_user_raises_error(
        self, db_session: AsyncSession, admin_user: User
    ):
        """Test granting subscription to non-existent user raises ValueError."""
        fake_user_id = uuid4()

        with pytest.raises(ValueError, match=f"User {fake_user_id} not found"):
            await subscription_service.grant_premium_subscription(
                db=db_session,
                user_id=fake_user_id,
                days=30,
                admin_user=admin_user,
            )

    async def test_grant_creates_audit_log(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test granting subscription creates audit log."""
        from app.repositories.audit_repository import AuditRepository

        audit_repo = AuditRepository(db_session)

        # Grant subscription
        subscription = await subscription_service.grant_premium_subscription(
            db=db_session,
            user_id=test_user.id,
            days=30,
            admin_user=admin_user,
        )

        # Verify audit log exists
        logs = await audit_repo.get_by_user(user_id=test_user.id)
        assert len(logs) > 0

        # Find subscription_granted log
        grant_log = next((log for log in logs if log.action == "subscription_granted"), None)
        assert grant_log is not None
        assert grant_log.resource_type == "subscription"
        assert grant_log.resource_id == subscription.id
        assert grant_log.extra_data["admin_id"] == str(admin_user.id)
        assert grant_log.extra_data["admin_email"] == admin_user.email
        assert grant_log.extra_data["days"] == 30


class TestRevokePremiumSubscription:
    """Tests for revoking premium subscriptions."""

    async def test_revoke_active_subscription(
        self,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
    ):
        """Test revoking active subscription."""
        # Revoke subscription
        await subscription_service.revoke_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            admin_user=admin_user,
        )

        # Verify subscription cancelled
        await db_session.refresh(active_subscription)
        assert active_subscription.status == SubscriptionStatus.CANCELLED.value

        # Verify user downgraded to FREE
        await db_session.refresh(premium_user)
        assert premium_user.role == UserRole.FREE.value

    async def test_revoke_nonexistent_user_raises_error(
        self, db_session: AsyncSession, admin_user: User
    ):
        """Test revoking from non-existent user raises ValueError."""
        fake_user_id = uuid4()

        with pytest.raises(ValueError, match=f"User {fake_user_id} not found"):
            await subscription_service.revoke_premium_subscription(
                db=db_session,
                user_id=fake_user_id,
                admin_user=admin_user,
            )

    async def test_revoke_user_without_subscription_raises_error(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test revoking from user without subscription raises ValueError."""
        with pytest.raises(ValueError, match=f"Subscription not found for user {test_user.id}"):
            await subscription_service.revoke_premium_subscription(
                db=db_session,
                user_id=test_user.id,
                admin_user=admin_user,
            )

    async def test_revoke_creates_audit_log(
        self,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
    ):
        """Test revoking subscription creates audit log."""
        from app.repositories.audit_repository import AuditRepository

        audit_repo = AuditRepository(db_session)

        # Revoke subscription
        await subscription_service.revoke_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            admin_user=admin_user,
        )

        # Verify audit log exists
        logs = await audit_repo.get_by_user(user_id=premium_user.id)
        assert len(logs) > 0

        # Find subscription_revoked log
        revoke_log = next((log for log in logs if log.action == "subscription_revoked"), None)
        assert revoke_log is not None
        assert revoke_log.resource_type == "subscription"
        assert revoke_log.resource_id == active_subscription.id
        assert revoke_log.extra_data["admin_id"] == str(admin_user.id)
        assert revoke_log.extra_data["admin_email"] == admin_user.email


class TestExtendPremiumSubscription:
    """Tests for extending premium subscriptions."""

    async def test_extend_active_subscription_preserves_started_at(
        self,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
    ):
        """Test extending active subscription preserves original started_at."""
        original_started_at = active_subscription.started_at
        original_expires_at = active_subscription.expires_at

        # Extend by 30 days
        subscription = await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            extend_days=30,
            admin_user=admin_user,
        )

        # Verify started_at NOT changed (key difference from grant)
        assert subscription.started_at == original_started_at

        # Verify expires_at extended
        expected_expires = original_expires_at + timedelta(days=30)
        delta = abs((subscription.expires_at - expected_expires).total_seconds())
        assert delta < 5

        # Verify still active
        assert subscription.status == SubscriptionStatus.ACTIVE.value

    async def test_extend_expired_subscription_reactivates(
        self, db_session: AsyncSession, premium_user: User, admin_user: User
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
            expires_at=now - timedelta(days=30),  # Expired 30 days ago
        )
        await subscription_repo.create(expired_sub)
        await db_session.commit()

        # Downgrade user to FREE
        premium_user.role = UserRole.FREE.value
        await db_session.commit()

        # Extend by 30 days
        subscription = await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            extend_days=30,
            admin_user=admin_user,
        )

        # Verify reactivated
        assert subscription.status == SubscriptionStatus.ACTIVE.value

        # Verify expires_at extended from NOW (not from old expiration)
        expected_expires = now + timedelta(days=30)
        delta = abs((subscription.expires_at - expected_expires).total_seconds())
        assert delta < 5

        # Verify user upgraded back to PREMIUM
        await db_session.refresh(premium_user)
        assert premium_user.role == UserRole.PREMIUM.value

    async def test_extend_cancelled_subscription_reactivates(
        self, db_session: AsyncSession, premium_user: User, admin_user: User
    ):
        """Test extending cancelled subscription reactivates it."""
        from app.repositories.subscription_repository import SubscriptionRepository

        subscription_repo = SubscriptionRepository(db_session)

        # Create cancelled subscription
        now = datetime.now(UTC)
        cancelled_sub = Subscription(
            id=uuid4(),
            user_id=premium_user.id,
            status=SubscriptionStatus.CANCELLED.value,
            started_at=now - timedelta(days=30),
            expires_at=now + timedelta(days=30),  # Would expire in future
        )
        await subscription_repo.create(cancelled_sub)
        await db_session.commit()

        # Extend by 30 days
        subscription = await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            extend_days=30,
            admin_user=admin_user,
        )

        # Verify reactivated
        assert subscription.status == SubscriptionStatus.ACTIVE.value

        # Verify user upgraded to PREMIUM
        await db_session.refresh(premium_user)
        assert premium_user.role == UserRole.PREMIUM.value

    async def test_extend_lifetime_subscription_raises_error(
        self, db_session: AsyncSession, premium_user: User, admin_user: User
    ):
        """Test extending lifetime subscription raises ValueError."""
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
        with pytest.raises(ValueError, match="Cannot extend lifetime subscription"):
            await subscription_service.extend_premium_subscription(
                db=db_session,
                user_id=premium_user.id,
                extend_days=30,
                admin_user=admin_user,
            )

    async def test_extend_nonexistent_subscription_raises_error(
        self, db_session: AsyncSession, test_user: User, admin_user: User
    ):
        """Test extending non-existent subscription raises ValueError."""
        with pytest.raises(ValueError, match=f"No subscription found for user {test_user.id}"):
            await subscription_service.extend_premium_subscription(
                db=db_session,
                user_id=test_user.id,
                extend_days=30,
                admin_user=admin_user,
            )

    async def test_extend_creates_audit_log(
        self,
        db_session: AsyncSession,
        premium_user: User,
        active_subscription: Subscription,
        admin_user: User,
    ):
        """Test extending subscription creates audit log."""
        from app.repositories.audit_repository import AuditRepository

        audit_repo = AuditRepository(db_session)

        # Extend subscription
        await subscription_service.extend_premium_subscription(
            db=db_session,
            user_id=premium_user.id,
            extend_days=30,
            admin_user=admin_user,
        )

        # Verify audit log exists
        logs = await audit_repo.get_by_user(user_id=premium_user.id)
        assert len(logs) > 0

        # Find subscription_extended log
        extend_log = next((log for log in logs if log.action == "subscription_extended"), None)
        assert extend_log is not None
        assert extend_log.resource_type == "subscription"
        assert extend_log.resource_id == active_subscription.id
        assert extend_log.extra_data["admin_id"] == str(admin_user.id)
        assert extend_log.extra_data["extend_days"] == 30


class TestGetUserSubscription:
    """Tests for getting user subscription."""

    async def test_get_existing_subscription(
        self, db_session: AsyncSession, premium_user: User, active_subscription: Subscription
    ):
        """Test getting existing subscription."""
        subscription = await subscription_service.get_user_subscription(
            db=db_session,
            user_id=premium_user.id,
        )

        assert subscription is not None
        assert subscription.id == active_subscription.id
        assert subscription.user_id == premium_user.id

    async def test_get_nonexistent_subscription_returns_none(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test getting non-existent subscription returns None."""
        subscription = await subscription_service.get_user_subscription(
            db=db_session,
            user_id=test_user.id,
        )

        assert subscription is None


class TestCheckAndExpireSubscriptions:
    """Tests for automatic subscription expiration."""

    async def test_expire_expired_subscriptions(self, db_session: AsyncSession):
        """Test expiring subscriptions past expiration date."""
        from app.repositories.subscription_repository import SubscriptionRepository
        from app.repositories.user_repository import UserRepository

        subscription_repo = SubscriptionRepository(db_session)
        user_repo = UserRepository(db_session)

        # Create 2 users with expired subscriptions
        now = datetime.now(UTC)
        expired_users = []
        for i in range(2):
            user = User(
                id=uuid4(),
                email=f"expired{i}@test.com",
                password_hash="hashed",
                full_name=f"Expired User {i}",
                role=UserRole.PREMIUM.value,
                email_verified=True,
                is_active=True,
            )
            created_user = await user_repo.create(user)
            expired_users.append(created_user)

            # Create expired subscription
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
        expired_count = await subscription_service.check_and_expire_subscriptions(db_session)

        # Verify 2 subscriptions expired
        assert expired_count == 2

        # Verify subscriptions marked as expired
        for user in expired_users:
            subscription = await subscription_repo.get_by_user_id(user.id)
            assert subscription.status == SubscriptionStatus.EXPIRED.value

            # Verify user downgraded to FREE
            await db_session.refresh(user)
            assert user.role == UserRole.FREE.value

    async def test_skip_active_subscriptions(self, db_session: AsyncSession):
        """Test expiration check skips active subscriptions."""
        from app.repositories.subscription_repository import SubscriptionRepository
        from app.repositories.user_repository import UserRepository

        subscription_repo = SubscriptionRepository(db_session)
        user_repo = UserRepository(db_session)

        # Create user with active subscription
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email="active@test.com",
            password_hash="hashed",
            full_name="Active User",
            role=UserRole.PREMIUM.value,
            email_verified=True,
            is_active=True,
        )
        created_user = await user_repo.create(user)

        # Create active subscription (expires in future)
        subscription = Subscription(
            id=uuid4(),
            user_id=created_user.id,
            status=SubscriptionStatus.ACTIVE.value,
            started_at=now,
            expires_at=now + timedelta(days=30),  # Still active
        )
        await subscription_repo.create(subscription)
        await db_session.commit()

        # Run expiration check
        expired_count = await subscription_service.check_and_expire_subscriptions(db_session)

        # Verify no subscriptions expired
        assert expired_count == 0

        # Verify subscription still active
        await db_session.refresh(subscription)
        assert subscription.status == SubscriptionStatus.ACTIVE.value

        # Verify user still premium
        await db_session.refresh(created_user)
        assert created_user.role == UserRole.PREMIUM.value

    async def test_skip_lifetime_subscriptions(self, db_session: AsyncSession):
        """Test expiration check skips lifetime subscriptions."""
        from app.repositories.subscription_repository import SubscriptionRepository
        from app.repositories.user_repository import UserRepository

        subscription_repo = SubscriptionRepository(db_session)
        user_repo = UserRepository(db_session)

        # Create user with lifetime subscription
        user = User(
            id=uuid4(),
            email="lifetime@test.com",
            password_hash="hashed",
            full_name="Lifetime User",
            role=UserRole.PREMIUM.value,
            email_verified=True,
            is_active=True,
        )
        created_user = await user_repo.create(user)

        # Create lifetime subscription (expires_at = None)
        subscription = Subscription(
            id=uuid4(),
            user_id=created_user.id,
            status=SubscriptionStatus.ACTIVE.value,
            started_at=datetime.now(UTC),
            expires_at=None,  # Lifetime
        )
        await subscription_repo.create(subscription)
        await db_session.commit()

        # Run expiration check
        expired_count = await subscription_service.check_and_expire_subscriptions(db_session)

        # Verify no subscriptions expired
        assert expired_count == 0

        # Verify subscription still active
        await db_session.refresh(subscription)
        assert subscription.status == SubscriptionStatus.ACTIVE.value

    async def test_expiration_creates_audit_logs(self, db_session: AsyncSession):
        """Test expiration check creates audit logs."""
        from app.repositories.audit_repository import AuditRepository
        from app.repositories.subscription_repository import SubscriptionRepository
        from app.repositories.user_repository import UserRepository

        subscription_repo = SubscriptionRepository(db_session)
        user_repo = UserRepository(db_session)
        audit_repo = AuditRepository(db_session)

        # Create user with expired subscription
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email="expired@test.com",
            password_hash="hashed",
            full_name="Expired User",
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
            expires_at=now - timedelta(days=1),
        )
        created_sub = await subscription_repo.create(subscription)
        await db_session.commit()

        # Run expiration check
        await subscription_service.check_and_expire_subscriptions(db_session)

        # Verify audit log exists
        logs = await audit_repo.get_by_user(user_id=created_user.id)
        assert len(logs) > 0

        # Find subscription_expired log
        expire_log = next((log for log in logs if log.action == "subscription_expired"), None)
        assert expire_log is not None
        assert expire_log.resource_type == "subscription"
        assert expire_log.resource_id == created_sub.id
        assert expire_log.extra_data["auto_expired"] is True
