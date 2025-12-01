"""
Domain interfaces for the astro natal chart application.

This package contains abstract interfaces (protocols) that define contracts
for infrastructure implementations, following the Dependency Inversion Principle.
"""

from app.domain.interfaces.interpretation_generator import IInterpretationGenerator
from app.domain.interfaces.interpretation_storage import IInterpretationStorage

__all__ = [
    "IInterpretationStorage",
    "IInterpretationGenerator",
]
