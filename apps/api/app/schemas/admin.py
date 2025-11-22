"""
Admin schemas for administrative endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class AdminUserSummary(BaseModel):
    """User summary for admin listing."""

    id: UUID
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class AdminUserList(BaseModel):
    """Paginated list of users for admin."""

    total: int
    users: list[AdminUserSummary]
    skip: int
    limit: int


class AdminUserDetail(BaseModel):
    """Detailed user information for admin."""

    id: UUID
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    locale: str
    timezone: str | None
    avatar_url: str | None
    bio: str | None
    profile_public: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
    last_activity_at: datetime | None
    chart_count: int

    model_config = {"from_attributes": True}


class UpdateUserRoleRequest(BaseModel):
    """Request to update user role."""

    role: UserRole


class UpdateUserRoleResponse(BaseModel):
    """Response after updating user role."""

    message: str
    new_role: str


class SystemStats(BaseModel):
    """System statistics for admin dashboard."""

    total_users: int
    total_charts: int
    active_users: int
    verified_users: int
    users_by_role: dict[str, int]
