"""
Portuguese (Brazil) translations for lunar and solar phases.
"""

from typing import Any

translations: dict[str, Any] = {
    "lunar_phases": {
        "new_moon": {
            "name": "Lua Nova",
            "keywords": "Começo, Instinto, Impulso, Subjetividade",
            "interpretation": (
                "Nascido na Lua Nova, você é uma pessoa de novos começos e iniciativas. "
                "Seu caminho é instintivo e subjetivo, guiado por impulsos internos. "
                "Você possui uma qualidade pioneira e a capacidade de iniciar projetos "
                "com entusiasmo natural. Sua jornada é sobre descobrir seu próprio caminho "
                "através da experiência direta."
            ),
        },
        "waxing_crescent": {
            "name": "Lua Crescente",
            "keywords": "Expansão, Luta, Determinação, Resistência",
            "interpretation": (
                "Nascido na Lua Crescente, você é uma pessoa voltada para a expansão e o crescimento. "
                "Enfrenta desafios com determinação e busca constantemente superar obstáculos. "
                "Sua energia natural é de luta e construção, sempre empurrando limites. "
                "Você aprende através do esforço e da resistência, desenvolvendo força "
                "ao enfrentar dificuldades."
            ),
        },
        "first_quarter": {
            "name": "Quarto Crescente",
            "keywords": "Ação, Crise, Decisão, Construção",
            "interpretation": (
                "Nascido no Quarto Crescente, você é uma pessoa de ação e decisão. "
                "Frequentemente enfrenta crises que exigem escolhas claras e compromisso. "
                "Sua natureza é construtiva e orientada para resultados concretos. "
                "Você possui a capacidade de agir sob pressão e tomar decisões difíceis "
                "quando necessário, construindo estruturas duradouras."
            ),
        },
        "waxing_gibbous": {
            "name": "Lua Gibosa Crescente",
            "keywords": "Análise, Refinamento, Aperfeiçoamento, Preparação",
            "interpretation": (
                "Nascido na Lua Gibosa Crescente, você é uma pessoa analítica e perfeccionista. "
                "Busca constantemente refinar e melhorar tudo que toca. "
                "Sua energia está focada em preparação e aperfeiçoamento dos detalhes. "
                "Você tem a capacidade de ver o que precisa ser ajustado antes da manifestação "
                "completa, atuando como um artesão cuidadoso."
            ),
        },
        "full_moon": {
            "name": "Lua Cheia",
            "keywords": "Realização, Objetividade, Consciência, Relacionamentos",
            "interpretation": (
                "Nascido na Lua Cheia, você é uma pessoa de realização e objetividade. "
                "Possui forte consciência do outro e dos relacionamentos. "
                "Sua natureza busca equilíbrio entre opostos e manifestação completa. "
                "Você tem a capacidade de ver as coisas claramente e de forma objetiva, "
                "frequentemente atuando como mediador ou trazendo luz para situações."
            ),
        },
        "waning_gibbous": {
            "name": "Lua Gibosa Minguante",
            "keywords": "Distribuição, Compartilhamento, Ensino, Disseminação",
            "interpretation": (
                "Nascido na Lua Gibosa Minguante, você é uma pessoa voltada para compartilhar "
                "e distribuir conhecimento. Seu papel é ensinar e disseminar o que aprendeu. "
                "Possui uma qualidade de mentor natural, buscando passar adiante suas experiências. "
                "Você encontra significado em ajudar outros a compreender e crescer através "
                "do que você já vivenciou."
            ),
        },
        "last_quarter": {
            "name": "Quarto Minguante",
            "keywords": "Transição, Reorientação, Crise de Consciência, Transformação",
            "interpretation": (
                "Nascido no Quarto Minguante, você é uma pessoa de transição e reorientação. "
                "Frequentemente enfrenta crises de consciência que levam a mudanças profundas. "
                "Sua natureza questiona estruturas antigas e busca novos significados. "
                "Você tem a capacidade de desmantelar o que não serve mais e preparar "
                "o terreno para novas formas de ser."
            ),
        },
        "waning_crescent": {
            "name": "Lua Minguante (Balsâmica)",
            "keywords": "Liberação, Encerramento, Profecia, Visão",
            "interpretation": (
                "Nascido na Lua Minguante (Balsâmica), você é uma pessoa de liberação e encerramento. "
                "Possui uma qualidade visionária e profética, conectada com o futuro. "
                "Sua energia está focada em soltar o passado e preparar novos ciclos. "
                "Você tem a capacidade de ver além do momento presente e semear intenções "
                "para o que está por vir, atuando como ponte entre ciclos."
            ),
        },
    },
    "solar_phases": {
        "first": {
            "name": "1ª Fase Solar",
            "temperament": "Sanguíneo",
            "qualities": "Quente e Úmido",
            "signs": ["Áries", "Touro", "Gêmeos"],
            "description": (
                "Nascido na 1ª Fase Solar (temperamento Sanguíneo), você é uma pessoa "
                "naturalmente otimista, sociável e expansiva. Este temperamento quente e úmido "
                "favorece a adaptabilidade, comunicação e o desejo de experiências variadas. "
                "Você tende a ser versátil, curioso e orientado para conexões sociais, "
                "buscando sempre novas possibilidades e mantendo uma perspectiva esperançosa da vida."
            ),
        },
        "second": {
            "name": "2ª Fase Solar",
            "temperament": "Colérico",
            "qualities": "Quente e Seco",
            "signs": ["Câncer", "Leão", "Virgem"],
            "description": (
                "Nascido na 2ª Fase Solar (temperamento Colérico), você é uma pessoa "
                "naturalmente assertiva, ambiciosa e orientada para ação. Este temperamento quente e seco "
                "favorece a liderança, determinação e o desejo de realizar e construir. "
                "Você tende a ser dinâmico, focado e orientado para resultados, "
                "buscando sempre manifestar sua vontade e deixar sua marca no mundo."
            ),
        },
        "third": {
            "name": "3ª Fase Solar",
            "temperament": "Melancólico",
            "qualities": "Frio e Seco",
            "signs": ["Libra", "Escorpião", "Sagitário"],
            "description": (
                "Nascido na 3ª Fase Solar (temperamento Melancólico), você é uma pessoa "
                "naturalmente reflexiva, analítica e orientada para profundidade. Este temperamento frio e seco "
                "favorece a introspecção, o pensamento crítico e o desejo de compreender verdades profundas. "
                "Você tende a ser cuidadoso, meticuloso e orientado para qualidade, "
                "buscando sempre perfeição e significado genuíno em tudo que faz."
            ),
        },
        "fourth": {
            "name": "4ª Fase Solar",
            "temperament": "Fleumático",
            "qualities": "Frio e Úmido",
            "signs": ["Capricórnio", "Aquário", "Peixes"],
            "description": (
                "Nascido na 4ª Fase Solar (temperamento Fleumático), você é uma pessoa "
                "naturalmente calma, receptiva e orientada para harmonia. Este temperamento frio e úmido "
                "favorece a paciência, empatia e o desejo de paz e estabilidade. "
                "Você tende a ser compassivo, adaptável e orientado para o bem-estar coletivo, "
                "buscando sempre equilíbrio e evitando conflitos desnecessários."
            ),
        },
    },
    # Simplified lunar phase names for temperament calculation (4 divisions)
    "lunar_temperament_phases": {
        "1": "Lua Nova",
        "2": "Quarto Crescente",
        "3": "Lua Cheia",
        "4": "Quarto Minguante",
    },
}
