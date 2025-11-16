"""
User statistics schemas.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserStats(BaseModel):
    """Schema for user statistics."""

    total_charts: int = Field(..., description="Total number of birth charts created")
    account_age_days: int = Field(..., description="Days since account creation")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")
    last_activity_at: datetime | None = Field(None, description="Last activity timestamp")
