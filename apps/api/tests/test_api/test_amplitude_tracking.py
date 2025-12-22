"""
Tests for Amplitude tracking events in API endpoints.

These tests verify that the correct Amplitude events are tracked
when users perform actions like updating profile, changing password, etc.
"""

from unittest.mock import MagicMock, patch

from httpx import AsyncClient

from app.models.user import User


class TestProfileAmplitudeTracking:
    """Tests for Amplitude tracking in profile-related endpoints."""

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

    @patch("app.api.v1.endpoints.users.amplitude_service")
    async def test_oauth_disconnect_tracks_event(
        self,
        mock_amplitude: MagicMock,
        client: AsyncClient,
        test_user_with_oauth: User,
    ) -> None:
        """Should track oauth_connection_removed event when OAuth is disconnected."""
        from app.core.security import create_access_token

        # Create auth headers for the user with OAuth
        access_token = create_access_token(data={"sub": str(test_user_with_oauth.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.delete(
            "/api/v1/users/me/oauth-connections/google",
            headers=headers,
        )

        assert response.status_code == 204
        mock_amplitude.track.assert_called_once()

        call_args = mock_amplitude.track.call_args
        assert call_args.kwargs["event_type"] == "oauth_connection_removed"
        assert call_args.kwargs["user_id"] == str(test_user_with_oauth.id)
        assert call_args.kwargs["event_properties"]["provider"] == "google"


class TestPrivacyAmplitudeTracking:
    """Tests for Amplitude tracking in privacy-related endpoints."""

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
    ) -> None:
        """Should track account_deletion_cancelled event when deletion is cancelled."""
        from app.core.security import create_access_token

        # Create auth headers for the user with deletion request
        access_token = create_access_token(data={"sub": str(test_user_with_deletion_request.id)})
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.post(
            "/api/v1/users/me/cancel-deletion",
            headers=headers,
        )

        assert response.status_code == 200
        mock_amplitude.track.assert_called_once()

        call_args = mock_amplitude.track.call_args
        assert call_args.kwargs["event_type"] == "account_deletion_cancelled"
        assert call_args.kwargs["user_id"] == str(test_user_with_deletion_request.id)
        assert "days_remaining" in call_args.kwargs["event_properties"]
