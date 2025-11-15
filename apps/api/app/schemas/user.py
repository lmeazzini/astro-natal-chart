"""
User schemas for request/response validation.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core.core_schema import ValidationInfo


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


class UserUpdate(BaseModel):
    """Schema for user profile updates."""

    full_name: str | None = Field(None, min_length=3, max_length=100)
    locale: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50)
    avatar_url: str | None = None


class UserRead(UserBase):
    """Schema for user response."""

    id: UUID
    locale: str
    timezone: str | None
    avatar_url: str | None
    email_verified: bool
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserInDB(UserRead):
    """Schema for user in database (includes password hash)."""

    password_hash: str | None

    model_config = {"from_attributes": True}
