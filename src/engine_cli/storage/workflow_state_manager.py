"""Workflow State Manager - Redis-based volatile state for workflow execution."""

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import redis.asyncio as redis


class WorkflowExecutionState(Enum):
    """Workflow execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VertexExecutionState(Enum):
    """Vertex execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowExecutionStatus:
    """Workflow execution status data."""

    execution_id: str
    workflow_id: str
    workflow_name: str
    state: WorkflowExecutionState
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    vertex_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    progress_percentage: float = 0.0
    current_vertex: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert enums to strings
        data["state"] = self.state.value
        for vertex_id, vertex_state in data["vertex_states"].items():
            if "state" in vertex_state and isinstance(
                vertex_state["state"], Enum
            ):
                vertex_state["state"] = vertex_state["state"].value
        # Convert datetime to ISO string
        data["start_time"] = self.start_time.isoformat()
        if self.end_time:
            data["end_time"] = self.end_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowExecutionStatus":
        """Create from dictionary."""
        # Convert ISO strings back to datetime
        data["start_time"] = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        # Convert strings back to enums
        data["state"] = WorkflowExecutionState(data["state"])
        for vertex_id, vertex_state in data.get("vertex_states", {}).items():
            if "state" in vertex_state:
                vertex_state["state"] = VertexExecutionState(
                    vertex_state["state"]
                )
        return cls(**data)


class WorkflowStateManager:
    """Redis-based volatile state manager for workflow executions."""

    def __init__(
        self, redis_url: Optional[str] = None, enable_fallback: bool = True
    ):
        self.redis_url = redis_url or os.getenv(
            "REDIS_URL", "redis://localhost:6379/0"
        )
        self.redis_client: Optional[redis.Redis] = None
        self._connected = False
        self.enable_fallback = enable_fallback
        self._memory_storage: Dict[str, Any] = {}  # Fallback in-memory storage

    async def connect(self) -> None:
        """Connect to Redis."""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()  # type: ignore
                self._connected = True
            except Exception:
                self._connected = False
                if not self.enable_fallback:
                    raise
                # Fallback to in-memory storage
                print("⚠️  Redis not available, using in-memory fallback")
                self.redis_client = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()  # type: ignore
            self.redis_client = None
            self._connected = False

    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected or (
            self.enable_fallback and self.redis_client is None
        )

    def _memory_get(self, key: str) -> Optional[str]:
        """Get value from memory storage."""
        return self._memory_storage.get(key)

    def _memory_set(
        self, key: str, value: str, expire_seconds: Optional[int] = None
    ) -> None:
        """Set value in memory storage."""
        self._memory_storage[key] = value

    def _memory_lpush(self, key: str, value: str) -> int:
        """Push value to memory list."""
        if key not in self._memory_storage:
            self._memory_storage[key] = []
        if not isinstance(self._memory_storage[key], list):
            self._memory_storage[key] = [self._memory_storage[key]]
        self._memory_storage[key].append(value)
        return len(self._memory_storage[key])

    def _memory_lrange(self, key: str, start: int, end: int) -> List[bytes]:
        """Get range from memory list."""
        if key not in self._memory_storage or not isinstance(
            self._memory_storage[key], list
        ):
            return []
        lst = self._memory_storage[key]
        # Handle negative indices like Redis
        if end == -1:
            end = len(lst)
        return [item.encode("utf-8") for item in lst[start:end]]

    async def _get_data(self, key: str) -> Optional[str]:
        """Get data from Redis or memory fallback."""
        if self._connected and self.redis_client:
            return await self.redis_client.get(key)  # type: ignore
        elif self.enable_fallback:
            return self._memory_get(key)
        return None

    async def _set_data(
        self, key: str, value: str, expire_seconds: Optional[int] = None
    ) -> None:
        """Set data in Redis or memory fallback."""
        if self._connected and self.redis_client:
            if expire_seconds:
                await self.redis_client.setex(key, expire_seconds, value)  # type: ignore
            else:
                await self.redis_client.set(key, value)  # type: ignore
        elif self.enable_fallback:
            self._memory_set(key, value, expire_seconds)

    async def _list_push(self, key: str, value: str) -> int:
        """Push to list in Redis or memory fallback."""
        if self._connected and self.redis_client:
            return await self.redis_client.lpush(key, value)  # type: ignore
        elif self.enable_fallback:
            return self._memory_lpush(key, value)
        return 0

    async def _list_range(self, key: str, start: int, end: int) -> List[bytes]:
        """Get list range from Redis or memory fallback."""
        if self._connected and self.redis_client:
            return await self.redis_client.lrange(key, start, end)  # type: ignore
        elif self.enable_fallback:
            return self._memory_lrange(key, start, end)
        return []

    async def create_execution(
        self,
        workflow_id: str,
        workflow_name: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new workflow execution and return execution ID."""
        await self.connect()

        execution_id = (
            f"wf_exec_{workflow_id}_{int(datetime.now().timestamp())}"
        )

        status = WorkflowExecutionStatus(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            state=WorkflowExecutionState.PENDING,
            start_time=datetime.now(),
            input_data=input_data or {},
        )

        # Store in Redis/memory with 24 hour expiration
        key = f"workflow:execution:{execution_id}"
        await self._set_data(key, json.dumps(status.to_dict()), 86400)

        # Also store in executions list for the workflow
        list_key = f"workflow:executions:{workflow_id}"
        await self._list_push(list_key, execution_id)
        # Note: Memory fallback doesn't support expiration for lists

        return execution_id

    async def update_execution_state(
        self,
        execution_id: str,
        state: WorkflowExecutionState,
        current_vertex: Optional[str] = None,
        progress_percentage: Optional[float] = None,
    ) -> None:
        """Update workflow execution state."""
        await self.connect()

        key = f"workflow:execution:{execution_id}"
        data_str = await self._get_data(key)

        if not data_str:
            return

        data = json.loads(data_str)
        status = WorkflowExecutionStatus.from_dict(data)

        status.state = state
        if current_vertex is not None:
            status.current_vertex = current_vertex
        if progress_percentage is not None:
            status.progress_percentage = progress_percentage

        if state in [
            WorkflowExecutionState.COMPLETED,
            WorkflowExecutionState.FAILED,
            WorkflowExecutionState.CANCELLED,
        ]:
            status.end_time = datetime.now()

        await self._set_data(key, json.dumps(status.to_dict()), 86400)

    async def update_vertex_state(
        self,
        execution_id: str,
        vertex_id: str,
        state: VertexExecutionState,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Update vertex execution state."""
        await self.connect()

        key = f"workflow:execution:{execution_id}"
        data_str = await self._get_data(key)

        if not data_str:
            return

        data = json.loads(data_str)
        status = WorkflowExecutionStatus.from_dict(data)

        vertex_state = {
            "state": state,
            "updated_at": datetime.now().isoformat(),
            "output_data": output_data,
            "error_message": error_message,
        }

        status.vertex_states[vertex_id] = vertex_state

        # Recalculate progress
        total_vertices = len(status.vertex_states)
        completed_vertices = sum(
            1
            for vs in status.vertex_states.values()
            if vs.get("state") == VertexExecutionState.COMPLETED.value
        )
        status.progress_percentage = (
            (completed_vertices / total_vertices * 100)
            if total_vertices > 0
            else 0
        )

        await self._set_data(key, json.dumps(status.to_dict()), 86400)

    async def set_execution_output(
        self, execution_id: str, output_data: Dict[str, Any]
    ) -> None:
        """Set final execution output."""
        await self.connect()

        key = f"workflow:execution:{execution_id}"
        data_str = await self._get_data(key)

        if not data_str:
            return

        data = json.loads(data_str)
        status = WorkflowExecutionStatus.from_dict(data)

        status.output_data = output_data
        await self._set_data(key, json.dumps(status.to_dict()), 86400)

    async def set_execution_error(
        self, execution_id: str, error_message: str
    ) -> None:
        """Set execution error."""
        await self.connect()

        key = f"workflow:execution:{execution_id}"
        data_str = await self._get_data(key)

        if not data_str:
            return

        data = json.loads(data_str)
        status = WorkflowExecutionStatus.from_dict(data)

        status.error_message = error_message
        status.state = WorkflowExecutionState.FAILED
        status.end_time = datetime.now()

        await self._set_data(key, json.dumps(status.to_dict()), 86400)

    async def get_execution_status(
        self, execution_id: str
    ) -> Optional[WorkflowExecutionStatus]:
        """Get workflow execution status."""
        await self.connect()

        key = f"workflow:execution:{execution_id}"
        data_str = await self._get_data(key)

        if not data_str:
            return None

        data = json.loads(data_str)
        return WorkflowExecutionStatus.from_dict(data)

    async def get_workflow_executions(
        self, workflow_id: str, limit: int = 10
    ) -> List[WorkflowExecutionStatus]:
        """Get recent executions for a workflow."""
        await self.connect()

        list_key = f"workflow:executions:{workflow_id}"
        execution_ids = await self._list_range(list_key, 0, limit - 1)

        executions = []
        for exec_id_bytes in execution_ids:
            exec_id = exec_id_bytes.decode("utf-8")
            status = await self.get_execution_status(exec_id)
            if status:
                executions.append(status)

        return executions

    async def get_active_executions(self) -> List[WorkflowExecutionStatus]:
        """Get all currently active (running) executions."""
        await self.connect()

        # If using fallback (no Redis), we can't efficiently scan for active executions
        # Return empty list for now - in production you'd need a different approach
        if not self._connected or self.redis_client is None:
            return []

        # This is a simplified implementation - in production you'd use Redis sets or pub/sub
        # For now, we'll scan for keys (not efficient but works for demo)
        pattern = "workflow:execution:*"
        keys = []
        async for key in self.redis_client.scan_iter(pattern):  # type: ignore
            keys.append(key)

        active_executions = []
        for key_bytes in keys[:50]:  # Limit to avoid performance issues
            key = key_bytes.decode("utf-8")
            data_str = await self.redis_client.get(key)  # type: ignore
            if data_str:
                data = json.loads(data_str)
                status = WorkflowExecutionStatus.from_dict(data)
                if status.state == WorkflowExecutionState.RUNNING:
                    active_executions.append(status)

        return active_executions

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution."""
        await self.connect()

        key = f"workflow:execution:{execution_id}"
        data_str = await self.redis_client.get(key)  # type: ignore

        if not data_str:
            return False

        data = json.loads(data_str)
        status = WorkflowExecutionStatus.from_dict(data)

        if status.state == WorkflowExecutionState.RUNNING:
            status.state = WorkflowExecutionState.CANCELLED
            status.end_time = datetime.now()
            await self.redis_client.setex(key, 86400, json.dumps(status.to_dict()))  # type: ignore
            return True

        return False


# Global instance
workflow_state_manager = WorkflowStateManager()
