"""
Portuguese (Brazil) translations for mentality-related terms.
"""

from typing import Any

translations: dict[str, Any] = {
    "mentality": {
        # Score labels
        "strength": "Força",
        "speed": "Velocidade",
        "depth": "Profundidade",
        "versatility": "Versatilidade",
        # Mentality types
        "types": {
            "agile_and_superficial": {
                "name": "Ágil e Superficial",
                "description": (
                    "Sua mente opera com notável rapidez, captando conceitos facilmente e "
                    "passando de uma ideia para outra com fluidez. Você se destaca em fazer "
                    "conexões rápidas e comunicar ideias de forma eficiente. No entanto, pode "
                    "haver uma tendência a passar superficialmente por assuntos complexos em "
                    "vez de mergulhar profundamente. Este estilo mental é excelente para "
                    "multitarefas e resolução rápida de problemas."
                ),
            },
            "agile_and_deep": {
                "name": "Ágil e Profundo",
                "description": (
                    "Você possui uma combinação rara de velocidade mental e profundidade "
                    "analítica. Sua mente consegue processar rapidamente informações complexas "
                    "enquanto simultaneamente explora suas implicações mais profundas. Esta é "
                    "uma configuração mental excepcional que permite tanto compreensão rápida "
                    "quanto entendimento profundo. Você pode se destacar em campos que exigem "
                    "tanto pensamento rápido quanto análise aprofundada."
                ),
            },
            "slow_and_deep": {
                "name": "Lento e Profundo",
                "description": (
                    "Seu processo de pensamento é metódico e minucioso, preferindo compreender "
                    "completamente cada conceito antes de seguir em frente. Você tem um talento "
                    "natural para análise profunda e descoberta de significados ocultos. Embora "
                    "possa levar mais tempo para chegar a conclusões, seus insights tendem a ser "
                    "mais profundos e bem ponderados. Este estilo mental se destaca em pesquisa, "
                    "filosofia e resolução de problemas complexos."
                ),
            },
            "slow_and_superficial": {
                "name": "Lento e Superficial",
                "description": (
                    "Sua abordagem mental tende a um ritmo cuidadoso e medido, com preferência "
                    "por informações práticas e diretas. Você pode achar discussões teóricas "
                    "profundas menos envolventes do que conhecimento concreto e aplicável. Este "
                    "estilo pode ser excelente para trabalho constante e confiável que requer "
                    "consistência em vez de inovação. Concentre-se em construir conhecimento "
                    "sistematicamente em áreas que lhe interessam."
                ),
            },
            "versatile": {
                "name": "Versátil",
                "description": (
                    "Sua mente é altamente adaptável, capaz de alternar entre diferentes modos "
                    "de pensamento conforme as circunstâncias exigem. Você pode ser rápido "
                    "quando necessário e minucioso quando a profundidade é necessária. Esta "
                    "flexibilidade mental permite que você prospere em ambientes intelectuais "
                    "variados e se comunique efetivamente com diferentes tipos de pensadores. "
                    "Você é naturalmente adequado para funções que exigem adaptabilidade."
                ),
            },
            "specialized": {
                "name": "Especializado",
                "description": (
                    "Sua energia mental é altamente focada, permitindo desenvolver expertise "
                    "profunda em áreas específicas. Em vez de dispersar atenção entre muitos "
                    "assuntos, você prefere dominar domínios particulares de conhecimento. "
                    "Esta abordagem concentrada permite alcançar níveis de compreensão que "
                    "mentes mais dispersas podem perder. A excelência vem através da dedicação "
                    "aos seus campos escolhidos."
                ),
            },
            "abstract": {
                "name": "Abstrato",
                "description": (
                    "Seu pensamento naturalmente gravita em direção a conceitos teóricos, "
                    "filosofias e ideias de grande alcance. Você encontra significado em "
                    "padrões, princípios e verdades universais, em vez de detalhes concretos. "
                    "Esta orientação abstrata o torna bem adequado para campos como filosofia, "
                    "ciências teóricas, direito ou qualquer domínio onde o pensamento "
                    "conceitual é valorizado sobre a aplicação prática."
                ),
            },
            "concrete": {
                "name": "Concreto",
                "description": (
                    "Sua mente se destaca em assuntos práticos e tangíveis. Você prefere "
                    "informações que pode aplicar diretamente e pode achar discussões "
                    "puramente teóricas menos envolventes. Esta abordagem mental fundamentada "
                    "o torna excelente na resolução de problemas do mundo real e na "
                    "comunicação em termos claros e acessíveis. Campos que requerem "
                    "habilidades práticas e conhecimento prático se alinham bem com seu "
                    "estilo de pensamento."
                ),
            },
            "unknown": {
                "name": "Desconhecido",
                "description": (
                    "A mentalidade não pôde ser calculada devido à falta de dados de Mercúrio."
                ),
            },
        },
        # Factor labels
        "factors": {
            "mercury_dignity": "Dignidade de Mercúrio",
            "benefic_aspects": "Aspectos Benéficos com Mercúrio",
            "malefic_aspects": "Aspectos Maléficos com Mercúrio",
            "moon_strength": "Força da Lua",
            "benefics_in_mental_houses": "Benéficos nas Casas 3/9",
            "mercury_sign_speed": "Signo de Mercúrio (Velocidade)",
            "mercury_retrograde": "Mercúrio Retrógrado",
            "mercury_direct": "Mercúrio Direto",
            "mercury_sign_depth": "Signo de Mercúrio (Profundidade)",
            "mercury_depth_house": "Mercúrio em Casa de Profundidade",
            "mercury_dignity_depth": "Dignidade de Mercúrio (Profundidade)",
            "mercury_mutable": "Mercúrio em Signo Mutável",
            "mercury_many_aspects": "Aspectos de Mercúrio (3+)",
            "cadent_emphasis": "Ênfase em Casas Cadentes",
        },
    },
    "common": {
        "yes": "Sim",
        "no": "Não",
        # Duplicated from astrology.py - needed because dict.update() overwrites keys
        "planet_in_sign": "{planet} em {sign}",
    },
}
