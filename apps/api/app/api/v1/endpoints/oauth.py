"""
OAuth2 authentication endpoints for social login.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.oauth_service import OAuthService, oauth

router = APIRouter()


class OAuthTokenResponse(BaseModel):
    """OAuth token response model."""
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


@router.get("/login/{provider}")
async def oauth_login(provider: str, request: Request):
    """
    Initiate OAuth login with a provider.

    Args:
        provider: OAuth provider (google, github, facebook)
        request: FastAPI request object

    Returns:
        Redirect to OAuth provider authorization URL
    """
    if provider not in ["google", "github", "facebook"]:
        raise HTTPException(status_code=400, detail="Invalid OAuth provider")

    # Get the OAuth client for the provider
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth provider {provider} is not configured"
        )

    # Generate redirect URI based on provider
    if provider == "google":
        redirect_uri = settings.GOOGLE_REDIRECT_URI
    elif provider == "github":
        redirect_uri = settings.GITHUB_REDIRECT_URI
    else:  # facebook
        redirect_uri = settings.FACEBOOK_REDIRECT_URI

    if not redirect_uri:
        raise HTTPException(
            status_code=500,
            detail=f"Redirect URI for {provider} is not configured"
        )

    # Generate authorization URL and redirect user
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from provider.

    Args:
        provider: OAuth provider (google, github, facebook)
        request: FastAPI request object
        db: Database session

    Returns:
        OAuth token response with access and refresh tokens
    """
    if provider not in ["google", "github", "facebook"]:
        raise HTTPException(status_code=400, detail="Invalid OAuth provider")

    # Get the OAuth client
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth provider {provider} is not configured"
        )

    try:
        # Exchange authorization code for access token
        token = await client.authorize_access_token(request)

        # Fetch user information from provider
        if provider == "google":
            userinfo = token.get("userinfo")
            if not userinfo:
                userinfo = await client.userinfo(token=token)
        elif provider == "github":
            # GitHub requires a separate API call to get user info
            resp = await client.get("https://api.github.com/user", token=token)
            userinfo = resp.json()

            # GitHub doesn't always return email in the main user object
            if not userinfo.get("email"):
                email_resp = await client.get("https://api.github.com/user/emails", token=token)
                emails = email_resp.json()
                # Get the primary email
                for email_obj in emails:
                    if email_obj.get("primary"):
                        userinfo["email"] = email_obj.get("email")
                        break
        else:  # facebook
            resp = await client.get(
                "https://graph.facebook.com/v18.0/me?fields=id,name,email,picture",
                token=token
            )
            userinfo = resp.json()

        # Extract user info based on provider
        oauth_service = OAuthService(db)
        user_data = oauth_service.extract_user_info(provider, userinfo)

        # Validate that we got required fields
        if not user_data.get("email") or not user_data.get("provider_user_id"):
            raise HTTPException(
                status_code=400,
                detail="Failed to retrieve required user information from OAuth provider"
            )

        # Get or create user
        user, is_new = await oauth_service.get_or_create_user_from_oauth(
            provider=provider,
            provider_user_id=user_data["provider_user_id"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            avatar_url=user_data.get("avatar_url"),
        )

        # Create tokens
        tokens = oauth_service.create_tokens_for_user(user)

        # In production, you might want to redirect to frontend with tokens
        # For now, we'll return a redirect to the frontend with tokens in query params
        frontend_url = settings.cors_origins[0]  # Get first allowed origin
        redirect_url = (
            f"{frontend_url}/oauth/callback?"
            f"access_token={tokens['access_token']}&"
            f"refresh_token={tokens['refresh_token']}"
        )

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # In production, log this error
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authentication failed: {str(e)}"
        ) from e


@router.get("/providers")
async def get_oauth_providers():
    """
    Get list of available OAuth providers.

    Returns:
        List of configured OAuth providers
    """
    providers = []

    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        providers.append({
            "name": "google",
            "display_name": "Google",
        })

    if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
        providers.append({
            "name": "github",
            "display_name": "GitHub",
        })

    if settings.FACEBOOK_CLIENT_ID and settings.FACEBOOK_CLIENT_SECRET:
        providers.append({
            "name": "facebook",
            "display_name": "Facebook",
        })

    return {"providers": providers}
