"""
Domain layer for the astro natal chart application.

This layer contains core business entities, value objects, and interfaces
that define the domain model independent of infrastructure concerns.
"""

from app.domain.interpretation import InterpretationMetadata, InterpretationResult

__all__ = [
    "InterpretationResult",
    "InterpretationMetadata",
]
