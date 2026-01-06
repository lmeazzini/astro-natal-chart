#!/usr/bin/env python3
"""
Script to fix user credits for users whose webhooks failed.

Usage:
    # Check user status
    uv run python scripts/fix_user_credits.py check <email>

    # Fix user credits (non-interactive, used by ECS tasks)
    uv run python scripts/fix_user_credits.py fix <email> <plan_type>

Example:
    uv run python scripts/fix_user_credits.py fix luis.meazzini@gmail.com pro
"""

import asyncio
import os
import sys
from datetime import UTC, datetime, timedelta
from uuid import UUID

import asyncpg
from loguru import logger

# Plan credit limits (same as credit_config.py)
PLAN_CREDIT_LIMITS = {
    "free": 10,
    "starter": 50,
    "pro": 200,
    "unlimited": None,  # Unlimited
}


async def check_user(conn, email: str) -> dict | None:
    """Check user status and return user info."""
    user = await conn.fetchrow(
        "SELECT id, email, role FROM users WHERE email = $1",
        email,
    )

    if not user:
        print(f"User not found: {email}")
        return None

    user_id = user["id"]
    print(f"User: {email} (ID: {user_id}, role: {user['role']})")

    # Check subscription
    sub = await conn.fetchrow(
        "SELECT status, plan_type, started_at, stripe_subscription_id FROM subscriptions WHERE user_id = $1",
        user_id,
    )

    if sub:
        print(f"Subscription: status={sub['status']}, plan={sub['plan_type']}, stripe_id={sub['stripe_subscription_id']}")
    else:
        print("Subscription: None")

    # Check credits
    credits = await conn.fetchrow(
        "SELECT plan_type, credits_balance, credits_limit, period_end FROM user_credits WHERE user_id = $1",
        user_id,
    )

    if credits:
        print(
            f"Credits: balance={credits['credits_balance']}, "
            f"limit={credits['credits_limit']}, plan={credits['plan_type']}, "
            f"expires={credits['period_end']}"
        )
    else:
        print("Credits: None")

    # Check recent webhook events
    events = await conn.fetch(
        """
        SELECT stripe_event_id, event_type, status, error_message, created_at
        FROM webhook_events
        ORDER BY created_at DESC
        LIMIT 5
        """
    )
    print(f"\nRecent webhook events: {len(events)}")
    for e in events:
        print(f"  - {e['event_type']}: {e['status']} ({e['created_at']})")
        if e['error_message']:
            print(f"    Error: {e['error_message']}")

    return {"user_id": user_id, "role": user["role"], "sub": sub, "credits": credits}


async def fix_user(conn, email: str, plan_type: str) -> bool:
    """Fix user credits for a given plan type."""
    if plan_type not in PLAN_CREDIT_LIMITS:
        print(f"Invalid plan type: {plan_type}")
        print(f"Valid plans: {list(PLAN_CREDIT_LIMITS.keys())}")
        return False

    user = await conn.fetchrow(
        "SELECT id, email, role FROM users WHERE email = $1",
        email,
    )

    if not user:
        print(f"User not found: {email}")
        return False

    user_id = user["id"]
    print(f"Found user: {email} (ID: {user_id})")

    # Get current state
    sub = await conn.fetchrow("SELECT * FROM subscriptions WHERE user_id = $1", user_id)
    credits = await conn.fetchrow("SELECT * FROM user_credits WHERE user_id = $1", user_id)

    # Calculate new values
    credits_limit = PLAN_CREDIT_LIMITS[plan_type]
    credits_balance = credits_limit if credits_limit else 0
    now = datetime.now(UTC)
    period_end = now + timedelta(days=30) if plan_type != "free" else None

    print(f"Updating to: plan={plan_type}, balance={credits_balance}, limit={credits_limit}")

    # Update user role to premium if not free
    if plan_type != "free":
        await conn.execute("UPDATE users SET role = 'premium' WHERE id = $1", user_id)
        print("  Updated user role to 'premium'")

    # Update or create subscription
    if sub:
        await conn.execute(
            """
            UPDATE subscriptions
            SET status = 'active', plan_type = $2, started_at = $3, updated_at = $3
            WHERE user_id = $1
            """,
            user_id, plan_type, now,
        )
        print("  Updated subscription")
    else:
        await conn.execute(
            """
            INSERT INTO subscriptions (user_id, status, plan_type, started_at, created_at, updated_at)
            VALUES ($1, 'active', $2, $3, $3, $3)
            """,
            user_id, plan_type, now,
        )
        print("  Created subscription")

    # Update or create credits
    if credits:
        await conn.execute(
            """
            UPDATE user_credits
            SET plan_type = $2, credits_balance = $3, credits_limit = $4,
                period_start = $5, period_end = $6, updated_at = $5
            WHERE user_id = $1
            """,
            user_id, plan_type, credits_balance, credits_limit, now, period_end,
        )
        print("  Updated credits")
    else:
        await conn.execute(
            """
            INSERT INTO user_credits
                (user_id, plan_type, credits_balance, credits_limit,
                 period_start, period_end, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $5, $5)
            """,
            user_id, plan_type, credits_balance, credits_limit, now, period_end,
        )
        print("  Created credits")

    # Create credit transaction record
    await conn.execute(
        """
        INSERT INTO credit_transactions
            (user_id, transaction_type, amount, balance_after, description, created_at)
        VALUES ($1, 'credit', $2, $2, $3, $4)
        """,
        user_id, credits_balance, f"Manual fix: {plan_type} plan activation", now,
    )
    print("  Created credit transaction")

    print(f"\nDone! User {email} now has {credits_balance} credits on {plan_type} plan.")
    return True


async def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    email = sys.argv[2]

    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("DATABASE_URL environment variable not set")
        sys.exit(1)

    # Convert SQLAlchemy URL to asyncpg format
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    logger.info("Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        if command == "check":
            await check_user(conn, email)
        elif command == "fix":
            if len(sys.argv) < 4:
                print("Usage: fix <email> <plan_type>")
                sys.exit(1)
            plan_type = sys.argv[3].lower()
            success = await fix_user(conn, email, plan_type)
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown command: {command}")
            print("Valid commands: check, fix")
            sys.exit(1)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
