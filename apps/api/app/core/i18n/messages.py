"""
Message key constants for i18n.

Defines all translatable message keys as constants to avoid typos
and enable IDE autocomplete.
"""

from enum import StrEnum


class AuthMessages(StrEnum):
    """Authentication-related messages."""

    USER_ALREADY_EXISTS = "auth.user_already_exists"
    INVALID_CREDENTIALS = "auth.invalid_credentials"
    USER_NOT_FOUND = "auth.user_not_found"
    USER_INACTIVE = "auth.user_inactive"
    INVALID_TOKEN = "auth.invalid_token"
    INVALID_TOKEN_TYPE = "auth.invalid_token_type"
    INVALID_TOKEN_PAYLOAD = "auth.invalid_token_payload"
    TOKEN_EXPIRED = "auth.token_expired"
    TOKEN_INVALIDATED = "auth.token_invalidated"
    EMAIL_ALREADY_VERIFIED = "auth.email_already_verified"
    VERIFICATION_SENT = "auth.verification_sent"
    VERIFICATION_FAILED = "auth.verification_failed"
    INVALID_VERIFICATION_TOKEN = "auth.invalid_verification_token"
    NOT_ENOUGH_PRIVILEGES = "auth.not_enough_privileges"
    ADMIN_EMAIL_NOT_VERIFIED = "auth.admin_email_not_verified"


class PasswordMessages(StrEnum):
    """Password-related messages."""

    RESET_EMAIL_SENT = "password.reset_email_sent"
    INVALID_RESET_TOKEN = "password.invalid_reset_token"
    PASSWORD_CHANGED = "password.password_changed"
    PASSWORD_TOO_SHORT = "password.too_short"
    PASSWORD_MISSING_UPPERCASE = "password.missing_uppercase"
    PASSWORD_MISSING_LOWERCASE = "password.missing_lowercase"
    PASSWORD_MISSING_DIGIT = "password.missing_digit"
    PASSWORD_MISSING_SPECIAL = "password.missing_special"
    PASSWORDS_DONT_MATCH = "password.passwords_dont_match"


class ValidationMessages(StrEnum):
    """General validation messages."""

    REQUIRED_FIELD = "validation.required_field"
    INVALID_EMAIL = "validation.invalid_email"
    MUST_ACCEPT_TERMS = "validation.must_accept_terms"
    INVALID_DATE = "validation.invalid_date"
    INVALID_TIME = "validation.invalid_time"
    INVALID_LOCATION = "validation.invalid_location"


class ChartMessages(StrEnum):
    """Chart-related messages."""

    CHART_NOT_FOUND = "chart.not_found"
    CHART_CREATED = "chart.created"
    CHART_UPDATED = "chart.updated"
    CHART_DELETED = "chart.deleted"
    CALCULATION_ERROR = "chart.calculation_error"
    PDF_GENERATING = "chart.pdf_generating"
    PDF_READY = "chart.pdf_ready"
    PDF_FAILED = "chart.pdf_failed"


class UserMessages(StrEnum):
    """User-related messages."""

    PROFILE_UPDATED = "user.profile_updated"
    AVATAR_UPLOADED = "user.avatar_uploaded"
    ACCOUNT_DELETED = "user.account_deleted"
    DELETION_CANCELLED = "user.deletion_cancelled"
    DATA_EXPORTED = "user.data_exported"


class CommonMessages(StrEnum):
    """Common/generic messages."""

    INTERNAL_ERROR = "common.internal_error"
    NOT_FOUND = "common.not_found"
    FORBIDDEN = "common.forbidden"
    BAD_REQUEST = "common.bad_request"
    SUCCESS = "common.success"
    RATE_LIMIT_EXCEEDED = "common.rate_limit_exceeded"
