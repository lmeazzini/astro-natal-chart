"""
User service for profile management and account operations.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.chart import AuditLog, BirthChart
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.password import PasswordChange
from app.schemas.user import UserUpdate
from app.schemas.user_activity import UserActivityItem, UserActivityList
from app.schemas.user_stats import UserStats


async def update_profile(
    db: AsyncSession,
    user: User,
    profile_data: UserUpdate,
) -> User:
    """
    Update user profile.

    Args:
        db: Database session
        user: Current user
        profile_data: Profile update data

    Returns:
        Updated user instance
    """
    user_repo = UserRepository(db)

    # Update only provided fields
    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name
    if profile_data.locale is not None:
        user.locale = profile_data.locale
    if profile_data.timezone is not None:
        user.timezone = profile_data.timezone
    if profile_data.avatar_url is not None:
        user.avatar_url = profile_data.avatar_url
    if profile_data.bio is not None:
        user.bio = profile_data.bio
    if profile_data.profile_public is not None:
        user.profile_public = profile_data.profile_public

    # Update last_activity_at
    user.last_activity_at = datetime.now(UTC)

    return await user_repo.update(user)


async def change_password(
    db: AsyncSession,
    user: User,
    password_data: PasswordChange,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """
    Change user password.

    Args:
        db: Database session
        user: Current user
        password_data: Password change data
        ip_address: User's IP address
        user_agent: User's browser User-Agent

    Raises:
        HTTPException: If current password is incorrect
    """
    # Verify current password
    if user.password_hash is None or not verify_password(
        password_data.current_password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    user.last_activity_at = datetime.now(UTC)

    user_repo = UserRepository(db)
    await user_repo.update(user)

    # Create audit log
    audit_repo = AuditRepository(db)
    await audit_repo.create_log(
        user_id=UUID(str(user.id)),
        action="password_changed",
        ip_address=ip_address,
        user_agent=user_agent,
    )


async def get_stats(
    db: AsyncSession,
    user: User,
) -> UserStats:
    """
    Get user statistics.

    Counts ONLY active charts (excludes soft-deleted).
    Returns user statistics including OAuth connections.

    Args:
        db: Database session
        user: Current user

    Returns:
        User statistics
    """
    # Count total charts (exclude soft-deleted)
    count_stmt = select(func.count()).select_from(BirthChart).where(
        BirthChart.user_id == user.id,
        BirthChart.deleted_at.is_(None),
    )
    count_result = await db.execute(count_stmt)
    total_charts = count_result.scalar_one()

    # Get last chart created timestamp
    last_chart_stmt = (
        select(BirthChart.created_at)
        .where(
            BirthChart.user_id == user.id,
            BirthChart.deleted_at.is_(None),
        )
        .order_by(BirthChart.created_at.desc())
        .limit(1)
    )
    last_chart_result = await db.execute(last_chart_stmt)
    last_chart_created_at = last_chart_result.scalar_one_or_none()

    # Calculate account age
    account_age_days = (datetime.now(UTC) - user.created_at).days

    # Get OAuth connections
    user_repo = UserRepository(db)
    user_with_oauth = await user_repo.get_with_oauth_accounts(UUID(str(user.id)))

    oauth_providers = []
    if user_with_oauth and user_with_oauth.oauth_accounts:
        oauth_providers = [account.provider for account in user_with_oauth.oauth_accounts]

    return UserStats(
        total_charts=total_charts,
        account_age_days=account_age_days,
        last_chart_created_at=last_chart_created_at,
        email_verified=user.email_verified,
        has_oauth_connections=len(oauth_providers) > 0,
        oauth_providers=oauth_providers,
    )


async def get_activities(
    db: AsyncSession,
    user: User,
    limit: int = 50,
    offset: int = 0,
) -> UserActivityList:
    """
    Get user activity log.

    Args:
        db: Database session
        user: Current user
        limit: Maximum number of activities to return
        offset: Number of activities to skip

    Returns:
        List of user activities
    """
    # Get audit logs for user
    stmt = (
        select(AuditLog)
        .where(AuditLog.user_id == user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    # Count total activities
    count_stmt = select(func.count()).select_from(AuditLog).where(AuditLog.user_id == user.id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Convert to activity items
    activities = [
        UserActivityItem(
            id=log.id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return UserActivityList(activities=activities, total=total)


async def export_data(
    db: AsyncSession,
    user: User,
) -> dict:
    """
    Export all user data (LGPD/GDPR compliance).

    Args:
        db: Database session
        user: Current user

    Returns:
        Dictionary with all user data
    """
    user_repo = UserRepository(db)

    # Get user with OAuth accounts
    user_with_oauth = await user_repo.get_with_oauth_accounts(UUID(str(user.id)))
    if not user_with_oauth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get all birth charts
    stmt = select(BirthChart).where(
        BirthChart.user_id == user.id,
        BirthChart.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    charts = result.scalars().all()

    # Get audit logs
    audit_stmt = select(AuditLog).where(AuditLog.user_id == user.id).order_by(
        AuditLog.created_at.desc()
    )
    audit_result = await db.execute(audit_stmt)
    audit_logs = audit_result.scalars().all()

    # Build export data
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "locale": user.locale,
            "timezone": user.timezone,
            "bio": user.bio,
            "profile_public": user.profile_public,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "last_activity_at": (
                user.last_activity_at.isoformat() if user.last_activity_at else None
            ),
        },
        "oauth_accounts": [
            {
                "provider": account.provider,
                "provider_user_id": account.provider_user_id,
                "created_at": account.created_at.isoformat(),
            }
            for account in user_with_oauth.oauth_accounts
        ],
        "birth_charts": [
            {
                "id": str(chart.id),
                "person_name": chart.person_name,
                "birth_datetime": chart.birth_datetime.isoformat(),
                "latitude": float(chart.latitude),
                "longitude": float(chart.longitude),
                "city": chart.city,
                "country": chart.country,
                "created_at": chart.created_at.isoformat(),
                "chart_data": chart.chart_data,
            }
            for chart in charts
        ],
        "audit_logs": [
            {
                "action": log.action,
                "resource_type": log.resource_type,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
            }
            for log in audit_logs
        ],
        "exported_at": datetime.now(UTC).isoformat(),
    }


async def soft_delete_user(
    db: AsyncSession,
    user: User,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """
    Soft delete user account.

    Args:
        db: Database session
        user: User to delete
        ip_address: User's IP address
        user_agent: User's browser User-Agent
    """
    user_repo = UserRepository(db)

    # Create audit log before deletion
    audit_repo = AuditRepository(db)
    await audit_repo.create_log(
        user_id=UUID(str(user.id)),
        action="account_deleted",
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Soft delete user
    await user_repo.soft_delete(user)
