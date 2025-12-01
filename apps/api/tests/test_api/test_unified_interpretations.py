"""
Tests for unified interpretations endpoint.

This module tests the unified interpretations API endpoint that returns
all 5 interpretation types with intelligent 3-tier caching.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

pytestmark = pytest.mark.asyncio


class TestUnifiedInterpretationsEndpoint:
    """Test suite for unified interpretations endpoint."""

    async def test_get_unified_interpretations_requires_auth(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
    ):
        """Test that endpoint requires authentication."""
        chart = await test_chart_factory(user=test_user, status="completed")
        response = await client.get(f"/api/v1/charts/{chart.id}/interpretations")

        assert response.status_code == 401

    async def test_get_unified_interpretations_requires_verified_email(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        db_session: AsyncSession,
    ):
        """Test that endpoint requires verified email."""
        chart = await test_chart_factory(user=test_user, status="completed")

        # Unverify user
        test_user.email_verified = False
        await db_session.commit()

        # Get auth token
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "Test123!@#"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Try to access endpoint
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "email_not_verified" in response.json()["detail"]["error"]

    async def test_get_unified_interpretations_chart_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test 404 when chart doesn't exist."""
        from uuid import uuid4

        fake_chart_id = uuid4()
        response = await client.get(
            f"/api/v1/charts/{fake_chart_id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_get_unified_interpretations_unauthorized_access(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        test_user_factory,
        db_session: AsyncSession,
    ):
        """Test that users can't access other users' charts.

        Note: Returns 404 (not 403) to avoid revealing existence of other users' charts.
        This is a security best practice.
        """
        # Create a chart for test_user
        chart = await test_chart_factory(user=test_user, status="completed")

        # Create another user
        other_user = await test_user_factory(email="other@example.com")
        await db_session.commit()

        # Get auth token for other user
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": other_user.email, "password": "Test123!@#"},
        )
        token = response.json()["access_token"]

        # Try to access chart (belongs to test_user)
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Returns 404 to not reveal existence of other users' charts (security best practice)
        assert response.status_code == 404

    async def test_get_unified_interpretations_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test successful retrieval of all interpretation types."""
        chart = await test_chart_factory(user=test_user, status="completed")
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "planets" in data
        assert "houses" in data
        assert "aspects" in data
        assert "arabic_parts" in data
        assert "growth" in data
        assert "metadata" in data
        assert "language" in data

        # Verify metadata structure
        metadata = data["metadata"]
        assert "total_items" in metadata
        assert "cache_hits_db" in metadata
        assert "cache_hits_cache" in metadata
        assert "rag_generations" in metadata
        assert "outdated_count" in metadata
        assert "documents_used" in metadata
        assert "current_prompt_version" in metadata
        assert "response_time_ms" in metadata

        # Verify we have some interpretations
        assert len(data["planets"]) > 0
        assert len(data["houses"]) > 0

    async def test_get_unified_interpretations_partial_regeneration(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test partial regeneration of specific types."""
        chart = await test_chart_factory(user=test_user, status="completed")

        # First request to populate cache
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Second request with partial regeneration
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations?regenerate=planets,houses",
            headers=auth_headers,
        )
        assert response.status_code == 200
        second_data = response.json()

        # Should have regenerated planets and houses
        assert second_data["metadata"]["rag_generations"] >= 11 + 12  # 11 planets + 12 houses

    async def test_get_unified_interpretations_invalid_regenerate_param(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test invalid regenerate parameter validation."""
        chart = await test_chart_factory(user=test_user, status="completed")
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations?regenerate=invalid_type",
            headers=auth_headers,
        )

        # Should reject invalid parameter
        assert response.status_code == 422  # Validation error

    async def test_get_unified_interpretations_language_from_user_locale(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test that language is taken from user locale."""
        chart = await test_chart_factory(user=test_user, status="completed")
        # Update user locale to en-US
        test_user.locale = "en-US"
        await db_session.commit()

        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en-US"

    async def test_interpretation_item_metadata(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test that each interpretation item has proper metadata."""
        chart = await test_chart_factory(user=test_user, status="completed")
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Check a planet interpretation
        if data["planets"]:
            planet_key = list(data["planets"].keys())[0]
            planet_interp = data["planets"][planet_key]

            # Verify InterpretationItemWithMeta fields
            assert "content" in planet_interp
            assert "source" in planet_interp  # 'database', 'cache', or 'rag'
            assert "rag_sources" in planet_interp
            assert "is_outdated" in planet_interp
            assert "cached" in planet_interp
            assert "generated_at" in planet_interp
            assert "interpretation_type" in planet_interp
            assert "subject" in planet_interp
            assert "prompt_version" in planet_interp
            assert "openai_model" in planet_interp

    async def test_growth_suggestions_structure(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test that growth suggestions have proper structure."""
        chart = await test_chart_factory(user=test_user, status="completed")
        response = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify growth suggestions structure
        growth = data["growth"]
        assert growth is not None
        assert "growth_points" in growth
        assert "challenges" in growth
        assert "opportunities" in growth
        assert "purpose" in growth
        assert "summary" in growth

    async def test_caching_improves_performance(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test that second request is faster (cached)."""
        chart = await test_chart_factory(user=test_user, status="completed")

        # First request (cold start)
        response1 = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )
        assert response1.status_code == 200
        time1 = response1.json()["metadata"]["response_time_ms"]

        # Second request (warm cache)
        response2 = await client.get(
            f"/api/v1/charts/{chart.id}/interpretations",
            headers=auth_headers,
        )
        assert response2.status_code == 200
        time2 = response2.json()["metadata"]["response_time_ms"]

        # Second request should be faster (or similar if very fast)
        assert time2 <= time1 * 1.5  # Allow 50% margin

        # Check cache hit statistics
        metadata2 = response2.json()["metadata"]
        assert metadata2["cache_hits_db"] > 0 or metadata2["cache_hits_cache"] > 0
