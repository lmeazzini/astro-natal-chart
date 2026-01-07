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
    EMAIL_NOT_VERIFIED = "auth.email_not_verified"
    PREMIUM_REQUIRED = "auth.premium_required"


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
    UNVERIFIED_CHART_LIMIT = "chart.unverified_chart_limit"
    UNVERIFIED_PDF_BLOCKED = "chart.unverified_pdf_blocked"
    ACCESS_DENIED = "chart.access_denied"
    NOT_CALCULATED = "chart.not_calculated"
    DATA_NOT_AVAILABLE = "chart.data_not_available"
    PROCESSING_UNAVAILABLE = "chart.processing_unavailable"
    PDF_NOT_GENERATED = "chart.pdf_not_generated"
    STILL_PROCESSING = "chart.still_processing"
    PUBLIC_NOT_FOUND = "chart.public_not_found"
    PDF_ALREADY_GENERATING = "chart.pdf_already_generating"
    PDF_GENERATION_STARTED = "chart.pdf_generation_started"
    S3_DOWNLOAD_FAILED = "chart.s3_download_failed"
    CREATE_ERROR = "chart.create_error"


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
    INSUFFICIENT_CREDITS = "common.insufficient_credits"


class LongevityMessages(StrEnum):
    """Longevity analysis messages."""

    HYLEG_CALCULATION_FAILED = "longevity.hyleg_calculation_failed"
    ALCOCHODEN_CALCULATION_FAILED = "longevity.alcochoden_calculation_failed"
    ANALYSIS_FAILED = "longevity.analysis_failed"


class SaturnReturnMessages(StrEnum):
    """Saturn Return analysis messages."""

    SATURN_NOT_FOUND = "saturn_return.saturn_not_found"


class SolarReturnMessages(StrEnum):
    """Solar Return analysis messages."""

    SUN_NOT_FOUND = "solar_return.sun_not_found"
    MAX_RANGE_EXCEEDED = "solar_return.max_range_exceeded"
    INVALID_YEAR_RANGE = "solar_return.invalid_year_range"


class OAuthMessages(StrEnum):
    """OAuth-related messages."""

    INVALID_PROVIDER = "oauth.invalid_provider"
    PROVIDER_NOT_CONFIGURED = "oauth.provider_not_configured"
    REDIRECT_URI_NOT_CONFIGURED = "oauth.redirect_uri_not_configured"
    AUTH_FAILED = "oauth.auth_failed"
    CONNECTION_NOT_FOUND = "oauth.connection_not_found"
    CANNOT_DISCONNECT_LAST = "oauth.cannot_disconnect_last"
    FAILED_TO_RETRIEVE_USER_INFO = "oauth.failed_to_retrieve_user_info"


class StorageMessages(StrEnum):
    """File storage/upload messages."""

    INVALID_FILE_TYPE = "storage.invalid_file_type"
    FILE_TOO_LARGE = "storage.file_too_large"
    UPLOAD_FAILED = "storage.upload_failed"
    UPLOAD_SUCCESS = "storage.upload_success"


class ProfileMessages(StrEnum):
    """Profile-related messages."""

    PROFILE_PRIVATE = "profile.private"


class AdminMessages(StrEnum):
    """Admin-related messages."""

    CANNOT_MODIFY_OWN_ROLE = "admin.cannot_modify_own_role"
    CANNOT_MODIFY_ADMIN = "admin.cannot_modify_admin"
    CANNOT_REMOVE_LAST_ADMIN = "admin.cannot_remove_last_admin"


class GeocodingMessages(StrEnum):
    """Geocoding-related messages."""

    LOCATION_NOT_FOUND = "geocoding.location_not_found"
    SEARCH_FAILED = "geocoding.search_failed"
    COORDINATES_FAILED = "geocoding.coordinates_failed"
    TIMEZONE_NOT_FOUND = "geocoding.timezone_not_found"


class StripeMessages(StrEnum):
    """Stripe/Payment-related messages."""

    INVALID_PLAN_TYPE = "stripe.invalid_plan_type"
    PRICE_NOT_CONFIGURED = "stripe.price_not_configured"
    INVALID_SIGNATURE = "stripe.invalid_signature"
    NOT_CONFIGURED = "stripe.not_configured"
    ALREADY_SUBSCRIBED = "stripe.already_subscribed"
    NO_BILLING_ACCOUNT = "stripe.no_billing_account"
    NO_SUBSCRIPTION_TO_CANCEL = "stripe.no_subscription_to_cancel"
    CANCELLED_AT_PERIOD_END = "stripe.cancelled_at_period_end"
    CANCELLED_IMMEDIATELY = "stripe.cancelled_immediately"
    NO_SUBSCRIPTION_TO_REACTIVATE = "stripe.no_subscription_to_reactivate"
    NOT_SCHEDULED_FOR_CANCELLATION = "stripe.not_scheduled_for_cancellation"
    SUBSCRIPTION_REACTIVATED = "stripe.subscription_reactivated"


class EmailMessages(StrEnum):
    """Email-related messages (subjects and content)."""

    # Subjects
    PASSWORD_RESET_SUBJECT = "email.password_reset_subject"
    PASSWORD_CHANGED_SUBJECT = "email.password_changed_subject"
    VERIFY_EMAIL_SUBJECT = "email.verify_email_subject"
    WELCOME_SUBJECT = "email.welcome_subject"

    # Common
    GREETING = "email.greeting"
    FOOTER_COPYRIGHT = "email.footer_copyright"
    BUTTON_NOT_WORKING = "email.button_not_working"

    # Password Reset
    PASSWORD_RESET_TITLE = "email.password_reset_title"
    PASSWORD_RESET_INTRO = "email.password_reset_intro"
    PASSWORD_RESET_ACTION = "email.password_reset_action"
    PASSWORD_RESET_BUTTON = "email.password_reset_button"
    PASSWORD_RESET_EXPIRY = "email.password_reset_expiry"
    PASSWORD_RESET_IGNORE = "email.password_reset_ignore"

    # Password Changed
    PASSWORD_CHANGED_TITLE = "email.password_changed_title"
    PASSWORD_CHANGED_SUCCESS = "email.password_changed_success"
    PASSWORD_CHANGED_WARNING = "email.password_changed_warning"
    PASSWORD_CHANGED_LOGIN = "email.password_changed_login"

    # Email Verification
    VERIFY_EMAIL_TITLE = "email.verify_email_title"
    VERIFY_EMAIL_INTRO = "email.verify_email_intro"
    VERIFY_EMAIL_ACTION = "email.verify_email_action"
    VERIFY_EMAIL_BUTTON = "email.verify_email_button"
    VERIFY_EMAIL_EXPIRY = "email.verify_email_expiry"
    VERIFY_EMAIL_IGNORE = "email.verify_email_ignore"


class PDFReportMessages(StrEnum):
    """PDF Report-related messages."""

    # Section titles
    CHART_INFO = "pdf.chart_info"
    PLANETS = "pdf.planets"
    PLANETARY_POSITIONS = "pdf.planetary_positions"
    PLANETARY_INTERPRETATIONS = "pdf.planetary_interpretations"
    HOUSES = "pdf.houses"
    HOUSE_CUSPS = "pdf.house_cusps"
    HOUSE_INTERPRETATIONS = "pdf.house_interpretations"
    ASPECTS = "pdf.aspects"
    MAIN_ASPECTS = "pdf.main_aspects"
    ASPECT_INTERPRETATIONS = "pdf.aspect_interpretations"

    # Table headers
    PLANET = "pdf.planet"
    SIGN = "pdf.sign"
    DEGREE = "pdf.degree"
    HOUSE = "pdf.house"
    DIGNITY = "pdf.dignity"
    RETROGRADE = "pdf.retrograde"
    ASPECT = "pdf.aspect"
    ORB = "pdf.orb"

    # Chart details
    HOUSE_SYSTEM = "pdf.house_system"
    ZODIAC_TYPE = "pdf.zodiac_type"
    ASCENDANT = "pdf.ascendant"
    MIDHEAVEN = "pdf.midheaven"

    # Footer
    PAGE_OF = "pdf.page_of"
    TRADITIONAL_ASTROLOGY = "pdf.traditional_astrology"
    REPORT_GENERATED = "pdf.report_generated"
    CONTINUED = "pdf.continued"
    CONTINUES_NEXT = "pdf.continues_next"
