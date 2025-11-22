"""
Tests for chart_service.py - Update functionality
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.schemas.chart import BirthChartUpdate
from app.services.chart_service import (
    ChartNotFoundError,
    _needs_recalculation,
    update_birth_chart,
)


class TestNeedsRecalculation:
    """Tests for _needs_recalculation helper function."""

    def test_no_changes_returns_false(self):
        """No changes should not trigger recalculation."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(person_name="New Name")

        result = _needs_recalculation(update_data, chart)
        assert result is False

    def test_name_change_only_returns_false(self):
        """Name change should not trigger recalculation."""
        chart = MagicMock()
        chart.person_name = "Old Name"

        update_data = BirthChartUpdate(person_name="New Name")

        result = _needs_recalculation(update_data, chart)
        assert result is False

    def test_notes_change_only_returns_false(self):
        """Notes change should not trigger recalculation."""
        chart = MagicMock()
        chart.notes = "Old notes"

        update_data = BirthChartUpdate(notes="New notes")

        result = _needs_recalculation(update_data, chart)
        assert result is False

    def test_datetime_change_returns_true(self):
        """Datetime change should trigger recalculation."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(
            birth_datetime=datetime(1990, 5, 15, 12, 0)
        )

        result = _needs_recalculation(update_data, chart)
        assert result is True

    def test_timezone_change_returns_true(self):
        """Timezone change should trigger recalculation."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(birth_timezone="America/New_York")

        result = _needs_recalculation(update_data, chart)
        assert result is True

    def test_latitude_change_returns_true(self):
        """Latitude change should trigger recalculation."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(latitude=-22.9068)

        result = _needs_recalculation(update_data, chart)
        assert result is True

    def test_longitude_change_returns_true(self):
        """Longitude change should trigger recalculation."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(longitude=-43.1729)

        result = _needs_recalculation(update_data, chart)
        assert result is True

    def test_house_system_change_returns_true(self):
        """House system change should trigger recalculation."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(house_system="whole_sign")

        result = _needs_recalculation(update_data, chart)
        assert result is True

    def test_same_value_returns_false(self):
        """Same value should not trigger recalculation."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        # Sending same value
        update_data = BirthChartUpdate(house_system="placidus")

        result = _needs_recalculation(update_data, chart)
        assert result is False

    def test_multiple_fields_with_one_change_returns_true(self):
        """Multiple fields with at least one recalc field changed should return True."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"
        chart.person_name = "Old Name"

        update_data = BirthChartUpdate(
            person_name="New Name",  # No recalc
            latitude=-22.9068  # Recalc needed
        )

        result = _needs_recalculation(update_data, chart)
        assert result is True


class TestUpdateBirthChart:
    """Tests for update_birth_chart function."""

    @pytest.mark.asyncio
    async def test_update_without_recalculation(self):
        """Update without birth data changes should not recalculate."""
        chart_id = uuid4()
        user_id = uuid4()

        mock_chart = MagicMock()
        mock_chart.id = chart_id
        mock_chart.user_id = user_id
        mock_chart.person_name = "Old Name"
        mock_chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        mock_chart.birth_timezone = "America/Sao_Paulo"
        mock_chart.latitude = -23.5505
        mock_chart.longitude = -46.6333
        mock_chart.house_system = "placidus"
        mock_chart.zodiac_type = "tropical"
        mock_chart.node_type = "true"

        update_data = BirthChartUpdate(person_name="New Name")

        with patch("app.services.chart_service.ChartRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            mock_repo_instance.get_by_id_and_user.return_value = mock_chart
            mock_repo_instance.update.return_value = mock_chart
            MockRepo.return_value = mock_repo_instance

            with patch("app.services.chart_service.calculate_birth_chart") as mock_calc:
                with patch("app.services.chart_service.AuditRepository") as MockAudit:
                    mock_audit_instance = AsyncMock()
                    MockAudit.return_value = mock_audit_instance

                    mock_db = AsyncMock()
                    result = await update_birth_chart(mock_db, chart_id, user_id, update_data)

                    # Should not call calculate_birth_chart
                    mock_calc.assert_not_called()
                    assert result.person_name == "New Name"

    @pytest.mark.asyncio
    async def test_update_with_recalculation(self):
        """Update with birth data changes should recalculate."""
        chart_id = uuid4()
        user_id = uuid4()

        mock_chart = MagicMock()
        mock_chart.id = chart_id
        mock_chart.user_id = user_id
        mock_chart.person_name = "Test Person"
        mock_chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        mock_chart.birth_timezone = "America/Sao_Paulo"
        mock_chart.latitude = -23.5505
        mock_chart.longitude = -46.6333
        mock_chart.house_system = "placidus"
        mock_chart.zodiac_type = "tropical"
        mock_chart.node_type = "true"
        mock_chart.chart_data = {}

        new_latitude = -22.9068
        update_data = BirthChartUpdate(latitude=new_latitude)

        mock_calculated_data = {"planets": [], "houses": [], "aspects": []}

        with patch("app.services.chart_service.ChartRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            mock_repo_instance.get_by_id_and_user.return_value = mock_chart
            mock_repo_instance.update.return_value = mock_chart
            MockRepo.return_value = mock_repo_instance

            with patch("app.services.chart_service.calculate_birth_chart") as mock_calc:
                mock_calc.return_value = mock_calculated_data

                with patch("app.services.chart_service.InterpretationService") as MockInterp:
                    mock_interp_instance = AsyncMock()
                    MockInterp.return_value = mock_interp_instance

                    with patch("app.services.chart_service.AuditRepository") as MockAudit:
                        mock_audit_instance = AsyncMock()
                        MockAudit.return_value = mock_audit_instance

                        mock_db = AsyncMock()
                        result = await update_birth_chart(mock_db, chart_id, user_id, update_data)

                        # Should call calculate_birth_chart
                        mock_calc.assert_called_once()
                        # Chart data should be updated
                        assert mock_chart.chart_data == mock_calculated_data
                        # Result should be the updated chart
                        assert result == mock_chart

    @pytest.mark.asyncio
    async def test_update_chart_not_found(self):
        """Update should raise ChartNotFoundError when chart doesn't exist."""
        chart_id = uuid4()
        user_id = uuid4()
        update_data = BirthChartUpdate(person_name="New Name")

        with patch("app.services.chart_service.ChartRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            mock_repo_instance.get_by_id_and_user.return_value = None
            MockRepo.return_value = mock_repo_instance

            mock_db = AsyncMock()

            with pytest.raises(ChartNotFoundError):
                await update_birth_chart(mock_db, chart_id, user_id, update_data)

    @pytest.mark.asyncio
    async def test_update_unauthorized_access(self):
        """Update should raise UnauthorizedAccessError when user doesn't own chart."""
        chart_id = uuid4()
        user_id = uuid4()
        other_user_id = uuid4()

        mock_chart = MagicMock()
        mock_chart.id = chart_id
        mock_chart.user_id = other_user_id  # Different user owns this chart

        update_data = BirthChartUpdate(person_name="New Name")

        with patch("app.services.chart_service.ChartRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            # Simulate chart belonging to another user
            mock_repo_instance.get_by_id_and_user.return_value = None
            MockRepo.return_value = mock_repo_instance

            mock_db = AsyncMock()

            with pytest.raises(ChartNotFoundError):
                await update_birth_chart(mock_db, chart_id, user_id, update_data)

    @pytest.mark.asyncio
    async def test_update_creates_audit_log(self):
        """Update should create an audit log entry."""
        chart_id = uuid4()
        user_id = uuid4()

        mock_chart = MagicMock()
        mock_chart.id = chart_id
        mock_chart.user_id = user_id
        mock_chart.person_name = "Old Name"
        mock_chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        mock_chart.birth_timezone = "America/Sao_Paulo"
        mock_chart.latitude = -23.5505
        mock_chart.longitude = -46.6333
        mock_chart.house_system = "placidus"
        mock_chart.zodiac_type = "tropical"
        mock_chart.node_type = "true"

        update_data = BirthChartUpdate(person_name="New Name")

        with patch("app.services.chart_service.ChartRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            mock_repo_instance.get_by_id_and_user.return_value = mock_chart
            mock_repo_instance.update.return_value = mock_chart
            MockRepo.return_value = mock_repo_instance

            with patch("app.services.chart_service.AuditRepository") as MockAudit:
                mock_audit_instance = AsyncMock()
                MockAudit.return_value = mock_audit_instance

                mock_db = AsyncMock()
                await update_birth_chart(mock_db, chart_id, user_id, update_data)

                # Verify audit log was created
                mock_audit_instance.create_log.assert_called_once()
                call_args = mock_audit_instance.create_log.call_args
                assert call_args.kwargs["user_id"] == user_id
                assert call_args.kwargs["action"] == "update_chart"
                assert call_args.kwargs["resource_type"] == "chart"
                assert call_args.kwargs["resource_id"] == chart_id
                assert "fields_updated" in call_args.kwargs["extra_data"]
                assert "recalculated" in call_args.kwargs["extra_data"]
