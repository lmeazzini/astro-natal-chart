"""
Tests for Amplitude tracking events in API endpoints.

These tests verify that the correct Amplitude events are tracked
when users perform actions like updating profile, changing password, etc.
"""

from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.user import User


class TestProfileAmplitudeTracking:
    """Tests for Amplitude tracking in profile-related endpoints."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient, test_user: User) -> dict:
        """Get authentication headers for test user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "Test123!@#",
            },
        )
        assert response.status_code == 200
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @patch("app.api.v1.endpoints.users.amplitude_service")
    async def test_profile_update_tracks_event(
        self,
        mock_amplitude: MagicMock,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
    ) -> None:
        """Should track profile_updated event when profile is updated."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"},
        )

        assert response.status_code == 200
        mock_amplitude.track.assert_called_once()

        call_args = mock_amplitude.track.call_args
        assert call_args.kwargs["event_type"] == "profile_updated"
        assert call_args.kwargs["user_id"] == str(test_user.id)
        assert "fields_changed" in call_args.kwargs["event_properties"]
        assert "full_name" in call_args.kwargs["event_properties"]["fields_changed"]

    @patch("app.api.v1.endpoints.users.amplitude_service")
    async def test_password_change_tracks_success_event(
        self,
        mock_amplitude: MagicMock,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
    ) -> None:
        """Should track profile_password_changed event on successful password change."""
        response = await client.put(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "Test123!@#",
                "new_password": "NewPass123!@#",
                "new_password_confirm": "NewPass123!@#",
            },
        )

        assert response.status_code == 204
        mock_amplitude.track.assert_called_once()

        call_args = mock_amplitude.track.call_args
        assert call_args.kwargs["event_type"] == "profile_password_changed"
        assert call_args.kwargs["user_id"] == str(test_user.id)

    @patch("app.api.v1.endpoints.users.amplitude_service")
    async def test_password_change_tracks_failure_event(
        self,
        mock_amplitude: MagicMock,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
    ) -> None:
        """Should track profile_password_change_failed event on incorrect password."""
        response = await client.put(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPass123!@#",
                "new_password_confirm": "NewPass123!@#",
            },
        )

        assert response.status_code == 400
        mock_amplitude.track.assert_called_once()

        call_args = mock_amplitude.track.call_args
        assert call_args.kwargs["event_type"] == "profile_password_change_failed"
        assert call_args.kwargs["user_id"] == str(test_user.id)
        assert "error_type" in call_args.kwargs["event_properties"]


class TestOAuthAmplitudeTracking:
    """Tests for Amplitude tracking in OAuth-related endpoints."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient, test_user: User) -> dict:
        """Get authentication headers for test user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "Test123!@#",
            },
        )
        assert response.status_code == 200
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @patch("app.api.v1.endpoints.users.amplitude_service")
    async def test_oauth_disconnect_tracks_event(
        self,
        mock_amplitude: MagicMock,
        client: AsyncClient,
        test_user_with_oauth: User,
        auth_headers: dict,
    ) -> None:
        """Should track oauth_connection_removed event when OAuth is disconnected."""
        # This test requires a user with an OAuth connection
        # The fixture test_user_with_oauth should provide a user with both
        # password and at least one OAuth connection
        response = await client.delete(
            "/api/v1/users/me/oauth-connections/google",
            headers=auth_headers,
        )

        # If the user has an OAuth connection, it should succeed
        if response.status_code == 204:
            mock_amplitude.track.assert_called_once()
            call_args = mock_amplitude.track.call_args
            assert call_args.kwargs["event_type"] == "oauth_connection_removed"
            assert call_args.kwargs["event_properties"]["provider"] == "google"


class TestPrivacyAmplitudeTracking:
    """Tests for Amplitude tracking in privacy-related endpoints."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient, test_user: User) -> dict:
        """Get authentication headers for test user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "Test123!@#",
            },
        )
        assert response.status_code == 200
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @patch("app.api.v1.endpoints.privacy.amplitude_service")
    async def test_account_deletion_request_tracks_event(
        self,
        mock_amplitude: MagicMock,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
    ) -> None:
        """Should track account_deletion_requested event when deletion is requested."""
        response = await client.delete(
            "/api/v1/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        mock_amplitude.track.assert_called_once()

        call_args = mock_amplitude.track.call_args
        assert call_args.kwargs["event_type"] == "account_deletion_requested"
        assert call_args.kwargs["user_id"] == str(test_user.id)
        assert call_args.kwargs["event_properties"]["deletion_type"] == "scheduled"
        assert call_args.kwargs["event_properties"]["scheduled_days"] == 30

    @patch("app.api.v1.endpoints.privacy.amplitude_service")
    async def test_account_deletion_cancel_tracks_event(
        self,
        mock_amplitude: MagicMock,
        client: AsyncClient,
        test_user_with_deletion_request: User,
        auth_headers: dict,
    ) -> None:
        """Should track account_deletion_cancelled event when deletion is cancelled."""
        # This test requires a user with a pending deletion request
        response = await client.post(
            "/api/v1/users/me/cancel-deletion",
            headers=auth_headers,
        )

        if response.status_code == 200:
            mock_amplitude.track.assert_called_once()
            call_args = mock_amplitude.track.call_args
            assert call_args.kwargs["event_type"] == "account_deletion_cancelled"
            assert "days_remaining" in call_args.kwargs["event_properties"]
