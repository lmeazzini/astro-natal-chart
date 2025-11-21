"""
User statistics schemas.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserStats(BaseModel):
    """Schema for user statistics."""

    total_charts: int = Field(..., description="Total number of active birth charts (excludes deleted)")
    account_age_days: int = Field(..., description="Days since account creation")
    last_chart_created_at: datetime | None = Field(
        None, description="Timestamp when the last chart was created"
    )
    email_verified: bool = Field(..., description="Whether email is verified")
    has_oauth_connections: bool = Field(..., description="Whether user has OAuth connections")
    oauth_providers: list[str] = Field(
        default_factory=list, description="List of connected OAuth providers (google, github, facebook)"
    )
