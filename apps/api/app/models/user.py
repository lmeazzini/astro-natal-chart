"""
User model for database.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import UserRole


class UserType(str, Enum):
    """User type enumeration."""

    PROFESSIONAL = "professional"
    STUDENT = "student"
    CURIOUS = "curious"


if TYPE_CHECKING:
    from app.models.chart import BirthChart
    from app.models.payment import Payment
    from app.models.subscription import Subscription
    from app.models.user_credit import UserCredit


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="pt-BR", nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    time_format: Mapped[str] = mapped_column(String(5), default="24h", nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Role-based access control
    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.FREE.value,
        nullable=False,
        index=True,
    )

    # Profile fields
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_type: Mapped[str] = mapped_column(
        String(50), default=UserType.CURIOUS.value, nullable=False
    )

    # Social links
    website: Mapped[str | None] = mapped_column(String(200), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(100), nullable=True)
    twitter: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Professional info
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    professional_since: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specializations: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Preferences
    allow_email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    analytics_consent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Activity tracking
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    birth_charts: Mapped[list["BirthChart"]] = relationship(  # noqa: F821
        "BirthChart",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(  # noqa: F821
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    subscription: Mapped["Subscription | None"] = relationship(  # noqa: F821
        "Subscription",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    credits: Mapped["UserCredit | None"] = relationship(  # noqa: F821
        "UserCredit",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN.value or self.is_superuser

    @property
    def is_premium(self) -> bool:
        """Check if user has premium or higher role."""
        return self.role in [UserRole.PREMIUM.value, UserRole.ADMIN.value] or self.is_superuser

    @property
    def user_role(self) -> UserRole:
        """Get user role as enum."""
        try:
            return UserRole(self.role)
        except ValueError:
            return UserRole.FREE


class OAuthAccount(Base):
    """OAuth account model for social login."""

    __tablename__ = "oauth_accounts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")

    def __repr__(self) -> str:
        return f"<OAuthAccount {self.provider}:{self.provider_user_id}>"
