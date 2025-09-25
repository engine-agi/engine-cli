"""Unit tests for main CLI entry point."""

import os
import sys
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from engine_cli.main import cli


class TestMainCLI:
    """Test main CLI entry point."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_cli_group_exists(self, runner):
        """Test that the main CLI group exists."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Engine Framework CLI" in result.output
        assert "AI Agent Orchestration System" in result.output

    def test_cli_version_option(self, runner):
        """Test CLI version option."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "Engine CLI" in result.output
        assert "1.1.0" in result.output

    @patch("engine_cli.main.start_interactive")
    def test_interactive_command(self, mock_interactive, runner):
        """Test interactive command."""
        result = runner.invoke(cli, ["interactive"])
        assert result.exit_code == 0
        assert "Starting Interactive Mode" in result.output
        mock_interactive.assert_called_once()

    @patch("engine_core.__version__", "2.0.0")
    def test_version_command_with_core(self, runner):
        """Test version command when core is available."""
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "Engine Framework Versions" in result.output
        assert "Engine CLI" in result.output
        assert "1.1.0" in result.output
        assert "Engine Core" in result.output
        assert "2.0.0" in result.output

    @patch.dict("sys.modules", {"engine_core": None})
    def test_version_command_without_core(self, runner):
        """Test version command when core is not available."""
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "Engine Core" in result.output
        assert "Not available" in result.output
        assert "Engine Framework Versions" in result.output
        assert "Engine CLI" in result.output
        assert "1.1.0" in result.output
        assert "Engine Core" in result.output
        assert "Not available" in result.output

    @patch("engine_core.AgentBuilder")
    @patch("engine_core.TeamBuilder")
    @patch("engine_core.WorkflowBuilder")
    def test_status_command_all_available(
        self, mock_workflow, mock_team, mock_agent, runner
    ):
        """Test status command when all modules are available."""
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "System Status" in result.output
        assert "Engine CLI is running" in result.output
        assert "Engine Core is available" in result.output

    @patch("engine_core.AgentBuilder", side_effect=ImportError)
    @patch("engine_core.TeamBuilder", side_effect=ImportError)
    @patch("engine_core.WorkflowBuilder", side_effect=ImportError)
    def test_status_command_core_unavailable(
        self, mock_workflow, mock_team, mock_agent, runner
    ):
        """Test status command when core is not available."""
        with patch.dict("sys.modules", {"engine_core": None}):
            result = runner.invoke(cli, ["status"])
            assert result.exit_code == 0
            assert "System Status" in result.output
            assert "Engine CLI is running" in result.output
            assert "Engine Core is not available" in result.output

    def test_agent_group_exists(self, runner):
        """Test that agent command group exists."""
        result = runner.invoke(cli, ["agent", "--help"])
        assert result.exit_code == 0
        assert "Agent management commands" in result.output

    def test_team_group_exists(self, runner):
        """Test that team command group exists."""
        result = runner.invoke(cli, ["team", "--help"])
        assert result.exit_code == 0
        # The team command may show different descriptions based on import success
        assert (
            "Manage agent teams" in result.output
            or "Team management commands" in result.output
        )

    def test_workflow_group_exists(self, runner):
        """Test that workflow command group exists."""
        result = runner.invoke(cli, ["workflow", "--help"])
        assert result.exit_code == 0
        assert "Workflow management commands" in result.output

    def test_tool_group_exists(self, runner):
        """Test that tool command group exists."""
        result = runner.invoke(cli, ["tool", "--help"])
        assert result.exit_code == 0
        assert "Tool management commands" in result.output

    def test_protocol_group_exists(self, runner):
        """Test that protocol command group exists."""
        result = runner.invoke(cli, ["protocol", "--help"])
        assert result.exit_code == 0
        assert "Protocol management commands" in result.output

    def test_book_group_exists(self, runner):
        """Test that book command group exists."""
        result = runner.invoke(cli, ["book", "--help"])
        assert result.exit_code == 0
        assert "Book management commands" in result.output

    def test_project_group_exists(self, runner):
        """Test that project command group exists."""
        result = runner.invoke(cli, ["project", "--help"])
        assert result.exit_code == 0
        assert "Project management commands" in result.output

    def test_examples_group_exists(self, runner):
        """Test that examples command group exists."""
        result = runner.invoke(cli, ["examples", "--help"])
        assert result.exit_code == 0
        assert "Examples management commands" in result.output

    def test_config_group_exists(self, runner):
        """Test that config command group exists."""
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "Configuration management commands" in result.output

    def test_advanced_group_exists(self, runner):
        """Test that advanced command group exists."""
        result = runner.invoke(cli, ["advanced", "--help"])
        assert result.exit_code == 0
        assert "Advanced operations and utilities" in result.output

    def test_monitoring_group_exists(self, runner):
        """Test that monitoring command group exists."""
        result = runner.invoke(cli, ["monitoring", "--help"])
        assert result.exit_code == 0
        assert "Monitoring and observability commands" in result.output
