"""
Portuguese (Brazil) translations for Hyleg and Alcochoden longevity calculations.
"""

translations = {
    # Hyleg section
    "hyleg": {
        "title": "Hyleg - Doador da Vida",
        "no_hyleg_found": "Não foi possível determinar o Hyleg para este mapa. Isso é raro e pode indicar desafios na avaliação tradicional de longevidade.",
        "qualification": {
            "aspected_by_domicile_lord": "Aspectado pelo seu senhor domiciliar",
            "aspected_by_prorogatory": "Aspectado por um planeta prorogatório",
            "no_aspects": "Nenhum aspecto qualificador encontrado",
            "no_qualifying_aspects": "Aspectado, mas não por planetas qualificadores",
            "not_in_hylegical_place": "Não está em um lugar hilegíaco",
        },
        "candidates": {
            "sun": "Sol",
            "moon": "Lua",
            "ascendant": "Ascendente",
            "part_of_fortune": "Parte da Fortuna",
            "prenatal_syzygy": "Sizígia Pré-Natal",
        },
        "day_chart": "Mapa Diurno",
        "night_chart": "Mapa Noturno",
        "hylegical_places": "Lugares Hilegíacos (Casas 1, 7, 9, 10, 11)",
    },
    # Alcochoden section
    "alcochoden": {
        "title": "Alcochoden - Doador dos Anos",
        "no_hyleg": "Não é possível calcular o Alcochoden sem um Hyleg válido.",
        "no_candidates": "Nenhum planeta com dignidade no grau do Hyleg aspecta o Hyleg.",
        "year_type": {
            "minor": "Anos Menores",
            "middle": "Anos Médios",
            "major": "Anos Maiores",
        },
        "house_type": {
            "angular": "Posição em casa angular",
            "succedent": "Posição em casa sucedente",
            "cadent": "Posição em casa cadente",
        },
        "condition": {
            "combust": "Combusto (a menos de 8° do Sol)",
            "retrograde": "Movimento retrógrado",
            "debilitated": "Essencialmente debilitado",
            "dignified": "Essencialmente dignificado",
        },
        "dignity_types": {
            "domicile": "Domicílio",
            "exaltation": "Exaltação",
            "triplicity": "Triplicidade",
            "term": "Termo",
            "face": "Face",
        },
    },
    # Longevity summary section
    "longevity": {
        "title": "Análise de Longevidade",
        "educational_disclaimer": "Este cálculo de longevidade é apresentado apenas para fins históricos e educacionais. A abordagem da astrologia tradicional para prever o tempo de vida não é cientificamente validada. Esta informação nunca deve ser usada para decisões médicas, previsões de saúde ou para causar ansiedade sobre a expectativa de vida.",
        "summary": {
            "no_hyleg": "Não foi possível determinar o significador da força vital (Hyleg).",
            "vital_force": {
                "strong": "A força vital é indicada como forte.",
                "moderate": "A força vital é indicada como moderada.",
                "weak": "A força vital é indicada como fraca.",
                "undetermined": "A força vital não pôde ser determinada.",
            },
        },
    },
}
