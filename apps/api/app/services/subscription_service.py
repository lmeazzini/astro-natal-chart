"""Service for managing user subscriptions."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SubscriptionStatus, UserRole
from app.models.subscription import Subscription
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository


async def grant_premium_subscription(
    db: AsyncSession,
    user_id: UUID,
    days: int | None,
    admin_user: User,
) -> Subscription:
    """
    Grant premium subscription to a user.

    Args:
        db: Database session
        user_id: User ID to grant premium
        days: Number of days for subscription (None = lifetime)
        admin_user: Admin user performing the action

    Returns:
        Created or updated subscription

    Raises:
        ValueError: If user not found
    """
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)

    # Get user
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Check if subscription already exists
    existing_subscription = await subscription_repo.get_by_user_id(user_id)

    now = datetime.now(UTC)
    expires_at = now + timedelta(days=days) if days is not None else None

    if existing_subscription:
        # Update existing subscription
        existing_subscription.status = SubscriptionStatus.ACTIVE.value
        existing_subscription.started_at = now
        existing_subscription.expires_at = expires_at
        existing_subscription.updated_at = now
        subscription = existing_subscription
        action = "extended"
    else:
        # Create new subscription
        subscription = Subscription(
            user_id=user_id,
            status=SubscriptionStatus.ACTIVE.value,
            started_at=now,
            expires_at=expires_at,
        )
        subscription = await subscription_repo.create(subscription)
        action = "granted"

    # Update user role to PREMIUM
    user.role = UserRole.PREMIUM.value

    # Create audit log BEFORE commit (atomic transaction)
    audit_repo = AuditRepository(db)
    await audit_repo.create_log(
        user_id=user_id,
        action="subscription_granted",
        resource_type="subscription",
        resource_id=subscription.id,
        extra_data={
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "days": days,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "action": action,
        },
    )

    # Commit everything atomically
    await db.commit()
    await db.refresh(subscription)

    logger.bind(user_id=user_id, admin_id=admin_user.id).info(
        f"Premium subscription {action}",
        days=days,
        expires_at=expires_at,
    )

    return subscription


async def revoke_premium_subscription(
    db: AsyncSession,
    user_id: UUID,
    admin_user: User,
) -> None:
    """
    Revoke premium subscription from a user.

    Args:
        db: Database session
        user_id: User ID to revoke premium
        admin_user: Admin user performing the action

    Raises:
        ValueError: If user or subscription not found
    """
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)

    # Get user
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Get subscription
    subscription = await subscription_repo.get_by_user_id(user_id)
    if not subscription:
        raise ValueError(f"Subscription not found for user {user_id}")

    # Update subscription status
    subscription.status = SubscriptionStatus.CANCELLED.value
    subscription.updated_at = datetime.now(UTC)

    # Downgrade user role to FREE
    user.role = UserRole.FREE.value

    # Create audit log BEFORE commit (atomic transaction)
    audit_repo = AuditRepository(db)
    await audit_repo.create_log(
        user_id=user_id,
        action="subscription_revoked",
        resource_type="subscription",
        resource_id=subscription.id,
        extra_data={
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "previous_expires_at": subscription.expires_at.isoformat()
            if subscription.expires_at
            else None,
        },
    )

    # Commit everything atomically
    await db.commit()

    logger.bind(user_id=user_id, admin_id=admin_user.id).info("Premium subscription revoked")


async def get_user_subscription(
    db: AsyncSession,
    user_id: UUID,
) -> Subscription | None:
    """
    Get user's subscription.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Subscription if exists, None otherwise
    """
    subscription_repo = SubscriptionRepository(db)
    return await subscription_repo.get_by_user_id(user_id)


async def check_and_expire_subscriptions(db: AsyncSession) -> int:
    """
    Check and expire subscriptions that have passed their expiration date.

    This function is meant to be called by a Celery task daily.

    Args:
        db: Database session

    Returns:
        Number of subscriptions expired
    """
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)

    # Get all expired subscriptions
    expired_subscriptions = await subscription_repo.get_expired_subscriptions()

    count = 0
    audit_repo = AuditRepository(db)

    for subscription in expired_subscriptions:
        # Update subscription status
        subscription.status = SubscriptionStatus.EXPIRED.value
        subscription.updated_at = datetime.now(UTC)

        # Downgrade user role to FREE
        user = await user_repo.get_by_id(subscription.user_id)
        if user:
            user.role = UserRole.FREE.value

        # Create audit log (will be committed atomically with all changes)
        await audit_repo.create_log(
            user_id=subscription.user_id,
            action="subscription_expired",
            resource_type="subscription",
            resource_id=subscription.id,
            extra_data={
                "expires_at": subscription.expires_at.isoformat()
                if subscription.expires_at
                else None,
                "auto_expired": True,
            },
        )

        count += 1

    # Commit all changes atomically
    await db.commit()

    if count > 0:
        logger.info(f"Expired {count} subscriptions")

    return count
