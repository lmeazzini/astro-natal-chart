"""
Storage adapters for interpretations.

This package contains concrete implementations of the IInterpretationStorage
interface for various persistence mechanisms (database, cache).
"""

from app.infrastructure.storage.cache_interpretation_storage import (
    CacheInterpretationStorage,
)
from app.infrastructure.storage.database_interpretation_storage import (
    DatabaseInterpretationStorage,
)

__all__ = [
    "DatabaseInterpretationStorage",
    "CacheInterpretationStorage",
]
