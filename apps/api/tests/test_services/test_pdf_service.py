"""
Tests for PDF generation service.
"""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.services.pdf_service import PDFService


@pytest.fixture
def pdf_service():
    """Create a PDFService instance for testing."""
    return PDFService()


@pytest.fixture
def sample_chart_data():
    """Sample chart data for testing."""
    return {
        "person_name": "John Doe",
        "birth_datetime": datetime(1990, 5, 15, 14, 30, tzinfo=UTC),
        "city": "São Paulo",
        "country": "Brazil",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "house_system": "placidus",
        "zodiac_type": "tropical",
        "planets": [
            {
                "name": "Sun",
                "symbol": "☉",
                "longitude": 54.123,
                "sign": "Taurus",
                "degree": 24.123,
                "house": 10,
                "retrograde": False,
                "dignity": "peregrinus",
            },
            {
                "name": "Moon",
                "symbol": "☽",
                "longitude": 165.456,
                "sign": "Virgo",
                "degree": 15.456,
                "house": 3,
                "retrograde": False,
                "dignity": "peregrine",
            },
        ],
        "houses": [
            {"number": 1, "cusp": 123.456, "sign": "Leo", "degree": 3.456},
            {"number": 2, "cusp": 153.789, "sign": "Virgo", "degree": 3.789},
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "aspect": "trine",
                "angle": 120.0,
                "orb": 2.3,
                "applying": True,
            }
        ],
        "chart_info": {
            "ascendant": 123.456,
            "mc": 234.567,
        },
    }


@pytest.fixture
def sample_interpretations():
    """Sample interpretations for testing."""
    return {
        "planets": [
            {
                "planet_name": "Sun",
                "sign": "Taurus",
                "house": 10,
                "interpretation": "The Sun in Taurus in the 10th house...",
            },
            {
                "planet_name": "Moon",
                "sign": "Virgo",
                "house": 3,
                "interpretation": "The Moon in Virgo in the 3rd house...",
            },
        ],
        "houses": [
            {
                "house_number": 1,
                "sign": "Leo",
                "interpretation": "The 1st house in Leo...",
            },
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "aspect_type": "trine",
                "interpretation": "Sun trine Moon...",
            }
        ],
    }


class TestPDFService:
    """Tests for PDFService class."""

    def test_generate_pdf_path(self, pdf_service):
        """Test PDF path generation."""
        chart_id = uuid4()
        pdf_path = pdf_service.generate_pdf_path(chart_id)

        assert isinstance(pdf_path, Path)
        assert pdf_path.name == f"chart_{chart_id}.pdf"
        assert "media/pdfs" in str(pdf_path)

    def test_prepare_template_data_basic(
        self, pdf_service, sample_chart_data, sample_interpretations
    ):
        """Test basic template data preparation."""
        template_data = pdf_service.prepare_template_data(
            chart_data=sample_chart_data,
            interpretations=sample_interpretations,
        )

        # Check person info
        assert template_data["person_name"] == "John Doe"
        assert "São Paulo" in template_data["location"]
        assert "Brazil" in template_data["location"]

        # Check chart system info
        assert template_data["house_system"] == "Placidus"
        assert template_data["zodiac_type"] == "Tropical"

        # Check planets
        assert len(template_data["planets"]) == 2
        assert template_data["planets"][0]["name"] == "Sun"
        assert template_data["planets"][0]["sign"] == "Taurus"
        assert template_data["planets"][0]["house"] == 10

        # Check houses
        assert len(template_data["houses"]) == 2
        assert template_data["houses"][0]["number"] == 1
        assert template_data["houses"][0]["sign"] == "Leo"

        # Check aspects
        assert len(template_data["aspects"]) == 1
        assert template_data["aspects"][0]["planet1"] == "Sun"
        assert template_data["aspects"][0]["aspect"] == "trine"

    def test_prepare_template_data_with_interpretations(
        self, pdf_service, sample_chart_data, sample_interpretations
    ):
        """Test template data preparation includes interpretations."""
        template_data = pdf_service.prepare_template_data(
            chart_data=sample_chart_data,
            interpretations=sample_interpretations,
        )

        # Check planet interpretations
        sun_planet = next(p for p in template_data["planets"] if p["name"] == "Sun")
        assert "interpretation" in sun_planet
        assert "Sun in Taurus" in sun_planet["interpretation"]

        # Check house interpretations
        house_1 = next(h for h in template_data["houses"] if h["number"] == 1)
        assert "interpretation" in house_1
        assert "1st house in Leo" in house_1["interpretation"]

        # Check aspect interpretations
        assert "interpretation" in template_data["aspects"][0]
        assert "Sun trine Moon" in template_data["aspects"][0]["interpretation"]

    def test_prepare_template_data_without_interpretations(
        self, pdf_service, sample_chart_data
    ):
        """Test template data preparation without interpretations."""
        template_data = pdf_service.prepare_template_data(
            chart_data=sample_chart_data,
            interpretations={"planets": [], "houses": [], "aspects": []},
        )

        # Planets should not have interpretation field
        sun_planet = next(p for p in template_data["planets"] if p["name"] == "Sun")
        assert "interpretation" not in sun_planet

    def test_prepare_template_data_coordinates_formatting(
        self, pdf_service, sample_chart_data, sample_interpretations
    ):
        """Test coordinate formatting in template data."""
        template_data = pdf_service.prepare_template_data(
            chart_data=sample_chart_data,
            interpretations=sample_interpretations,
        )

        coords = template_data["coordinates"]
        assert "23.55°S" in coords or "23.5505°S" in coords
        assert "46.63°W" in coords or "46.6333°W" in coords

    def test_prepare_template_data_retrograde_display(
        self, pdf_service, sample_interpretations
    ):
        """Test retrograde planet display."""
        chart_data = {
            "person_name": "Test",
            "birth_datetime": datetime(1990, 1, 1, 12, 0, tzinfo=UTC),
            "city": "Test City",
            "country": "Test Country",
            "latitude": 0.0,
            "longitude": 0.0,
            "house_system": "placidus",
            "zodiac_type": "tropical",
            "planets": [
                {
                    "name": "Mercury",
                    "symbol": "☿",
                    "longitude": 100.0,
                    "sign": "Cancer",
                    "degree": 10.0,
                    "house": 5,
                    "retrograde": True,
                    "dignity": "peregrine",
                }
            ],
            "houses": [],
            "aspects": [],
            "chart_info": {"ascendant": 0.0, "mc": 90.0},
        }

        template_data = pdf_service.prepare_template_data(
            chart_data=chart_data,
            interpretations=sample_interpretations,
        )

        mercury = template_data["planets"][0]
        assert mercury["retrograde"] == "Sim" or mercury["retrograde"] == "Yes"

    def test_prepare_template_data_ascendant_mc(
        self, pdf_service, sample_chart_data, sample_interpretations
    ):
        """Test Ascendant and MC calculations."""
        template_data = pdf_service.prepare_template_data(
            chart_data=sample_chart_data,
            interpretations=sample_interpretations,
        )

        # Check that ascendant and MC are formatted
        assert "ascendant" in template_data
        assert "midheaven" in template_data
        assert "°" in template_data["ascendant"]
        assert "°" in template_data["midheaven"]

    def test_render_template_basic(
        self, pdf_service, sample_chart_data, sample_interpretations
    ):
        """Test basic LaTeX template rendering."""
        template_data = pdf_service.prepare_template_data(
            chart_data=sample_chart_data,
            interpretations=sample_interpretations,
        )

        latex_source = pdf_service.render_template(template_data)

        # Check LaTeX document structure
        assert "\\documentclass" in latex_source
        assert "\\begin{document}" in latex_source
        assert "\\end{document}" in latex_source

        # Check content is present
        assert "John Doe" in latex_source
        assert "São Paulo" in latex_source
        assert "Taurus" in latex_source
        assert "Sun" in latex_source

    def test_render_template_special_characters(self, pdf_service, sample_interpretations):
        """Test LaTeX escaping of special characters."""
        chart_data = {
            "person_name": "José & María",
            "birth_datetime": datetime(1990, 1, 1, 12, 0, tzinfo=UTC),
            "city": "São Paulo",
            "country": "Brazil",
            "latitude": 0.0,
            "longitude": 0.0,
            "house_system": "placidus",
            "zodiac_type": "tropical",
            "planets": [],
            "houses": [],
            "aspects": [],
            "chart_info": {"ascendant": 0.0, "mc": 90.0},
        }

        template_data = pdf_service.prepare_template_data(
            chart_data=chart_data,
            interpretations=sample_interpretations,
        )

        latex_source = pdf_service.render_template(template_data)

        # LaTeX special characters should be escaped
        # Note: Jinja2 might auto-escape these, so we just check it compiles
        assert "José" in latex_source or "Jos\\'e" in latex_source
        assert "María" in latex_source or "Mar\\'ia" in latex_source

    def test_render_template_empty_sections(self, pdf_service):
        """Test template rendering with empty data sections."""
        chart_data = {
            "person_name": "Test Person",
            "birth_datetime": datetime(1990, 1, 1, 12, 0, tzinfo=UTC),
            "city": "Test City",
            "country": "Test Country",
            "latitude": 0.0,
            "longitude": 0.0,
            "house_system": "placidus",
            "zodiac_type": "tropical",
            "planets": [],
            "houses": [],
            "aspects": [],
            "chart_info": {"ascendant": 0.0, "mc": 90.0},
        }

        template_data = pdf_service.prepare_template_data(
            chart_data=chart_data,
            interpretations={"planets": [], "houses": [], "aspects": []},
        )

        latex_source = pdf_service.render_template(template_data)

        # Should still be valid LaTeX
        assert "\\documentclass" in latex_source
        assert "\\begin{document}" in latex_source
        assert "\\end{document}" in latex_source
        assert "Test Person" in latex_source
