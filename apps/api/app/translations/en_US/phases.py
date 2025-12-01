"""
English translations for lunar and solar phases.
"""

from typing import Any

translations: dict[str, Any] = {
    "lunar_phases": {
        "new_moon": {
            "name": "New Moon",
            "keywords": "Beginning, Instinct, Impulse, Subjectivity",
            "interpretation": (
                "Born at the New Moon, you are a person of new beginnings and initiatives. "
                "Your path is instinctive and subjective, guided by internal impulses. "
                "You possess a pioneering quality and the ability to start projects "
                "with natural enthusiasm. Your journey is about discovering your own path "
                "through direct experience."
            ),
        },
        "waxing_crescent": {
            "name": "Waxing Crescent",
            "keywords": "Expansion, Struggle, Determination, Resistance",
            "interpretation": (
                "Born at the Waxing Crescent, you are a person oriented toward expansion and growth. "
                "You face challenges with determination and constantly seek to overcome obstacles. "
                "Your natural energy is one of struggle and construction, always pushing boundaries. "
                "You learn through effort and resistance, developing strength "
                "by facing difficulties."
            ),
        },
        "first_quarter": {
            "name": "First Quarter",
            "keywords": "Action, Crisis, Decision, Construction",
            "interpretation": (
                "Born at the First Quarter, you are a person of action and decision. "
                "You frequently face crises that require clear choices and commitment. "
                "Your nature is constructive and oriented toward concrete results. "
                "You possess the ability to act under pressure and make difficult decisions "
                "when necessary, building lasting structures."
            ),
        },
        "waxing_gibbous": {
            "name": "Waxing Gibbous",
            "keywords": "Analysis, Refinement, Perfection, Preparation",
            "interpretation": (
                "Born at the Waxing Gibbous, you are an analytical and perfectionist person. "
                "You constantly seek to refine and improve everything you touch. "
                "Your energy is focused on preparation and perfecting details. "
                "You have the ability to see what needs adjustment before complete manifestation, "
                "acting as a careful craftsperson."
            ),
        },
        "full_moon": {
            "name": "Full Moon",
            "keywords": "Fulfillment, Objectivity, Consciousness, Relationships",
            "interpretation": (
                "Born at the Full Moon, you are a person of fulfillment and objectivity. "
                "You possess strong awareness of others and relationships. "
                "Your nature seeks balance between opposites and complete manifestation. "
                "You have the ability to see things clearly and objectively, "
                "often acting as a mediator or bringing light to situations."
            ),
        },
        "waning_gibbous": {
            "name": "Waning Gibbous",
            "keywords": "Distribution, Sharing, Teaching, Dissemination",
            "interpretation": (
                "Born at the Waning Gibbous, you are a person oriented toward sharing "
                "and distributing knowledge. Your role is to teach and disseminate what you have learned. "
                "You possess a natural mentor quality, seeking to pass on your experiences. "
                "You find meaning in helping others understand and grow through "
                "what you have already experienced."
            ),
        },
        "last_quarter": {
            "name": "Last Quarter",
            "keywords": "Transition, Reorientation, Crisis of Consciousness, Transformation",
            "interpretation": (
                "Born at the Last Quarter, you are a person of transition and reorientation. "
                "You frequently face crises of consciousness that lead to profound changes. "
                "Your nature questions old structures and seeks new meanings. "
                "You have the ability to dismantle what no longer serves and prepare "
                "the ground for new ways of being."
            ),
        },
        "waning_crescent": {
            "name": "Waning Crescent",
            "keywords": "Release, Closure, Prophecy, Vision",
            "interpretation": (
                "Born at the Waning Crescent (Balsamic), you are a person of release and closure. "
                "You possess a visionary and prophetic quality, connected with the future. "
                "Your energy is focused on letting go of the past and preparing new cycles. "
                "You have the ability to see beyond the present moment and sow intentions "
                "for what is to come, acting as a bridge between cycles."
            ),
        },
    },
    "solar_phases": {
        "first": {
            "name": "First Solar Phase",
            "temperament": "Sanguine",
            "qualities": "Hot & Moist",
            "signs": ["Aries", "Taurus", "Gemini"],
            "description": (
                "Born in the 1st Solar Phase (Sanguine temperament), you are a person "
                "naturally optimistic, sociable, and expansive. This hot and moist temperament "
                "favors adaptability, communication, and the desire for varied experiences. "
                "You tend to be versatile, curious, and oriented toward social connections, "
                "always seeking new possibilities and maintaining a hopeful perspective on life."
            ),
        },
        "second": {
            "name": "Second Solar Phase",
            "temperament": "Choleric",
            "qualities": "Hot & Dry",
            "signs": ["Cancer", "Leo", "Virgo"],
            "description": (
                "Born in the 2nd Solar Phase (Choleric temperament), you are a person "
                "naturally assertive, ambitious, and action-oriented. This hot and dry temperament "
                "favors leadership, determination, and the desire to achieve and build. "
                "You tend to be dynamic, focused, and results-oriented, "
                "always seeking to manifest your will and leave your mark on the world."
            ),
        },
        "third": {
            "name": "Third Solar Phase",
            "temperament": "Melancholic",
            "qualities": "Cold & Dry",
            "signs": ["Libra", "Scorpio", "Sagittarius"],
            "description": (
                "Born in the 3rd Solar Phase (Melancholic temperament), you are a person "
                "naturally reflective, analytical, and oriented toward depth. This cold and dry temperament "
                "favors introspection, critical thinking, and the desire to understand profound truths. "
                "You tend to be careful, meticulous, and quality-oriented, "
                "always seeking perfection and genuine meaning in everything you do."
            ),
        },
        "fourth": {
            "name": "Fourth Solar Phase",
            "temperament": "Phlegmatic",
            "qualities": "Cold & Moist",
            "signs": ["Capricorn", "Aquarius", "Pisces"],
            "description": (
                "Born in the 4th Solar Phase (Phlegmatic temperament), you are a person "
                "naturally calm, receptive, and oriented toward harmony. This cold and moist temperament "
                "favors patience, empathy, and the desire for peace and stability. "
                "You tend to be compassionate, adaptable, and oriented toward collective well-being, "
                "always seeking balance and avoiding unnecessary conflicts."
            ),
        },
    },
    # Simplified lunar phase names for temperament calculation (4 divisions)
    "lunar_temperament_phases": {
        "1": "New Moon",
        "2": "First Quarter",
        "3": "Full Moon",
        "4": "Last Quarter",
    },
}
