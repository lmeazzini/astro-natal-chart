"""
Tests for Amplitude Analytics service.
"""

from unittest.mock import MagicMock, patch

from app.services.amplitude_service import AmplitudeService


class TestAmplitudeServiceInitialization:
    """Test service initialization under different configurations."""

    @patch("app.services.amplitude_service.settings")
    def test_service_disabled_by_default(self, mock_settings: MagicMock) -> None:
        """Service should be disabled when AMPLITUDE_ENABLED is False."""
        mock_settings.AMPLITUDE_ENABLED = False
        mock_settings.AMPLITUDE_API_KEY = None

        service = AmplitudeService()

        assert service.enabled is False
        assert service.client is None

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    def test_service_enabled_with_valid_key(
        self, mock_amplitude: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Service should initialize when enabled with valid API key."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-api-key"

        service = AmplitudeService()

        assert service.enabled is True
        assert service.client is not None
        mock_amplitude.assert_called_once_with("test-api-key")

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.logger")
    def test_service_disabled_when_key_missing(
        self, mock_logger: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Service should disable itself if enabled but API key is missing."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = None

        service = AmplitudeService()

        assert service.enabled is False
        assert service.client is None
        mock_logger.warning.assert_called_once()


class TestAmplitudeServicePropertyValidation:
    """Test property validation and sanitization."""

    @patch("app.services.amplitude_service.settings")
    def test_validate_empty_properties(self, mock_settings: MagicMock) -> None:
        """Should return empty dict for None properties."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        result = service._validate_properties(None)

        assert result == {}

    @patch("app.services.amplitude_service.settings")
    def test_validate_valid_properties(self, mock_settings: MagicMock) -> None:
        """Should accept all valid property types."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        properties = {
            "string_prop": "value",
            "int_prop": 42,
            "float_prop": 3.14,
            "bool_prop": True,
            "list_prop": ["item1", "item2"],
        }

        result = service._validate_properties(properties)

        assert result == properties

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.logger")
    def test_validate_truncates_long_strings(
        self, mock_logger: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Should truncate strings longer than MAX_PROPERTY_LENGTH."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        long_string = "x" * 2000
        properties = {"long_value": long_string}

        result = service._validate_properties(properties)

        assert len(result["long_value"]) == service.MAX_PROPERTY_LENGTH  # type: ignore[arg-type]
        mock_logger.warning.assert_called_once()

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.logger")
    def test_validate_skips_invalid_types(
        self, mock_logger: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Should skip properties with invalid types."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        properties = {
            "valid": "value",
            "invalid_dict": {"nested": "dict"},
            "invalid_tuple": (1, 2, 3),
        }

        result = service._validate_properties(properties)

        assert result == {"valid": "value"}
        assert mock_logger.warning.call_count == 2

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.logger")
    def test_validate_skips_invalid_list_elements(
        self, mock_logger: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Should skip lists containing non-string elements."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        properties = {
            "valid_list": ["item1", "item2"],
            "invalid_list": [1, 2, 3],
            "mixed_list": ["string", 123],
        }

        result = service._validate_properties(properties)

        assert result == {"valid_list": ["item1", "item2"]}
        assert mock_logger.warning.call_count == 2

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.logger")
    def test_validate_skips_invalid_keys(
        self, mock_logger: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Should skip properties with invalid keys."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        properties = {
            "valid_key": "value",
            "": "empty_key",  # Invalid: empty string
        }

        result = service._validate_properties(properties)

        assert result == {"valid_key": "value"}
        mock_logger.warning.assert_called_once()


class TestAmplitudeServiceTrack:
    """Test event tracking functionality."""

    @patch("app.services.amplitude_service.settings")
    def test_track_noop_when_disabled(self, mock_settings: MagicMock) -> None:
        """Should not track events when service is disabled."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        # Should not raise any exceptions
        service.track(event_type="test_event")

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    def test_track_event_success(
        self, mock_amplitude_class: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Should track event when enabled."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_amplitude_class.return_value = mock_client

        service = AmplitudeService()
        service.track(
            event_type="chart_created",
            user_id="user123",
            event_properties={"chart_type": "natal"},
        )

        mock_client.track.assert_called_once()

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    @patch("app.services.amplitude_service.logger")
    def test_track_handles_exceptions(
        self,
        mock_logger: MagicMock,
        mock_amplitude_class: MagicMock,
        mock_settings: MagicMock,
    ) -> None:
        """Should log errors without crashing when tracking fails."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_client.track.side_effect = Exception("Network error")
        mock_amplitude_class.return_value = mock_client

        service = AmplitudeService()
        # Should not raise exception
        service.track(event_type="test_event")

        mock_logger.error.assert_called_once()

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    def test_track_validates_properties(
        self, mock_amplitude_class: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Should validate properties before tracking."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_amplitude_class.return_value = mock_client

        service = AmplitudeService()
        service.track(
            event_type="test_event",
            event_properties={
                "valid": "value",
                "invalid": {"nested": "dict"},  # Should be filtered out
            },
        )

        # Verify that only valid properties were passed to Amplitude
        call_args = mock_client.track.call_args
        event = call_args[0][0]
        assert "valid" in event.event_properties
        assert "invalid" not in event.event_properties


class TestAmplitudeServiceIdentify:
    """Test user identification functionality."""

    @patch("app.services.amplitude_service.settings")
    def test_identify_noop_when_disabled(self, mock_settings: MagicMock) -> None:
        """Should not identify users when service is disabled."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        # Should not raise any exceptions
        service.identify(user_id="user123")

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    def test_identify_user_success(
        self, mock_amplitude_class: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Should identify user when enabled."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_amplitude_class.return_value = mock_client

        service = AmplitudeService()
        service.identify(
            user_id="user123",
            user_properties={"plan": "premium", "locale": "pt-BR"},
        )

        mock_client.identify.assert_called_once()

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    @patch("app.services.amplitude_service.logger")
    def test_identify_handles_exceptions(
        self,
        mock_logger: MagicMock,
        mock_amplitude_class: MagicMock,
        mock_settings: MagicMock,
    ) -> None:
        """Should log errors without crashing when identification fails."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_client.identify.side_effect = Exception("Network error")
        mock_amplitude_class.return_value = mock_client

        service = AmplitudeService()
        # Should not raise exception
        service.identify(user_id="user123")

        mock_logger.error.assert_called_once()


class TestAmplitudeServiceFlush:
    """Test flush functionality."""

    @patch("app.services.amplitude_service.settings")
    def test_flush_noop_when_disabled(self, mock_settings: MagicMock) -> None:
        """Should not flush when service is disabled."""
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()
        # Should not raise any exceptions
        service.flush()

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    def test_flush_success(self, mock_amplitude_class: MagicMock, mock_settings: MagicMock) -> None:
        """Should flush events when enabled."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_amplitude_class.return_value = mock_client

        service = AmplitudeService()
        service.flush()

        mock_client.flush.assert_called_once()

    @patch("app.services.amplitude_service.settings")
    @patch("app.services.amplitude_service.Amplitude")
    @patch("app.services.amplitude_service.logger")
    def test_flush_handles_exceptions(
        self,
        mock_logger: MagicMock,
        mock_amplitude_class: MagicMock,
        mock_settings: MagicMock,
    ) -> None:
        """Should log errors without crashing when flush fails."""
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_client.flush.side_effect = Exception("Network error")
        mock_amplitude_class.return_value = mock_client

        service = AmplitudeService()
        # Should not raise exception
        service.flush()

        mock_logger.error.assert_called_once()
