"""
Locale middleware for extracting and setting the request locale.

Extracts locale from:
1. Accept-Language header
2. User's stored locale preference (if authenticated)
3. Falls back to DEFAULT_LOCALE
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.context import set_locale

# Supported locales
SUPPORTED_LOCALES = {"pt-BR", "en-US", "pt", "en"}


def parse_accept_language(header: str | None) -> str | None:
    """
    Parse the Accept-Language header and return the best matching locale.

    Args:
        header: The Accept-Language header value

    Returns:
        The best matching supported locale, or None if no match
    """
    if not header:
        return None

    # Parse header like "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    locales_with_quality: list[tuple[str, float]] = []

    for part in header.split(","):
        part = part.strip()
        if not part:
            continue

        if ";" in part:
            locale, quality_str = part.split(";", 1)
            locale = locale.strip()
            # Parse quality value (e.g., "q=0.9")
            try:
                q_value = float(quality_str.strip().replace("q=", ""))
            except ValueError:
                q_value = 1.0
        else:
            locale = part
            q_value = 1.0

        locales_with_quality.append((locale, q_value))

    # Sort by quality (descending)
    locales_with_quality.sort(key=lambda x: x[1], reverse=True)

    # Find the first supported locale
    for locale, _ in locales_with_quality:
        normalized = normalize_locale(locale)
        if normalized in {"pt-BR", "en-US"}:
            return normalized

    return None


def normalize_locale(locale: str) -> str:
    """
    Normalize a locale string to our supported format.

    Args:
        locale: The locale string to normalize

    Returns:
        Normalized locale string (pt-BR or en-US)
    """
    locale = locale.strip().lower()

    # Map common variants
    if locale.startswith("pt"):
        return "pt-BR"
    if locale.startswith("en"):
        return "en-US"

    # Default to Portuguese
    return settings.DEFAULT_LOCALE


class LocaleMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts the locale from the request and sets it in the context.

    The locale is determined by:
    1. Accept-Language header (if provided)
    2. Falls back to DEFAULT_LOCALE

    Note: User-specific locale from database should be applied in the endpoint
    after authentication, as the middleware runs before auth.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request and set the locale in context."""
        # Extract locale from Accept-Language header
        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language)

        # Use default if no match found
        if locale is None:
            locale = settings.DEFAULT_LOCALE

        # Set locale in context (will be available throughout the request)
        set_locale(locale)

        # Continue processing the request
        response = await call_next(request)

        # Add Content-Language header to response
        response.headers["Content-Language"] = locale

        return response
