"""
User activity schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserActivityItem(BaseModel):
    """Schema for a single activity log entry."""

    id: UUID
    action: str = Field(..., description="Action performed (e.g., 'login', 'chart_created')")
    resource_type: str | None = Field(None, description="Type of resource affected")
    resource_id: UUID | None = Field(None, description="ID of resource affected")
    ip_address: str | None = Field(None, description="IP address")
    created_at: datetime = Field(..., description="When the activity occurred")

    model_config = {"from_attributes": True}


class UserActivityList(BaseModel):
    """Schema for list of user activities."""

    activities: list[UserActivityItem]
    total: int = Field(..., description="Total number of activities")
