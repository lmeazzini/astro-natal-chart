"""Schemas for credit-related API responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreditResponse(BaseModel):
    """User credit balance response."""

    plan_type: str = Field(..., description="Current plan type (free, starter, pro, unlimited)")
    credits_balance: int = Field(..., description="Current credit balance")
    credits_limit: int | None = Field(None, description="Credit limit (None for unlimited)")
    credits_used: int = Field(..., description="Credits used in current period")
    usage_percentage: float = Field(..., description="Percentage of credits used (0-100)")
    is_unlimited: bool = Field(..., description="Whether the plan has unlimited credits")
    purchased_credits: int = Field(0, description="Purchased credits (never expire)")
    period_start: datetime = Field(..., description="Current billing period start")
    period_end: datetime | None = Field(None, description="Current billing period end")
    days_until_reset: int | None = Field(None, description="Days until credit reset")

    class Config:
        from_attributes = True


class CreditTransactionRead(BaseModel):
    """Credit transaction record."""

    id: UUID
    transaction_type: str = Field(..., description="Type: debit, credit, reset, upgrade, bonus")
    amount: int = Field(..., description="Amount (negative for debits)")
    balance_after: int = Field(..., description="Balance after transaction")
    feature_type: str | None = Field(None, description="Feature that consumed credits")
    resource_id: UUID | None = Field(None, description="Related resource ID")
    description: str | None = Field(None, description="Transaction description")
    created_at: datetime

    class Config:
        from_attributes = True


class CreditHistoryResponse(BaseModel):
    """Paginated credit transaction history."""

    transactions: list[CreditTransactionRead]
    total: int = Field(..., description="Total number of transactions")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")


class CreditUsageResponse(BaseModel):
    """Credit usage breakdown by feature."""

    usage_by_feature: dict[str, int] = Field(
        ...,
        description="Credits consumed per feature type",
        examples=[{"interpretation_basic": 5, "pdf_report": 4}],
    )
    total_used: int = Field(..., description="Total credits used in period")
    period_start: datetime
    period_end: datetime | None


class AddBonusCreditsRequest(BaseModel):
    """Request to add bonus credits to a user."""

    amount: int = Field(..., gt=0, description="Number of credits to add")
    reason: str | None = Field(None, max_length=500, description="Reason for bonus")


class UpgradePlanRequest(BaseModel):
    """Request to change a user's plan."""

    plan_type: str = Field(..., description="New plan type")


class CreditCostInfo(BaseModel):
    """Information about credit costs for features."""

    feature_type: str
    cost: int = Field(..., description="Credit cost for this feature")


class CreditsInfoResponse(BaseModel):
    """Public information about credit costs and plans."""

    plans: dict[str, int | None] = Field(
        ...,
        description="Credit limits per plan (None for unlimited)",
        examples=[{"free": 10, "starter": 50, "pro": 200, "unlimited": None}],
    )
    feature_costs: list[CreditCostInfo] = Field(
        ...,
        description="Credit costs per feature",
    )


class UnlockedFeaturesResponse(BaseModel):
    """Response for unlocked features for a chart."""

    unlocked_features: list[str] = Field(
        ...,
        description="List of feature types that have been unlocked (paid) for this chart",
        examples=[["longevity", "saturn_return", "growth"]],
    )
    unlocked_solar_return_years: list[int] = Field(
        ...,
        description="List of years for which Solar Return has been unlocked",
        examples=[[2024, 2025]],
    )
