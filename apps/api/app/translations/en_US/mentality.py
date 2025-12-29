"""
English translations for mentality-related terms.
"""

from typing import Any

translations: dict[str, Any] = {
    "mentality": {
        # Score labels
        "strength": "Strength",
        "speed": "Speed",
        "depth": "Depth",
        "versatility": "Versatility",
        # Mentality types
        "types": {
            "agile_and_superficial": {
                "name": "Agile & Superficial",
                "description": (
                    "Your mind operates with remarkable quickness, easily grasping concepts and "
                    "moving from one idea to the next with fluidity. You excel at making quick "
                    "connections and communicating ideas efficiently. However, there may be a "
                    "tendency to skim the surface rather than diving deep into complex subjects. "
                    "This mental style is excellent for multitasking and rapid problem-solving."
                ),
            },
            "agile_and_deep": {
                "name": "Agile & Deep",
                "description": (
                    "You possess a rare combination of mental speed and analytical depth. Your "
                    "mind can quickly process complex information while simultaneously exploring "
                    "its deeper implications. This is an exceptional mental configuration that "
                    "allows for both rapid comprehension and thorough understanding. You can "
                    "excel in fields requiring both quick thinking and profound analysis."
                ),
            },
            "slow_and_deep": {
                "name": "Slow & Deep",
                "description": (
                    "Your thinking process is methodical and thorough, preferring to fully "
                    "understand each concept before moving forward. You have a natural talent "
                    "for deep analysis and uncovering hidden meanings. While you may take longer "
                    "to reach conclusions, your insights tend to be more profound and well-considered. "
                    "This mental style excels in research, philosophy, and complex problem-solving."
                ),
            },
            "slow_and_superficial": {
                "name": "Slow & Superficial",
                "description": (
                    "Your mental approach tends toward a careful, measured pace with a preference "
                    "for practical, straightforward information. You may find deep theoretical "
                    "discussions less engaging than concrete, applicable knowledge. This style "
                    "can be excellent for steady, reliable work that requires consistency rather "
                    "than innovation. Focus on building knowledge systematically in areas you care about."
                ),
            },
            "versatile": {
                "name": "Versatile",
                "description": (
                    "Your mind is highly adaptable, capable of shifting between different modes "
                    "of thinking as circumstances require. You can be quick when needed and "
                    "thorough when depth is called for. This mental flexibility allows you to "
                    "thrive in varied intellectual environments and communicate effectively with "
                    "different types of thinkers. You're naturally suited for roles requiring adaptability."
                ),
            },
            "specialized": {
                "name": "Specialized",
                "description": (
                    "Your mental energy is highly focused, allowing you to develop deep expertise "
                    "in specific areas. Rather than spreading attention across many subjects, you "
                    "prefer to master particular domains of knowledge. This concentrated approach "
                    "enables you to achieve levels of understanding that more scattered minds may "
                    "miss. Excellence comes through dedication to your chosen fields."
                ),
            },
            "abstract": {
                "name": "Abstract",
                "description": (
                    "Your thinking naturally gravitates toward theoretical concepts, philosophies, "
                    "and big-picture ideas. You find meaning in patterns, principles, and universal "
                    "truths rather than concrete details. This abstract orientation makes you well-suited "
                    "for fields like philosophy, theoretical sciences, law, or any domain where "
                    "conceptual thinking is valued over practical application."
                ),
            },
            "concrete": {
                "name": "Concrete",
                "description": (
                    "Your mind excels at practical, tangible matters. You prefer information you can "
                    "apply directly and may find purely theoretical discussions less engaging. This "
                    "grounded mental approach makes you excellent at solving real-world problems and "
                    "communicating in clear, accessible terms. Fields requiring practical skills and "
                    "hands-on knowledge align well with your thinking style."
                ),
            },
            "unknown": {
                "name": "Unknown",
                "description": ("Mentality could not be calculated due to missing Mercury data."),
            },
        },
        # Factor labels
        "factors": {
            "mercury_dignity": "Mercury Dignity",
            "benefic_aspects": "Benefic Aspects to Mercury",
            "malefic_aspects": "Malefic Aspects to Mercury",
            "moon_strength": "Moon Strength",
            "benefics_in_mental_houses": "Benefics in Houses 3/9",
            "mercury_sign_speed": "Mercury Sign (Speed)",
            "mercury_retrograde": "Mercury Retrograde",
            "mercury_direct": "Mercury Direct",
            "mercury_sign_depth": "Mercury Sign (Depth)",
            "mercury_depth_house": "Mercury in Depth House",
            "mercury_dignity_depth": "Mercury Dignity (Depth)",
            "mercury_mutable": "Mercury in Mutable Sign",
            "mercury_many_aspects": "Mercury Aspects (3+)",
            "cadent_emphasis": "Cadent House Emphasis",
        },
    },
    "common": {
        "yes": "Yes",
        "no": "No",
        # Duplicated from astrology.py - needed because dict.update() overwrites keys
        "planet_in_sign": "{planet} in {sign}",
    },
}
