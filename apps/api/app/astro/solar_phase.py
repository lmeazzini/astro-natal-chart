"""
Solar Phase calculation based on Sun sign.

This module calculates the solar phase at birth based on the zodiac sign
where the Sun is positioned. The 12 signs are divided into 4 phases of 3 signs each,
corresponding to the 4 traditional temperaments.
"""

from typing import Any


def calculate_solar_phase(sun_sign: str) -> dict[str, Any]:
    """
    Calculate the solar phase based on the Sun's zodiac sign.

    The 12 signs are divided into 4 phases:
    - Phase 1 (Signs 1-3): Aries, Taurus, Gemini → Sanguine (Hot & Moist)
    - Phase 2 (Signs 4-6): Cancer, Leo, Virgo → Choleric (Hot & Dry)
    - Phase 3 (Signs 7-9): Libra, Scorpio, Sagittarius → Melancholic (Cold & Dry)
    - Phase 4 (Signs 10-12): Capricorn, Aquarius, Pisces → Phlegmatic (Cold & Moist)

    Args:
        sun_sign: Name of the zodiac sign (e.g., "Aries", "Taurus")

    Returns:
        Dictionary containing:
        - phase_number: Number of the phase (1-4)
        - phase_name: Name of the phase in Portuguese
        - temperament: Traditional temperament name
        - temperament_pt: Temperament in Portuguese
        - qualities: Hot/Cold and Dry/Moist qualities
        - qualities_pt: Qualities in Portuguese
        - signs: List of signs in this phase
        - description: Interpretation in Portuguese

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
    # Phase definitions
    phases = {
        # Phase 1: Signs 1-3 (Aries, Taurus, Gemini)
        # Sanguine - Hot & Moist
        "Aries": {
            "phase_number": 1,
            "phase_name": "1ª Fase",
            "temperament": "Sanguine",
            "temperament_pt": "Sanguíneo",
            "qualities": "Hot & Moist",
            "qualities_pt": "Quente e Úmido",
            "signs": ["Aries", "Taurus", "Gemini"],
            "signs_pt": ["Áries", "Touro", "Gêmeos"],
            "description": (
                "Nascido na 1ª Fase Solar (temperamento Sanguíneo), você é uma pessoa "
                "naturalmente otimista, sociável e expansiva. Este temperamento quente e úmido "
                "favorece a adaptabilidade, comunicação e o desejo de experiências variadas. "
                "Você tende a ser versátil, curioso e orientado para conexões sociais, "
                "buscando sempre novas possibilidades e mantendo uma perspectiva esperançosa da vida."
            ),
        },
        "Taurus": {
            "phase_number": 1,
            "phase_name": "1ª Fase",
            "temperament": "Sanguine",
            "temperament_pt": "Sanguíneo",
            "qualities": "Hot & Moist",
            "qualities_pt": "Quente e Úmido",
            "signs": ["Aries", "Taurus", "Gemini"],
            "signs_pt": ["Áries", "Touro", "Gêmeos"],
            "description": (
                "Nascido na 1ª Fase Solar (temperamento Sanguíneo), você é uma pessoa "
                "naturalmente otimista, sociável e expansiva. Este temperamento quente e úmido "
                "favorece a adaptabilidade, comunicação e o desejo de experiências variadas. "
                "Você tende a ser versátil, curioso e orientado para conexões sociais, "
                "buscando sempre novas possibilidades e mantendo uma perspectiva esperançosa da vida."
            ),
        },
        "Gemini": {
            "phase_number": 1,
            "phase_name": "1ª Fase",
            "temperament": "Sanguine",
            "temperament_pt": "Sanguíneo",
            "qualities": "Hot & Moist",
            "qualities_pt": "Quente e Úmido",
            "signs": ["Aries", "Taurus", "Gemini"],
            "signs_pt": ["Áries", "Touro", "Gêmeos"],
            "description": (
                "Nascido na 1ª Fase Solar (temperamento Sanguíneo), você é uma pessoa "
                "naturalmente otimista, sociável e expansiva. Este temperamento quente e úmido "
                "favorece a adaptabilidade, comunicação e o desejo de experiências variadas. "
                "Você tende a ser versátil, curioso e orientado para conexões sociais, "
                "buscando sempre novas possibilidades e mantendo uma perspectiva esperançosa da vida."
            ),
        },
        # Phase 2: Signs 4-6 (Cancer, Leo, Virgo)
        # Choleric - Hot & Dry
        "Cancer": {
            "phase_number": 2,
            "phase_name": "2ª Fase",
            "temperament": "Choleric",
            "temperament_pt": "Colérico",
            "qualities": "Hot & Dry",
            "qualities_pt": "Quente e Seco",
            "signs": ["Cancer", "Leo", "Virgo"],
            "signs_pt": ["Câncer", "Leão", "Virgem"],
            "description": (
                "Nascido na 2ª Fase Solar (temperamento Colérico), você é uma pessoa "
                "naturalmente assertiva, ambiciosa e orientada para ação. Este temperamento quente e seco "
                "favorece a liderança, determinação e o desejo de realizar e construir. "
                "Você tende a ser dinâmico, focado e orientado para resultados, "
                "buscando sempre manifestar sua vontade e deixar sua marca no mundo."
            ),
        },
        "Leo": {
            "phase_number": 2,
            "phase_name": "2ª Fase",
            "temperament": "Choleric",
            "temperament_pt": "Colérico",
            "qualities": "Hot & Dry",
            "qualities_pt": "Quente e Seco",
            "signs": ["Cancer", "Leo", "Virgo"],
            "signs_pt": ["Câncer", "Leão", "Virgem"],
            "description": (
                "Nascido na 2ª Fase Solar (temperamento Colérico), você é uma pessoa "
                "naturalmente assertiva, ambiciosa e orientada para ação. Este temperamento quente e seco "
                "favorece a liderança, determinação e o desejo de realizar e construir. "
                "Você tende a ser dinâmico, focado e orientado para resultados, "
                "buscando sempre manifestar sua vontade e deixar sua marca no mundo."
            ),
        },
        "Virgo": {
            "phase_number": 2,
            "phase_name": "2ª Fase",
            "temperament": "Choleric",
            "temperament_pt": "Colérico",
            "qualities": "Hot & Dry",
            "qualities_pt": "Quente e Seco",
            "signs": ["Cancer", "Leo", "Virgo"],
            "signs_pt": ["Câncer", "Leão", "Virgem"],
            "description": (
                "Nascido na 2ª Fase Solar (temperamento Colérico), você é uma pessoa "
                "naturalmente assertiva, ambiciosa e orientada para ação. Este temperamento quente e seco "
                "favorece a liderança, determinação e o desejo de realizar e construir. "
                "Você tende a ser dinâmico, focado e orientado para resultados, "
                "buscando sempre manifestar sua vontade e deixar sua marca no mundo."
            ),
        },
        # Phase 3: Signs 7-9 (Libra, Scorpio, Sagittarius)
        # Melancholic - Cold & Dry
        "Libra": {
            "phase_number": 3,
            "phase_name": "3ª Fase",
            "temperament": "Melancholic",
            "temperament_pt": "Melancólico",
            "qualities": "Cold & Dry",
            "qualities_pt": "Frio e Seco",
            "signs": ["Libra", "Scorpio", "Sagittarius"],
            "signs_pt": ["Libra", "Escorpião", "Sagitário"],
            "description": (
                "Nascido na 3ª Fase Solar (temperamento Melancólico), você é uma pessoa "
                "naturalmente reflexiva, analítica e orientada para profundidade. Este temperamento frio e seco "
                "favorece a introspecção, o pensamento crítico e o desejo de compreender verdades profundas. "
                "Você tende a ser cuidadoso, meticuloso e orientado para qualidade, "
                "buscando sempre perfeição e significado genuíno em tudo que faz."
            ),
        },
        "Scorpio": {
            "phase_number": 3,
            "phase_name": "3ª Fase",
            "temperament": "Melancholic",
            "temperament_pt": "Melancólico",
            "qualities": "Cold & Dry",
            "qualities_pt": "Frio e Seco",
            "signs": ["Libra", "Scorpio", "Sagittarius"],
            "signs_pt": ["Libra", "Escorpião", "Sagitário"],
            "description": (
                "Nascido na 3ª Fase Solar (temperamento Melancólico), você é uma pessoa "
                "naturalmente reflexiva, analítica e orientada para profundidade. Este temperamento frio e seco "
                "favorece a introspecção, o pensamento crítico e o desejo de compreender verdades profundas. "
                "Você tende a ser cuidadoso, meticuloso e orientado para qualidade, "
                "buscando sempre perfeição e significado genuíno em tudo que faz."
            ),
        },
        "Sagittarius": {
            "phase_number": 3,
            "phase_name": "3ª Fase",
            "temperament": "Melancholic",
            "temperament_pt": "Melancólico",
            "qualities": "Cold & Dry",
            "qualities_pt": "Frio e Seco",
            "signs": ["Libra", "Scorpio", "Sagittarius"],
            "signs_pt": ["Libra", "Escorpião", "Sagitário"],
            "description": (
                "Nascido na 3ª Fase Solar (temperamento Melancólico), você é uma pessoa "
                "naturalmente reflexiva, analítica e orientada para profundidade. Este temperamento frio e seco "
                "favorece a introspecção, o pensamento crítico e o desejo de compreender verdades profundas. "
                "Você tende a ser cuidadoso, meticuloso e orientado para qualidade, "
                "buscando sempre perfeição e significado genuíno em tudo que faz."
            ),
        },
        # Phase 4: Signs 10-12 (Capricorn, Aquarius, Pisces)
        # Phlegmatic - Cold & Moist
        "Capricorn": {
            "phase_number": 4,
            "phase_name": "4ª Fase",
            "temperament": "Phlegmatic",
            "temperament_pt": "Fleumático",
            "qualities": "Cold & Moist",
            "qualities_pt": "Frio e Úmido",
            "signs": ["Capricorn", "Aquarius", "Pisces"],
            "signs_pt": ["Capricórnio", "Aquário", "Peixes"],
            "description": (
                "Nascido na 4ª Fase Solar (temperamento Fleumático), você é uma pessoa "
                "naturalmente calma, receptiva e orientada para harmonia. Este temperamento frio e úmido "
                "favorece a paciência, empatia e o desejo de paz e estabilidade. "
                "Você tende a ser compassivo, adaptável e orientado para o bem-estar coletivo, "
                "buscando sempre equilíbrio e evitando conflitos desnecessários."
            ),
        },
        "Aquarius": {
            "phase_number": 4,
            "phase_name": "4ª Fase",
            "temperament": "Phlegmatic",
            "temperament_pt": "Fleumático",
            "qualities": "Cold & Moist",
            "qualities_pt": "Frio e Úmido",
            "signs": ["Capricorn", "Aquarius", "Pisces"],
            "signs_pt": ["Capricórnio", "Aquário", "Peixes"],
            "description": (
                "Nascido na 4ª Fase Solar (temperamento Fleumático), você é uma pessoa "
                "naturalmente calma, receptiva e orientada para harmonia. Este temperamento frio e úmido "
                "favorece a paciência, empatia e o desejo de paz e estabilidade. "
                "Você tende a ser compassivo, adaptável e orientado para o bem-estar coletivo, "
                "buscando sempre equilíbrio e evitando conflitos desnecessários."
            ),
        },
        "Pisces": {
            "phase_number": 4,
            "phase_name": "4ª Fase",
            "temperament": "Phlegmatic",
            "temperament_pt": "Fleumático",
            "qualities": "Cold & Moist",
            "qualities_pt": "Frio e Úmido",
            "signs": ["Capricorn", "Aquarius", "Pisces"],
            "signs_pt": ["Capricórnio", "Aquário", "Peixes"],
            "description": (
                "Nascido na 4ª Fase Solar (temperamento Fleumático), você é uma pessoa "
                "naturalmente calma, receptiva e orientada para harmonia. Este temperamento frio e úmido "
                "favorece a paciência, empatia e o desejo de paz e estabilidade. "
                "Você tende a ser compassivo, adaptável e orientado para o bem-estar coletivo, "
                "buscando sempre equilíbrio e evitando conflitos desnecessários."
            ),
        },
    }

    # Get phase data for the sun sign
    phase_data = phases.get(sun_sign)

    if not phase_data:
        # Default fallback (should not happen with valid zodiac signs)
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
        }

    return phase_data
