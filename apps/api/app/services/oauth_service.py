"""
OAuth2 service for social authentication.
Supports Google, GitHub, and Facebook.
"""

from typing import Any

from authlib.integrations.starlette_client import OAuth
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.config import Config

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import OAuthAccount, User

# Initialize OAuth with settings
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID or "",
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET or "",
    "GITHUB_CLIENT_ID": settings.GITHUB_CLIENT_ID or "",
    "GITHUB_CLIENT_SECRET": settings.GITHUB_CLIENT_SECRET or "",
    "FACEBOOK_CLIENT_ID": settings.FACEBOOK_CLIENT_ID or "",
    "FACEBOOK_CLIENT_SECRET": settings.FACEBOOK_CLIENT_SECRET or "",
})

oauth = OAuth(config)

# Register OAuth providers
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=settings.GITHUB_REDIRECT_URI,
    client_kwargs={"scope": "user:email"},
)

oauth.register(
    name="facebook",
    authorize_url="https://www.facebook.com/v18.0/dialog/oauth",
    authorize_params=None,
    access_token_url="https://graph.facebook.com/v18.0/oauth/access_token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=settings.FACEBOOK_REDIRECT_URI,
    client_kwargs={"scope": "email public_profile"},
)


class OAuthService:
    """Service for handling OAuth2 authentication."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_user_from_oauth(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        full_name: str,
        avatar_url: str | None = None,
    ) -> tuple[User, bool]:
        """
        Get or create a user from OAuth provider data.

        Args:
            provider: OAuth provider name (google, github, facebook)
            provider_user_id: User ID from the provider
            email: User's email
            full_name: User's full name
            avatar_url: Optional avatar URL

        Returns:
            Tuple of (user, is_new) where is_new is True if user was created
        """
        # Check if OAuth account already exists
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
        result = await self.db.execute(stmt)
        oauth_account = result.scalar_one_or_none()

        if oauth_account:
            # OAuth account exists, return the associated user
            stmt = select(User).where(User.id == oauth_account.user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one()
            return user, False

        # Check if user with this email already exists
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # User exists, link the OAuth account
            new_oauth_account = OAuthAccount(
                user_id=existing_user.id,
                provider=provider,
                provider_user_id=provider_user_id,
            )
            self.db.add(new_oauth_account)
            await self.db.commit()
            return existing_user, False

        # Create new user with OAuth account
        new_user = User(
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            email_verified=True,  # OAuth emails are considered verified
            password_hash=None,  # OAuth users don't need password
            locale=settings.DEFAULT_LOCALE,
            timezone=settings.DEFAULT_TIMEZONE,
        )
        self.db.add(new_user)
        await self.db.flush()  # Flush to get the user ID

        # Create OAuth account
        new_oauth_account = OAuthAccount(
            user_id=new_user.id,
            provider=provider,
            provider_user_id=provider_user_id,
        )
        self.db.add(new_oauth_account)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user, True

    def create_tokens_for_user(self, user: User) -> dict[str, str]:
        """
        Create access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def extract_user_info_from_google(userinfo: dict[str, Any]) -> dict[str, str]:
        """Extract user information from Google OAuth response."""
        return {
            "provider_user_id": userinfo.get("sub", ""),
            "email": userinfo.get("email", ""),
            "full_name": userinfo.get("name", ""),
            "avatar_url": userinfo.get("picture"),
        }

    @staticmethod
    def extract_user_info_from_github(userinfo: dict[str, Any]) -> dict[str, str]:
        """Extract user information from GitHub OAuth response."""
        return {
            "provider_user_id": str(userinfo.get("id", "")),
            "email": userinfo.get("email", ""),
            "full_name": userinfo.get("name") or userinfo.get("login", ""),
            "avatar_url": userinfo.get("avatar_url"),
        }

    @staticmethod
    def extract_user_info_from_facebook(userinfo: dict[str, Any]) -> dict[str, str]:
        """Extract user information from Facebook OAuth response."""
        return {
            "provider_user_id": userinfo.get("id", ""),
            "email": userinfo.get("email", ""),
            "full_name": userinfo.get("name", ""),
            "avatar_url": userinfo.get("picture", {}).get("data", {}).get("url"),
        }

    def extract_user_info(self, provider: str, userinfo: dict[str, Any]) -> dict[str, str]:
        """
        Extract user information based on provider.

        Args:
            provider: OAuth provider name
            userinfo: Raw userinfo from provider

        Returns:
            Normalized user information dictionary
        """
        if provider == "google":
            return self.extract_user_info_from_google(userinfo)
        elif provider == "github":
            return self.extract_user_info_from_github(userinfo)
        elif provider == "facebook":
            return self.extract_user_info_from_facebook(userinfo)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
