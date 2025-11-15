"""
Security headers middleware for HTTP security best practices.

This middleware adds essential security headers to all HTTP responses to protect
against common web vulnerabilities like XSS, clickjacking, MIME sniffing, etc.

References:
- OWASP Secure Headers Project: https://owasp.org/www-project-secure-headers/
- Mozilla Web Security Guidelines: https://infosec.mozilla.org/guidelines/web_security
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security-related HTTP headers to all responses.

    Headers added:
    - Strict-Transport-Security (HSTS): Forces HTTPS connections (production only)
    - X-Frame-Options: Prevents clickjacking attacks
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-XSS-Protection: Legacy XSS protection (still useful for older browsers)
    - Content-Security-Policy (CSP): Controls resource loading
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Controls browser features access
    """

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        """Process request and add security headers to response."""
        response = await call_next(request)

        # HSTS - HTTP Strict Transport Security
        # Only enable in production to avoid issues in development
        # Forces browsers to use HTTPS for all future requests for 1 year
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # X-Frame-Options - Prevents clickjacking
        # DENY: Page cannot be displayed in a frame/iframe
        # Alternative: "SAMEORIGIN" to allow same-origin framing
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options - Prevents MIME type sniffing
        # Forces browsers to respect declared content types
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection - Legacy XSS protection
        # Modern browsers use CSP, but this helps older browsers
        # 1; mode=block: Enable XSS filter and block page if attack detected
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content-Security-Policy (CSP) - Controls resource loading
        # Prevents XSS attacks by controlling allowed resource sources
        csp_directives = [
            "default-src 'self'",  # Default: only same origin
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Scripts (unsafe for React)
            "style-src 'self' 'unsafe-inline'",  # Styles (unsafe for Tailwind)
            "img-src 'self' data: https:",  # Images from self, data URIs, any HTTPS
            "font-src 'self' data:",  # Fonts from self and data URIs
            # API connections to OpenAI and geocoding services
            "connect-src 'self' https://api.openai.com https://nominatim.openstreetmap.org",
            "object-src 'none'",  # Disable plugins (Flash, Java)
            "base-uri 'self'",  # Restrict <base> tag URLs
            "form-action 'self'",  # Restrict form submissions
            "frame-ancestors 'none'",  # Same as X-Frame-Options DENY
            "upgrade-insecure-requests",  # Auto-upgrade HTTP to HTTPS
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer-Policy - Controls referrer information sent to other sites
        # strict-origin-when-cross-origin: Send full URL for same-origin,
        # only origin for cross-origin HTTPS, nothing for HTTP
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy (formerly Feature-Policy)
        # Controls which browser features can be used
        # Deny access to sensitive features like geolocation, camera, microphone
        permissions = [
            "geolocation=()",  # No geolocation access
            "microphone=()",  # No microphone access
            "camera=()",  # No camera access
            "payment=()",  # No payment API
            "usb=()",  # No USB access
            "magnetometer=()",  # No magnetometer
            "gyroscope=()",  # No gyroscope
            "accelerometer=()",  # No accelerometer
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        return response
