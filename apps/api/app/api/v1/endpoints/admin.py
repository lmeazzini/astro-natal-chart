"""
Admin endpoints - restricted to admin users only.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.rate_limit import RateLimits, limiter
from app.models.chart import BirthChart
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
    admin_user: User = Depends(require_admin),
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
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUserDetail:
    """Get detailed user information (admin only)."""
    # Get user
    user = await db.get(User, user_id)
    if not user or user.deleted_at:
        raise HTTPException(status_code=404, detail="User not found")

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
@limiter.limit(RateLimits.PASSWORD_RESET_CONFIRM)
async def update_user_role(
    user_id: UUID,
    request: UpdateUserRoleRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UpdateUserRoleResponse:
    """Update user role (admin only)."""
    # Get target user
    user = await db.get(User, user_id)
    if not user or user.deleted_at:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-modification
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own role",
        )

    # Prevent modifying another admin
    if user.is_admin and user.id != admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify another admin's role",
        )

    # If demoting an admin, check if there's at least one other admin
    if user.role == UserRole.ADMIN.value and request.role == UserRole.GERAL:
        admin_count_stmt = select(func.count(User.id)).where(
            User.role == UserRole.ADMIN.value,
            User.deleted_at.is_(None),
        )
        admin_count = await db.scalar(admin_count_stmt) or 0
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove role from last admin",
            )

    # Update role
    old_role = user.role
    user.role = request.role.value
    user.is_superuser = request.role == UserRole.ADMIN

    await db.commit()

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
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SystemStats:
    """Get system statistics (admin only)."""
    # Total users
    total_users = (
        await db.scalar(
            select(func.count(User.id)).where(User.deleted_at.is_(None))
        )
        or 0
    )

    # Total charts
    total_charts = (
        await db.scalar(
            select(func.count(BirthChart.id)).where(BirthChart.deleted_at.is_(None))
        )
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
        select(User.role, func.count(User.id))
        .where(User.deleted_at.is_(None))
        .group_by(User.role)
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
