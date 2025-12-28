"""
Traditional astrology calculation modules.

This package contains modules for traditional astrology calculations including:
- Essential dignities (rulership, exaltation, triplicity, term, face)
- Lunar phase calculations
- Solar phase calculations
- Temperament analysis
- Hyleg (Giver of Life) determination
- Alcochoden (Giver of Years) calculation
- Combined longevity analysis
"""

from app.astro.alcochoden import calculate_alcochoden
from app.astro.dignities import calculate_essential_dignities
from app.astro.hyleg import calculate_hyleg
from app.astro.longevity import calculate_longevity_analysis
from app.astro.lunar_phase import calculate_lunar_phase
from app.astro.solar_phase import calculate_solar_phase
from app.astro.temperament import calculate_temperament

__all__ = [
    "calculate_essential_dignities",
    "calculate_lunar_phase",
    "calculate_solar_phase",
    "calculate_temperament",
    "calculate_hyleg",
    "calculate_alcochoden",
    "calculate_longevity_analysis",
]
