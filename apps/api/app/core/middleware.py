"""
FastAPI middleware for request logging and tracking.
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


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
        request_id = str(uuid.uuid4())

        # Add request_id to request state for access in endpoints
        request.state.request_id = request_id

        # Start timer
        start_time = time.time()

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Log incoming request with context
        with logger.contextualize(request_id=request_id, client_ip=client_ip):
            logger.info(
                "Incoming request",
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params),
            )

            try:
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
