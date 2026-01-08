"""
Enums for the application.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC.

    Hierarchy (lowest to highest):
    - FREE: Default for new users, basic features only
    - PREMIUM: Paying subscribers, access to premium features (e.g., horary)
    - ADMIN: System administrators, full access + admin panel
    """

    FREE = "free"  # Default user role (basic features)
    PREMIUM = "premium"  # Premium subscriber (all features)
    ADMIN = "admin"  # Administrator with full access

    def __str__(self) -> str:
        return self.value


class SubscriptionStatus(str, Enum):
    """Subscription status values.

    - PENDING: Subscription created but payment not completed
    - ACTIVE: Subscription is currently active and valid
    - EXPIRED: Subscription has passed its expiration date
    - CANCELLED: Subscription was manually cancelled by admin
    - PAST_DUE: Payment failed but in grace period
    - CANCELLING: Scheduled for cancellation at period end
    """

    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    CANCELLING = "cancelling"

    def __str__(self) -> str:
        return self.value


class SubscriptionChangeType(str, Enum):
    """Types of subscription changes for history tracking.

    - GRANTED: New subscription granted or existing reactivated
    - EXTENDED: Subscription duration extended
    - REVOKED: Subscription manually revoked by admin
    - EXPIRED: Subscription automatically expired by system
    - STRIPE_SUBSCRIBED: New subscription via Stripe checkout
    - RENEWED: Monthly renewal via Stripe
    - UPGRADED: Plan upgrade
    - DOWNGRADED: Plan downgrade
    - CANCELLATION_SCHEDULED: User scheduled cancellation
    - PAYMENT_FAILED: Payment failed
    """

    GRANTED = "granted"
    EXTENDED = "extended"
    REVOKED = "revoked"
    EXPIRED = "expired"
    STRIPE_SUBSCRIBED = "stripe_subscribed"
    RENEWED = "renewed"
    UPGRADED = "upgraded"
    DOWNGRADED = "downgraded"
    CANCELLATION_SCHEDULED = "cancellation_scheduled"
    PAYMENT_FAILED = "payment_failed"

    def __str__(self) -> str:
        return self.value


class PlanType(str, Enum):
    """Subscription plan types with credit allocation.

    - FREE: 10 credits/month (default for all users)
    - STARTER: 50 credits/month (R$ 19,90)
    - PRO: 200 credits/month (R$ 49,90)
    - UNLIMITED: Unlimited credits (R$ 99,90)
    """

    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    UNLIMITED = "unlimited"

    def __str__(self) -> str:
        return self.value


class TransactionType(str, Enum):
    """Types of credit transactions.

    - DEBIT: Credits consumed by using a feature
    - CREDIT: Credits added (bonus, refund, etc.)
    - RESET: Monthly credit reset
    - UPGRADE: Credits adjusted due to plan upgrade
    - BONUS: Promotional credits added by admin
    - REFUND: Credits refunded by admin
    """

    DEBIT = "debit"
    CREDIT = "credit"
    RESET = "reset"
    UPGRADE = "upgrade"
    BONUS = "bonus"
    REFUND = "refund"

    def __str__(self) -> str:
        return self.value


class FeatureType(str, Enum):
    """Premium features that consume credits.

    Each feature has an associated credit cost defined in credit_config.py.
    """

    INTERPRETATION_BASIC = "interpretation_basic"
    INTERPRETATION_FULL = "interpretation_full"
    PDF_REPORT = "pdf_report"
    SYNASTRY = "synastry"
    SOLAR_RETURN = "solar_return"
    SATURN_RETURN = "saturn_return"
    LONGEVITY = "longevity"
    GROWTH = "growth"
    PROFECTIONS = "profections"
    TRANSITS = "transits"

    def __str__(self) -> str:
        return self.value
