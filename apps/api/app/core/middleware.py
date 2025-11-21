"""
FastAPI middleware for request logging and tracking.
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context import clear_request_context, generate_request_id, set_request_context


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
