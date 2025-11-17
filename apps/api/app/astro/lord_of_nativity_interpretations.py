"""
Lord of Nativity interpretations in Portuguese.

The Lord of Nativity represents the dominant life force and vital energy
in the natal chart according to traditional astrology. It is the planet
with the highest essential dignity score.
"""

from typing import Any

# Interpretations for each planet as Lord of Nativity
LORD_INTERPRETATIONS = {
    "Sun": {
        "title": "Sol como Senhor da Natividade",
        "symbol": "☉",
        "essence": "Identidade, Vitalidade e Propósito",
        "description": (
            "Com o Sol como Senhor da Natividade, sua essência vital está fortemente conectada "
            "à sua identidade individual e ao propósito de vida. Você possui uma natureza solar "
            "marcante, com tendência natural à liderança, criatividade e autenticidade. "
            "Sua força vital se manifesta através da autoexpressão e do brilho pessoal."
        ),
        "strengths": [
            "Forte senso de identidade e propósito",
            "Capacidade natural de liderança",
            "Vitalidade e energia radiante",
            "Criatividade e autoexpressão",
            "Confiança e dignidade pessoal",
        ],
        "life_path": (
            "Seu caminho de vida envolve desenvolver e expressar sua individualidade única, "
            "assumir papéis de destaque e liderança, e irradiar sua luz criativa no mundo. "
            "O reconhecimento e a autorrealização são temas centrais em sua jornada."
        ),
        "advice": (
            "Cultive sua autenticidade e não tenha medo de brilhar. Desenvolva sua criatividade "
            "e aceite posições de liderança quando apropriado. Equilibre o orgulho saudável com "
            "humildade genuína. Lembre-se: seu propósito é iluminar e inspirar os outros."
        ),
    },
    "Moon": {
        "title": "Lua como Senhor da Natividade",
        "symbol": "☽",
        "essence": "Emoção, Nutrição e Intuição",
        "description": (
            "Com a Lua como Senhor da Natividade, sua essência vital está profundamente conectada "
            "ao mundo emocional, às necessidades de segurança e ao cuidado. Você possui uma natureza "
            "lunar marcante, com forte intuição, sensibilidade e capacidade de nutrir. "
            "Sua força vital se manifesta através da conexão emocional e do acolhimento."
        ),
        "strengths": [
            "Inteligência emocional desenvolvida",
            "Forte intuição e sensibilidade",
            "Capacidade natural de cuidar e nutrir",
            "Adaptabilidade e receptividade",
            "Conexão profunda com o inconsciente",
        ],
        "life_path": (
            "Seu caminho de vida envolve honrar e integrar suas emoções, criar segurança emocional "
            "para si e para outros, e desenvolver sua intuição natural. A família, o lar e as "
            "conexões emocionais profundas são temas centrais em sua jornada."
        ),
        "advice": (
            "Confie em sua intuição e honre suas necessidades emocionais. Crie espaços seguros "
            "para você e outros. Desenvolva sua sensibilidade como força, não fraqueza. "
            "Lembre-se: seu propósito é nutrir, acolher e refletir a luz emocional do mundo."
        ),
    },
    "Mercury": {
        "title": "Mercúrio como Senhor da Natividade",
        "symbol": "☿",
        "essence": "Comunicação, Intelecto e Conexão",
        "description": (
            "Com Mercúrio como Senhor da Natividade, sua essência vital está intrinsecamente ligada "
            "à comunicação, ao aprendizado e às conexões mentais. Você possui uma natureza mercurial "
            "marcante, com agilidade mental, curiosidade insaciável e habilidade para mediar ideias. "
            "Sua força vital se manifesta através da palavra, do pensamento e da troca de informações."
        ),
        "strengths": [
            "Inteligência ágil e versátil",
            "Excelentes habilidades de comunicação",
            "Curiosidade intelectual constante",
            "Capacidade de aprender rapidamente",
            "Talento para conectar pessoas e ideias",
        ],
        "life_path": (
            "Seu caminho de vida envolve desenvolver suas habilidades comunicativas, mediar "
            "conhecimentos, e criar pontes entre diferentes mundos e perspectivas. O aprendizado "
            "contínuo, o ensino e a troca de ideias são temas centrais em sua jornada."
        ),
        "advice": (
            "Cultive sua curiosidade e nunca pare de aprender. Use suas palavras com sabedoria "
            "e propósito. Desenvolva tanto a profundidade quanto a amplitude de conhecimento. "
            "Lembre-se: seu propósito é comunicar, conectar e transmitir sabedoria."
        ),
    },
    "Venus": {
        "title": "Vênus como Senhor da Natividade",
        "symbol": "♀",
        "essence": "Amor, Beleza e Harmonia",
        "description": (
            "Com Vênus como Senhor da Natividade, sua essência vital está profundamente conectada "
            "ao amor, à beleza e à busca por harmonia. Você possui uma natureza venusiana marcante, "
            "com apreciação pela estética, talento para relacionamentos e desejo natural de equilíbrio. "
            "Sua força vital se manifesta através da criação de beleza e conexões harmoniosas."
        ),
        "strengths": [
            "Capacidade natural para relacionamentos",
            "Apreciação refinada pela beleza",
            "Talento artístico e criativo",
            "Diplomacia e habilidades sociais",
            "Busca por harmonia e equilíbrio",
        ],
        "life_path": (
            "Seu caminho de vida envolve cultivar relacionamentos significativos, criar beleza "
            "no mundo e promover harmonia em todas as áreas. O amor, a arte e a diplomacia "
            "são temas centrais em sua jornada."
        ),
        "advice": (
            "Honre sua necessidade de beleza e harmonia, mas não evite conflitos necessários. "
            "Desenvolva seus talentos artísticos e relacionais. Cultive o amor próprio antes "
            "de buscar validação externa. Lembre-se: seu propósito é harmonizar, embelezar e amar."
        ),
    },
    "Mars": {
        "title": "Marte como Senhor da Natividade",
        "symbol": "♂",
        "essence": "Ação, Coragem e Vontade",
        "description": (
            "Com Marte como Senhor da Natividade, sua essência vital está intrinsecamente ligada "
            "à ação, à coragem e à manifestação da vontade. Você possui uma natureza marciana "
            "marcante, com energia dinâmica, espírito guerreiro e capacidade de iniciar e conquistar. "
            "Sua força vital se manifesta através da ação decisiva e da determinação inabalável."
        ),
        "strengths": [
            "Coragem e determinação naturais",
            "Energia e dinamismo abundantes",
            "Capacidade de ação e iniciativa",
            "Competitividade saudável",
            "Força de vontade desenvolvida",
        ],
        "life_path": (
            "Seu caminho de vida envolve desenvolver sua coragem, tomar iniciativa em situações "
            "desafiadoras e lutar por suas convicções. A ação, a competição saudável e a defesa "
            "de causas importantes são temas centrais em sua jornada."
        ),
        "advice": (
            "Canalize sua energia marciana de forma construtiva. Desenvolva a coragem, mas "
            "tempere com sabedoria. Aprenda quando lutar e quando recuar estrategicamente. "
            "Lembre-se: seu propósito é agir, conquistar e defender o que é justo."
        ),
    },
    "Jupiter": {
        "title": "Júpiter como Senhor da Natividade",
        "symbol": "♃",
        "essence": "Expansão, Sabedoria e Abundância",
        "description": (
            "Com Júpiter como Senhor da Natividade, sua essência vital está profundamente conectada "
            "à expansão, ao crescimento e à busca por significado. Você possui uma natureza jupiteriana "
            "marcante, com otimismo natural, visão ampla e desejo de compreender verdades maiores. "
            "Sua força vital se manifesta através da generosidade, sabedoria e fé na vida."
        ),
        "strengths": [
            "Otimismo e fé natural",
            "Visão ampla e perspectiva filosófica",
            "Generosidade e magnanimidade",
            "Capacidade de ensinar e inspirar",
            "Atração por crescimento e expansão",
        ],
        "life_path": (
            "Seu caminho de vida envolve expandir horizontes, buscar sabedoria e significado, "
            "e compartilhar abundância com outros. A educação superior, viagens, filosofia "
            "e o ensino são temas centrais em sua jornada."
        ),
        "advice": (
            "Cultive seu otimismo, mas mantenha os pés no chão. Busque sabedoria através "
            "de experiências e estudos. Seja generoso, mas estabeleça limites saudáveis. "
            "Lembre-se: seu propósito é expandir, ensinar e trazer significado ao mundo."
        ),
    },
    "Saturn": {
        "title": "Saturno como Senhor da Natividade",
        "symbol": "♄",
        "essence": "Estrutura, Disciplina e Maestria",
        "description": (
            "Com Saturno como Senhor da Natividade, sua essência vital está intrinsecamente ligada "
            "à estrutura, à responsabilidade e ao domínio através do tempo. Você possui uma natureza "
            "saturnina marcante, com maturidade natural, disciplina e capacidade de construir legados "
            "duradouros. Sua força vital se manifesta através da persistência, sabedoria e maestria."
        ),
        "strengths": [
            "Disciplina e autocontrole naturais",
            "Maturidade e sabedoria além da idade",
            "Capacidade de trabalho árduo e persistente",
            "Senso de responsabilidade desenvolvido",
            "Habilidade para construir estruturas duradouras",
        ],
        "life_path": (
            "Seu caminho de vida envolve desenvolver maestria através da disciplina, assumir "
            "responsabilidades importantes e construir algo duradouro. A paciência, o trabalho "
            "árduo e a conquista de autoridade legítima são temas centrais em sua jornada."
        ),
        "advice": (
            "Honre sua necessidade de estrutura e propósito de longo prazo. Desenvolva paciência "
            "com os processos da vida. Equilibre responsabilidade com autocuidado. Confie que "
            "seus esforços persistentes trarão recompensas com o tempo. Lembre-se: seu propósito "
            "é construir, estruturar e deixar um legado sólido."
        ),
    },
}


def get_lord_interpretation(planet: str) -> dict[str, Any]:
    """
    Get the interpretation for a planet as Lord of Nativity.

    Args:
        planet: Planet name (e.g., "Sun", "Moon", "Mars")

    Returns:
        Dictionary containing interpretation data for the planet

    Example:
        >>> get_lord_interpretation("Sun")
        {
            "title": "Sol como Senhor da Natividade",
            "symbol": "☉",
            "essence": "Identidade, Vitalidade e Propósito",
            "description": "...",
            "strengths": [...],
            "life_path": "...",
            "advice": "..."
        }
    """
    interpretation = LORD_INTERPRETATIONS.get(planet)

    if not interpretation:
        # Fallback for non-classical planets (should not happen)
        return {
            "title": f"{planet} como Senhor da Natividade",
            "symbol": "★",
            "essence": "Força Vital Dominante",
            "description": (
                f"{planet} possui a maior dignidade essencial em seu mapa natal, "
                "representando a força vital dominante que guia sua vida."
            ),
            "strengths": ["Força vital única", "Energia planetária marcante"],
            "life_path": "Seu caminho envolve expressar as qualidades desta energia planetária.",
            "advice": "Desenvolva as qualidades positivas deste planeta em sua vida.",
        }

    return interpretation
