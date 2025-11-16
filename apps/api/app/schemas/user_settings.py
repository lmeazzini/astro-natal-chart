"""
User settings schemas.
"""

from pydantic import BaseModel, Field


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""

    allow_email_notifications: bool | None = Field(
        None,
        description="Allow email notifications",
    )
    analytics_consent: bool | None = Field(
        None,
        description="Consent to analytics tracking",
    )


class UserSettingsRead(BaseModel):
    """Schema for reading user settings."""

    allow_email_notifications: bool
    analytics_consent: bool

    model_config = {"from_attributes": True}
