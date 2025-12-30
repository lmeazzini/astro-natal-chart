"""
English (US) translations for the astrology API.
"""

from typing import Any

from app.translations.en_US.astrology import translations as astrology
from app.translations.en_US.dignities import translations as dignities
from app.translations.en_US.longevity import translations as longevity
from app.translations.en_US.mentality import translations as mentality
from app.translations.en_US.phases import translations as phases
from app.translations.en_US.prenatal_syzygy import translations as prenatal_syzygy
from app.translations.en_US.saturn_return import translations as saturn_return
from app.translations.en_US.temperament import translations as temperament

# Merge all translation modules into a single dictionary
translations: dict[str, Any] = {}
translations.update(astrology)
translations.update(phases)
translations.update(temperament)
translations.update(dignities)
translations.update(mentality)
translations.update(longevity)
translations.update(prenatal_syzygy)
translations.update(saturn_return)
