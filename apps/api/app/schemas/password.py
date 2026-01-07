"""
Password change schemas.
"""

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from app.core.i18n.messages import PasswordMessages
from app.core.i18n.translator import translate


class PasswordChange(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password must be at least 8 characters",
    )
    new_password_confirm: str = Field(..., description="New password confirmation")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError(translate(PasswordMessages.PASSWORD_MISSING_UPPERCASE))
        if not any(c.islower() for c in v):
            raise ValueError(translate(PasswordMessages.PASSWORD_MISSING_LOWERCASE))
        if not any(c.isdigit() for c in v):
            raise ValueError(translate(PasswordMessages.PASSWORD_MISSING_DIGIT))
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError(translate(PasswordMessages.PASSWORD_MISSING_SPECIAL))
        return v

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Validate that passwords match."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError(translate(PasswordMessages.PASSWORDS_DONT_MATCH))
        return v
