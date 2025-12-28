"""
Portuguese (Brazil) translations for the astrology API.
"""

from typing import Any

from app.translations.pt_BR.astrology import translations as astrology
from app.translations.pt_BR.dignities import translations as dignities
from app.translations.pt_BR.longevity import translations as longevity
from app.translations.pt_BR.mentality import translations as mentality
from app.translations.pt_BR.phases import translations as phases
from app.translations.pt_BR.temperament import translations as temperament

# Merge all translation modules into a single dictionary
translations: dict[str, Any] = {}
translations.update(astrology)
translations.update(phases)
translations.update(temperament)
translations.update(dignities)
translations.update(mentality)
translations.update(longevity)
