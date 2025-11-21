"""
Request context management for distributed tracing and structured logging.

This module provides thread-safe context management using Python's contextvars,
allowing request-scoped data (request_id, user_id, etc.) to be propagated
throughout the application, including async tasks.
"""

import contextvars
from typing import Any
from uuid import uuid4

# Context variable to store request-scoped data
_request_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "request_context", default={}
)


def set_request_context(**kwargs: Any) -> None:
    """
    Set request context variables.

    This updates the current context with new key-value pairs.
    Thread-safe and async-safe due to contextvars.

    Example:
        set_request_context(request_id="abc123", user_id="user-456")
    """
    context = _request_context.get().copy()
    context.update(kwargs)
    _request_context.set(context)


def get_request_context() -> dict[str, Any]:
    """
    Get current request context.

    Returns:
        Dictionary with all context variables (request_id, user_id, etc.)

    Example:
        context = get_request_context()
        request_id = context.get("request_id")
    """
    return _request_context.get()


def clear_request_context() -> None:
    """
    Clear request context.

    Should be called at the end of request processing to avoid
    context leakage between requests.
    """
    _request_context.set({})


def generate_request_id() -> str:
    """
    Generate unique request ID for tracing.

    Returns:
        UUID v4 string

    Example:
        request_id = generate_request_id()
        # "a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c"
    """
    return str(uuid4())


def get_request_id() -> str | None:
    """
    Get current request ID from context.

    Returns:
        Request ID if available, None otherwise
    """
    return get_request_context().get("request_id")


def get_user_id() -> str | None:
    """
    Get current user ID from context.

    Returns:
        User ID if available, None otherwise
    """
    return get_request_context().get("user_id")
