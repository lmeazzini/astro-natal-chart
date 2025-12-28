"""
API integration tests for planetary terms (bounds) endpoints.
"""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import BirthChart

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def chart_data_with_planets() -> dict:
    """Sample chart data with planet positions."""
    return {
        "planets": [
            {"name": "Sun", "longitude": 45.0, "sign": "Taurus"},  # 15° Taurus
            {"name": "Moon", "longitude": 120.0, "sign": "Leo"},  # 0° Leo
            {"name": "Mercury", "longitude": 65.0, "sign": "Gemini"},  # 5° Gemini
            {"name": "Venus", "longitude": 35.0, "sign": "Taurus"},  # 5° Taurus
            {"name": "Mars", "longitude": 200.0, "sign": "Libra"},  # 20° Libra
            {"name": "Jupiter", "longitude": 270.0, "sign": "Capricorn"},  # 0° Cap
            {"name": "Saturn", "longitude": 310.0, "sign": "Aquarius"},  # 10° Aqua
        ],
        "houses": [{"house": 1, "longitude": 0.0}],
        "aspects": [],
        "ascendant": 0.0,
        "midheaven": 270.0,
    }


# =============================================================================
# Test GET /api/v1/charts/{chart_id}/terms
# =============================================================================


class TestGetChartTerms:
    """Tests for GET /api/v1/charts/{chart_id}/terms endpoint."""

    @pytest.mark.asyncio
    async def test_requires_authentication(
        self,
        client: AsyncClient,
    ) -> None:
        """Should return 401 if not authenticated."""
        response = await client.get("/api/v1/charts/123e4567-e89b-12d3-a456-426614174000/terms")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_chart_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Should return 404 if chart doesn't exist."""
        response = await client.get(
            "/api/v1/charts/123e4567-e89b-12d3-a456-426614174000/terms",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_terms_for_chart(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        test_user,
        chart_data_with_planets: dict,
    ) -> None:
        """Should return term rulers for all planets in chart."""
        # Create a chart with planet data
        chart = BirthChart(
            user_id=test_user.id,
            person_name="Test Chart",
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
            birth_timezone="UTC",
            latitude=0.0,
            longitude=0.0,
            chart_data=chart_data_with_planets,
            status="completed",
        )
        db_session.add(chart)
        await db_session.commit()
        await db_session.refresh(chart)

        response = await client.get(
            f"/api/v1/charts/{chart.id}/terms",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "system" in data
        assert data["system"] == "egyptian"
        assert "planets" in data
        assert len(data["planets"]) == 7

        # Check planet info structure
        planet_info = data["planets"][0]
        assert "planet" in planet_info
        assert "term_ruler" in planet_info
        assert "in_own_term" in planet_info

        # Check summary
        assert "summary" in data
        assert "planets_in_own_term" in data["summary"]
        assert "term_ruler_frequency" in data["summary"]

    @pytest.mark.asyncio
    async def test_different_term_systems(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        test_user,
        chart_data_with_planets: dict,
    ) -> None:
        """Should support different term systems."""
        # Create chart
        chart = BirthChart(
            user_id=test_user.id,
            person_name="Test Chart",
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
            birth_timezone="UTC",
            latitude=0.0,
            longitude=0.0,
            chart_data=chart_data_with_planets,
            status="completed",
        )
        db_session.add(chart)
        await db_session.commit()
        await db_session.refresh(chart)

        # Test each system
        for system in ["egyptian", "ptolemaic", "chaldean", "dorothean"]:
            response = await client.get(
                f"/api/v1/charts/{chart.id}/terms?system={system}",
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["system"] == system

    @pytest.mark.asyncio
    async def test_invalid_system_parameter(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        test_user,
        chart_data_with_planets: dict,
    ) -> None:
        """Should return 422 for invalid system parameter."""
        chart = BirthChart(
            user_id=test_user.id,
            person_name="Test Chart",
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
            birth_timezone="UTC",
            latitude=0.0,
            longitude=0.0,
            chart_data=chart_data_with_planets,
            status="completed",
        )
        db_session.add(chart)
        await db_session.commit()
        await db_session.refresh(chart)

        response = await client.get(
            f"/api/v1/charts/{chart.id}/terms?system=invalid",
            headers=auth_headers,
        )
        assert response.status_code == 422


# =============================================================================
# Test GET /api/v1/dignities/term
# =============================================================================


class TestLookupTermRuler:
    """Tests for GET /api/v1/dignities/term endpoint."""

    @pytest.mark.asyncio
    async def test_basic_lookup(self, client: AsyncClient) -> None:
        """Should return term ruler for a longitude."""
        response = await client.get("/api/v1/dignities/term?longitude=0")
        assert response.status_code == 200

        data = response.json()
        assert data["sign"] == "Aries"
        assert data["degree_in_sign"] == 0.0
        assert data["term_ruler"] == "Jupiter"
        assert data["term_start"] == 0
        assert data["term_end"] == 6
        assert data["term_system"] == "egyptian"

    @pytest.mark.asyncio
    async def test_different_systems(self, client: AsyncClient) -> None:
        """Should support different term systems."""
        for system in ["egyptian", "ptolemaic", "chaldean", "dorothean"]:
            response = await client.get(f"/api/v1/dignities/term?longitude=0&system={system}")
            assert response.status_code == 200
            data = response.json()
            assert data["term_system"] == system

    @pytest.mark.asyncio
    async def test_various_longitudes(self, client: AsyncClient) -> None:
        """Should correctly handle various longitudes."""
        test_cases = [
            (0, "Aries", 0.0),
            (45, "Taurus", 15.0),
            (90, "Cancer", 0.0),
            (180, "Libra", 0.0),
            (270, "Capricorn", 0.0),
            (359.9, "Pisces", 29.9),
        ]

        for longitude, expected_sign, expected_degree in test_cases:
            response = await client.get(f"/api/v1/dignities/term?longitude={longitude}")
            assert response.status_code == 200
            data = response.json()
            assert data["sign"] == expected_sign
            assert abs(data["degree_in_sign"] - expected_degree) < 0.1

    @pytest.mark.asyncio
    async def test_longitude_required(self, client: AsyncClient) -> None:
        """Should return 422 if longitude is missing."""
        response = await client.get("/api/v1/dignities/term")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_longitude_negative(self, client: AsyncClient) -> None:
        """Should return 422 for negative longitude."""
        response = await client.get("/api/v1/dignities/term?longitude=-1")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_longitude_too_high(self, client: AsyncClient) -> None:
        """Should return 422 for longitude >= 360."""
        response = await client.get("/api/v1/dignities/term?longitude=360")
        assert response.status_code == 422


# =============================================================================
# Test GET /api/v1/dignities/terms/table
# =============================================================================


class TestGetTermsTable:
    """Tests for GET /api/v1/dignities/terms/table endpoint."""

    @pytest.mark.asyncio
    async def test_returns_full_table(self, client: AsyncClient) -> None:
        """Should return complete terms table with all 12 signs."""
        response = await client.get("/api/v1/dignities/terms/table")
        assert response.status_code == 200

        data = response.json()
        assert data["system"] == "egyptian"
        assert len(data["signs"]) == 12

        # Check all signs are present
        expected_signs = [
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
        for sign in expected_signs:
            assert sign in data["signs"]
            assert len(data["signs"][sign]) == 5  # 5 terms per sign

    @pytest.mark.asyncio
    async def test_term_entry_structure(self, client: AsyncClient) -> None:
        """Each term entry should have ruler, start, and end."""
        response = await client.get("/api/v1/dignities/terms/table")
        assert response.status_code == 200

        data = response.json()
        aries_terms = data["signs"]["Aries"]

        for term in aries_terms:
            assert "ruler" in term
            assert "start" in term
            assert "end" in term
            assert term["ruler"] in ["Saturn", "Jupiter", "Mars", "Venus", "Mercury"]
            assert 0 <= term["start"] < 30
            assert 0 < term["end"] <= 30

    @pytest.mark.asyncio
    async def test_different_systems(self, client: AsyncClient) -> None:
        """Should return different tables for different systems."""
        egyptian = await client.get("/api/v1/dignities/terms/table?system=egyptian")
        ptolemaic = await client.get("/api/v1/dignities/terms/table?system=ptolemaic")
        chaldean = await client.get("/api/v1/dignities/terms/table?system=chaldean")

        assert egyptian.status_code == 200
        assert ptolemaic.status_code == 200
        assert chaldean.status_code == 200

        egyptian_data = egyptian.json()
        ptolemaic_data = ptolemaic.json()
        chaldean_data = chaldean.json()

        # Systems should be different
        assert egyptian_data["system"] == "egyptian"
        assert ptolemaic_data["system"] == "ptolemaic"
        assert chaldean_data["system"] == "chaldean"

        # Chaldean should have regular 8-7-6-5-4 pattern
        aries_chaldean = chaldean_data["signs"]["Aries"]
        degrees = [t["end"] - t["start"] for t in aries_chaldean]
        assert degrees == [8, 7, 6, 5, 4]

    @pytest.mark.asyncio
    async def test_no_auth_required(self, client: AsyncClient) -> None:
        """Reference endpoints should not require authentication."""
        response = await client.get("/api/v1/dignities/terms/table")
        assert response.status_code == 200


# =============================================================================
# Test Venus in own term scenario
# =============================================================================


class TestPlanetsInOwnTerm:
    """Test scenarios where planets are in their own terms."""

    @pytest.mark.asyncio
    async def test_venus_in_own_term_taurus(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        test_user,
    ) -> None:
        """Venus at 5° Taurus should be in own term (0-8° Taurus = Venus)."""
        chart_data = {
            "planets": [
                {"name": "Venus", "longitude": 35.0, "sign": "Taurus"},  # 5° Taurus
            ],
            "houses": [],
            "aspects": [],
            "ascendant": 0.0,
        }

        chart = BirthChart(
            user_id=test_user.id,
            person_name="Venus Test",
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
            birth_timezone="UTC",
            latitude=0.0,
            longitude=0.0,
            chart_data=chart_data,
            status="completed",
        )
        db_session.add(chart)
        await db_session.commit()
        await db_session.refresh(chart)

        response = await client.get(
            f"/api/v1/charts/{chart.id}/terms",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        venus_info = next(p for p in data["planets"] if p["planet"] == "Venus")
        assert venus_info["term_ruler"] == "Venus"
        assert venus_info["in_own_term"] is True
        assert "Venus" in data["summary"]["planets_in_own_term"]
