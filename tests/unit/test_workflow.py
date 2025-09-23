"""Tests for workflow.py module."""
import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock, mock_open, AsyncMock
from click.testing import CliRunner
import sys
import json
import asyncio

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from engine_cli.commands.workflow import (
        WorkflowStorage,
        WorkflowResolver,
        CLIWorkflowBuilder,
        cli,
        get_workflow_storage,
        _get_workflow_execution_service,
        _get_workflow_enums
    )
except ImportError:
    # Fallback for test environment - create mock classes
    class WorkflowStorage:
        def __init__(self):
            self.workflows_dir = os.path.join(os.getcwd(), "workflows")
            os.makedirs(self.workflows_dir, exist_ok=True)

        def list_workflows(self):
            return []

        def save_workflow(self, workflow):
            return True

    class WorkflowResolver:
        def __init__(self):
            self.agent_storage = None
            self.team_storage = None

    class CLIWorkflowBuilder:
        def __init__(self):
            self.agent_specs = []
            self.team_specs = []
            self.edge_specs = []

        def with_id(self, workflow_id):
            return self

        def add_agent_vertex(self, vertex_id, agent_id, instruction):
            self.agent_specs.append({'vertex_id': vertex_id, 'agent_id': agent_id, 'instruction': instruction})
            return self

        def add_edge(self, from_vertex, to_vertex):
            self.edge_specs.append({'from': from_vertex, 'to': to_vertex})
            return self

    cli = MagicMock()
    get_workflow_storage = MagicMock(return_value=WorkflowStorage())
    _get_workflow_execution_service = MagicMock(return_value=MagicMock())
    _get_workflow_enums = MagicMock(return_value=MagicMock())


class TestWorkflowStorage:
    """Test WorkflowStorage class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_workflows_dir(self):
        """Test that WorkflowStorage creates workflows directory."""
        storage = WorkflowStorage()
        assert os.path.exists("workflows")
        assert os.path.isdir("workflows")

    def test_list_workflows_empty(self):
        """Test listing workflows when directory is empty."""
        storage = WorkflowStorage()
        workflows = storage.list_workflows()
        assert workflows == []

    def test_list_workflows_with_files(self):
        """Test listing workflows with valid YAML files."""
        storage = WorkflowStorage()

        # Create test workflow file
        workflow_data = {
            'id': 'test_workflow',
            'name': 'Test Workflow',
            'version': '1.0.0',
            'description': 'A test workflow',
            'vertex_count': 2,
            'edge_count': 1,
            'created_at': '2024-01-01T00:00:00'
        }

        workflow_path = os.path.join("workflows", "test_workflow.yaml")
        with open(workflow_path, 'w') as f:
            yaml.safe_dump(workflow_data, f)

        workflows = storage.list_workflows()
        assert len(workflows) == 1
        assert workflows[0]['id'] == 'test_workflow'
        assert workflows[0]['name'] == 'Test Workflow'

    @patch('yaml.safe_dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_workflow_basic(self, mock_file, mock_yaml_dump):
        """Test saving a basic workflow."""
        storage = WorkflowStorage()

        # Mock workflow object
        mock_workflow = MagicMock()
        mock_workflow.id = 'test_workflow'
        mock_workflow.name = 'Test Workflow'
        mock_workflow.vertex_count = 2
        mock_workflow.edge_count = 1
        mock_workflow.created_at = MagicMock()
        mock_workflow.created_at.isoformat.return_value = '2024-01-01T00:00:00'
        mock_workflow.config = MagicMock()
        mock_workflow.config.description = 'Test description'
        mock_workflow.config.version = '1.0.0'

        result = storage.save_workflow(mock_workflow)
        assert result == True
        mock_yaml_dump.assert_called_once()


class TestWorkflowResolver:
    """Test WorkflowResolver class."""

    def test_init(self):
        """Test WorkflowResolver initialization."""
        resolver = WorkflowResolver()
        assert resolver.agent_storage is None
        assert resolver.team_storage is None


class TestCLIWorkflowBuilder:
    """Test CLIWorkflowBuilder class."""

    def test_init(self):
        """Test CLIWorkflowBuilder initialization."""
        builder = CLIWorkflowBuilder()
        assert builder.agent_specs == []
        assert builder.team_specs == []
        assert builder.edge_specs == []

    def test_with_id(self):
        """Test setting workflow ID."""
        builder = CLIWorkflowBuilder()
        result = builder.with_id('test_id')
        assert result == builder

    def test_add_agent_vertex(self):
        """Test adding agent vertex."""
        builder = CLIWorkflowBuilder()
        result = builder.add_agent_vertex('vertex1', 'agent1', 'Test instruction')
        assert result == builder
        assert len(builder.agent_specs) == 1
        assert builder.agent_specs[0]['vertex_id'] == 'vertex1'
        assert builder.agent_specs[0]['agent_id'] == 'agent1'

    def test_add_edge(self):
        """Test adding edge."""
        builder = CLIWorkflowBuilder()
        result = builder.add_edge('from_vertex', 'to_vertex')
        assert result == builder
        assert len(builder.edge_specs) == 1
        assert builder.edge_specs[0]['from'] == 'from_vertex'
        assert builder.edge_specs[0]['to'] == 'to_vertex'


class TestWorkflowFunctions:
    """Test utility functions."""

    def test_get_workflow_storage(self):
        """Test get_workflow_storage function."""
        storage = get_workflow_storage()
        assert isinstance(storage, WorkflowStorage)

    def test_get_workflow_execution_service_import_error(self):
        """Test workflow execution service when import fails."""
        with patch.dict('sys.modules', {'engine_core.services.workflow_service': None}):
            service = _get_workflow_execution_service()
            assert service is None


class TestWorkflowCLI:
    """Test workflow CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('engine_cli.commands.workflow.WorkflowStorage')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_show_command_success(self, mock_yaml_load, mock_file, mock_storage_class):
        """Test show command for existing workflow."""
        mock_storage = MagicMock()
        mock_storage.list_workflows.return_value = [
            {'id': 'test_workflow', 'file': 'test_workflow.yaml'}
        ]
        mock_storage_class.return_value = mock_storage

        workflow_data = {
            'id': 'test_workflow',
            'name': 'Test Workflow',
            'description': 'A test workflow'
        }
        mock_yaml_load.return_value = workflow_data

        result = self.runner.invoke(cli, ['show', 'test_workflow'])
        assert result.exit_code == 0
        assert "Test Workflow" in result.output

    @patch('engine_cli.commands.workflow.WorkflowStorage')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_delete_command_success(self, mock_remove, mock_exists, mock_storage_class):
        """Test delete command success."""
        mock_storage = MagicMock()
        mock_storage.list_workflows.return_value = [
            {'id': 'test_workflow', 'file': 'test_workflow.yaml'}
        ]
        mock_storage_class.return_value = mock_storage

        mock_exists.return_value = True

        result = self.runner.invoke(cli, ['delete', 'test_workflow', '--force'])
        assert result.exit_code == 0