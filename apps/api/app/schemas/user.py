"""
User schemas for request/response validation.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator


class UserType(str, Enum):
    """User type enumeration."""

    PROFESSIONAL = "professional"
    STUDENT = "student"
    CURIOUS = "curious"


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    full_name: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password must be at least 8 characters",
    )
    password_confirm: str = Field(..., description="Password confirmation")
    accept_terms: bool = Field(
        default=False,
        description="User must accept terms of service and privacy policy",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Validate that passwords match."""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("accept_terms")
    @classmethod
    def validate_terms_accepted(cls, v: bool) -> bool:
        """Validate that user has accepted terms."""
        if not v:
            raise ValueError("You must accept the terms of service and privacy policy")
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates."""

    full_name: str | None = Field(None, min_length=3, max_length=100)
    locale: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50, description="IANA timezone identifier")
    time_format: str | None = Field(
        None,
        pattern="^(12h|24h)$",
        description="Time format preference: 12h or 24h",
    )
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500, description="User biography")
    profile_public: bool | None = Field(None, description="Make profile publicly visible")
    user_type: UserType | None = Field(
        None, description="User type: professional, student, or curious"
    )

    # Social links
    website: str | None = Field(None, max_length=200)
    instagram: str | None = Field(None, max_length=100)
    twitter: str | None = Field(None, max_length=100)

    # Professional info
    location: str | None = Field(None, max_length=200)
    professional_since: int | None = Field(None, ge=1900, le=2100)
    specializations: list[str] | None = Field(
        None,
        description="List of specializations (max 10 items, 100 chars each)",
    )

    @field_validator("specializations")
    @classmethod
    def validate_specializations(cls, v: list[str] | None) -> list[str] | None:
        """Validate specializations list: max 10 items, max 100 chars each."""
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("Maximum of 10 specializations allowed")
        for i, spec in enumerate(v):
            if len(spec) > 100:
                raise ValueError(f"Specialization {i + 1} exceeds 100 characters")
            if len(spec.strip()) == 0:
                raise ValueError(f"Specialization {i + 1} cannot be empty")
        # Remove duplicates and strip whitespace
        return list(dict.fromkeys(s.strip() for s in v if s.strip()))

    @field_validator("instagram", "twitter")
    @classmethod
    def validate_social_handle(cls, v: str | None) -> str | None:
        """Remove @ if present."""
        if v:
            return v.lstrip("@")
        return v

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        """Validate website URL format."""
        if v:
            if not v.startswith(("http://", "https://")):
                v = f"https://{v}"
        return v

    @field_validator("professional_since")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        """Validate year is reasonable."""
        if v is not None:
            current_year = datetime.now().year
            if v > current_year:
                raise ValueError("Year cannot be in the future")
        return v


class UserRead(UserBase):
    """Schema for user response."""

    id: UUID
    locale: str
    timezone: str | None
    time_format: str
    avatar_url: str | None
    email_verified: bool
    is_active: bool
    is_superuser: bool
    role: str  # User role (free, premium, admin)
    bio: str | None
    profile_public: bool
    user_type: str
    # Social links
    website: str | None
    instagram: str | None
    twitter: str | None
    # Professional info
    location: str | None
    professional_since: int | None
    specializations: list[str] | None
    # Settings
    allow_email_notifications: bool
    analytics_consent: bool
    last_login_at: datetime | None
    last_activity_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserPublicProfile(BaseModel):
    """Schema for public user profile (limited info)."""

    id: UUID
    full_name: str
    avatar_url: str | None
    bio: str | None
    user_type: str
    website: str | None
    instagram: str | None
    twitter: str | None
    location: str | None
    professional_since: int | None
    specializations: list[str] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserInDB(UserRead):
    """Schema for user in database (includes password hash)."""

    password_hash: str | None

    model_config = {"from_attributes": True}
