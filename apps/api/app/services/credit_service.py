"""Service for managing user credits."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.credit_config import (
    LOW_CREDITS_THRESHOLD_PERCENT,
    PLAN_CREDIT_LIMITS,
    get_credit_limit,
    get_feature_cost,
    is_unlimited_plan,
)
from app.models.credit_transaction import CreditTransaction
from app.models.enums import PlanType, TransactionType
from app.models.user import User
from app.models.user_credit import UserCredit
from app.repositories.credit_repository import CreditRepository
from app.repositories.credit_transaction_repository import CreditTransactionRepository
from app.services.amplitude_service import amplitude_service


class InsufficientCreditsError(Exception):
    """Raised when user doesn't have enough credits for an operation."""

    def __init__(
        self,
        required: int,
        available: int,
        feature_type: str,
    ):
        self.required = required
        self.available = available
        self.feature_type = feature_type
        super().__init__(
            f"Insufficient credits: {available} available, {required} required for {feature_type}"
        )


async def get_or_create_user_credits(
    db: AsyncSession,
    user_id: UUID,
    plan_type: str = PlanType.FREE.value,
) -> UserCredit:
    """
    Get user credits or create if not exists.

    Args:
        db: Database session
        user_id: User UUID
        plan_type: Plan type for new credit records

    Returns:
        UserCredit instance
    """
    credit_repo = CreditRepository(db)
    user_credit = await credit_repo.get_by_user_id(user_id)

    if user_credit:
        return user_credit

    # Create new credit record
    now = datetime.now(UTC)
    credits_limit = get_credit_limit(plan_type)

    user_credit = UserCredit(
        user_id=user_id,
        plan_type=plan_type,
        credits_balance=credits_limit if credits_limit else 0,
        credits_limit=credits_limit,
        period_start=now,
        period_end=None,  # Free tier never expires
        created_at=now,
        updated_at=now,
    )

    await credit_repo.create(user_credit)
    logger.bind(user_id=str(user_id)).info(f"Created credit record for user with plan {plan_type}")

    return user_credit


async def get_user_credits(
    db: AsyncSession,
    user_id: UUID,
) -> UserCredit | None:
    """
    Get user credits.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        UserCredit instance or None
    """
    credit_repo = CreditRepository(db)
    return await credit_repo.get_by_user_id(user_id)


async def allocate_credits(
    db: AsyncSession,
    user_id: UUID,
    plan_type: str,
    changed_by_admin_id: UUID | None = None,
) -> UserCredit:
    """
    Allocate credits based on plan type.

    Used when:
    - New user registration (free tier)
    - User upgrades plan (Stripe checkout)
    - User downgrades plan (subscription cancelled)

    Args:
        db: Database session
        user_id: User UUID
        plan_type: New plan type
        changed_by_admin_id: Optional admin who triggered the change

    Returns:
        Updated UserCredit instance
    """
    credit_repo = CreditRepository(db)
    transaction_repo = CreditTransactionRepository(db)

    user_credit = await credit_repo.get_by_user_id(user_id)
    now = datetime.now(UTC)
    credits_limit = get_credit_limit(plan_type)
    new_balance = credits_limit if credits_limit else 0

    if user_credit:
        # Update existing credit record
        old_plan = user_credit.plan_type
        old_balance = user_credit.credits_balance

        user_credit.plan_type = plan_type
        user_credit.credits_balance = new_balance
        user_credit.credits_limit = credits_limit
        user_credit.updated_at = now

        # Set period for paid plans
        if plan_type != PlanType.FREE.value:
            user_credit.period_start = now
            user_credit.period_end = now + timedelta(days=30)
        else:
            user_credit.period_end = None

        await db.commit()
        await db.refresh(user_credit)

        # Create transaction record
        transaction_type = (
            TransactionType.UPGRADE.value
            if PLAN_CREDIT_LIMITS.get(plan_type, 0)
            or 0 > (PLAN_CREDIT_LIMITS.get(old_plan, 0) or 0)
            else TransactionType.RESET.value
        )

        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=new_balance - old_balance,
            balance_after=new_balance,
            description=f"Plan changed from {old_plan} to {plan_type}",
            created_at=now,
        )
        await transaction_repo.create(transaction)

        logger.bind(user_id=str(user_id)).info(
            f"Updated credits: {old_plan} -> {plan_type}, balance: {old_balance} -> {new_balance}"
        )

    else:
        # Create new credit record
        user_credit = UserCredit(
            user_id=user_id,
            plan_type=plan_type,
            credits_balance=new_balance,
            credits_limit=credits_limit,
            period_start=now,
            period_end=now + timedelta(days=30) if plan_type != PlanType.FREE.value else None,
            created_at=now,
            updated_at=now,
        )
        await credit_repo.create(user_credit)

        # Create initial credit transaction
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=TransactionType.CREDIT.value,
            amount=new_balance,
            balance_after=new_balance,
            description=f"Initial allocation for {plan_type} plan",
            created_at=now,
        )
        await transaction_repo.create(transaction)

        logger.bind(user_id=str(user_id)).info(
            f"Allocated {new_balance} credits for new {plan_type} plan"
        )

    # Track with Amplitude
    amplitude_service.track(
        event_type="credits_allocated",
        user_id=str(user_id),
        event_properties={
            "plan_type": plan_type,
            "credits_allocated": new_balance,
            "is_unlimited": is_unlimited_plan(plan_type),
            "source": "admin" if changed_by_admin_id else "system",
        },
    )

    return user_credit


async def has_sufficient_credits(
    db: AsyncSession,
    user_id: UUID,
    feature_type: str,
) -> tuple[bool, int, int]:
    """
    Check if user has sufficient credits for a feature.

    Args:
        db: Database session
        user_id: User UUID
        feature_type: Type of feature to check

    Returns:
        Tuple of (has_credits, required_amount, available_amount)
    """
    user_credit = await get_or_create_user_credits(db, user_id)

    # Unlimited plans always have sufficient credits
    if user_credit.is_unlimited:
        return (True, 0, -1)  # -1 indicates unlimited

    required = get_feature_cost(feature_type)
    available = user_credit.credits_balance

    return (available >= required, required, available)


async def consume_credits(
    db: AsyncSession,
    user_id: UUID,
    feature_type: str,
    resource_id: UUID | None = None,
    description: str | None = None,
) -> CreditTransaction:
    """
    Consume credits for a feature using atomic database operations.

    This function uses an atomic UPDATE with a WHERE clause to prevent race conditions.
    If two concurrent requests try to consume credits, only one will succeed if the
    balance would go negative.

    Args:
        db: Database session
        user_id: User UUID
        feature_type: Type of feature consuming credits
        resource_id: Optional ID of the resource (e.g., chart_id)
        description: Optional description

    Returns:
        CreditTransaction record

    Raises:
        InsufficientCreditsError: If user doesn't have enough credits
    """
    transaction_repo = CreditTransactionRepository(db)

    user_credit = await get_or_create_user_credits(db, user_id)

    # Unlimited plans don't consume credits
    if user_credit.is_unlimited:
        now = datetime.now(UTC)
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=TransactionType.DEBIT.value,
            amount=0,  # No actual debit for unlimited
            balance_after=0,
            feature_type=feature_type,
            resource_id=resource_id,
            description=description or f"Used {feature_type} (unlimited plan)",
            created_at=now,
        )
        await transaction_repo.create(transaction)
        return transaction

    required = get_feature_cost(feature_type)
    now = datetime.now(UTC)

    # Atomic UPDATE: Only succeeds if balance >= required
    # This prevents race conditions where concurrent requests could overdraw
    stmt = (
        update(UserCredit)
        .where(
            UserCredit.user_id == user_id,
            UserCredit.credits_balance >= required,
        )
        .values(
            credits_balance=UserCredit.credits_balance - required,
            updated_at=now,
        )
        .returning(UserCredit.credits_balance)
    )

    result = await db.execute(stmt)
    new_balance_row = result.scalar_one_or_none()

    # If no row was updated, either user doesn't exist or insufficient credits
    if new_balance_row is None:
        # Refresh to get current balance for error message
        await db.refresh(user_credit)
        amplitude_service.track(
            event_type="insufficient_credits",
            user_id=str(user_id),
            event_properties={
                "feature_type": feature_type,
                "required": required,
                "available": user_credit.credits_balance,
                "plan_type": user_credit.plan_type,
            },
        )
        raise InsufficientCreditsError(
            required=required,
            available=user_credit.credits_balance,
            feature_type=feature_type,
        )

    new_balance = new_balance_row

    # Create transaction record
    transaction = CreditTransaction(
        user_id=user_id,
        transaction_type=TransactionType.DEBIT.value,
        amount=-required,
        balance_after=new_balance,
        feature_type=feature_type,
        resource_id=resource_id,
        description=description or f"Used {feature_type}",
        created_at=now,
    )

    await transaction_repo.create(transaction)
    await db.commit()

    # Track with Amplitude
    amplitude_service.track(
        event_type="credits_consumed",
        user_id=str(user_id),
        event_properties={
            "feature_type": feature_type,
            "credits_consumed": required,
            "balance_after": new_balance,
            "plan_type": user_credit.plan_type,
        },
    )

    # Check if credits are low and track warning
    credits_limit = user_credit.credits_limit
    if credits_limit and credits_limit > 0:
        threshold = int(credits_limit * LOW_CREDITS_THRESHOLD_PERCENT)
        if new_balance <= threshold and (new_balance + required) > threshold:
            # Only track once when crossing the threshold
            amplitude_service.track(
                event_type="credits_low_warning",
                user_id=str(user_id),
                event_properties={
                    "balance_remaining": new_balance,
                    "credits_limit": credits_limit,
                    "threshold_percent": int(LOW_CREDITS_THRESHOLD_PERCENT * 100),
                    "plan_type": user_credit.plan_type,
                },
            )
            logger.bind(user_id=str(user_id)).info(
                f"Low credits warning: {new_balance}/{credits_limit} credits remaining"
            )

    logger.bind(user_id=str(user_id)).debug(
        f"Consumed {required} credits for {feature_type}, balance: {new_balance}"
    )

    return transaction


async def add_bonus_credits(
    db: AsyncSession,
    user_id: UUID,
    amount: int,
    admin_user: User,
    reason: str | None = None,
) -> CreditTransaction:
    """
    Add bonus credits to a user.

    Args:
        db: Database session
        user_id: User UUID
        amount: Number of credits to add
        admin_user: Admin performing the action
        reason: Optional reason for the bonus

    Returns:
        CreditTransaction record
    """
    transaction_repo = CreditTransactionRepository(db)

    user_credit = await get_or_create_user_credits(db, user_id)

    now = datetime.now(UTC)
    new_balance = user_credit.credits_balance + amount

    user_credit.credits_balance = new_balance
    user_credit.updated_at = now

    transaction = CreditTransaction(
        user_id=user_id,
        transaction_type=TransactionType.BONUS.value,
        amount=amount,
        balance_after=new_balance,
        description=reason or "Bonus credits from admin",
        created_at=now,
    )

    await db.commit()
    await db.refresh(user_credit)
    await transaction_repo.create(transaction)

    # Track with Amplitude
    amplitude_service.track(
        event_type="bonus_credits_added",
        user_id=str(user_id),
        event_properties={
            "amount": amount,
            "balance_after": new_balance,
            "added_by_admin_id": str(admin_user.id),
            "reason": reason or "no_reason_provided",
        },
    )

    logger.bind(user_id=str(user_id), admin_id=str(admin_user.id)).info(
        f"Added {amount} bonus credits, new balance: {new_balance}"
    )

    return transaction


async def refund_credits(
    db: AsyncSession,
    user_id: UUID,
    amount: int,
    admin_user: User,
    reason: str | None = None,
    original_transaction_id: UUID | None = None,
) -> CreditTransaction:
    """
    Refund credits to a user.

    Args:
        db: Database session
        user_id: User UUID
        amount: Number of credits to refund
        admin_user: Admin performing the action
        reason: Optional reason for the refund
        original_transaction_id: Optional ID of the original transaction being refunded

    Returns:
        CreditTransaction record
    """
    transaction_repo = CreditTransactionRepository(db)

    user_credit = await get_or_create_user_credits(db, user_id)

    now = datetime.now(UTC)
    new_balance = user_credit.credits_balance + amount

    user_credit.credits_balance = new_balance
    user_credit.updated_at = now

    transaction = CreditTransaction(
        user_id=user_id,
        transaction_type=TransactionType.REFUND.value,
        amount=amount,
        balance_after=new_balance,
        description=reason or "Credits refunded by admin",
        created_at=now,
    )

    await db.commit()
    await db.refresh(user_credit)
    await transaction_repo.create(transaction)

    # Track with Amplitude
    amplitude_service.track(
        event_type="credits_refunded",
        user_id=str(user_id),
        event_properties={
            "amount": amount,
            "balance_after": new_balance,
            "refunded_by_admin_id": str(admin_user.id),
            "reason": reason or "no_reason_provided",
            "original_transaction_id": str(original_transaction_id)
            if original_transaction_id
            else None,
        },
    )

    logger.bind(user_id=str(user_id), admin_id=str(admin_user.id)).info(
        f"Refunded {amount} credits, new balance: {new_balance}"
    )

    return transaction


async def reset_monthly_credits(
    db: AsyncSession,
    user_id: UUID,
) -> UserCredit:
    """
    Reset user credits to their plan limit.

    Called on monthly subscription renewal.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Updated UserCredit instance
    """
    credit_repo = CreditRepository(db)
    transaction_repo = CreditTransactionRepository(db)

    user_credit = await credit_repo.get_by_user_id(user_id)
    if not user_credit:
        raise ValueError(f"No credit record found for user {user_id}")

    now = datetime.now(UTC)
    credits_limit = get_credit_limit(user_credit.plan_type)
    old_balance = user_credit.credits_balance
    new_balance = credits_limit if credits_limit else 0

    # Update credit record
    user_credit.credits_balance = new_balance
    user_credit.period_start = now
    user_credit.period_end = now + timedelta(days=30) if credits_limit else None
    user_credit.updated_at = now

    # Create transaction record
    transaction = CreditTransaction(
        user_id=user_id,
        transaction_type=TransactionType.RESET.value,
        amount=new_balance - old_balance,
        balance_after=new_balance,
        description=f"Monthly credit reset for {user_credit.plan_type} plan",
        created_at=now,
    )

    await db.commit()
    await db.refresh(user_credit)
    await transaction_repo.create(transaction)

    # Track with Amplitude
    amplitude_service.track(
        event_type="credits_reset",
        user_id=str(user_id),
        event_properties={
            "plan_type": user_credit.plan_type,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "source": "monthly_reset",
        },
    )

    logger.bind(user_id=str(user_id)).info(f"Reset credits: {old_balance} -> {new_balance}")

    return user_credit


async def check_and_reset_expired_periods(db: AsyncSession) -> int:
    """
    Check and reset credits for users whose period has expired.

    Called daily by Celery task.

    Args:
        db: Database session

    Returns:
        Number of users whose credits were reset
    """
    credit_repo = CreditRepository(db)
    now = datetime.now(UTC)

    # Get users needing reset
    expired_credits = await credit_repo.get_users_needing_reset(before_date=now)

    count = 0
    for user_credit in expired_credits:
        try:
            await reset_monthly_credits(db, user_credit.user_id)
            count += 1
        except Exception as e:
            logger.error(f"Failed to reset credits for user {user_credit.user_id}: {e}")

    if count > 0:
        logger.info(f"Reset credits for {count} users")

    return count


async def get_credit_history(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[CreditTransaction], int]:
    """
    Get credit transaction history for a user.

    Args:
        db: Database session
        user_id: User UUID
        skip: Number of records to skip
        limit: Maximum number of records

    Returns:
        Tuple of (transactions list, total count)
    """
    transaction_repo = CreditTransactionRepository(db)
    transactions = await transaction_repo.get_by_user_id(user_id, skip=skip, limit=limit)
    total = await transaction_repo.count_by_user_id(user_id)
    return (transactions, total)


async def get_usage_breakdown(
    db: AsyncSession,
    user_id: UUID,
) -> dict[str, int]:
    """
    Get credit usage breakdown by feature type.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Dictionary mapping feature_type to total credits consumed
    """
    # Get current period
    user_credit = await get_user_credits(db, user_id)
    if not user_credit:
        return {}

    transaction_repo = CreditTransactionRepository(db)
    return await transaction_repo.get_usage_by_feature(
        user_id=user_id,
        start_date=user_credit.period_start,
        end_date=user_credit.period_end,
    )


async def get_unlocked_features_for_chart(
    db: AsyncSession,
    user_id: UUID,
    chart_id: UUID,
) -> dict:
    """
    Get features that have been unlocked (paid) for a specific chart.

    Args:
        db: Database session
        user_id: User UUID
        chart_id: Chart UUID

    Returns:
        Dictionary with:
        - unlocked_features: list of feature types that are unlocked
        - unlocked_solar_return_years: list of years for Solar Return
    """
    import re

    transaction_repo = CreditTransactionRepository(db)

    # Get all unlocked features for this chart
    unlocked_features = await transaction_repo.get_unlocked_features_for_chart(
        user_id=user_id,
        chart_id=chart_id,
    )

    # Get Solar Return transactions to extract years
    sr_transactions = await transaction_repo.get_solar_return_transactions_for_chart(
        user_id=user_id,
        chart_id=chart_id,
    )

    # Extract years from descriptions like "Solar Return 2024 for chart Name"
    unlocked_years: list[int] = []
    year_pattern = re.compile(r"Solar Return (\d{4})")
    for tx in sr_transactions:
        if tx.description:
            match = year_pattern.search(tx.description)
            if match:
                year = int(match.group(1))
                if year not in unlocked_years:
                    unlocked_years.append(year)

    return {
        "unlocked_features": unlocked_features,
        "unlocked_solar_return_years": sorted(unlocked_years),
    }


async def has_feature_unlocked(
    db: AsyncSession,
    user_id: UUID,
    chart_id: UUID,
    feature_type: str,
) -> bool:
    """
    Check if a feature has been unlocked (paid) for a specific chart.

    Args:
        db: Database session
        user_id: User UUID
        chart_id: Chart UUID
        feature_type: Feature type to check

    Returns:
        True if feature was previously paid for, False otherwise
    """
    transaction_repo = CreditTransactionRepository(db)
    return await transaction_repo.has_feature_unlocked(
        user_id=user_id,
        chart_id=chart_id,
        feature_type=feature_type,
    )


async def has_solar_return_year_unlocked(
    db: AsyncSession,
    user_id: UUID,
    chart_id: UUID,
    year: int,
) -> bool:
    """
    Check if a specific Solar Return year has been unlocked for a chart.

    Args:
        db: Database session
        user_id: User UUID
        chart_id: Chart UUID
        year: Year to check

    Returns:
        True if Solar Return for this year was previously paid for
    """
    import re

    transaction_repo = CreditTransactionRepository(db)
    sr_transactions = await transaction_repo.get_solar_return_transactions_for_chart(
        user_id=user_id,
        chart_id=chart_id,
    )

    year_pattern = re.compile(r"Solar Return (\d{4})")
    for tx in sr_transactions:
        if tx.description:
            match = year_pattern.search(tx.description)
            if match and int(match.group(1)) == year:
                return True

    return False
