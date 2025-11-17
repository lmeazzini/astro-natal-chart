"""
Lunar Phase calculation and interpretations.

This module calculates the Moon phase at birth based on the angle
between the Sun and Moon, following the 8-phase lunation cycle.
"""

import math
from typing import Any


def calculate_lunar_phase(sun_longitude: float, moon_longitude: float) -> dict[str, Any]:
    """
    Calculate the lunar phase at birth.

    The lunar phase is determined by the angle between the Sun and Moon.
    Formula: (Moon longitude - Sun longitude) % 360

    Args:
        sun_longitude: Sun's ecliptic longitude in degrees (0-360)
        moon_longitude: Moon's ecliptic longitude in degrees (0-360)

    Returns:
        Dictionary containing:
        - phase_name: English name of the phase
        - phase_name_pt: Portuguese name of the phase
        - angle: Exact angle between Moon and Sun (0-360)
        - illumination_percentage: Approximate illumination (0-100)
        - emoji: Unicode emoji representing the phase
        - keywords: Key characteristics of the phase
        - interpretation: Detailed interpretation in Portuguese
    """
    # Calculate angle (Moon - Sun), normalized to 0-360
    angle = (moon_longitude - sun_longitude) % 360

    # Determine phase based on angle
    if 0 <= angle < 45:
        phase_name = "New Moon"
        phase_name_pt = "Lua Nova"
        emoji = "🌑"
        keywords = "Início, Instinto, Impulso, Subjetividade"
        interpretation = (
            "Nascido na Lua Nova, você é uma pessoa de novos começos e iniciativas. "
            "Seu caminho é instintivo e subjetivo, guiado por impulsos internos. "
            "Você possui uma qualidade pioneira e a capacidade de iniciar projetos "
            "com entusiasmo natural. Sua jornada é sobre descobrir seu próprio caminho "
            "através da experiência direta."
        )
    elif 45 <= angle < 90:
        phase_name = "Waxing Crescent"
        phase_name_pt = "Lua Crescente"
        emoji = "🌒"
        keywords = "Expansão, Luta, Determinação, Resistência"
        interpretation = (
            "Nascido na Lua Crescente, você é uma pessoa voltada para a expansão e o crescimento. "
            "Enfrenta desafios com determinação e busca constantemente superar obstáculos. "
            "Sua energia natural é de luta e construção, sempre empurrando limites. "
            "Você aprende através do esforço e da resistência, desenvolvendo força "
            "ao enfrentar dificuldades."
        )
    elif 90 <= angle < 135:
        phase_name = "First Quarter"
        phase_name_pt = "Quarto Crescente"
        emoji = "🌓"
        keywords = "Ação, Crise, Decisão, Construção"
        interpretation = (
            "Nascido no Quarto Crescente, você é uma pessoa de ação e decisão. "
            "Frequentemente enfrenta crises que exigem escolhas claras e compromisso. "
            "Sua natureza é construtiva e orientada para resultados concretos. "
            "Você possui a capacidade de agir sob pressão e tomar decisões difíceis "
            "quando necessário, construindo estruturas duradouras."
        )
    elif 135 <= angle < 180:
        phase_name = "Waxing Gibbous"
        phase_name_pt = "Lua Gibosa Crescente"
        emoji = "🌔"
        keywords = "Análise, Refinamento, Aperfeiçoamento, Preparação"
        interpretation = (
            "Nascido na Lua Gibosa Crescente, você é uma pessoa analítica e perfeccionista. "
            "Busca constantemente refinar e melhorar tudo que toca. "
            "Sua energia está focada em preparação e aperfeiçoamento dos detalhes. "
            "Você tem a capacidade de ver o que precisa ser ajustado antes da manifestação "
            "completa, atuando como um artesão cuidadoso."
        )
    elif 180 <= angle < 225:
        phase_name = "Full Moon"
        phase_name_pt = "Lua Cheia"
        emoji = "🌕"
        keywords = "Realização, Objetividade, Consciência, Relacionamentos"
        interpretation = (
            "Nascido na Lua Cheia, você é uma pessoa de realização e objetividade. "
            "Possui forte consciência do outro e dos relacionamentos. "
            "Sua natureza busca equilíbrio entre opostos e manifestação completa. "
            "Você tem a capacidade de ver as coisas claramente e de forma objetiva, "
            "frequentemente atuando como mediador ou trazendo luz para situações."
        )
    elif 225 <= angle < 270:
        phase_name = "Waning Gibbous"
        phase_name_pt = "Lua Gibosa Minguante"
        emoji = "🌖"
        keywords = "Distribuição, Compartilhamento, Ensino, Disseminação"
        interpretation = (
            "Nascido na Lua Gibosa Minguante, você é uma pessoa voltada para compartilhar "
            "e distribuir conhecimento. Seu papel é ensinar e disseminar o que aprendeu. "
            "Possui uma qualidade de mentor natural, buscando passar adiante suas experiências. "
            "Você encontra significado em ajudar outros a compreender e crescer através "
            "do que você já vivenciou."
        )
    elif 270 <= angle < 315:
        phase_name = "Last Quarter"
        phase_name_pt = "Quarto Minguante"
        emoji = "🌗"
        keywords = "Transição, Reorientação, Crise de Consciência, Transformação"
        interpretation = (
            "Nascido no Quarto Minguante, você é uma pessoa de transição e reorientação. "
            "Frequentemente enfrenta crises de consciência que levam a mudanças profundas. "
            "Sua natureza questiona estruturas antigas e busca novos significados. "
            "Você tem a capacidade de desmantelar o que não serve mais e preparar "
            "o terreno para novas formas de ser."
        )
    else:  # 315 <= angle < 360
        phase_name = "Waning Crescent"
        phase_name_pt = "Lua Minguante (Balsâmica)"
        emoji = "🌘"
        keywords = "Liberação, Encerramento, Profecia, Visão"
        interpretation = (
            "Nascido na Lua Minguante (Balsâmica), você é uma pessoa de liberação e encerramento. "
            "Possui uma qualidade visionária e profética, conectada com o futuro. "
            "Sua energia está focada em soltar o passado e preparar novos ciclos. "
            "Você tem a capacidade de ver além do momento presente e semear intenções "
            "para o que está por vir, atuando como ponte entre ciclos."
        )

    # Calculate approximate illumination percentage
    # Formula: (1 - cos(angle)) / 2 * 100
    # This gives 0% at New Moon (0°) and 100% at Full Moon (180°)
    illumination = (1 - math.cos(math.radians(angle))) / 2 * 100

    return {
        "phase_name": phase_name,
        "phase_name_pt": phase_name_pt,
        "angle": round(angle, 2),
        "illumination_percentage": round(illumination, 1),
        "emoji": emoji,
        "keywords": keywords,
        "interpretation": interpretation,
    }
