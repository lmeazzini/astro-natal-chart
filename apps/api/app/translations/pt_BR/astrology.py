"""
Portuguese (Brazil) translations for core astrological terms.
"""

from typing import Any

translations: dict[str, Any] = {
    "planets": {
        "Sun": "Sol",
        "Moon": "Lua",
        "Mercury": "Mercúrio",
        "Venus": "Vênus",
        "Mars": "Marte",
        "Jupiter": "Júpiter",
        "Saturn": "Saturno",
        "Uranus": "Urano",
        "Neptune": "Netuno",
        "Pluto": "Plutão",
        "North Node": "Nodo Norte",
        "South Node": "Nodo Sul",
    },
    "signs": {
        "Aries": "Áries",
        "Taurus": "Touro",
        "Gemini": "Gêmeos",
        "Cancer": "Câncer",
        "Leo": "Leão",
        "Virgo": "Virgem",
        "Libra": "Libra",
        "Scorpio": "Escorpião",
        "Sagittarius": "Sagitário",
        "Capricorn": "Capricórnio",
        "Aquarius": "Aquário",
        "Pisces": "Peixes",
    },
    "elements": {
        "Fire": "Fogo",
        "Earth": "Terra",
        "Air": "Ar",
        "Water": "Água",
    },
    "qualities": {
        "hot": "Quente",
        "cold": "Frio",
        "wet": "Úmido",
        "dry": "Seco",
    },
    "factors": {
        "ascendant": "Ascendente",
        "ascendant_ruler": "Regente do Ascendente",
        "solar_phase": "Fase Solar",
        "lunar_phase": "Fase Lunar",
        "lord_of_nativity": "Senhor da Natividade",
    },
    "aspects": {
        "conjunction": "Conjunção",
        "opposition": "Oposição",
        "trine": "Trígono",
        "square": "Quadratura",
        "sextile": "Sextil",
        "quincunx": "Quincúncio",
        "semisextile": "Semisextil",
        "semisquare": "Semiquadratura",
        "sesquiquadrate": "Sesquiquadratura",
    },
    "common": {
        "planet_in_sign": "{planet} em {sign}",
    },
}
