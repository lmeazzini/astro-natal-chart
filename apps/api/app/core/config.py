"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""

import json
from typing import Literal, Self

from pydantic import PostgresDsn, RedisDsn, model_validator
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

    # Email Support
    SUPPORT_EMAIL: str = "support@realastrology.ai"

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
        return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY and self.S3_BUCKET_NAME)

    # AWS S3 - Backup Storage (uses same AWS credentials)
    BACKUP_S3_BUCKET: str | None = None
    BACKUP_S3_PREFIX: str = "backups"
    BACKUP_S3_RETENTION_DAYS: int = 30  # Local retention after S3 upload
    BACKUP_S3_GLACIER_DAYS: int = 30  # Days before transitioning to Glacier
    BACKUP_S3_DELETE_DAYS: int = 90  # Days before permanent deletion

    @property
    def backup_s3_enabled(self) -> bool:
        """Check if Backup S3 is properly configured."""
        return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY and self.BACKUP_S3_BUCKET)

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

    # GitHub API Integration (for dynamic feature list)
    GITHUB_REPO: str = "lmeazzini/astro-natal-chart"
    GITHUB_TOKEN: str | None = None  # Optional, increases rate limit from 60 to 5000/hour
    GITHUB_FEATURES_CACHE_TTL: int = 300  # Cache TTL in seconds (5 minutes)

    # Qdrant Vector Database (RAG)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "astrology_knowledge"
    QDRANT_VECTOR_SIZE: int = 1536  # OpenAI ada-002 embedding size

    # OpenAI Embeddings (for RAG)
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"

    # RAG Settings
    RAG_MAX_ASPECTS: int = 10  # Maximum aspects to interpret in RAG mode

    # RAG Document Storage
    RAG_STORAGE_TYPE: Literal["local", "s3"] = "local"  # Storage backend
    RAG_S3_BUCKET: str | None = None  # S3 bucket for RAG documents (uses AWS credentials above)
    RAG_S3_PREFIX: str = "rag-documents"  # S3 prefix for RAG documents
    RAG_LOCAL_PATH: str = "rag_docs"  # Local path for RAG documents (relative to app root)
    RAG_CACHE_DIR: str | None = "/tmp/rag_cache"  # Cache directory for S3 documents
    RAG_CACHE_TTL: int = 3600  # Cache TTL in seconds (1 hour)

    @property
    def rag_s3_enabled(self) -> bool:
        """Check if RAG S3 storage is enabled and configured."""
        return bool(
            self.RAG_STORAGE_TYPE == "s3"
            and self.AWS_ACCESS_KEY_ID
            and self.AWS_SECRET_ACCESS_KEY
            and self.RAG_S3_BUCKET
        )

    # Cookie Security Settings
    COOKIE_SECURE: bool = True  # Use secure cookies (HTTPS only) in production
    COOKIE_HTTPONLY: bool = True  # Prevent JavaScript access to cookies
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"  # CSRF protection
    COOKIE_DOMAIN: str | None = None  # Cookie domain (None = current domain)

    # Unverified User Limits
    UNVERIFIED_USER_CHART_LIMIT: int = 1  # Max charts for unverified users

    # Amplitude Analytics
    AMPLITUDE_API_KEY: str | None = None
    AMPLITUDE_ENABLED: bool = False

    # Stripe Payment Integration
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    STRIPE_PRICE_IDS: str | None = None  # JSON object from AWS Secrets Manager
    STRIPE_PRICE_STARTER: str | None = None  # Stripe Price ID for Starter plan
    STRIPE_PRICE_PRO: str | None = None  # Stripe Price ID for Pro plan
    STRIPE_PRICE_UNLIMITED: str | None = None  # Stripe Price ID for Unlimited plan
    # Credit pack prices (one-time purchases)
    STRIPE_CREDIT_PRICES: str | None = None  # JSON object from AWS Secrets Manager
    STRIPE_PRICE_CREDITS_SMALL: str | None = None  # Price ID for small credit pack
    STRIPE_PRICE_CREDITS_MEDIUM: str | None = None  # Price ID for medium credit pack
    STRIPE_PRICE_CREDITS_LARGE: str | None = None  # Price ID for large credit pack

    @model_validator(mode="after")
    def parse_stripe_price_ids(self) -> Self:
        """Parse STRIPE_PRICE_IDS and STRIPE_CREDIT_PRICES JSON into individual fields."""
        # Parse subscription plan prices
        if self.STRIPE_PRICE_IDS:
            try:
                price_ids = json.loads(self.STRIPE_PRICE_IDS)
                if isinstance(price_ids, dict):
                    if not self.STRIPE_PRICE_STARTER and "starter" in price_ids:
                        object.__setattr__(self, "STRIPE_PRICE_STARTER", price_ids["starter"])
                    if not self.STRIPE_PRICE_PRO and "pro" in price_ids:
                        object.__setattr__(self, "STRIPE_PRICE_PRO", price_ids["pro"])
                    if not self.STRIPE_PRICE_UNLIMITED and "unlimited" in price_ids:
                        object.__setattr__(self, "STRIPE_PRICE_UNLIMITED", price_ids["unlimited"])
            except json.JSONDecodeError:
                pass  # Invalid JSON, ignore

        # Parse credit pack prices
        if self.STRIPE_CREDIT_PRICES:
            try:
                credit_prices = json.loads(self.STRIPE_CREDIT_PRICES)
                if isinstance(credit_prices, dict):
                    if not self.STRIPE_PRICE_CREDITS_SMALL and "small" in credit_prices:
                        object.__setattr__(
                            self, "STRIPE_PRICE_CREDITS_SMALL", credit_prices["small"]
                        )
                    if not self.STRIPE_PRICE_CREDITS_MEDIUM and "medium" in credit_prices:
                        object.__setattr__(
                            self, "STRIPE_PRICE_CREDITS_MEDIUM", credit_prices["medium"]
                        )
                    if not self.STRIPE_PRICE_CREDITS_LARGE and "large" in credit_prices:
                        object.__setattr__(
                            self, "STRIPE_PRICE_CREDITS_LARGE", credit_prices["large"]
                        )
            except json.JSONDecodeError:
                pass  # Invalid JSON, ignore

        return self

    @property
    def stripe_enabled(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.STRIPE_SECRET_KEY and self.STRIPE_WEBHOOK_SECRET)

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        url = str(self.DATABASE_URL)
        return url.replace("postgresql+asyncpg://", "postgresql://")


# Global settings instance
settings = Settings()
