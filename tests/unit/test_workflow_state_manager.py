"""Tests for WorkflowStateManager - Redis-based volatile state management."""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from engine_cli.storage.workflow_state_manager import (
    WorkflowStateManager,
    WorkflowExecutionStatus,
    WorkflowExecutionState,
    VertexExecutionState
)


class TestWorkflowStateManager:
    """Test cases for WorkflowStateManager."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_client.get = AsyncMock(return_value=None)
        mock_client.setex = AsyncMock(return_value=True)
        mock_client.lpush = AsyncMock(return_value=1)
        mock_client.expire = AsyncMock(return_value=True)
        mock_client.lrange = AsyncMock(return_value=[])
        
        # Mock scan_iter to return an async iterable
        async def mock_scan_iter(pattern):
            # Return some mock keys
            yield b"workflow:execution:exec_1"
            yield b"workflow:execution:exec_2"
        
        mock_client.scan_iter = mock_scan_iter
        return mock_client

    @pytest.fixture
    def state_manager(self, mock_redis):
        """WorkflowStateManager instance with mocked Redis."""
        manager = WorkflowStateManager()
        manager.redis_client = mock_redis
        manager._connected = True
        return manager

    @pytest.mark.asyncio
    async def test_connect_success(self, mock_redis):
        """Test successful Redis connection."""
        manager = WorkflowStateManager()
        manager.redis_client = None

        with patch('redis.asyncio.from_url', return_value=mock_redis):
            await manager.connect()
            assert manager.is_connected()
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, mock_redis):
        """Test Redis connection failure."""
        mock_redis.ping.side_effect = Exception("Connection failed")
        manager = WorkflowStateManager(enable_fallback=False)  # Disable fallback for this test
        manager.redis_client = None

        with patch('redis.asyncio.from_url', return_value=mock_redis):
            with pytest.raises(Exception, match="Connection failed"):
                await manager.connect()

    @pytest.mark.asyncio
    async def test_create_execution(self, state_manager, mock_redis):
        """Test creating a new workflow execution."""
        execution_id = await state_manager.create_execution(
            workflow_id="test_workflow",
            workflow_name="Test Workflow",
            input_data={"param": "value"}
        )

        assert execution_id.startswith("wf_exec_test_workflow_")
        assert mock_redis.setex.called
        assert mock_redis.lpush.called

        # Verify the stored data
        call_args = mock_redis.setex.call_args
        stored_data = json.loads(call_args[0][2])  # Third argument is the JSON data
        assert stored_data["workflow_id"] == "test_workflow"
        assert stored_data["workflow_name"] == "Test Workflow"
        assert stored_data["state"] == "pending"
        assert stored_data["input_data"] == {"param": "value"}

    @pytest.mark.asyncio
    async def test_update_execution_state(self, state_manager, mock_redis):
        """Test updating execution state."""
        # Mock existing execution data
        existing_data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "pending",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        mock_redis.get.return_value = json.dumps(existing_data)

        await state_manager.update_execution_state(
            execution_id="test_exec_123",
            state=WorkflowExecutionState.RUNNING,
            current_vertex="vertex1",
            progress_percentage=25.0
        )

        # Verify update was called
        assert mock_redis.setex.called
        call_args = mock_redis.setex.call_args
        updated_data = json.loads(call_args[0][2])
        assert updated_data["state"] == "running"
        assert updated_data["current_vertex"] == "vertex1"
        assert updated_data["progress_percentage"] == 25.0

    @pytest.mark.asyncio
    async def test_update_vertex_state(self, state_manager, mock_redis):
        """Test updating vertex execution state."""
        # Mock existing execution data
        existing_data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        mock_redis.get.return_value = json.dumps(existing_data)

        await state_manager.update_vertex_state(
            execution_id="test_exec_123",
            vertex_id="vertex1",
            state=VertexExecutionState.COMPLETED,
            output_data={"result": "success"}
        )

        # Verify update was called
        assert mock_redis.setex.called
        call_args = mock_redis.setex.call_args
        updated_data = json.loads(call_args[0][2])
        assert "vertex1" in updated_data["vertex_states"]
        vertex_state = updated_data["vertex_states"]["vertex1"]
        assert vertex_state["state"] == "completed"
        assert vertex_state["output_data"] == {"result": "success"}

    @pytest.mark.asyncio
    async def test_set_execution_output(self, state_manager, mock_redis):
        """Test setting execution output."""
        existing_data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        mock_redis.get.return_value = json.dumps(existing_data)

        output_data = {"final_result": "workflow completed"}
        await state_manager.set_execution_output("test_exec_123", output_data)

        assert mock_redis.setex.called
        call_args = mock_redis.setex.call_args
        updated_data = json.loads(call_args[0][2])
        assert updated_data["output_data"] == output_data

    @pytest.mark.asyncio
    async def test_set_execution_error(self, state_manager, mock_redis):
        """Test setting execution error."""
        existing_data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        mock_redis.get.return_value = json.dumps(existing_data)

        error_message = "Workflow execution failed"
        await state_manager.set_execution_error("test_exec_123", error_message)

        assert mock_redis.setex.called
        call_args = mock_redis.setex.call_args
        updated_data = json.loads(call_args[0][2])
        assert updated_data["error_message"] == error_message
        assert updated_data["state"] == "failed"
        assert "end_time" in updated_data

    @pytest.mark.asyncio
    async def test_get_execution_status(self, state_manager, mock_redis):
        """Test getting execution status."""
        execution_data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": datetime.now().isoformat(),
            "input_data": {"param": "value"},
            "vertex_states": {},
            "progress_percentage": 50.0
        }
        mock_redis.get.return_value = json.dumps(execution_data)

        status = await state_manager.get_execution_status("test_exec_123")

        assert status is not None
        assert status.execution_id == "test_exec_123"
        assert status.workflow_id == "test_workflow"
        assert status.state == WorkflowExecutionState.RUNNING
        assert status.progress_percentage == 50.0

    @pytest.mark.asyncio
    async def test_get_execution_status_not_found(self, state_manager, mock_redis):
        """Test getting status for non-existent execution."""
        mock_redis.get.return_value = None

        status = await state_manager.get_execution_status("non_existent")

        assert status is None

    @pytest.mark.asyncio
    async def test_get_workflow_executions(self, state_manager, mock_redis):
        """Test getting executions for a workflow."""
        # Mock execution IDs from Redis list
        mock_redis.lrange.return_value = [
            b"exec_1",
            b"exec_2"
        ]

        # Mock execution data
        exec_data_1 = {
            "execution_id": "exec_1",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "completed",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        exec_data_2 = {
            "execution_id": "exec_2",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "failed",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }

        mock_redis.get.side_effect = [
            json.dumps(exec_data_1),
            json.dumps(exec_data_2)
        ]

        executions = await state_manager.get_workflow_executions("test_workflow", limit=5)

        assert len(executions) == 2
        assert executions[0].execution_id == "exec_1"
        assert executions[1].execution_id == "exec_2"

    @pytest.mark.asyncio
    async def test_get_active_executions(self, state_manager, mock_redis):
        """Test getting active executions."""
        # Mock scan results
        mock_redis.scan_iter.return_value = [
            b"workflow:execution:exec_1",
            b"workflow:execution:exec_2"
        ]

        # Mock execution data - one running, one completed
        running_exec = {
            "execution_id": "exec_1",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        completed_exec = {
            "execution_id": "exec_2",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "completed",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }

        mock_redis.get.side_effect = [
            json.dumps(running_exec),
            json.dumps(completed_exec)
        ]

        active_executions = await state_manager.get_active_executions()

        assert len(active_executions) == 1
        assert active_executions[0].execution_id == "exec_1"
        assert active_executions[0].state == WorkflowExecutionState.RUNNING

    @pytest.mark.asyncio
    async def test_cancel_execution(self, state_manager, mock_redis):
        """Test canceling a running execution."""
        existing_data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        mock_redis.get.return_value = json.dumps(existing_data)

        result = await state_manager.cancel_execution("test_exec_123")

        assert result is True
        assert mock_redis.setex.called

        call_args = mock_redis.setex.call_args
        updated_data = json.loads(call_args[0][2])
        assert updated_data["state"] == "cancelled"
        assert "end_time" in updated_data

    @pytest.mark.asyncio
    async def test_cancel_execution_not_running(self, state_manager, mock_redis):
        """Test canceling a non-running execution."""
        existing_data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "completed",
            "start_time": datetime.now().isoformat(),
            "input_data": {},
            "vertex_states": {}
        }
        mock_redis.get.return_value = json.dumps(existing_data)

        result = await state_manager.cancel_execution("test_exec_123")

        assert result is False
        # Should not update if not running
        assert not mock_redis.setex.called

    @pytest.mark.asyncio
    async def test_cancel_execution_not_found(self, state_manager, mock_redis):
        """Test canceling a non-existent execution."""
        mock_redis.get.return_value = None

        result = await state_manager.cancel_execution("non_existent")

        assert result is False


class TestWorkflowExecutionStatus:
    """Test cases for WorkflowExecutionStatus dataclass."""

    def test_to_dict(self):
        """Test converting status to dictionary."""
        start_time = datetime.now()
        status = WorkflowExecutionStatus(
            execution_id="test_exec_123",
            workflow_id="test_workflow",
            workflow_name="Test Workflow",
            state=WorkflowExecutionState.RUNNING,
            start_time=start_time,
            input_data={"param": "value"},
            progress_percentage=75.5
        )

        data = status.to_dict()

        assert data["execution_id"] == "test_exec_123"
        assert data["workflow_id"] == "test_workflow"
        assert data["state"] == "running"
        assert data["progress_percentage"] == 75.5
        assert data["input_data"] == {"param": "value"}
        assert "start_time" in data

    def test_from_dict(self):
        """Test creating status from dictionary."""
        start_time_str = datetime.now().isoformat()
        data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": start_time_str,
            "input_data": {"param": "value"},
            "vertex_states": {},
            "progress_percentage": 75.5
        }

        status = WorkflowExecutionStatus.from_dict(data)

        assert status.execution_id == "test_exec_123"
        assert status.workflow_id == "test_workflow"
        assert status.state == WorkflowExecutionState.RUNNING
        assert status.progress_percentage == 75.5
        assert status.input_data == {"param": "value"}

    def test_from_dict_with_vertex_states(self):
        """Test creating status from dictionary with vertex states."""
        start_time_str = datetime.now().isoformat()
        data = {
            "execution_id": "test_exec_123",
            "workflow_id": "test_workflow",
            "workflow_name": "Test Workflow",
            "state": "running",
            "start_time": start_time_str,
            "input_data": {},
            "vertex_states": {
                "vertex1": {
                    "state": "completed",
                    "updated_at": datetime.now().isoformat(),
                    "output_data": {"result": "success"}
                }
            },
            "progress_percentage": 50.0
        }

        status = WorkflowExecutionStatus.from_dict(data)

        assert "vertex1" in status.vertex_states
        vertex_state = status.vertex_states["vertex1"]
        assert vertex_state["state"] == VertexExecutionState.COMPLETED
        assert vertex_state["output_data"] == {"result": "success"}