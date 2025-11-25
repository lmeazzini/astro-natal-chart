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

    def __init__(self) -> None:
        """Initialize Amplitude client."""
        self.enabled = settings.AMPLITUDE_ENABLED
        self.client: Amplitude | None = None

        if self.enabled:
            if not settings.AMPLITUDE_API_KEY:
                logger.warning("Amplitude is enabled but API key is missing")
                self.enabled = False
            else:
                self.client = Amplitude(settings.AMPLITUDE_API_KEY)
                logger.info("Amplitude Analytics initialized")
        else:
            logger.info("Amplitude Analytics disabled")

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
        if not self.enabled or not self.client:
            return

        try:
            event = BaseEvent(
                event_type=event_type,
                user_id=user_id,
                device_id=device_id,
                event_properties=event_properties or {},
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
        if not self.enabled or not self.client:
            return

        try:
            identify_obj = Identify()

            if user_properties:
                for key, value in user_properties.items():
                    identify_obj.set(key, value)

            self.client.identify(identify_obj, EventOptions(user_id=user_id))
            logger.debug(f"Amplitude user identified: {user_id}")

        except Exception as e:
            logger.error(f"Failed to identify user '{user_id}' in Amplitude: {e}")

    def flush(self) -> None:
        """Flush pending events to Amplitude (useful for testing and shutdown)."""
        if not self.enabled or not self.client:
            return

        try:
            self.client.flush()
            logger.debug("Amplitude events flushed")
        except Exception as e:
            logger.error(f"Failed to flush Amplitude events: {e}")


# Global instance
amplitude_service = AmplitudeService()
