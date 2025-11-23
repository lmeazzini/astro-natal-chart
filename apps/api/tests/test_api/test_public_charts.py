"""
Tests for Public Charts API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_public_charts(client: AsyncClient):
    """Test listing public charts without authentication."""
    response = await client.get("/api/v1/public-charts")
    assert response.status_code == 200

    data = response.json()
    assert "charts" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["charts"], list)


@pytest.mark.asyncio
async def test_list_public_charts_with_category_filter(client: AsyncClient):
    """Test filtering public charts by category."""
    response = await client.get("/api/v1/public-charts?category=scientist")
    assert response.status_code == 200

    data = response.json()
    assert "charts" in data
    # All returned charts should be in the scientist category
    for chart in data["charts"]:
        assert chart["category"] == "scientist"


@pytest.mark.asyncio
async def test_list_public_charts_with_search(client: AsyncClient):
    """Test searching public charts by name."""
    response = await client.get("/api/v1/public-charts?search=einstein")
    assert response.status_code == 200

    data = response.json()
    assert "charts" in data


@pytest.mark.asyncio
async def test_list_public_charts_with_sort(client: AsyncClient):
    """Test sorting public charts."""
    # Sort by name
    response = await client.get("/api/v1/public-charts?sort=name")
    assert response.status_code == 200

    # Sort by views
    response = await client.get("/api/v1/public-charts?sort=views")
    assert response.status_code == 200

    # Sort by date
    response = await client.get("/api/v1/public-charts?sort=date")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_public_charts_pagination(client: AsyncClient):
    """Test pagination of public charts."""
    response = await client.get("/api/v1/public-charts?page=1&page_size=5")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["charts"]) <= 5


@pytest.mark.asyncio
async def test_get_featured_charts(client: AsyncClient):
    """Test getting featured public charts."""
    response = await client.get("/api/v1/public-charts/featured")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    # All returned charts should be featured
    for chart in data:
        assert chart["featured"] is True


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient):
    """Test getting categories with counts."""
    response = await client.get("/api/v1/public-charts/categories")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    # Each category should have category name and count
    for category in data:
        assert "category" in category
        assert "count" in category


@pytest.mark.asyncio
async def test_get_public_chart_by_slug(client: AsyncClient):
    """Test getting a public chart by slug."""
    # First list to get a valid slug
    list_response = await client.get("/api/v1/public-charts")
    charts = list_response.json()["charts"]

    if not charts:
        pytest.skip("No public charts available for testing")

    slug = charts[0]["slug"]

    # Get the chart by slug
    response = await client.get(f"/api/v1/public-charts/{slug}")
    assert response.status_code == 200

    data = response.json()
    assert data["slug"] == slug
    assert "full_name" in data
    assert "chart_data" in data
    assert "birth_datetime" in data


@pytest.mark.asyncio
async def test_get_public_chart_not_found(client: AsyncClient):
    """Test getting a non-existent public chart."""
    response = await client.get("/api/v1/public-charts/non-existent-slug")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_endpoints_require_auth(client: AsyncClient):
    """Test that admin endpoints require authentication/authorization."""
    # Try to create without auth - returns 403 (Forbidden) because
    # require_admin dependency checks for admin role after authentication
    response = await client.post(
        "/api/v1/admin/public-charts",
        json={
            "slug": "test-chart",
            "full_name": "Test Person",
            "birth_datetime": "2000-01-01T12:00:00Z",
            "birth_timezone": "UTC",
            "latitude": 0,
            "longitude": 0,
        },
    )
    assert response.status_code == 403

    # Try to list admin without auth
    response = await client.get("/api/v1/admin/public-charts")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_view_count_increments(client: AsyncClient):
    """Test that view count increments when viewing a chart."""
    # First list to get a valid slug
    list_response = await client.get("/api/v1/public-charts")
    charts = list_response.json()["charts"]

    if not charts:
        pytest.skip("No public charts available for testing")

    slug = charts[0]["slug"]
    initial_view_count = charts[0]["view_count"]

    # Get the chart (should increment view count)
    await client.get(f"/api/v1/public-charts/{slug}")

    # Get it again to check if view count increased
    response = await client.get(f"/api/v1/public-charts/{slug}")
    data = response.json()

    # View count should have increased by at least 1
    assert data["view_count"] >= initial_view_count + 1
