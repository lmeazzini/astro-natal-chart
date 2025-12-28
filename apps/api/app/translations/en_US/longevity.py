"""
English translations for Hyleg and Alcochoden longevity calculations.
"""

translations = {
    # Hyleg section
    "hyleg": {
        "title": "Hyleg - Giver of Life",
        "no_hyleg_found": "No Hyleg could be determined for this chart. This is rare and may indicate challenges in traditional longevity assessment.",
        "qualification": {
            "aspected_by_domicile_lord": "Aspected by its domicile lord",
            "aspected_by_prorogatory": "Aspected by a prorogatory planet",
            "no_aspects": "No qualifying aspects found",
            "no_qualifying_aspects": "Aspected but not by qualifying planets",
            "not_in_hylegical_place": "Not in a hylegical place",
        },
        "candidates": {
            "sun": "Sun",
            "moon": "Moon",
            "ascendant": "Ascendant",
            "part_of_fortune": "Part of Fortune",
            "prenatal_syzygy": "Prenatal Syzygy",
        },
        "day_chart": "Day Chart",
        "night_chart": "Night Chart",
        "hylegical_places": "Hylegical Places (Houses 1, 7, 9, 10, 11)",
    },
    # Alcochoden section
    "alcochoden": {
        "title": "Alcochoden - Giver of Years",
        "no_hyleg": "Cannot calculate Alcochoden without a valid Hyleg.",
        "no_candidates": "No planet with dignity at the Hyleg's degree aspects the Hyleg.",
        "year_type": {
            "minor": "Minor Years",
            "middle": "Middle Years",
            "major": "Major Years",
        },
        "house_type": {
            "angular": "Angular house position",
            "succedent": "Succedent house position",
            "cadent": "Cadent house position",
        },
        "condition": {
            "combust": "Combust (within 8° of Sun)",
            "retrograde": "Retrograde motion",
            "debilitated": "Essentially debilitated",
            "dignified": "Essentially dignified",
        },
        "dignity_types": {
            "domicile": "Domicile",
            "exaltation": "Exaltation",
            "triplicity": "Triplicity",
            "term": "Term",
            "face": "Face",
        },
    },
    # Longevity summary section
    "longevity": {
        "title": "Longevity Analysis",
        "educational_disclaimer": "This longevity calculation is presented for historical and educational purposes only. Traditional astrology's approach to predicting lifespan is not scientifically validated. This information should never be used for medical decisions, health predictions, or to cause anxiety about life expectancy.",
        "summary": {
            "no_hyleg": "No vital force significator (Hyleg) could be determined.",
            "vital_force": {
                "strong": "The vital force is indicated as strong.",
                "moderate": "The vital force is indicated as moderate.",
                "weak": "The vital force is indicated as weak.",
                "undetermined": "The vital force could not be determined.",
            },
        },
    },
}
