"""Service for managing user subscriptions."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SubscriptionChangeType, SubscriptionStatus, UserRole
from app.models.subscription import Subscription
from app.models.subscription_history import SubscriptionHistory
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.subscription_history_repository import SubscriptionHistoryRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository


async def _create_history_record(
    db: AsyncSession,
    subscription: Subscription,
    change_type: SubscriptionChangeType,
    changed_by_user_id: UUID | None = None,
    change_reason: str | None = None,
) -> SubscriptionHistory:
    """
    Create an immutable history record for a subscription change.

    Args:
        db: Database session
        subscription: The subscription being changed
        change_type: Type of change (granted, extended, revoked, expired)
        changed_by_user_id: Admin user who made the change (None if system auto-expired)
        change_reason: Optional reason for the change

    Returns:
        Created history record
    """
    history_repo = SubscriptionHistoryRepository(db)
    history = SubscriptionHistory(
        subscription_id=subscription.id,
        user_id=subscription.user_id,
        status=subscription.status,
        started_at=subscription.started_at,
        expires_at=subscription.expires_at,
        change_type=change_type.value,
        changed_by_user_id=changed_by_user_id,
        change_reason=change_reason,
    )
    return await history_repo.create(history)


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

    # Create subscription history record
    await _create_history_record(
        db=db,
        subscription=subscription,
        change_type=SubscriptionChangeType.GRANTED,
        changed_by_user_id=admin_user.id,
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

    # Create subscription history record
    await _create_history_record(
        db=db,
        subscription=subscription,
        change_type=SubscriptionChangeType.REVOKED,
        changed_by_user_id=admin_user.id,
    )

    # Commit everything atomically
    await db.commit()

    logger.bind(user_id=user_id, admin_id=admin_user.id).info("Premium subscription revoked")


async def extend_premium_subscription(
    db: AsyncSession,
    user_id: UUID,
    extend_days: int,
    admin_user: User,
) -> Subscription:
    """
    Extend an existing premium subscription without resetting started_at.

    This is different from grant_premium_subscription which resets the started_at date.
    Use this when you want to add more time to an existing subscription while preserving
    the original start date.

    Args:
        db: Database session
        user_id: User ID whose subscription to extend
        extend_days: Number of days to add to the subscription
        admin_user: Admin user performing the action

    Returns:
        Updated subscription

    Raises:
        ValueError: If user not found or subscription doesn't exist
    """
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)

    # Get user
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Get existing subscription
    subscription = await subscription_repo.get_by_user_id(user_id)
    if not subscription:
        raise ValueError(f"No subscription found for user {user_id}. Use grant instead.")

    # Calculate new expiration date
    now = datetime.now(UTC)
    if subscription.expires_at is None:
        # Lifetime subscription - cannot extend further
        raise ValueError("Cannot extend lifetime subscription")

    # Extend from current expires_at (if in future) or from now (if expired)
    base_date = max(subscription.expires_at, now)
    new_expires_at = base_date + timedelta(days=extend_days)

    # Update subscription
    old_expires_at = subscription.expires_at
    subscription.expires_at = new_expires_at
    subscription.updated_at = now

    # Reactivate if expired or cancelled
    if subscription.status != SubscriptionStatus.ACTIVE.value:
        subscription.status = SubscriptionStatus.ACTIVE.value
        user.role = UserRole.PREMIUM.value

    # Create audit log BEFORE commit (atomic transaction)
    audit_repo = AuditRepository(db)
    await audit_repo.create_log(
        user_id=user_id,
        action="subscription_extended",
        resource_type="subscription",
        resource_id=subscription.id,
        extra_data={
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "extend_days": extend_days,
            "old_expires_at": old_expires_at.isoformat(),
            "new_expires_at": new_expires_at.isoformat(),
        },
    )

    # Create subscription history record
    await _create_history_record(
        db=db,
        subscription=subscription,
        change_type=SubscriptionChangeType.EXTENDED,
        changed_by_user_id=admin_user.id,
    )

    # Commit everything atomically
    await db.commit()
    await db.refresh(subscription)

    logger.bind(user_id=user_id, admin_id=admin_user.id).info(
        f"Premium subscription extended by {extend_days} days",
        old_expires_at=old_expires_at,
        new_expires_at=new_expires_at,
    )

    return subscription


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

        # Create subscription history record (system auto-expired, no changed_by_user_id)
        await _create_history_record(
            db=db,
            subscription=subscription,
            change_type=SubscriptionChangeType.EXPIRED,
            changed_by_user_id=None,  # System auto-expired
        )

        count += 1

    # Commit all changes atomically
    await db.commit()

    if count > 0:
        logger.info(f"Expired {count} subscriptions")

    return count


async def get_subscription_history(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> list[SubscriptionHistory]:
    """
    Get subscription history for a user.

    Args:
        db: Database session
        user_id: User ID to get history for
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of subscription history records, ordered by created_at descending
    """
    history_repo = SubscriptionHistoryRepository(db)
    return await history_repo.get_by_user_id(user_id, skip=skip, limit=limit)
