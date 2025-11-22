"""
FastAPI middleware for request logging, tracking, and token refresh.
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from jose import JWTError, jwt
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.context import clear_request_context, generate_request_id, set_request_context
from app.core.security import create_access_token

# Token refresh threshold in seconds (5 minutes)
TOKEN_REFRESH_THRESHOLD = 300


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests with request_id for tracking.

    Automatically adds:
    - request_id: unique UUID for each request
    - Request duration
    - HTTP method, path, status code
    - Client IP address
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore[override]
        """Process request and add logging context."""
        # Generate unique request ID
        request_id = generate_request_id()

        # Add request_id to request state for access in endpoints
        request.state.request_id = request_id

        # Start timer
        start_time = time.time()

        # Get client IP (check X-Forwarded-For for proxied requests)
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"

        # Get user agent
        user_agent = request.headers.get("User-Agent", "unknown")

        # Set request context (propagates through all logs and async tasks)
        set_request_context(
            request_id=request_id,
            path=str(request.url.path),
            method=request.method,
            client_ip=client_ip,
            user_agent=user_agent,
            query_params=str(request.query_params),
        )

        try:
            # Log incoming request
            logger.info(
                "Incoming request",
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params),
                user_agent=user_agent,
            )

            # Process request
            response: Response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            # Add request_id to response headers for client-side tracking
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.exception(
                "Request failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration * 1000, 2),
                error=str(exc),
            )

            raise

        finally:
            # Clear context to prevent leakage between requests
            clear_request_context()


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically refresh tokens before expiration.

    If access token has less than 5 minutes remaining, automatically
    generates a new token and returns it in the X-New-Access-Token header.
    The frontend can detect this header and update the stored token.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore[override]
        """Process request and refresh token if needed."""
        # Extract access token from Authorization header
        auth_header = request.headers.get("Authorization")
        new_access_token: str | None = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

            try:
                # Decode token without verification to check expiration
                # (verification happens in the actual endpoint)
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )
                exp = payload.get("exp")
                user_id = payload.get("sub")

                # If token expires in less than 5 minutes, prepare new token
                if exp and user_id and (exp - time.time()) < TOKEN_REFRESH_THRESHOLD:
                    # Generate new access token
                    new_access_token = create_access_token(data={"sub": user_id})
                    logger.debug(
                        "Token near expiration, generating new token",
                        user_id=user_id,
                        expires_in=int(exp - time.time()),
                    )

            except JWTError:
                # Token is invalid or expired, let the endpoint handle it
                pass
            except Exception as e:
                # Log unexpected errors but don't block the request
                logger.warning(f"Token refresh middleware error: {e}")

        # Process request
        response: Response = await call_next(request)

        # Add new token to response header if generated
        if new_access_token:
            response.headers["X-New-Access-Token"] = new_access_token
            # Append to CORS exposed headers (preserve existing headers)
            existing_expose = response.headers.get("Access-Control-Expose-Headers", "")
            new_headers = ["X-New-Access-Token", "X-Request-ID"]
            if existing_expose:
                # Parse existing headers and add new ones
                existing_set = {h.strip() for h in existing_expose.split(",")}
                existing_set.update(new_headers)
                response.headers["Access-Control-Expose-Headers"] = ", ".join(sorted(existing_set))
            else:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(new_headers)

        return response
