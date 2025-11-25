"""
Timezone Service - Provides global timezone support.

Features:
- List all available IANA timezones
- Auto-detect timezone from coordinates
- Validate timezone strings
- Get timezone info (offset, DST status)
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, available_timezones

from loguru import logger
from timezonefinder import TimezoneFinder

# Initialize timezone finder (lazy loading)
_tf: TimezoneFinder | None = None


def _get_timezone_finder() -> TimezoneFinder:
    """Get or create TimezoneFinder instance (lazy loading for performance)."""
    global _tf
    if _tf is None:
        _tf = TimezoneFinder()
    return _tf


# Common timezone regions for grouping
TIMEZONE_REGIONS = {
    "America": "Americas",
    "Europe": "Europe",
    "Asia": "Asia",
    "Africa": "Africa",
    "Pacific": "Pacific",
    "Australia": "Australia",
    "Atlantic": "Atlantic",
    "Indian": "Indian Ocean",
    "Antarctica": "Antarctica",
    "Arctic": "Arctic",
    "Etc": "Other",
}

# Popular timezones to show first (most commonly used)
POPULAR_TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Sao_Paulo",
    "America/Mexico_City",
    "America/Buenos_Aires",
    "America/Toronto",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Madrid",
    "Europe/Rome",
    "Europe/Moscow",
    "Europe/Istanbul",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Hong_Kong",
    "Asia/Singapore",
    "Asia/Seoul",
    "Asia/Dubai",
    "Asia/Kolkata",
    "Asia/Bangkok",
    "Asia/Jakarta",
    "Australia/Sydney",
    "Australia/Melbourne",
    "Australia/Perth",
    "Pacific/Auckland",
    "Pacific/Honolulu",
    "Africa/Cairo",
    "Africa/Johannesburg",
    "Africa/Lagos",
]


class TimezoneInfo:
    """Timezone information container."""

    def __init__(
        self,
        timezone_id: str,
        reference_date: datetime | None = None,
    ):
        self.timezone_id = timezone_id
        self.reference_date = reference_date or datetime.now(UTC)
        self._tz = ZoneInfo(timezone_id)
        self._local_dt = self.reference_date.astimezone(self._tz)

    @property
    def name(self) -> str:
        """Human-readable timezone name."""
        # Convert America/Sao_Paulo to "Sao Paulo"
        parts = self.timezone_id.split("/")
        if len(parts) > 1:
            return parts[-1].replace("_", " ")
        return self.timezone_id

    @property
    def region(self) -> str:
        """Get timezone region."""
        parts = self.timezone_id.split("/")
        if len(parts) > 0:
            return TIMEZONE_REGIONS.get(parts[0], "Other")
        return "Other"

    @property
    def offset_seconds(self) -> int:
        """UTC offset in seconds."""
        offset = self._local_dt.utcoffset()
        return int(offset.total_seconds()) if offset else 0

    @property
    def offset_hours(self) -> float:
        """UTC offset in hours."""
        return self.offset_seconds / 3600

    @property
    def offset_string(self) -> str:
        """Formatted UTC offset string (e.g., 'UTC-03:00')."""
        hours = self.offset_seconds // 3600
        minutes = abs(self.offset_seconds % 3600) // 60
        sign = "+" if hours >= 0 else "-"
        return f"UTC{sign}{abs(hours):02d}:{minutes:02d}"

    @property
    def is_dst(self) -> bool:
        """Whether currently in daylight saving time."""
        dst = self._local_dt.dst()
        return bool(dst and dst.total_seconds() > 0)

    @property
    def abbreviation(self) -> str:
        """Timezone abbreviation (e.g., 'BRT', 'EST')."""
        return self._local_dt.strftime("%Z")

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.timezone_id,
            "name": self.name,
            "region": self.region,
            "offset": self.offset_string,
            "offset_hours": self.offset_hours,
            "is_dst": self.is_dst,
            "abbreviation": self.abbreviation,
        }


class TimezoneService:
    """Service for timezone operations."""

    @staticmethod
    def get_all_timezones() -> list[str]:
        """Get all available IANA timezone identifiers."""
        # Filter out deprecated/obscure timezones
        all_tzs = available_timezones()
        valid_tzs = [
            tz
            for tz in all_tzs
            if not tz.startswith(("Etc/", "SystemV/", "US/", "Canada/", "Brazil/"))
            and "/" in tz  # Exclude simple names like "UTC", "GMT"
        ]
        return sorted(valid_tzs)

    @staticmethod
    def get_popular_timezones() -> list[str]:
        """Get list of popular/common timezones."""
        return POPULAR_TIMEZONES.copy()

    @staticmethod
    def is_valid_timezone(timezone_id: str) -> bool:
        """Check if timezone identifier is valid."""
        try:
            ZoneInfo(timezone_id)
            return True
        except (KeyError, ValueError):
            return False

    @staticmethod
    def get_timezone_info(
        timezone_id: str,
        reference_date: datetime | None = None,
    ) -> TimezoneInfo | None:
        """Get detailed timezone information."""
        try:
            return TimezoneInfo(timezone_id, reference_date)
        except (KeyError, ValueError):
            return None

    @staticmethod
    def detect_timezone_from_coordinates(
        latitude: float,
        longitude: float,
    ) -> str | None:
        """
        Detect timezone from geographic coordinates.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees

        Returns:
            IANA timezone identifier or None if not found
        """
        try:
            tf = _get_timezone_finder()
            timezone_id = tf.timezone_at(lat=latitude, lng=longitude)
            if timezone_id:
                logger.debug(
                    f"Detected timezone {timezone_id} for coordinates ({latitude}, {longitude})"
                )
            return timezone_id
        except Exception as e:
            logger.warning(
                f"Failed to detect timezone for coordinates ({latitude}, {longitude}): {e}"
            )
            return None

    @staticmethod
    def get_historical_offset(
        timezone_id: str,
        date: datetime,
    ) -> tuple[float, bool] | None:
        """
        Get UTC offset for a specific historical date.

        This is important for birth charts as timezone rules
        may have changed since the birth date.

        Args:
            timezone_id: IANA timezone identifier
            date: The date to check

        Returns:
            Tuple of (offset_hours, is_dst) or None if invalid
        """
        try:
            tz = ZoneInfo(timezone_id)
            # Create timezone-aware datetime
            if date.tzinfo is None:
                dt_local = date.replace(tzinfo=tz)
            else:
                dt_local = date.astimezone(tz)

            offset = dt_local.utcoffset()
            dst = dt_local.dst()

            offset_hours = offset.total_seconds() / 3600 if offset else 0
            is_dst = bool(dst and dst.total_seconds() > 0)

            return (offset_hours, is_dst)
        except (KeyError, ValueError) as e:
            logger.warning(f"Failed to get historical offset: {e}")
            return None

    @staticmethod
    def search_timezones(
        query: str,
        limit: int = 20,
    ) -> list[dict]:
        """
        Search timezones by name, city, or region.

        Args:
            query: Search query (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching timezone info dictionaries
        """
        query_lower = query.lower().replace(" ", "_")
        all_tzs = TimezoneService.get_all_timezones()

        # Score and sort results
        scored_results: list[tuple[int, str]] = []

        for tz in all_tzs:
            tz_lower = tz.lower()
            score = 0

            # Exact match in city name
            if query_lower in tz_lower.split("/")[-1]:
                score = 100
            # Match in full timezone ID
            elif query_lower in tz_lower:
                score = 50
            # Match in region
            elif query_lower in tz_lower.split("/")[0]:
                score = 25

            if score > 0:
                # Boost popular timezones
                if tz in POPULAR_TIMEZONES:
                    score += 10
                scored_results.append((score, tz))

        # Sort by score (descending), then alphabetically
        scored_results.sort(key=lambda x: (-x[0], x[1]))

        # Convert to timezone info
        results = []
        for _, tz_id in scored_results[:limit]:
            info = TimezoneService.get_timezone_info(tz_id)
            if info:
                results.append(info.to_dict())

        return results

    @staticmethod
    def list_timezones_grouped(
        include_offset: bool = True,
    ) -> dict[str, list[dict]]:
        """
        List all timezones grouped by region.

        Returns:
            Dictionary with region names as keys and timezone lists as values
        """
        all_tzs = TimezoneService.get_all_timezones()
        grouped: dict[str, list[dict]] = {}

        for tz_id in all_tzs:
            info = TimezoneService.get_timezone_info(tz_id)
            if info:
                region = info.region
                if region not in grouped:
                    grouped[region] = []

                tz_data = info.to_dict() if include_offset else {"id": tz_id, "name": info.name}
                grouped[region].append(tz_data)

        # Sort timezones within each region by offset then name
        for region in grouped:
            grouped[region].sort(key=lambda x: (x.get("offset_hours", 0), x.get("name", "")))

        return grouped


# Singleton instance for convenience
timezone_service = TimezoneService()
