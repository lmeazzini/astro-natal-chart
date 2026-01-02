"""Stripe-related Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateCheckoutSessionRequest(BaseModel):
    """Request to create a Stripe checkout session."""

    plan_type: str = Field(
        ...,
        description="Plan type: starter, pro, or unlimited",
        pattern="^(starter|pro|unlimited)$",
    )
    success_url: str | None = Field(
        None,
        description="Custom success URL (optional, defaults to frontend)",
    )
    cancel_url: str | None = Field(
        None,
        description="Custom cancel URL (optional, defaults to pricing page)",
    )


class CheckoutSessionResponse(BaseModel):
    """Response with checkout session details."""

    session_id: str
    checkout_url: str


class CreatePortalSessionRequest(BaseModel):
    """Request to create a Stripe customer portal session."""

    return_url: str | None = Field(
        None,
        description="Custom return URL (optional, defaults to account page)",
    )


class PortalSessionResponse(BaseModel):
    """Response with customer portal session URL."""

    portal_url: str


class SubscriptionStatusResponse(BaseModel):
    """Current subscription status."""

    has_subscription: bool
    plan_type: str
    status: str | None = None
    stripe_subscription_id: str | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False
    days_until_renewal: int | None = None


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel subscription."""

    at_period_end: bool = Field(
        True,
        description="If true, cancel at end of billing period. If false, cancel immediately.",
    )


class CancelSubscriptionResponse(BaseModel):
    """Response after cancelling subscription."""

    success: bool
    message: str
    cancel_at_period_end: bool
    current_period_end: datetime | None = None


class PaymentRead(BaseModel):
    """Payment record response."""

    id: UUID
    amount: int
    currency: str
    status: str
    receipt_url: str | None = None
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @property
    def amount_display(self) -> str:
        """Format amount for display."""
        if self.currency.lower() == "brl":
            return (
                f"R$ {self.amount / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        return f"{self.currency.upper()} {self.amount / 100:.2f}"


class PaymentHistoryResponse(BaseModel):
    """Paginated payment history response."""

    payments: list[PaymentRead]
    total: int
    page: int
    page_size: int
    has_more: bool


class StripeConfigResponse(BaseModel):
    """Public Stripe configuration for frontend."""

    publishable_key: str
    enabled: bool
    plans: dict[str, dict[str, str | int | None]]


class WebhookEventRead(BaseModel):
    """Webhook event record (admin only)."""

    id: UUID
    stripe_event_id: str
    event_type: str
    status: str
    error_message: str | None = None
    created_at: datetime
    processed_at: datetime | None = None

    model_config = {"from_attributes": True}
