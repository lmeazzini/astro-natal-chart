"""
Enums for the application.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""

    GERAL = "geral"  # Default user role
    ADMIN = "admin"  # Administrator with full access

    def __str__(self) -> str:
        return self.value
