"""Unit tests for WorkflowExecutionService and PostgreSQL repository."""

import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the service and models only for type checking
if TYPE_CHECKING:
    from engine_core.models.workflow import (  # type: ignore
        WorkflowExecution,
        WorkflowExecutionStatus,
    )
    from engine_core.services.workflow_service import (  # type: ignore
        MockWorkflowRepository,
        PostgreSQLWorkflowExecutionRepository,
        WorkflowExecutionService,
    )

# Try to import at runtime, skip tests if not available
try:
    from engine_core.models.workflow import (  # type: ignore
        WorkflowExecution,
        WorkflowExecutionStatus,
    )
    from engine_core.services.workflow_service import (  # type: ignore
        MockWorkflowRepository,
        PostgreSQLWorkflowExecutionRepository,
        WorkflowExecutionService,
    )
except ImportError:
    pytest.skip(
        "Workflow execution service not available", allow_module_level=True
    )


class TestWorkflowExecutionService:
    """Test cases for WorkflowExecutionService."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        return AsyncMock()

    @pytest.fixture
    def execution_service(self, mock_repository):
        """Create a WorkflowExecutionService with mock repository."""
        return WorkflowExecutionService(mock_repository)

    @pytest.mark.asyncio
    async def test_create_execution(self, execution_service, mock_repository):
        """Test creating a new workflow execution."""
        # Setup mock
        mock_execution = MagicMock()
        mock_execution.execution_id = "test_exec_123"
        mock_repository.create_workflow_execution.return_value = mock_execution

        # Execute
        result = await execution_service.create_execution(
            workflow_id="test_workflow",
            workflow_name="Test Workflow",
            user_id="user123",
            input_data={"test": "data"},
        )

        # Assert
        assert result == mock_execution
        mock_repository.create_workflow_execution.assert_called_once()
        call_args = mock_repository.create_workflow_execution.call_args[1]
        assert call_args["workflow_id"] == "test_workflow"
        assert call_args["workflow_name"] == "Test Workflow"
        assert call_args["user_id"] == "user123"
        assert call_args["input_data"] == {"test": "data"}

    @pytest.mark.asyncio
    async def test_start_execution(self, execution_service, mock_repository):
        """Test starting an execution."""
        # Setup mock
        mock_execution = MagicMock()
        mock_repository.update_workflow_execution.return_value = mock_execution

        # Execute
        result = await execution_service.start_execution("exec_123")

        # Assert
        assert result == mock_execution
        mock_repository.update_workflow_execution.assert_called_once_with(
            "exec_123",
            {
                "status": WorkflowExecutionStatus.RUNNING.value,
                "started_at": mock_repository.update_workflow_execution.call_args[
                    1
                ][
                    "updates"
                ][
                    "started_at"
                ],
            },
        )

    @pytest.mark.asyncio
    async def test_complete_execution_success(
        self, execution_service, mock_repository
    ):
        """Test completing an execution successfully."""
        # Setup mock
        mock_execution = MagicMock()
        mock_execution.started_at = datetime.utcnow() - timedelta(seconds=10)
        mock_repository.update_workflow_execution.return_value = mock_execution

        # Execute
        result = await execution_service.complete_execution(
            "exec_123", success=True, output_data={"result": "success"}
        )

        # Assert
        assert result == mock_execution
        # Should have been called twice: once for completion, once for duration
        assert mock_repository.update_workflow_execution.call_count == 2

    @pytest.mark.asyncio
    async def test_fail_execution(self, execution_service, mock_repository):
        """Test failing an execution."""
        # Setup mock
        mock_execution = MagicMock()
        mock_execution.started_at = datetime.utcnow() - timedelta(seconds=5)
        mock_repository.update_workflow_execution.return_value = mock_execution

        # Execute
        result = await execution_service.fail_execution(
            "exec_123", "Test error message"
        )

        # Assert
        assert result == mock_execution
        # Should have been called twice: once for failure, once for duration
        assert mock_repository.update_workflow_execution.call_count == 2

    @pytest.mark.asyncio
    async def test_get_execution_analytics(
        self, execution_service, mock_repository
    ):
        """Test getting execution analytics."""
        # Setup mock
        mock_repository.get_execution_analytics.return_value = {
            "total_executions": 10,
            "successful_executions": 8,
            "success_rate": 0.8,
        }

        # Execute
        result = await execution_service.get_execution_analytics(
            "workflow_123"
        )

        # Assert
        assert result["total_executions"] == 10
        assert result["successful_executions"] == 8
        assert result["success_rate"] == 0.8
        mock_repository.get_execution_analytics.assert_called_once_with(
            "workflow_123"
        )


class TestPostgreSQLWorkflowExecutionRepository:
    """Test cases for PostgreSQLWorkflowExecutionRepository."""

    @pytest.fixture
    def mock_session_factory(self):
        """Create a mock session factory."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session_factory):
        """Create a PostgreSQL repository with mock session factory."""
        return PostgreSQLWorkflowExecutionRepository(mock_session_factory)

    @pytest.mark.asyncio
    async def test_create_workflow_execution(
        self, repository, mock_session_factory
    ):
        """Test creating a workflow execution in PostgreSQL."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_execution = MagicMock()
        mock_session_factory.return_value = mock_session
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        # Mock the WorkflowExecution constructor
        with patch(
            "engine_core.services.workflow_service.WorkflowExecution"
        ) as mock_wf_exec:
            mock_wf_exec.return_value = mock_execution

            # Execute
            result = await repository.create_workflow_execution(
                {"workflow_id": "test_workflow", "execution_id": "test_exec"}
            )

            # Assert
            assert result == mock_execution
            mock_session.add.assert_called_once_with(mock_execution)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_execution)

    @pytest.mark.asyncio
    async def test_get_workflow_execution(
        self, repository, mock_session_factory
    ):
        """Test getting a workflow execution by ID."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_execution = MagicMock()
        mock_session_factory.return_value = mock_session
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_execution

        # Execute
        result = await repository.get_workflow_execution("exec_123")

        # Assert
        assert result == mock_execution
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_workflow_executions(
        self, repository, mock_session_factory
    ):
        """Test getting workflow executions."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_executions = [MagicMock(), MagicMock()]
        mock_session_factory.return_value = mock_session
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value = mock_executions

        # Execute
        result = await repository.get_workflow_executions(
            "workflow_123", limit=10
        )

        # Assert
        assert result == mock_executions
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_execution_analytics_no_executions(
        self, repository, mock_session_factory
    ):
        """Test getting analytics when no executions exist."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session_factory.return_value = mock_session
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value = []

        # Execute
        result = await repository.get_execution_analytics("workflow_123")

        # Assert
        expected = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "success_rate": 0.0,
            "average_duration": 0.0,
            "last_execution_at": None,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_execution_analytics_with_executions(
        self, repository, mock_session_factory
    ):
        """Test getting analytics with executions."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session_factory.return_value = mock_session
        mock_session.execute.return_value = mock_result

        # Create mock executions
        mock_exec1 = MagicMock()
        mock_exec1.is_successful = True
        mock_exec1.duration_seconds = 10.0
        mock_exec1.created_at = datetime.utcnow()

        mock_exec2 = MagicMock()
        mock_exec2.is_successful = False
        mock_exec2.duration_seconds = 5.0
        mock_exec2.created_at = datetime.utcnow() - timedelta(hours=1)

        mock_result.scalars.return_value = [mock_exec1, mock_exec2]

        # Execute
        result = await repository.get_execution_analytics("workflow_123")

        # Assert
        assert result["total_executions"] == 2
        assert result["successful_executions"] == 1
        assert result["failed_executions"] == 1
        assert result["success_rate"] == 0.5
        assert result["average_duration"] == 7.5  # (10 + 5) / 2


class TestMockWorkflowRepository:
    """Test cases for MockWorkflowRepository."""

    @pytest.fixture
    def mock_repo(self):
        """Create a MockWorkflowRepository."""
        return MockWorkflowRepository()

    @pytest.mark.asyncio
    async def test_create_workflow(self, mock_repo):
        """Test creating a workflow in mock repository."""
        workflow_data = {
            "id": "test_workflow",
            "name": "Test Workflow",
            "description": "A test workflow",
        }

        result = await mock_repo.create_workflow(workflow_data)

        assert result.id == "test_workflow"
        assert result.name == "Test Workflow"
        assert result.description == "A test workflow"
        assert mock_repo.workflows["test_workflow"]["id"] == "test_workflow"

    @pytest.mark.asyncio
    async def test_get_workflow_by_id(self, mock_repo):
        """Test getting a workflow by ID."""
        # First create a workflow
        workflow_data = {"id": "test_workflow", "name": "Test"}
        await mock_repo.create_workflow(workflow_data)

        # Then retrieve it
        result = await mock_repo.get_workflow_by_id("test_workflow")

        assert result is not None
        assert result.id == "test_workflow"
        assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_workflow(self, mock_repo):
        """Test getting a workflow that doesn't exist."""
        result = await mock_repo.get_workflow_by_id("nonexistent")

        assert result is None
