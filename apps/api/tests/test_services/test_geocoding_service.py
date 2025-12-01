"""
Tests for geocoding service.

Tests cover:
- Location search via Nominatim API
- Location search via OpenCage API
- Error handling (rate limit, timeout, invalid response)
- Result parsing and normalization
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.geocoding_service import GeocodingService, LocationResult


class TestLocationResult:
    """Tests for LocationResult class."""

    def test_create_location_result(self):
        """Test creating a LocationResult instance."""
        result = LocationResult(
            display_name="São Paulo, Brazil",
            latitude=-23.5505,
            longitude=-46.6333,
            city="São Paulo",
            country="Brazil",
            country_code="BR",
        )

        assert result.display_name == "São Paulo, Brazil"
        assert result.latitude == -23.5505
        assert result.longitude == -46.6333
        assert result.city == "São Paulo"
        assert result.country == "Brazil"
        assert result.country_code == "BR"

    def test_location_result_defaults(self):
        """Test LocationResult with default values."""
        result = LocationResult(
            display_name="Test Location",
            latitude=0.0,
            longitude=0.0,
        )

        assert result.city == ""
        assert result.country == ""
        assert result.country_code == ""


class TestGeocodingServiceInit:
    """Tests for GeocodingService initialization."""

    def test_init_sets_urls(self):
        """Test that initialization sets correct API URLs."""
        service = GeocodingService()

        assert "nominatim" in service.nominatim_url.lower()
        assert "opencagedata" in service.opencage_url

    def test_init_sets_timeout(self):
        """Test that initialization sets timeout."""
        service = GeocodingService()

        assert service.timeout == 10.0


class TestSearchNominatim:
    """Tests for Nominatim search functionality."""

    @pytest.mark.asyncio
    async def test_search_nominatim_success(self):
        """Test successful Nominatim search."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "São Paulo, Brazil",
                    "lat": "-23.5505",
                    "lon": "-46.6333",
                    "address": {
                        "city": "São Paulo",
                        "country": "Brazil",
                        "country_code": "br",
                    },
                }
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("São Paulo", 5)

            assert len(results) == 1
            assert results[0].city == "São Paulo"
            assert results[0].latitude == -23.5505
            assert results[0].longitude == -46.6333

    @pytest.mark.asyncio
    async def test_search_nominatim_empty_response(self):
        """Test Nominatim search with empty results."""
        mock_response = httpx.Response(status_code=200, json=[])

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("Nonexistent City XYZ", 5)

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_nominatim_http_error(self):
        """Test Nominatim search with HTTP error."""
        mock_response = httpx.Response(status_code=429)  # Rate limited

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("São Paulo", 5)

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_nominatim_timeout(self):
        """Test Nominatim search with timeout."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("São Paulo", 5)

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_nominatim_extracts_town(self):
        """Test that town is extracted when city is not present."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "Small Town, Country",
                    "lat": "10.0",
                    "lon": "20.0",
                    "address": {
                        "town": "Small Town",
                        "country": "Test Country",
                        "country_code": "tc",
                    },
                }
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("Small Town", 5)

            assert results[0].city == "Small Town"

    @pytest.mark.asyncio
    async def test_search_nominatim_extracts_village(self):
        """Test that village is extracted when city/town are not present."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "Village, Country",
                    "lat": "10.0",
                    "lon": "20.0",
                    "address": {
                        "village": "Test Village",
                        "country": "Test Country",
                        "country_code": "tc",
                    },
                }
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("Village", 5)

            assert results[0].city == "Test Village"

    @pytest.mark.asyncio
    async def test_search_nominatim_extracts_municipality(self):
        """Test that municipality is extracted as fallback."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "Municipality, Country",
                    "lat": "10.0",
                    "lon": "20.0",
                    "address": {
                        "municipality": "Test Municipality",
                        "country": "Test Country",
                        "country_code": "tc",
                    },
                }
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("Municipality", 5)

            assert results[0].city == "Test Municipality"

    @pytest.mark.asyncio
    async def test_search_nominatim_country_code_uppercase(self):
        """Test that country code is uppercased."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "City, Country",
                    "lat": "10.0",
                    "lon": "20.0",
                    "address": {
                        "city": "City",
                        "country": "Country",
                        "country_code": "xx",
                    },
                }
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("City", 5)

            assert results[0].country_code == "XX"


class TestSearchOpenCage:
    """Tests for OpenCage search functionality."""

    @pytest.mark.asyncio
    async def test_search_opencage_no_api_key(self):
        """Test OpenCage search returns empty when no API key."""
        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.OPENCAGE_API_KEY = None

            service = GeocodingService()
            results = await service._search_opencage("São Paulo", 5)

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_opencage_success(self):
        """Test successful OpenCage search."""
        mock_response = httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "formatted": "São Paulo, Brazil",
                        "geometry": {"lat": -23.5505, "lng": -46.6333},
                        "components": {
                            "city": "São Paulo",
                            "country": "Brazil",
                            "country_code": "br",
                        },
                    }
                ]
            },
        )

        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.OPENCAGE_API_KEY = "test_api_key"

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_response)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_instance

                service = GeocodingService()
                results = await service._search_opencage("São Paulo", 5)

                assert len(results) == 1
                assert results[0].city == "São Paulo"
                assert results[0].latitude == -23.5505

    @pytest.mark.asyncio
    async def test_search_opencage_http_error(self):
        """Test OpenCage search with HTTP error."""
        mock_response = httpx.Response(status_code=403)  # Forbidden

        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.OPENCAGE_API_KEY = "test_api_key"

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_response)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_instance

                service = GeocodingService()
                results = await service._search_opencage("São Paulo", 5)

                assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_opencage_empty_results(self):
        """Test OpenCage search with empty results."""
        mock_response = httpx.Response(
            status_code=200,
            json={"results": []},
        )

        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.OPENCAGE_API_KEY = "test_api_key"

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_response)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_instance

                service = GeocodingService()
                results = await service._search_opencage("Nonexistent XYZ", 5)

                assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_opencage_timeout(self):
        """Test OpenCage search with timeout."""
        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.OPENCAGE_API_KEY = "test_api_key"

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_instance

                service = GeocodingService()
                results = await service._search_opencage("São Paulo", 5)

                assert len(results) == 0


class TestSearchLocation:
    """Tests for main search_location method."""

    @pytest.mark.asyncio
    async def test_search_uses_nominatim_first(self):
        """Test that search uses Nominatim first."""
        service = GeocodingService()

        nominatim_results = [
            LocationResult(
                display_name="Test City",
                latitude=10.0,
                longitude=20.0,
            )
        ]

        with patch.object(service, "_search_nominatim", new_callable=AsyncMock) as mock_nominatim:
            mock_nominatim.return_value = nominatim_results

            results = await service.search_location("Test City")

            mock_nominatim.assert_called_once_with("Test City", 5)
            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_falls_back_to_opencage(self):
        """Test that search falls back to OpenCage when Nominatim fails."""
        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.OPENCAGE_API_KEY = "test_api_key"

            service = GeocodingService()

            opencage_results = [
                LocationResult(
                    display_name="Test City",
                    latitude=10.0,
                    longitude=20.0,
                )
            ]

            with patch.object(
                service, "_search_nominatim", new_callable=AsyncMock
            ) as mock_nominatim:
                mock_nominatim.return_value = []

                with patch.object(
                    service, "_search_opencage", new_callable=AsyncMock
                ) as mock_opencage:
                    mock_opencage.return_value = opencage_results

                    results = await service.search_location("Test City")

                    mock_nominatim.assert_called_once()
                    mock_opencage.assert_called_once()
                    assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_no_fallback_without_api_key(self):
        """Test that search doesn't fall back without OpenCage API key."""
        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.OPENCAGE_API_KEY = None

            service = GeocodingService()

            with patch.object(
                service, "_search_nominatim", new_callable=AsyncMock
            ) as mock_nominatim:
                mock_nominatim.return_value = []

                with patch.object(
                    service, "_search_opencage", new_callable=AsyncMock
                ) as mock_opencage:
                    results = await service.search_location("Test City")

                    mock_nominatim.assert_called_once()
                    mock_opencage.assert_not_called()
                    assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_respects_limit(self):
        """Test that search respects the limit parameter."""
        service = GeocodingService()

        with patch.object(service, "_search_nominatim", new_callable=AsyncMock) as mock_nominatim:
            mock_nominatim.return_value = []

            await service.search_location("Test", limit=10)

            mock_nominatim.assert_called_once_with("Test", 10)


class TestGetCoordinates:
    """Tests for get_coordinates method."""

    @pytest.mark.asyncio
    async def test_get_coordinates_success(self):
        """Test successful coordinate lookup."""
        service = GeocodingService()

        mock_result = LocationResult(
            display_name="São Paulo, Brazil",
            latitude=-23.5505,
            longitude=-46.6333,
            city="São Paulo",
            country="Brazil",
        )

        with patch.object(service, "search_location", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [mock_result]

            result = await service.get_coordinates("São Paulo", "Brazil")

            assert result is not None
            assert result.latitude == -23.5505
            mock_search.assert_called_once_with("São Paulo, Brazil", limit=1)

    @pytest.mark.asyncio
    async def test_get_coordinates_city_only(self):
        """Test coordinate lookup with city only."""
        service = GeocodingService()

        mock_result = LocationResult(
            display_name="Paris",
            latitude=48.8566,
            longitude=2.3522,
        )

        with patch.object(service, "search_location", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [mock_result]

            coords = await service.get_coordinates("Paris")

            mock_search.assert_called_once_with("Paris", limit=1)
            assert coords is not None

    @pytest.mark.asyncio
    async def test_get_coordinates_not_found(self):
        """Test coordinate lookup when location not found."""
        service = GeocodingService()

        with patch.object(service, "search_location", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []

            result = await service.get_coordinates("Nonexistent City XYZ")

            assert result is None


class TestSpecialCharacters:
    """Tests for handling special characters in queries."""

    @pytest.mark.asyncio
    async def test_search_with_accents(self):
        """Test search with accented characters."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "São Paulo, Brazil",
                    "lat": "-23.5505",
                    "lon": "-46.6333",
                    "address": {
                        "city": "São Paulo",
                        "country": "Brasil",
                        "country_code": "br",
                    },
                }
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("São Paulo", 5)

            assert len(results) == 1
            assert results[0].city == "São Paulo"

    @pytest.mark.asyncio
    async def test_search_with_unicode(self):
        """Test search with unicode characters."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "東京, Japan",
                    "lat": "35.6762",
                    "lon": "139.6503",
                    "address": {
                        "city": "東京",
                        "country": "日本",
                        "country_code": "jp",
                    },
                }
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("東京", 5)

            assert len(results) == 1
            assert results[0].city == "東京"


class TestMultipleResults:
    """Tests for handling multiple search results."""

    @pytest.mark.asyncio
    async def test_multiple_results_returned(self):
        """Test that multiple results are returned."""
        mock_response = httpx.Response(
            status_code=200,
            json=[
                {
                    "display_name": "Springfield, Illinois, USA",
                    "lat": "39.7817",
                    "lon": "-89.6501",
                    "address": {"city": "Springfield", "country": "USA", "country_code": "us"},
                },
                {
                    "display_name": "Springfield, Massachusetts, USA",
                    "lat": "42.1015",
                    "lon": "-72.5898",
                    "address": {"city": "Springfield", "country": "USA", "country_code": "us"},
                },
                {
                    "display_name": "Springfield, Missouri, USA",
                    "lat": "37.2090",
                    "lon": "-93.2923",
                    "address": {"city": "Springfield", "country": "USA", "country_code": "us"},
                },
            ],
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("Springfield", 5)

            assert len(results) == 3
            # All should be Springfield
            for result in results:
                assert result.city == "Springfield"


class TestNetworkErrors:
    """Tests for network error handling."""

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("Test City", 5)

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        """Test handling of generic exceptions."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=Exception("Unknown error"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            service = GeocodingService()
            results = await service._search_nominatim("Test City", 5)

            assert len(results) == 0
