"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""


from typing import Literal

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Real Astrology API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    DEFAULT_LOCALE: str = "pt-BR"
    DEFAULT_TIMEZONE: str = "America/Sao_Paulo"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: PostgresDsn

    # Redis
    REDIS_URL: RedisDsn

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # OAuth2 - Google
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None

    # OAuth2 - GitHub
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    GITHUB_REDIRECT_URI: str | None = None

    # OAuth2 - Facebook
    FACEBOOK_CLIENT_ID: str | None = None
    FACEBOOK_CLIENT_SECRET: str | None = None
    FACEBOOK_REDIRECT_URI: str | None = None

    # Frontend URL (for password reset links, etc.)
    FRONTEND_URL: str = "http://localhost:5173"

    # Email (SMTP)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "noreply@real-astrology.com"
    SMTP_USE_TLS: bool = True

    # Email (OAuth2 - Gmail API)
    GMAIL_CLIENT_ID: str | None = None
    GMAIL_CLIENT_SECRET: str | None = None
    GMAIL_REFRESH_TOKEN: str | None = None
    GMAIL_TOKEN_URI: str = "https://oauth2.googleapis.com/token"

    # Geocoding
    OPENCAGE_API_KEY: str | None = None
    NOMINATIM_USER_AGENT: str = "real-astrology/1.0"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7

    # AWS S3 - PDF Storage
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str = "genesis-dev-559050210551"
    S3_PREFIX: str = "birth-charts"  # Prefix for all S3 keys
    S3_PRESIGNED_URL_EXPIRATION: int = 3600  # Presigned URL expiration (seconds)

    @property
    def s3_enabled(self) -> bool:
        """Check if S3 is properly configured."""
        return bool(
            self.AWS_ACCESS_KEY_ID
            and self.AWS_SECRET_ACCESS_KEY
            and self.S3_BUCKET_NAME
        )

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Celery
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    # Swiss Ephemeris
    EPHEMERIS_PATH: str = "/usr/share/ephe"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True  # Disable for testing

    # Cookie Security Settings
    COOKIE_SECURE: bool = True  # Use secure cookies (HTTPS only) in production
    COOKIE_HTTPONLY: bool = True  # Prevent JavaScript access to cookies
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"  # CSRF protection
    COOKIE_DOMAIN: str | None = None  # Cookie domain (None = current domain)

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        url = str(self.DATABASE_URL)
        return url.replace("postgresql+asyncpg://", "postgresql://")


# Global settings instance
settings = Settings()
