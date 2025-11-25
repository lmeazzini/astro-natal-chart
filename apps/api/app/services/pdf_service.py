"""
Service for generating PDF reports from natal chart data.
"""

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import cairosvg
from jinja2 import Environment, FileSystemLoader
from loguru import logger

# LaTeX special characters that need escaping
LATEX_SPECIAL_CHARS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}

# Planet symbols mapping - LaTeX commands from marvosym package
PLANET_SYMBOLS = {
    "Sun": r"\Sun",
    "Moon": r"\Moon",
    "Mercury": r"\Mercury",
    "Venus": r"\Venus",
    "Mars": r"\Mars",
    "Jupiter": r"\Jupiter",
    "Saturn": r"\Saturn",
    "Uranus": r"\Uranus",
    "Neptune": r"\Neptune",
    "Pluto": r"\Pluto",
    "North Node": r"\NorthNode",
    "South Node": r"\SouthNode",
    "Chiron": r"\Chiron",
}

# Sign symbols mapping - LaTeX commands from wasysym package
SIGN_SYMBOLS = {
    "Aries": r"\Aries",
    "Taurus": r"\Taurus",
    "Gemini": r"\Gemini",
    "Cancer": r"\Cancer",
    "Leo": r"\Leo",
    "Virgo": r"\Virgo",
    "Libra": r"\Libra",
    "Scorpio": r"\Scorpio",
    "Sagittarius": r"\Sagittarius",
    "Capricorn": r"\Capricorn",
    "Aquarius": r"\Aquarius",
    "Pisces": r"\Pisces",
}

# Aspect symbols mapping - LaTeX commands
ASPECT_SYMBOLS = {
    "conjunction": r"\conjunction",
    "opposition": r"\opposition",
    "trine": r"\trine",
    "square": r"\square",
    "sextile": r"\sextile",
    "quincunx": r"\quincunx",
    "semisextile": r"$\angle$",
    "semisquare": r"$\angle$",
    "sesquiquadrate": r"$\angle$",
}


class PDFService:
    """Service for generating PDF reports from natal charts."""

    def __init__(self) -> None:
        """Initialize PDF service with Jinja2 environment."""
        # Setup Jinja2 template environment
        template_path = Path(__file__).parent.parent / "report_templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=False,  # We'll handle escaping manually
        )

        # Register custom filters
        self.jinja_env.filters["escape_latex"] = self.escape_latex

        # Media directory for PDFs and images
        self.media_dir = Path(__file__).parent.parent / "media"
        self.pdf_dir = self.media_dir / "pdfs"
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

    def escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters in text.

        Args:
            text: Input text

        Returns:
            Escaped text safe for LaTeX
        """
        if not text:
            return ""

        # Replace special characters
        for char, escaped in LATEX_SPECIAL_CHARS.items():
            text = text.replace(char, escaped)

        return text

    def format_planet_data(self, planet: dict[str, Any]) -> dict[str, str]:
        """
        Format planet data for LaTeX template.

        Args:
            planet: Planet data dictionary

        Returns:
            Formatted planet data
        """
        name = planet["name"]
        sign = planet["sign"]
        degree = planet.get("degree", 0.0)
        house = planet.get("house", 1)
        retrograde = planet.get("retrograde", False)
        dignities = planet.get("dignities", {})

        # Format dignity
        dignity_text = "Peregrino"
        if dignities:
            if dignities.get("is_ruler"):
                dignity_text = "Domicílio"
            elif dignities.get("is_exalted"):
                dignity_text = "Exaltação"
            elif dignities.get("is_detriment"):
                dignity_text = "Detrimento"
            elif dignities.get("is_fall"):
                dignity_text = "Queda"

        return {
            "name": self.escape_latex(name),
            "symbol": PLANET_SYMBOLS.get(name, ""),
            "sign": self.escape_latex(sign),
            "sign_symbol": SIGN_SYMBOLS.get(sign, ""),
            "degree": f"{degree:.2f}",
            "house": str(house),
            "dignity": self.escape_latex(dignity_text),
            "retrograde": "Sim" if retrograde else "Não",
            "interpretation": self.escape_latex(planet.get("interpretation", "")),
        }

    def format_house_data(self, house: dict[str, Any]) -> dict[str, str]:
        """
        Format house data for LaTeX template.

        Args:
            house: House data dictionary

        Returns:
            Formatted house data
        """
        number = house.get("house", house.get("number", 1))
        sign = house.get("sign", "Unknown")
        cusp = house.get("cusp", house.get("longitude", 0.0))

        return {
            "number": str(number),
            "sign": self.escape_latex(sign),
            "sign_symbol": SIGN_SYMBOLS.get(sign, ""),
            "degree": f"{cusp:.2f}",
            "interpretation": self.escape_latex(house.get("interpretation", "")),
        }

    def format_aspect_data(self, aspect: dict[str, Any]) -> dict[str, str]:
        """
        Format aspect data for LaTeX template.

        Args:
            aspect: Aspect data dictionary

        Returns:
            Formatted aspect data
        """
        aspect_name = aspect["aspect"].lower()
        aspect_symbol = ASPECT_SYMBOLS.get(aspect_name, "")

        return {
            "planet1": self.escape_latex(aspect["planet1"]),
            "planet1_symbol": PLANET_SYMBOLS.get(aspect["planet1"], ""),
            "planet2": self.escape_latex(aspect["planet2"]),
            "planet2_symbol": PLANET_SYMBOLS.get(aspect["planet2"], ""),
            "aspect": self.escape_latex(aspect["aspect"]),
            "aspect_symbol": aspect_symbol,
            "orb": f"{aspect['orb']:.2f}",
            "interpretation": self.escape_latex(aspect.get("interpretation", "")),
        }

    def render_chart_wheel_image(
        self,
        chart_id: UUID,
        svg_data: str,
    ) -> Path | None:
        """
        Convert SVG chart wheel to PNG image for inclusion in PDF.

        Args:
            chart_id: Chart UUID
            svg_data: SVG data as string

        Returns:
            Path to generated PNG file, or None if conversion failed
        """
        try:
            # Generate unique filename
            image_filename = f"chart_{chart_id}.png"
            image_path = self.pdf_dir / image_filename

            # Convert SVG to PNG using cairosvg
            cairosvg.svg2png(
                bytestring=svg_data.encode("utf-8"),
                write_to=str(image_path),
                output_width=800,
                output_height=800,
            )

            logger.info(f"Chart wheel image generated: {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"Failed to generate chart wheel image: {e}")
            return None

    def prepare_template_data(
        self,
        chart_data: dict[str, Any],
        interpretations: dict[str, dict[str, str]] | None = None,
        chart_image_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Prepare complete template data for PDF generation.

        Args:
            chart_data: Complete chart data dictionary
            interpretations: Optional interpretations dict (planets, houses, aspects)
            chart_image_path: Optional path to chart wheel image

        Returns:
            Formatted template data ready for Jinja2
        """
        # Extract basic info
        person_name = chart_data.get("person_name", "Unknown")
        birth_datetime = chart_data.get("birth_datetime", "")
        city = chart_data.get("city", "")
        country = chart_data.get("country", "")
        latitude = chart_data.get("latitude", 0.0)
        longitude = chart_data.get("longitude", 0.0)

        # Format location
        location = f"{city}, {country}" if city and country else "Localização desconhecida"
        coordinates = f"{latitude:.4f}°, {longitude:.4f}°"

        # Extract chart info
        chart_info = chart_data.get("chart_info", {})
        ascendant_deg = chart_info.get("ascendant", 0.0)
        mc_deg = chart_info.get("mc", 0.0)

        # Format birth datetime
        if isinstance(birth_datetime, str):
            birth_date_obj = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        else:
            birth_date_obj = birth_datetime

        birth_date = birth_date_obj.strftime("%d/%m/%Y")
        birth_time = birth_date_obj.strftime("%H:%M:%S")

        # Format planets with interpretations
        planets = []
        for planet in chart_data.get("planets", []):
            formatted_planet = self.format_planet_data(planet)

            # Add interpretation if available
            if interpretations and "planets" in interpretations:
                planet_name = planet["name"]
                if planet_name in interpretations["planets"]:
                    formatted_planet["interpretation"] = self.escape_latex(
                        interpretations["planets"][planet_name]
                    )

            planets.append(formatted_planet)

        # Format houses with interpretations
        houses = []
        for house in chart_data.get("houses", []):
            formatted_house = self.format_house_data(house)

            # Add interpretation if available
            if interpretations and "houses" in interpretations:
                house_num = formatted_house["number"]
                if house_num in interpretations["houses"]:
                    formatted_house["interpretation"] = self.escape_latex(
                        interpretations["houses"][house_num]
                    )

            houses.append(formatted_house)

        # Format aspects with interpretations
        aspects = []
        for aspect in chart_data.get("aspects", []):
            formatted_aspect = self.format_aspect_data(aspect)

            # Add interpretation if available
            if interpretations and "aspects" in interpretations:
                aspect_key = f"{aspect['planet1']}-{aspect['aspect']}-{aspect['planet2']}"
                if aspect_key in interpretations["aspects"]:
                    formatted_aspect["interpretation"] = self.escape_latex(
                        interpretations["aspects"][aspect_key]
                    )

            aspects.append(formatted_aspect)

        # Calculate ascendant and MC in sign/degree format
        def deg_to_sign(degrees: float) -> str:
            signs = [
                "Aries",
                "Taurus",
                "Gemini",
                "Cancer",
                "Leo",
                "Virgo",
                "Libra",
                "Scorpio",
                "Sagittarius",
                "Capricorn",
                "Aquarius",
                "Pisces",
            ]
            sign_index = int(degrees // 30)
            degree_in_sign = degrees % 30
            return f"{degree_in_sign:.2f}° {signs[sign_index]}"

        ascendant = deg_to_sign(ascendant_deg)
        midheaven = deg_to_sign(mc_deg)

        return {
            "person_name": self.escape_latex(person_name),
            "birth_datetime": f"{birth_date} {birth_time}",
            "birth_date": birth_date,
            "birth_time": birth_time,
            "location": self.escape_latex(location),
            "coordinates": coordinates,
            "house_system": self.escape_latex(chart_data.get("house_system", "Placidus")),
            "zodiac_type": self.escape_latex(chart_data.get("zodiac_type", "Tropical")),
            "ascendant": self.escape_latex(ascendant),
            "midheaven": self.escape_latex(midheaven),
            "chart_image_path": chart_image_path or "",
            "generation_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "planets": planets,
            "houses": houses,
            "aspects": aspects,
        }

    def render_template(self, template_data: dict[str, Any]) -> str:
        """
        Render LaTeX template with data.

        Args:
            template_data: Template data dictionary

        Returns:
            Rendered LaTeX source code
        """
        template = self.jinja_env.get_template("natal_chart_report.tex")
        return template.render(**template_data)

    def generate_pdf_path(self, chart_id: UUID) -> Path:
        """
        Generate unique PDF file path for a chart.

        Args:
            chart_id: Chart UUID

        Returns:
            Path object for the PDF file
        """
        filename = f"natal_chart_{chart_id}.pdf"
        return self.pdf_dir / filename
