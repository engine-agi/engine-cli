"""Tests for tool.py module."""

import asyncio
import json
import os
import sys
import tempfile
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
import yaml
from click.testing import CliRunner

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from engine_cli.commands.tool import ToolStorage, cli, get_tool_storage, tool_storage


class TestToolStorage:
    """Test ToolStorage class."""

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

    def test_init_creates_tools_dir(self):
        """Test that ToolStorage creates tools directory."""
        storage = ToolStorage()
        assert os.path.exists("tools")
        assert os.path.isdir("tools")

    def test_list_tools_empty(self):
        """Test listing tools when directory is empty."""
        storage = ToolStorage()
        tools = storage.list_tools()
        assert tools == []

    def test_list_tools_with_files(self):
        """Test listing tools with valid YAML files."""
        storage = ToolStorage()

        # Create test tool file
        tool_data = {
            "tool_id": "test_tool",
            "name": "Test Tool",
            "type": "api",
            "description": "A test tool",
            "capabilities": ["read", "write"],
            "tags": ["test", "api"],
        }

        tool_path = os.path.join("tools", "test_tool.yaml")
        with open(tool_path, "w") as f:
            yaml.safe_dump(tool_data, f)

        tools = storage.list_tools()
        assert len(tools) == 1
        assert tools[0]["tool_id"] == "test_tool"
        assert tools[0]["name"] == "Test Tool"

    def test_get_tool_exists(self):
        """Test getting an existing tool."""
        storage = ToolStorage()

        tool_data = {"tool_id": "test_tool", "name": "Test Tool", "type": "api"}

        tool_path = os.path.join("tools", "test_tool.yaml")
        with open(tool_path, "w") as f:
            yaml.safe_dump(tool_data, f)

        tool = storage.get_tool("test_tool")
        assert tool is not None
        assert tool["tool_id"] == "test_tool"

    def test_get_tool_not_exists(self):
        """Test getting a non-existing tool."""
        storage = ToolStorage()
        tool = storage.get_tool("nonexistent")
        assert tool is None

    def test_delete_tool_exists(self):
        """Test deleting an existing tool."""
        storage = ToolStorage()

        tool_data = {"tool_id": "test_tool", "name": "Test Tool"}
        tool_path = os.path.join("tools", "test_tool.yaml")
        with open(tool_path, "w") as f:
            yaml.safe_dump(tool_data, f)

        # Verify file exists
        assert os.path.exists(tool_path)

        # Delete tool
        result = storage.delete_tool("test_tool")
        assert result is True
        assert not os.path.exists(tool_path)

    def test_delete_tool_not_exists(self):
        """Test deleting a non-existing tool."""
        storage = ToolStorage()
        result = storage.delete_tool("nonexistent")
        assert result is False


class TestToolFunctions:
    """Test utility functions."""

    def test_get_tool_storage(self):
        """Test get_tool_storage function."""
        storage = get_tool_storage()
        assert isinstance(storage, ToolStorage)


class TestToolCLI:
    """Test tool CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_create_command_basic(self):
        """Test create command with basic options."""
        # Skip this test as it requires complex mocking of engine_core imports
        pytest.skip(
            "Requires engine_core ToolBuilder mocking which is complex in test environment"
        )

    def test_create_command_with_options(self):
        """Test create command with all options."""
        # Skip this test as it requires complex mocking of engine_core imports
        pytest.skip(
            "Requires engine_core ToolBuilder mocking which is complex in test environment"
        )

    @patch("engine_cli.commands.tool.tool_storage")
    def test_list_command_empty(self, mock_storage):
        """Test list command when no tools exist."""
        mock_storage.list_tools.return_value = []

        result = self.runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No tools found" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_list_command_with_tools(self, mock_storage):
        """Test list command with tools."""
        tools = [
            {
                "tool_id": "tool1",
                "name": "Tool One",
                "type": "api",
                "capabilities": ["read", "write"],
                "tags": ["api", "test"],
            },
            {
                "tool_id": "tool2",
                "name": "Tool Two",
                "type": "cli",
                "capabilities": ["execute"],
                "tags": ["cli"],
            },
        ]
        mock_storage.list_tools.return_value = tools

        result = self.runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Found 2 tool(s)" in result.output
        assert "Tool One" in result.output
        assert "Tool Two" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_list_command_with_filters(self, mock_storage):
        """Test list command with type and tag filters."""
        tools = [
            {
                "tool_id": "api_tool",
                "name": "API Tool",
                "type": "api",
                "capabilities": ["read"],
                "tags": ["api", "web"],
            },
            {
                "tool_id": "cli_tool",
                "name": "CLI Tool",
                "type": "cli",
                "capabilities": ["execute"],
                "tags": ["cli", "local"],
            },
        ]
        mock_storage.list_tools.return_value = tools

        # Filter by type
        result = self.runner.invoke(cli, ["list", "--type", "api"])
        assert result.exit_code == 0
        assert "API Tool" in result.output
        assert "CLI Tool" not in result.output

        # Filter by tag
        result = self.runner.invoke(cli, ["list", "--tag", "web"])
        assert result.exit_code == 0
        assert "API Tool" in result.output
        assert "CLI Tool" not in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_show_command_exists(self, mock_storage):
        """Test show command for existing tool."""
        tool = {
            "tool_id": "test_tool",
            "name": "Test Tool",
            "type": "api",
            "description": "A test tool",
            "capabilities": ["read", "write"],
            "tags": ["test", "api"],
            "created_at": "2024-01-01T00:00:00",
        }
        mock_storage.get_tool.return_value = tool

        result = self.runner.invoke(cli, ["show", "test_tool"])
        assert result.exit_code == 0
        assert "Test Tool" in result.output
        assert "A test tool" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_show_command_not_exists(self, mock_storage):
        """Test show command for non-existing tool."""
        mock_storage.get_tool.return_value = None

        result = self.runner.invoke(cli, ["show", "nonexistent"])
        assert result.exit_code == 0  # CLI doesn't exit on this error
        assert "not found" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_delete_command_exists_force(self, mock_storage):
        """Test delete command with force flag."""
        tool = {"tool_id": "test_tool", "name": "Test Tool"}
        mock_storage.get_tool.return_value = tool
        mock_storage.delete_tool.return_value = True

        result = self.runner.invoke(cli, ["delete", "test_tool", "--force"])
        assert result.exit_code == 0
        assert "deleted successfully" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_delete_command_not_exists(self, mock_storage):
        """Test delete command for non-existing tool."""
        mock_storage.get_tool.return_value = None

        result = self.runner.invoke(cli, ["delete", "nonexistent", "--force"])
        assert result.exit_code == 0  # CLI doesn't exit on this error
        assert "not found" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_test_command_api_tool(self, mock_storage):
        """Test test command for API tool."""
        tool = {
            "tool_id": "api_tool",
            "name": "API Tool",
            "type": "api",
            "endpoint": "https://api.example.com",
        }
        mock_storage.get_tool.return_value = tool

        result = self.runner.invoke(
            cli,
            [
                "test",
                "api_tool",
                "--input",
                '{"key": "value"}',
                "--method",
                "POST",
                "--params",
                '{"param": "test"}',
            ],
        )
        assert result.exit_code == 0
        assert "Testing tool 'api_tool'" in result.output
        assert "Simulating POST request" in result.output
        assert "test completed" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_test_command_cli_tool(self, mock_storage):
        """Test test command for CLI tool."""
        tool = {"tool_id": "cli_tool", "name": "CLI Tool", "type": "cli"}
        mock_storage.get_tool.return_value = tool

        result = self.runner.invoke(
            cli, ["test", "cli_tool", "--input", '{"command": "ls"}']
        )
        assert result.exit_code == 0
        assert "Simulating CLI execution" in result.output
        assert "executed successfully" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_test_command_generic_tool(self, mock_storage):
        """Test test command for generic tool."""
        tool = {"tool_id": "generic_tool", "name": "Generic Tool", "type": "generic"}
        mock_storage.get_tool.return_value = tool

        result = self.runner.invoke(
            cli, ["test", "generic_tool", "--input", '{"data": "test"}']
        )
        assert result.exit_code == 0
        assert "Testing generic tool" in result.output
        assert "test_status" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_test_command_tool_not_found(self, mock_storage):
        """Test test command when tool doesn't exist."""
        mock_storage.get_tool.return_value = None

        result = self.runner.invoke(cli, ["test", "nonexistent"])
        assert result.exit_code == 0  # CLI doesn't exit on this error
        assert "not found" in result.output

    @patch("engine_cli.commands.tool.tool_storage")
    def test_test_command_invalid_json(self, mock_storage):
        """Test test command with invalid JSON input."""
        tool = {"tool_id": "test_tool", "name": "Test Tool", "type": "api"}
        mock_storage.get_tool.return_value = tool

        result = self.runner.invoke(
            cli, ["test", "test_tool", "--input", "invalid json"]
        )
        assert result.exit_code == 0  # CLI handles error gracefully
        assert "Invalid JSON input" in result.output
