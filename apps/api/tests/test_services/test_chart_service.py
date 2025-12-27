"""
Tests for chart_service.py - Update functionality and ChartService class
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.schemas.chart import BirthChartUpdate
from app.services.chart_service import (
    ChartNotFoundError,
    ChartService,
    UnauthorizedAccessError,
    _needs_recalculation,
    get_chart_service,
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

        update_data = BirthChartUpdate(birth_datetime=datetime(1990, 5, 15, 12, 0, tzinfo=UTC))

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
            latitude=-22.9068,  # Recalc needed
        )

        result = _needs_recalculation(update_data, chart)
        assert result is True


class TestUpdateBirthChart:
    """Tests for update_birth_chart function."""

    @pytest.mark.asyncio
    async def test_update_without_recalculation(self):
        """Update without birth data changes should not trigger Celery task."""
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

                with patch("app.services.chart_service.generate_birth_chart_task") as mock_task:
                    mock_db = AsyncMock()
                    result = await update_birth_chart(mock_db, chart_id, user_id, update_data)

                    # Should NOT dispatch Celery task (no recalc needed)
                    mock_task.delay.assert_not_called()
                    assert result.person_name == "New Name"

    @pytest.mark.asyncio
    async def test_update_with_recalculation(self):
        """Update with birth data changes should trigger Celery task for recalculation."""
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
        mock_chart.chart_data = {"planets": [], "houses": []}  # Has existing data

        new_latitude = -22.9068
        update_data = BirthChartUpdate(latitude=new_latitude)

        with patch("app.services.chart_service.ChartRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            mock_repo_instance.get_by_id_and_user.return_value = mock_chart
            mock_repo_instance.update.return_value = mock_chart
            MockRepo.return_value = mock_repo_instance

            with patch("app.services.chart_service.InterpretationRepository") as MockInterpRepo:
                mock_interp_repo = AsyncMock()
                mock_interp_repo.delete_by_chart_id.return_value = 5  # Mock deleted count
                MockInterpRepo.return_value = mock_interp_repo

                with patch("app.services.chart_service.AuditRepository") as MockAudit:
                    mock_audit_instance = AsyncMock()
                    MockAudit.return_value = mock_audit_instance

                    with patch("app.services.chart_service.generate_birth_chart_task") as mock_task:
                        mock_db = AsyncMock()
                        result = await update_birth_chart(mock_db, chart_id, user_id, update_data)

                        # Should dispatch Celery task for recalculation
                        mock_task.delay.assert_called_once_with(str(chart_id))
                        # Chart data should be cleared (will be regenerated by Celery task)
                        assert mock_chart.chart_data is None
                        # Status should be set to processing
                        assert mock_chart.status == "processing"
                        # Progress should be reset
                        assert mock_chart.progress == 0
                        # Interpretations should be deleted
                        mock_interp_repo.delete_by_chart_id.assert_called_once_with(chart_id)
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


# =============================================================================
# ChartService Class Tests (DI Pattern)
# =============================================================================


class TestChartServiceInit:
    """Tests for ChartService initialization and dependency injection."""

    def test_init_creates_repositories(self):
        """ChartService should initialize repositories with the provided session."""
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository") as MockInterpRepo:
                with patch("app.services.chart_service.AuditRepository") as MockAuditRepo:
                    service = ChartService(mock_db)

                    # Verify repositories were created with db session
                    MockChartRepo.assert_called_once_with(mock_db)
                    MockInterpRepo.assert_called_once_with(mock_db)
                    MockAuditRepo.assert_called_once_with(mock_db)

                    # Verify db is stored
                    assert service.db == mock_db

    def test_init_stores_repository_instances(self):
        """ChartService should store repository instances as attributes."""
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository") as MockInterpRepo:
                with patch("app.services.chart_service.AuditRepository") as MockAuditRepo:
                    mock_chart_repo = MagicMock()
                    mock_interp_repo = MagicMock()
                    mock_audit_repo = MagicMock()

                    MockChartRepo.return_value = mock_chart_repo
                    MockInterpRepo.return_value = mock_interp_repo
                    MockAuditRepo.return_value = mock_audit_repo

                    service = ChartService(mock_db)

                    assert service.chart_repo == mock_chart_repo
                    assert service.interp_repo == mock_interp_repo
                    assert service.audit_repo == mock_audit_repo


class TestChartServiceGetChartById:
    """Tests for ChartService.get_chart_by_id method."""

    @pytest.mark.asyncio
    async def test_get_chart_by_id_success(self):
        """get_chart_by_id should return chart when found."""
        chart_id = uuid4()
        user_id = uuid4()
        mock_chart = MagicMock()
        mock_chart.id = chart_id

        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    mock_repo = AsyncMock()
                    mock_repo.get_by_id_and_user.return_value = mock_chart
                    MockChartRepo.return_value = mock_repo

                    service = ChartService(mock_db)
                    result = await service.get_chart_by_id(chart_id, user_id)

                    assert result == mock_chart
                    mock_repo.get_by_id_and_user.assert_called_once_with(chart_id, user_id)

    @pytest.mark.asyncio
    async def test_get_chart_by_id_not_found(self):
        """get_chart_by_id should raise ChartNotFoundError when not found."""
        chart_id = uuid4()
        user_id = uuid4()
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    mock_repo = AsyncMock()
                    mock_repo.get_by_id_and_user.return_value = None
                    MockChartRepo.return_value = mock_repo

                    service = ChartService(mock_db)

                    with pytest.raises(ChartNotFoundError):
                        await service.get_chart_by_id(chart_id, user_id)

    @pytest.mark.asyncio
    async def test_get_chart_by_id_admin_access(self):
        """get_chart_by_id with is_admin=True should use get_by_id without user check."""
        chart_id = uuid4()
        mock_chart = MagicMock()
        mock_chart.id = chart_id

        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    mock_repo = AsyncMock()
                    mock_repo.get_by_id.return_value = mock_chart
                    MockChartRepo.return_value = mock_repo

                    service = ChartService(mock_db)
                    result = await service.get_chart_by_id(chart_id, is_admin=True)

                    assert result == mock_chart
                    mock_repo.get_by_id.assert_called_once_with(chart_id)
                    mock_repo.get_by_id_and_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_chart_by_id_requires_user_id_when_not_admin(self):
        """get_chart_by_id without is_admin should require user_id."""
        chart_id = uuid4()
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository"):
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    service = ChartService(mock_db)

                    with pytest.raises(UnauthorizedAccessError):
                        await service.get_chart_by_id(chart_id, user_id=None, is_admin=False)


class TestChartServiceStaticMethods:
    """Tests for ChartService static methods."""

    def test_needs_recalculation_is_static(self):
        """_needs_recalculation should be callable as a static method."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(person_name="New Name")

        # Call as static method (without instance)
        result = ChartService._needs_recalculation(update_data, chart)
        assert result is False

    def test_needs_recalculation_static_detects_changes(self):
        """Static _needs_recalculation should detect birth data changes."""
        chart = MagicMock()
        chart.birth_datetime = datetime(1990, 5, 15, 10, 30)
        chart.birth_timezone = "America/Sao_Paulo"
        chart.latitude = -23.5505
        chart.longitude = -46.6333
        chart.house_system = "placidus"
        chart.zodiac_type = "tropical"
        chart.node_type = "true"

        update_data = BirthChartUpdate(latitude=-22.9068)

        # Call as static method
        result = ChartService._needs_recalculation(update_data, chart)
        assert result is True


class TestGetChartServiceFactory:
    """Tests for get_chart_service FastAPI dependency factory."""

    def test_get_chart_service_returns_chart_service(self):
        """get_chart_service should return a ChartService instance."""
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository"):
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    result = get_chart_service(mock_db)

                    assert isinstance(result, ChartService)
                    assert result.db == mock_db


class TestChartServiceWithMockedRepos:
    """Tests demonstrating DI benefits - mocking repositories for unit tests."""

    @pytest.mark.asyncio
    async def test_count_user_charts_uses_repo(self):
        """count_user_charts should delegate to chart_repo."""
        user_id = uuid4()
        expected_count = 5
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    mock_repo = AsyncMock()
                    mock_repo.count_by_user.return_value = expected_count
                    MockChartRepo.return_value = mock_repo

                    service = ChartService(mock_db)
                    result = await service.count_user_charts(user_id)

                    assert result == expected_count
                    mock_repo.count_by_user.assert_called_once_with(
                        user_id=user_id, include_deleted=False
                    )

    @pytest.mark.asyncio
    async def test_get_user_charts_uses_repo(self):
        """get_user_charts should delegate to chart_repo."""
        user_id = uuid4()
        mock_charts = [MagicMock(), MagicMock()]
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    mock_repo = AsyncMock()
                    mock_repo.get_all_by_user.return_value = mock_charts
                    MockChartRepo.return_value = mock_repo

                    service = ChartService(mock_db)
                    result = await service.get_user_charts(user_id, skip=10, limit=20)

                    assert result == mock_charts
                    mock_repo.get_all_by_user.assert_called_once_with(
                        user_id=user_id, skip=10, limit=20, include_deleted=False
                    )

    @pytest.mark.asyncio
    async def test_delete_birth_chart_soft_delete(self):
        """delete_birth_chart should use soft delete by default."""
        chart_id = uuid4()
        user_id = uuid4()
        mock_chart = MagicMock()
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    mock_repo = AsyncMock()
                    mock_repo.get_by_id_and_user.return_value = mock_chart
                    MockChartRepo.return_value = mock_repo

                    service = ChartService(mock_db)
                    await service.delete_birth_chart(chart_id, user_id)

                    mock_repo.soft_delete.assert_called_once_with(mock_chart)
                    mock_repo.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_birth_chart_hard_delete(self):
        """delete_birth_chart with soft_delete=False should hard delete."""
        chart_id = uuid4()
        user_id = uuid4()
        mock_chart = MagicMock()
        mock_db = AsyncMock()

        with patch("app.services.chart_service.ChartRepository") as MockChartRepo:
            with patch("app.services.chart_service.InterpretationRepository"):
                with patch("app.services.chart_service.AuditRepository"):
                    mock_repo = AsyncMock()
                    mock_repo.get_by_id_and_user.return_value = mock_chart
                    MockChartRepo.return_value = mock_repo

                    service = ChartService(mock_db)
                    await service.delete_birth_chart(chart_id, user_id, soft_delete=False)

                    mock_repo.delete.assert_called_once_with(mock_chart)
                    mock_repo.soft_delete.assert_not_called()
