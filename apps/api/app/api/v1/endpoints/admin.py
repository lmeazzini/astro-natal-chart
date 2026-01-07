"""
Admin endpoints - restricted to admin users only.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_verified_admin
from app.core.i18n.messages import AdminMessages, AuthMessages
from app.core.i18n.translator import translate
from app.core.rate_limit import RateLimits, limiter
from app.models.chart import AuditLog, BirthChart
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.admin import (
    AdminUserDetail,
    AdminUserList,
    AdminUserSummary,
    SystemStats,
    UpdateUserRoleRequest,
    UpdateUserRoleResponse,
)
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionExtend,
    SubscriptionHistoryRead,
    SubscriptionRead,
    SubscriptionRevoke,
)
from app.services import subscription_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/users",
    response_model=AdminUserList,
    summary="List all users",
    description="**Admin only**. Returns paginated list of all users in the system.",
    responses={403: {"description": "Admin privileges required"}},
)
async def list_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUserList:
    """List all users in the system (admin only)."""
    # Count total users (excluding soft-deleted)
    count_stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
    total = await db.scalar(count_stmt) or 0

    # Get users with pagination
    stmt = (
        select(User)
        .where(User.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    return AdminUserList(
        total=total,
        users=[AdminUserSummary.model_validate(u) for u in users],
        skip=skip,
        limit=limit,
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetail,
    summary="Get user details",
    description="**Admin only**. Returns detailed information about a specific user.",
    responses={
        403: {"description": "Admin privileges required"},
        404: {"description": "User not found"},
    },
)
async def get_user_detail(
    user_id: UUID,
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUserDetail:
    """Get detailed user information (admin only)."""
    # Get user
    user = await db.get(User, user_id)
    if not user or user.deleted_at:
        raise HTTPException(status_code=404, detail=translate(AuthMessages.USER_NOT_FOUND))

    # Count user's charts
    chart_count_stmt = select(func.count(BirthChart.id)).where(
        BirthChart.user_id == user_id,
        BirthChart.deleted_at.is_(None),
    )
    chart_count = await db.scalar(chart_count_stmt) or 0

    return AdminUserDetail(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        email_verified=user.email_verified,
        locale=user.locale,
        timezone=user.timezone,
        avatar_url=user.avatar_url,
        bio=user.bio,
        profile_public=user.profile_public,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        last_activity_at=user.last_activity_at,
        chart_count=chart_count,
    )


@router.patch(
    "/users/{user_id}/role",
    response_model=UpdateUserRoleResponse,
    summary="Update user role",
    description="**Admin only**. Update the role of a user. Cannot modify another admin's role.",
    responses={
        400: {"description": "Cannot modify your own role or last admin"},
        403: {"description": "Admin privileges required or cannot modify another admin"},
        404: {"description": "User not found"},
    },
)
@limiter.limit(RateLimits.ADMIN_ROLE_UPDATE)
async def update_user_role(
    user_id: UUID,
    request: UpdateUserRoleRequest,
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> UpdateUserRoleResponse:
    """Update user role (admin only)."""
    # Get target user
    user = await db.get(User, user_id)
    if not user or user.deleted_at:
        raise HTTPException(status_code=404, detail=translate(AuthMessages.USER_NOT_FOUND))

    # Prevent self-modification
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate(AdminMessages.CANNOT_MODIFY_OWN_ROLE),
        )

    # Prevent modifying another admin (already checked it's not self above)
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate(AdminMessages.CANNOT_MODIFY_ADMIN),
        )

    # If demoting an admin, check if there's at least one other admin
    if user.role == UserRole.ADMIN.value and request.role == UserRole.FREE:
        admin_count_stmt = select(func.count(User.id)).where(
            User.role == UserRole.ADMIN.value,
            User.deleted_at.is_(None),
        )
        admin_count = await db.scalar(admin_count_stmt) or 0
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translate(AdminMessages.CANNOT_REMOVE_LAST_ADMIN),
            )

    # Update role
    old_role = user.role
    user.role = request.role.value
    user.is_superuser = request.role == UserRole.ADMIN

    # Create audit log for LGPD compliance
    audit_log = AuditLog(
        id=uuid4(),
        user_id=user_id,
        action="role_changed",
        resource_type="user",
        resource_id=user_id,
        extra_data={
            "old_role": old_role,
            "new_role": request.role.value,
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
        },
    )
    db.add(audit_log)

    await db.commit()
    await db.refresh(user)

    logger.info(
        "User role updated by admin",
        extra={
            "user_id": str(user_id),
            "old_role": old_role,
            "new_role": request.role.value,
            "admin_id": str(admin_user.id),
        },
    )

    return UpdateUserRoleResponse(
        message="Role updated successfully",
        new_role=request.role.value,
    )


@router.get(
    "/stats",
    response_model=SystemStats,
    summary="Get system statistics",
    description="**Admin only**. Returns overall system statistics.",
    responses={403: {"description": "Admin privileges required"}},
)
async def get_system_stats(
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> SystemStats:
    """Get system statistics (admin only)."""
    # Total users
    total_users = await db.scalar(select(func.count(User.id)).where(User.deleted_at.is_(None))) or 0

    # Total charts
    total_charts = (
        await db.scalar(select(func.count(BirthChart.id)).where(BirthChart.deleted_at.is_(None)))
        or 0
    )

    # Active users
    active_users = (
        await db.scalar(
            select(func.count(User.id)).where(
                User.deleted_at.is_(None),
                User.is_active.is_(True),
            )
        )
        or 0
    )

    # Verified users
    verified_users = (
        await db.scalar(
            select(func.count(User.id)).where(
                User.deleted_at.is_(None),
                User.email_verified.is_(True),
            )
        )
        or 0
    )

    # Users by role
    roles_stmt = (
        select(User.role, func.count(User.id)).where(User.deleted_at.is_(None)).group_by(User.role)
    )
    roles_result = await db.execute(roles_stmt)
    users_by_role: dict[str, int] = {row[0]: row[1] for row in roles_result}

    return SystemStats(
        total_users=total_users,
        total_charts=total_charts,
        active_users=active_users,
        verified_users=verified_users,
        users_by_role=users_by_role,
    )


# ============================
# Subscription Management
# ============================


@router.post(
    "/subscriptions/grant",
    response_model=SubscriptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Grant premium subscription",
    description="**Admin only**. Grant premium subscription to a user for a specified number of days or lifetime.",
    responses={
        403: {"description": "Admin privileges required"},
        404: {"description": "User not found"},
    },
)
@limiter.limit(RateLimits.ADMIN_ROLE_UPDATE)
async def grant_subscription(
    request: SubscriptionCreate,
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionRead:
    """Grant premium subscription to a user (admin only)."""
    try:
        subscription = await subscription_service.grant_premium_subscription(
            db=db,
            user_id=request.user_id,
            days=request.days,
            admin_user=admin_user,
        )

        logger.bind(
            user_id=request.user_id,
            admin_id=admin_user.id,
        ).info("Premium subscription granted", days=request.days)

        return SubscriptionRead.model_validate(subscription)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/subscriptions/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke premium subscription",
    description="**Admin only**. Revoke premium subscription from a user.",
    responses={
        403: {"description": "Admin privileges required"},
        404: {"description": "User or subscription not found"},
    },
)
@limiter.limit(RateLimits.ADMIN_ROLE_UPDATE)
async def revoke_subscription(
    request: SubscriptionRevoke,
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Revoke premium subscription from a user (admin only)."""
    try:
        await subscription_service.revoke_premium_subscription(
            db=db,
            user_id=request.user_id,
            admin_user=admin_user,
        )

        logger.bind(
            user_id=request.user_id,
            admin_id=admin_user.id,
        ).info("Premium subscription revoked")

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch(
    "/subscriptions/extend",
    response_model=SubscriptionRead,
    summary="Extend premium subscription",
    description="**Admin only**. Extend an existing subscription without resetting the start date.",
    responses={
        403: {"description": "Admin privileges required"},
        404: {"description": "User or subscription not found"},
        400: {"description": "Cannot extend lifetime subscription"},
    },
)
@limiter.limit(RateLimits.ADMIN_ROLE_UPDATE)
async def extend_subscription(
    request: SubscriptionExtend,
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionRead:
    """
    Extend an existing premium subscription (admin only).

    This endpoint extends the expiration date without resetting the started_at date.
    Use this when you want to add more time to an existing subscription.

    - If subscription is active: extends from current expires_at
    - If subscription is expired: extends from now and reactivates
    - If subscription is cancelled: extends from now and reactivates
    """
    try:
        subscription = await subscription_service.extend_premium_subscription(
            db=db,
            user_id=request.user_id,
            extend_days=request.extend_days,
            admin_user=admin_user,
        )

        logger.bind(
            user_id=request.user_id,
            admin_id=admin_user.id,
        ).info("Premium subscription extended", extend_days=request.extend_days)

        return SubscriptionRead.model_validate(subscription)
    except ValueError as e:
        # Determine appropriate status code based on error message
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e)) from e
        else:
            raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/subscriptions",
    response_model=list[SubscriptionRead],
    summary="List all active subscriptions",
    description="**Admin only**. Returns paginated list of all active subscriptions.",
    responses={403: {"description": "Admin privileges required"}},
)
async def list_subscriptions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> list[SubscriptionRead]:
    """List all active subscriptions (admin only)."""
    from app.repositories.subscription_repository import SubscriptionRepository

    subscription_repo = SubscriptionRepository(db)
    subscriptions = await subscription_repo.get_all_active(skip=skip, limit=limit)

    return [SubscriptionRead.model_validate(sub) for sub in subscriptions]


@router.get(
    "/subscriptions/{user_id}/history",
    response_model=list[SubscriptionHistoryRead],
    summary="Get subscription history for a user",
    description="**Admin only**. Returns paginated list of all subscription changes for a user.",
    responses={
        403: {"description": "Admin privileges required"},
        404: {"description": "User not found"},
    },
)
async def get_subscription_history(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    admin_user: User = Depends(require_verified_admin),
    db: AsyncSession = Depends(get_db),
) -> list[SubscriptionHistoryRead]:
    """
    Get subscription history for a user (admin only).

    Returns all subscription changes including grants, extensions, revocations,
    and automatic expirations, ordered by most recent first.
    """
    # Verify user exists
    user = await db.get(User, user_id)
    if not user or user.deleted_at:
        raise HTTPException(status_code=404, detail=translate(AuthMessages.USER_NOT_FOUND))

    history = await subscription_service.get_subscription_history(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return [SubscriptionHistoryRead.model_validate(h) for h in history]
