"""Subscription schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    """Base subscription schema."""

    status: str = Field(..., description="Subscription status (active, expired, cancelled)")
    started_at: datetime = Field(..., description="When subscription started")
    expires_at: datetime | None = Field(
        None, description="When subscription expires (None = lifetime)"
    )


class SubscriptionCreate(BaseModel):
    """Schema for granting a subscription (admin only)."""

    user_id: UUID = Field(..., description="User ID to grant subscription to")
    days: int | None = Field(
        None,
        ge=1,
        le=3650,  # Max 10 years
        description="Number of days for subscription (None = lifetime premium, max 3650 days)",
    )


class SubscriptionRevoke(BaseModel):
    """Schema for revoking a subscription (admin only)."""

    user_id: UUID = Field(..., description="User ID to revoke subscription from")


class SubscriptionExtend(BaseModel):
    """Schema for extending an existing subscription (admin only)."""

    user_id: UUID = Field(..., description="User ID whose subscription to extend")
    extend_days: int = Field(
        ...,
        ge=1,
        le=3650,  # Max 10 years extension
        description="Number of days to extend the subscription (max 3650 days)",
    )


class SubscriptionRead(SubscriptionBase):
    """Schema for reading subscription data."""

    id: UUID = Field(..., description="Subscription ID")
    user_id: UUID = Field(..., description="User ID")
    created_at: datetime = Field(..., description="When subscription was created")
    updated_at: datetime = Field(..., description="When subscription was last updated")
    is_active: bool = Field(..., description="Whether subscription is currently active")
    is_expired: bool = Field(..., description="Whether subscription has expired")
    days_remaining: int | None = Field(None, description="Days until expiration (None = lifetime)")

    model_config = {"from_attributes": True}


class UserSubscriptionRead(BaseModel):
    """Schema for user's subscription status (simplified view)."""

    has_subscription: bool = Field(..., description="Whether user has a subscription")
    is_premium: bool = Field(..., description="Whether user has active premium")
    subscription: SubscriptionRead | None = Field(
        None, description="Subscription details if exists"
    )

    model_config = {"from_attributes": True}


class SubscriptionHistoryRead(BaseModel):
    """Schema for reading subscription history records."""

    id: UUID = Field(..., description="History record ID")
    subscription_id: UUID = Field(..., description="Subscription ID")
    user_id: UUID = Field(..., description="User ID")

    # Snapshot of subscription state at this point in time
    status: str = Field(..., description="Subscription status at time of change")
    started_at: datetime = Field(..., description="Subscription start date at time of change")
    expires_at: datetime | None = Field(
        None, description="Subscription expiration at time of change (None = lifetime)"
    )

    # Change metadata
    change_type: str = Field(
        ..., description="Type of change (granted, extended, revoked, expired)"
    )
    changed_by_user_id: UUID | None = Field(
        None, description="Admin user who made the change (None if system auto-expired)"
    )
    change_reason: str | None = Field(None, description="Optional reason for the change")

    created_at: datetime = Field(..., description="When this history record was created")

    model_config = {"from_attributes": True}
