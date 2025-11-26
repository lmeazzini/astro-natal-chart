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

    - ACTIVE: Subscription is currently active and valid
    - EXPIRED: Subscription has passed its expiration date
    - CANCELLED: Subscription was manually cancelled by admin
    """

    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        return self.value
