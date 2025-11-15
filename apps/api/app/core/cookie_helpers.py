"""
Helper functions for setting secure cookies.

This module provides utility functions to set HTTP cookies with proper security flags
according to the application's configuration (development vs production).

Usage:
    from fastapi import Response
    from app.core.cookie_helpers import set_secure_cookie

    response = Response(...)
    set_secure_cookie(
        response=response,
        key="refresh_token",
        value=refresh_token_value,
        max_age=2592000  # 30 days
    )
"""

from fastapi import Response

from app.core.config import settings


def set_secure_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int | None = None,
    path: str = "/",
) -> None:
    """
    Set a cookie with secure flags based on environment configuration.

    This function sets a cookie with the appropriate security flags:
    - httponly: Prevents JavaScript access (XSS protection)
    - secure: Only send over HTTPS (production only)
    - samesite: CSRF protection
    - domain: Restrict to specific domain (production only)

    Args:
        response: FastAPI Response object
        key: Cookie name
        value: Cookie value
        max_age: Cookie expiration in seconds (None = session cookie)
        path: Cookie path (default: "/")

    Example:
        # Set refresh token cookie
        set_secure_cookie(
            response=response,
            key="refresh_token",
            value=token,
            max_age=30 * 24 * 60 * 60  # 30 days
        )

        # Set session cookie (expires when browser closes)
        set_secure_cookie(
            response=response,
            key="session_id",
            value=session_id
        )
    """
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        path=path,
        httponly=settings.COOKIE_HTTPONLY,  # Prevent JS access
        secure=settings.COOKIE_SECURE,  # HTTPS only (production)
        samesite=settings.COOKIE_SAMESITE,  # CSRF protection
        domain=settings.COOKIE_DOMAIN,  # Restrict to domain (production)
    )


def delete_secure_cookie(
    response: Response,
    key: str,
    path: str = "/",
) -> None:
    """
    Delete a cookie by setting its max_age to 0.

    Args:
        response: FastAPI Response object
        key: Cookie name to delete
        path: Cookie path (default: "/")

    Example:
        # Delete refresh token on logout
        delete_secure_cookie(response, "refresh_token")
    """
    response.delete_cookie(
        key=key,
        path=path,
        domain=settings.COOKIE_DOMAIN,
    )


# Example usage in auth endpoints:
# --------------------------------
#
# @router.post("/login")
# async def login(...) -> Response:
#     # ... authentication logic ...
#
#     # Create response with tokens in body
#     response_data = {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user_schema
#     }
#     response = JSONResponse(content=response_data)
#
#     # Set refresh token in HTTP-only cookie (not accessible via JavaScript)
#     set_secure_cookie(
#         response=response,
#         key="refresh_token",
#         value=refresh_token,
#         max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
#     )
#
#     return response
#
# @router.post("/logout")
# async def logout(...) -> Response:
#     response = JSONResponse(content={"message": "Logged out successfully"})
#
#     # Delete the refresh token cookie
#     delete_secure_cookie(response, "refresh_token")
#
#     return response
#
# @router.post("/refresh")
# async def refresh(request: Request, ...) -> Response:
#     # Get refresh token from HTTP-only cookie
#     refresh_token = request.cookies.get("refresh_token")
#
#     if not refresh_token:
#         raise HTTPException(status_code=401, detail="No refresh token")
#
#     # ... token validation and refresh logic ...
#
#     response_data = {"access_token": new_access_token}
#     response = JSONResponse(content=response_data)
#
#     # Optionally rotate refresh token
#     set_secure_cookie(
#         response=response,
#         key="refresh_token",
#         value=new_refresh_token,
#         max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
#     )
#
#     return response
