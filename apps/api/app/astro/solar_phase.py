"""
Solar Phase calculation based on Sun sign.

This module calculates the solar phase at birth based on the zodiac sign
where the Sun is positioned. The 12 signs are divided into 4 phases of 3 signs each,
corresponding to the 4 traditional temperaments.
"""

from typing import Any

PHASE_DESCRIPTIONS_EN = {
    1: (
        "Born in the 1st Solar Phase (Sanguine temperament), you are a person "
        "naturally optimistic, sociable, and expansive. This hot and moist temperament "
        "favors adaptability, communication, and the desire for varied experiences. "
        "You tend to be versatile, curious, and oriented toward social connections, "
        "always seeking new possibilities and maintaining a hopeful perspective on life."
    ),
    2: (
        "Born in the 2nd Solar Phase (Choleric temperament), you are a person "
        "naturally assertive, ambitious, and action-oriented. This hot and dry temperament "
        "favors leadership, determination, and the desire to achieve and build. "
        "You tend to be dynamic, focused, and results-oriented, "
        "always seeking to manifest your will and leave your mark on the world."
    ),
    3: (
        "Born in the 3rd Solar Phase (Melancholic temperament), you are a person "
        "naturally reflective, analytical, and oriented toward depth. This cold and dry temperament "
        "favors introspection, critical thinking, and the desire to understand profound truths. "
        "You tend to be careful, meticulous, and quality-oriented, "
        "always seeking perfection and genuine meaning in everything you do."
    ),
    4: (
        "Born in the 4th Solar Phase (Phlegmatic temperament), you are a person "
        "naturally calm, receptive, and oriented toward harmony. This cold and moist temperament "
        "favors patience, empathy, and the desire for peace and stability. "
        "You tend to be compassionate, adaptable, and oriented toward collective well-being, "
        "always seeking balance and avoiding unnecessary conflicts."
    ),
}

PHASE_DESCRIPTIONS_PT = {
    1: (
        "Nascido na 1ª Fase Solar (temperamento Sanguíneo), você é uma pessoa "
        "naturalmente otimista, sociável e expansiva. Este temperamento quente e úmido "
        "favorece a adaptabilidade, comunicação e o desejo de experiências variadas. "
        "Você tende a ser versátil, curioso e orientado para conexões sociais, "
        "buscando sempre novas possibilidades e mantendo uma perspectiva esperançosa da vida."
    ),
    2: (
        "Nascido na 2ª Fase Solar (temperamento Colérico), você é uma pessoa "
        "naturalmente assertiva, ambiciosa e orientada para ação. Este temperamento quente e seco "
        "favorece a liderança, determinação e o desejo de realizar e construir. "
        "Você tende a ser dinâmico, focado e orientado para resultados, "
        "buscando sempre manifestar sua vontade e deixar sua marca no mundo."
    ),
    3: (
        "Nascido na 3ª Fase Solar (temperamento Melancólico), você é uma pessoa "
        "naturalmente reflexiva, analítica e orientada para profundidade. Este temperamento frio e seco "
        "favorece a introspecção, o pensamento crítico e o desejo de compreender verdades profundas. "
        "Você tende a ser cuidadoso, meticuloso e orientado para qualidade, "
        "buscando sempre perfeição e significado genuíno em tudo que faz."
    ),
    4: (
        "Nascido na 4ª Fase Solar (temperamento Fleumático), você é uma pessoa "
        "naturalmente calma, receptiva e orientada para harmonia. Este temperamento frio e úmido "
        "favorece a paciência, empatia e o desejo de paz e estabilidade. "
        "Você tende a ser compassivo, adaptável e orientado para o bem-estar coletivo, "
        "buscando sempre equilíbrio e evitando conflitos desnecessários."
    ),
}

PHASES_DEF: list[dict[str, Any]] = [
    {
        "phase_number": 1,
        "phase_name": "1ª Fase",
        "temperament": "Sanguine",
        "temperament_pt": "Sanguíneo",
        "qualities": "Hot & Moist",
        "qualities_pt": "Quente e Úmido",
        "signs": ["Aries", "Taurus", "Gemini"],
        "signs_pt": ["Áries", "Touro", "Gêmeos"],
        "description": PHASE_DESCRIPTIONS_EN[1],
        "description_pt": PHASE_DESCRIPTIONS_PT[1],
    },
    {
        "phase_number": 2,
        "phase_name": "2ª Fase",
        "temperament": "Choleric",
        "temperament_pt": "Colérico",
        "qualities": "Hot & Dry",
        "qualities_pt": "Quente e Seco",
        "signs": ["Cancer", "Leo", "Virgo"],
        "signs_pt": ["Câncer", "Leão", "Virgem"],
        "description": PHASE_DESCRIPTIONS_EN[2],
        "description_pt": PHASE_DESCRIPTIONS_PT[2],
    },
    {
        "phase_number": 3,
        "phase_name": "3ª Fase",
        "temperament": "Melancholic",
        "temperament_pt": "Melancólico",
        "qualities": "Cold & Dry",
        "qualities_pt": "Frio e Seco",
        "signs": ["Libra", "Scorpio", "Sagittarius"],
        "signs_pt": ["Libra", "Escorpião", "Sagitário"],
        "description": PHASE_DESCRIPTIONS_EN[3],
        "description_pt": PHASE_DESCRIPTIONS_PT[3],
    },
    {
        "phase_number": 4,
        "phase_name": "4ª Fase",
        "temperament": "Phlegmatic",
        "temperament_pt": "Fleumático",
        "qualities": "Cold & Moist",
        "qualities_pt": "Frio e Úmido",
        "signs": ["Capricorn", "Aquarius", "Pisces"],
        "signs_pt": ["Capricórnio", "Aquário", "Peixes"],
        "description": PHASE_DESCRIPTIONS_EN[4],
        "description_pt": PHASE_DESCRIPTIONS_PT[4],
    },
]

# Map sign to phase index for quick lookup
SIGN_TO_PHASE_IDX = {}
for idx, phase in enumerate(PHASES_DEF):
    for sign in phase["signs"]:
        SIGN_TO_PHASE_IDX[sign] = idx


def calculate_solar_phase(sun_sign: str, language: str = "pt-BR") -> dict[str, Any]:
    """
    Calculate the solar phase based on the Sun's zodiac sign.

    The 12 signs are divided into 4 phases:
    - Phase 1 (Signs 1-3): Aries, Taurus, Gemini → Sanguine (Hot & Moist)
    - Phase 2 (Signs 4-6): Cancer, Leo, Virgo → Choleric (Hot & Dry)
    - Phase 3 (Signs 7-9): Libra, Scorpio, Sagittarius → Melancholic (Cold & Dry)
    - Phase 4 (Signs 10-12): Capricorn, Aquarius, Pisces → Phlegmatic (Cold & Moist)

    Args:
        sun_sign: Name of the zodiac sign (e.g., "Aries", "Taurus")
        language: Language for interpretation ('pt-BR' or 'en-US')

    Returns:
        Dictionary containing:
        - phase_number: Number of the phase (1-4)
        - phase_name: Name of the phase in Portuguese
        - temperament: Traditional temperament name
        - temperament_pt: Temperament in Portuguese
        - qualities: Hot/Cold and Dry/Moist qualities
        - qualities_pt: Qualities in Portuguese
        - signs: List of signs in this phase
        - description: Interpretation in english language
        - description_pt: Interpretation in portuguese language
    Example:
        >>> calculate_solar_phase("Aries")
        {
            "phase_number": 1,
            "phase_name": "1ª Fase",
            "temperament": "Sanguine",
            "temperament_pt": "Sanguíneo",
            "qualities": "Hot & Moist",
            "qualities_pt": "Quente e Úmido",
            "signs": ["Aries", "Taurus", "Gemini"],
            "description": "..."
        }
    """
    idx = SIGN_TO_PHASE_IDX.get(sun_sign)
    if idx is None:
        return {
            "phase_number": 0,
            "phase_name": "Desconhecida",
            "temperament": "Unknown",
            "temperament_pt": "Desconhecido",
            "qualities": "Unknown",
            "qualities_pt": "Desconhecido",
            "signs": [],
            "signs_pt": [],
            "description": "Fase solar não encontrada para este signo.",
            "description_pt": "Fase solar não encontrada para este signo.",
        }
    phase = PHASES_DEF[idx]
    description_en = phase["description"]
    description_pt = phase["description_pt"]

    ret = dict(phase)  # shallow copy
    ret["description"] = description_en
    ret["description_pt"] = description_pt
    return ret
