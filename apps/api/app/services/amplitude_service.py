"""
Amplitude Analytics service for product event tracking.

This service provides a simple wrapper around the Amplitude Python SDK
for tracking user events and product analytics.
"""

from amplitude import Amplitude, BaseEvent, EventOptions, Identify  # type: ignore[import-untyped]
from loguru import logger

from app.core.config import settings


class AmplitudeService:
    """Service for tracking events with Amplitude Analytics."""

    # Maximum length for string properties to prevent excessive data transmission
    MAX_PROPERTY_LENGTH = 1000

    def __init__(self) -> None:
        """Initialize Amplitude client."""
        if settings.AMPLITUDE_ENABLED and settings.AMPLITUDE_API_KEY:
            self.client: Amplitude = Amplitude(settings.AMPLITUDE_API_KEY)
            self.enabled = True
            logger.info("Amplitude Analytics initialized")
        else:
            self.client = None  # type: ignore[assignment]
            self.enabled = False
            if settings.AMPLITUDE_ENABLED and not settings.AMPLITUDE_API_KEY:
                logger.warning("Amplitude is enabled but API key is missing")
            else:
                logger.info("Amplitude Analytics disabled")

    def _validate_properties(
        self,
        properties: dict[str, str | int | float | bool | list[str]] | None,
    ) -> dict[str, str | int | float | bool | list[str]]:
        """
        Validate and sanitize event/user properties.

        Prevents sending excessive data or potentially problematic values.

        Args:
            properties: Raw properties dictionary

        Returns:
            Validated and sanitized properties dictionary
        """
        if not properties:
            return {}

        validated: dict[str, str | int | float | bool | list[str]] = {}

        for key, value in properties.items():
            # Validate key
            if not isinstance(key, str) or not key:
                logger.warning(f"Invalid property key: {key!r}, skipping")
                continue

            # Truncate long strings
            if isinstance(value, str) and len(value) > self.MAX_PROPERTY_LENGTH:
                logger.warning(
                    f"Property '{key}' is too large ({len(value)} chars), truncating to {self.MAX_PROPERTY_LENGTH}"
                )
                validated[key] = value[: self.MAX_PROPERTY_LENGTH]
            # Validate list elements
            elif isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    validated[key] = value
                else:
                    logger.warning(f"Property '{key}' contains non-string list items, skipping")
            # Accept other valid types
            elif isinstance(value, str | int | float | bool):
                validated[key] = value
            else:
                logger.warning(f"Property '{key}' has invalid type {type(value)}, skipping")

        return validated

    def track(
        self,
        event_type: str,
        user_id: str | None = None,
        device_id: str | None = None,
        event_properties: dict[str, str | int | float | bool | list[str]] | None = None,
    ) -> None:
        """
        Track an event with Amplitude.

        Args:
            event_type: Name of the event (e.g., "chart_created")
            user_id: Optional user identifier
            device_id: Optional device identifier
            event_properties: Optional event properties dictionary
        """
        if not self.enabled:
            return

        # Type narrowing: at this point, self.client is guaranteed to be Amplitude
        assert self.client is not None, "Client should be initialized when enabled"

        try:
            # Validate and sanitize properties
            validated_properties = self._validate_properties(event_properties)

            event = BaseEvent(
                event_type=event_type,
                user_id=user_id,
                device_id=device_id,
                event_properties=validated_properties,
            )

            self.client.track(event)
            logger.debug(f"Amplitude event tracked: {event_type}")

        except Exception as e:
            logger.error(f"Failed to track Amplitude event '{event_type}': {e}")

    def identify(
        self,
        user_id: str,
        user_properties: dict[str, str | int | float | bool | list[str]] | None = None,
    ) -> None:
        """
        Identify a user and set user properties.

        Args:
            user_id: User identifier
            user_properties: Optional user properties dictionary
        """
        if not self.enabled:
            return

        # Type narrowing: at this point, self.client is guaranteed to be Amplitude
        assert self.client is not None, "Client should be initialized when enabled"

        try:
            # Validate and sanitize properties
            validated_properties = self._validate_properties(user_properties)

            identify_obj = Identify()

            for key, value in validated_properties.items():
                identify_obj.set(key, value)

            self.client.identify(identify_obj, EventOptions(user_id=user_id))
            logger.debug(f"Amplitude user identified: {user_id}")

        except Exception as e:
            logger.error(f"Failed to identify user '{user_id}' in Amplitude: {e}")

    def flush(self) -> None:
        """Flush pending events to Amplitude (useful for testing and shutdown)."""
        if not self.enabled:
            return

        # Type narrowing: at this point, self.client is guaranteed to be Amplitude
        assert self.client is not None, "Client should be initialized when enabled"

        try:
            self.client.flush()
            logger.debug("Amplitude events flushed")
        except Exception as e:
            logger.error(f"Failed to flush Amplitude events: {e}")


# Global instance
amplitude_service = AmplitudeService()
