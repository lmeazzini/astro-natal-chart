"""
Celery tasks for subscription management.
"""

import asyncio
from datetime import UTC, datetime

from loguru import logger

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services import subscription_service


@celery_app.task(name="subscriptions.check_and_expire")
def check_and_expire_subscriptions() -> dict[str, int | str]:
    """
    Check and expire subscriptions that have passed their expiration date.

    This task automatically:
    1. Finds all active subscriptions with expires_at in the past
    2. Updates their status to "expired"
    3. Downgrades user role from PREMIUM to FREE
    4. Creates audit logs for compliance

    **Scheduling**: Run daily at 3 AM (low traffic period).

    Returns:
        Dict with expiration statistics
    """
    return asyncio.run(_check_and_expire_subscriptions_async())


async def _check_and_expire_subscriptions_async() -> dict[str, int | str]:
    """Async version of the subscription expiration task."""
    async with AsyncSessionLocal() as db:
        try:
            # Run subscription expiration check
            expired_count = await subscription_service.check_and_expire_subscriptions(db)

            result: dict[str, int | str] = {
                "expired_count": expired_count,
                "check_time": datetime.now(UTC).isoformat(),
                "status": "success",
            }

            if expired_count > 0:
                logger.info(
                    f"Subscription expiration check completed: {expired_count} subscriptions expired"
                )
            else:
                logger.debug("Subscription expiration check completed: no subscriptions expired")

            return result

        except Exception as e:
            logger.error(f"Error during subscription expiration check: {e}", exc_info=True)
            return {
                "expired_count": 0,
                "check_time": datetime.now(UTC).isoformat(),
                "status": "error",
                "error": str(e),
            }
