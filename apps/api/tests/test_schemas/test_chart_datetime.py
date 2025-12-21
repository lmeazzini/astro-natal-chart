"""
Tests for birth_datetime timezone handling in chart schemas.

These tests ensure that:
1. Timezone-aware datetimes are correctly converted to UTC for storage
2. Naive datetimes are rejected with a clear error message
3. Various ISO 8601 formats are handled correctly

Related bug fix: Frontend was sending local time without proper timezone interpretation,
causing birth times to be stored incorrectly (e.g., 19:30 São Paulo stored as 19:30 UTC
instead of 22:30 UTC).
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.chart import BirthChartCreate, BirthChartUpdate


class TestBirthChartCreateTimezone:
    """Tests for BirthChartCreate.birth_datetime validation."""

    def test_iso_with_positive_offset_converted_to_utc(self):
        """ISO string with positive offset (+05:30) is converted to UTC."""
        data = {
            "person_name": "Test User",
            "birth_datetime": "2024-12-03T14:30:00+05:30",  # India (UTC+5:30)
            "birth_timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
        }
        chart = BirthChartCreate(**data)

        # 14:30 +05:30 = 09:00 UTC
        assert chart.birth_datetime.hour == 9
        assert chart.birth_datetime.minute == 0
        assert chart.birth_datetime.tzinfo == UTC

    def test_iso_with_negative_offset_converted_to_utc(self):
        """ISO string with negative offset (-03:00) is converted to UTC."""
        data = {
            "person_name": "Test User",
            "birth_datetime": "2024-12-03T14:30:00-03:00",  # São Paulo (UTC-3)
            "birth_timezone": "America/Sao_Paulo",
            "latitude": -23.5505,
            "longitude": -46.6333,
        }
        chart = BirthChartCreate(**data)

        # 14:30 -03:00 = 17:30 UTC
        assert chart.birth_datetime.hour == 17
        assert chart.birth_datetime.minute == 30
        assert chart.birth_datetime.tzinfo == UTC

    def test_iso_with_z_suffix_treated_as_utc(self):
        """ISO string with 'Z' suffix is correctly treated as UTC."""
        data = {
            "person_name": "Test User",
            "birth_datetime": "2024-12-03T20:00:00Z",
            "birth_timezone": "UTC",
            "latitude": 0.0,
            "longitude": 0.0,
        }
        chart = BirthChartCreate(**data)

        # Z = UTC, no conversion needed
        assert chart.birth_datetime.hour == 20
        assert chart.birth_datetime.minute == 0
        assert chart.birth_datetime.tzinfo == UTC

    def test_naive_datetime_raises_validation_error(self):
        """Naive datetime (no timezone info) raises ValidationError."""
        data = {
            "person_name": "Test User",
            "birth_datetime": "2024-12-03T14:30:00",  # No timezone!
            "birth_timezone": "America/Sao_Paulo",
            "latitude": -23.5505,
            "longitude": -46.6333,
        }

        with pytest.raises(ValidationError) as exc_info:
            BirthChartCreate(**data)

        # Verify error message mentions timezone requirement
        error_message = str(exc_info.value)
        assert "timezone-aware" in error_message.lower() or "timezone" in error_message.lower()

    def test_datetime_object_with_tzinfo_converted_to_utc(self):
        """Python datetime object with tzinfo is converted to UTC."""
        from zoneinfo import ZoneInfo

        sao_paulo_tz = ZoneInfo("America/Sao_Paulo")
        birth_dt = datetime(2024, 12, 3, 14, 30, 0, tzinfo=sao_paulo_tz)

        data = {
            "person_name": "Test User",
            "birth_datetime": birth_dt,
            "birth_timezone": "America/Sao_Paulo",
            "latitude": -23.5505,
            "longitude": -46.6333,
        }
        chart = BirthChartCreate(**data)

        # 14:30 São Paulo (UTC-3) = 17:30 UTC
        assert chart.birth_datetime.hour == 17
        assert chart.birth_datetime.minute == 30
        assert chart.birth_datetime.tzinfo == UTC

    def test_midnight_crossing_handled_correctly(self):
        """Datetime that crosses midnight when converted to UTC is handled correctly."""
        data = {
            "person_name": "Test User",
            "birth_datetime": "2024-12-03T22:30:00-05:00",  # New York (UTC-5)
            "birth_timezone": "America/New_York",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }
        chart = BirthChartCreate(**data)

        # 22:30 -05:00 = 03:30 UTC (next day)
        assert chart.birth_datetime.day == 4  # Crosses to next day
        assert chart.birth_datetime.hour == 3
        assert chart.birth_datetime.minute == 30


class TestBirthChartUpdateTimezone:
    """Tests for BirthChartUpdate.birth_datetime validation."""

    def test_update_with_timezone_offset_converted_to_utc(self):
        """Update with timezone offset is converted to UTC."""
        data = {"birth_datetime": "2024-12-03T14:30:00-03:00"}
        update = BirthChartUpdate(**data)

        # 14:30 -03:00 = 17:30 UTC
        assert update.birth_datetime is not None
        assert update.birth_datetime.hour == 17
        assert update.birth_datetime.tzinfo == UTC

    def test_update_with_none_datetime_allowed(self):
        """Update with None birth_datetime is allowed (no update)."""
        data = {"person_name": "New Name"}
        update = BirthChartUpdate(**data)

        assert update.birth_datetime is None
        assert update.person_name == "New Name"

    def test_update_with_naive_datetime_raises_error(self):
        """Update with naive datetime raises ValidationError."""
        data = {"birth_datetime": "2024-12-03T14:30:00"}  # No timezone!

        with pytest.raises(ValidationError) as exc_info:
            BirthChartUpdate(**data)

        error_message = str(exc_info.value)
        assert "timezone" in error_message.lower()


class TestTimezoneEdgeCases:
    """Edge cases for timezone handling."""

    def test_dst_transition_handled_correctly(self):
        """Daylight Saving Time transitions are handled correctly."""
        # March 10, 2024: DST starts in US (clocks spring forward at 2:00 AM)
        # Before DST: EST (UTC-5), After DST: EDT (UTC-4)
        data = {
            "person_name": "Test User",
            "birth_datetime": "2024-03-10T10:30:00-04:00",  # EDT (after spring forward)
            "birth_timezone": "America/New_York",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }
        chart = BirthChartCreate(**data)

        # 10:30 EDT (UTC-4) = 14:30 UTC
        assert chart.birth_datetime.hour == 14
        assert chart.birth_datetime.minute == 30

    def test_various_timezone_formats_accepted(self):
        """Various ISO 8601 timezone formats are accepted."""
        test_cases = [
            ("2024-12-03T14:30:00+00:00", 14, 30),  # +00:00
            ("2024-12-03T14:30:00Z", 14, 30),  # Z
            ("2024-12-03T14:30:00-03:00", 17, 30),  # -03:00
            ("2024-12-03T14:30:00+05:30", 9, 0),  # +05:30
            ("2024-12-03T14:30:00-11:00", 1, 30),  # -11:00 (crosses day)
        ]

        for iso_string, expected_hour, expected_minute in test_cases:
            data = {
                "person_name": "Test User",
                "birth_datetime": iso_string,
                "birth_timezone": "UTC",  # Timezone field doesn't affect conversion
                "latitude": 0.0,
                "longitude": 0.0,
            }
            chart = BirthChartCreate(**data)
            assert (
                chart.birth_datetime.hour == expected_hour
            ), f"Failed for {iso_string}: expected hour {expected_hour}, got {chart.birth_datetime.hour}"
            assert (
                chart.birth_datetime.minute == expected_minute
            ), f"Failed for {iso_string}: expected minute {expected_minute}, got {chart.birth_datetime.minute}"
