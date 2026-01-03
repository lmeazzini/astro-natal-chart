"""
Celery tasks for credit system management.
"""

import asyncio
from datetime import UTC, datetime

from loguru import logger

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services import credit_service


@celery_app.task(name="credits.monthly_reset")
def reset_monthly_credits() -> dict[str, int | str]:
    """
    Reset credits for users whose billing period has expired.

    This task automatically:
    1. Finds all users with period_end in the past
    2. Resets their credits to their plan limit
    3. Updates period_start and period_end
    4. Creates transaction records for audit

    **Scheduling**: Run daily at 1 AM (before subscription expiration task).

    Returns:
        Dict with reset statistics
    """
    return asyncio.run(_reset_monthly_credits_async())


async def _reset_monthly_credits_async() -> dict[str, int | str]:
    """Async version of the credit reset task."""
    async with AsyncSessionLocal() as db:
        try:
            # Run credit reset check
            reset_count = await credit_service.check_and_reset_expired_periods(db)

            result: dict[str, int | str] = {
                "reset_count": reset_count,
                "check_time": datetime.now(UTC).isoformat(),
                "status": "success",
            }

            if reset_count > 0:
                logger.info(f"Credit reset completed: {reset_count} users reset")
            else:
                logger.debug("Credit reset check completed: no users needed reset")

            return result

        except Exception as e:
            logger.error(f"Error during credit reset: {e}", exc_info=True)
            return {
                "reset_count": 0,
                "check_time": datetime.now(UTC).isoformat(),
                "status": "error",
                "error": str(e),
            }


@celery_app.task(name="credits.allocate_for_existing_users")
def allocate_credits_for_existing_users() -> dict[str, int | str]:
    """
    One-time migration task to allocate credits for existing users.

    This task should be run once during initial deployment to:
    1. Find all users without credit records
    2. Create credit records based on their current role/subscription
    3. FREE users get 10 credits
    4. PREMIUM users get unlimited credits

    **Scheduling**: Run once manually after migration.

    Returns:
        Dict with allocation statistics
    """
    return asyncio.run(_allocate_credits_for_existing_users_async())


async def _allocate_credits_for_existing_users_async() -> dict[str, int | str]:
    """Async version of the existing user credit allocation task."""
    from sqlalchemy import select

    from app.models.enums import PlanType
    from app.models.user import User
    from app.models.user_credit import UserCredit

    async with AsyncSessionLocal() as db:
        try:
            # Find users without credit records
            subquery = select(UserCredit.user_id)
            stmt = select(User).where(
                User.id.notin_(subquery),
                User.deleted_at.is_(None),
            )
            result = await db.execute(stmt)
            users_without_credits = result.scalars().all()

            allocated_count = 0
            for user in users_without_credits:
                # Determine plan type based on user role
                if user.is_premium or user.is_admin:
                    plan_type = PlanType.UNLIMITED.value
                else:
                    plan_type = PlanType.FREE.value

                # Allocate credits
                await credit_service.allocate_credits(
                    db=db,
                    user_id=user.id,
                    plan_type=plan_type,
                )
                allocated_count += 1

            result_dict: dict[str, int | str] = {
                "allocated_count": allocated_count,
                "check_time": datetime.now(UTC).isoformat(),
                "status": "success",
            }

            logger.info(f"Credit allocation for existing users completed: {allocated_count} users")

            return result_dict

        except Exception as e:
            logger.error(f"Error during credit allocation: {e}", exc_info=True)
            return {
                "allocated_count": 0,
                "check_time": datetime.now(UTC).isoformat(),
                "status": "error",
                "error": str(e),
            }
