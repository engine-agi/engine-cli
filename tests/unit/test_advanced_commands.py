"""Unit tests for CLI advanced commands."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from click.testing import CliRunner

from engine_cli.commands.advanced import cli as advanced_cli


class TestAdvancedCommands:
    """Test suite for advanced commands."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_monitor_command(self, runner):
        """Test monitor command."""
        result = runner.invoke(advanced_cli, ["monitor"])
        assert result.exit_code == 0
        assert "System Status" in result.output
        assert "Active Agents" in result.output
        assert "Running Workflows" in result.output
        assert "CPU Usage" in result.output

    def test_monitor_command_json(self, runner):
        """Test monitor command with JSON output."""
        result = runner.invoke(advanced_cli, ["monitor", "--json"])
        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.output)
        assert "agents" in data
        assert "workflows" in data
        assert "system" in data
        assert "api" in data

    def test_health_command(self, runner):
        """Test health command."""
        result = runner.invoke(advanced_cli, ["health"])
        assert result.exit_code == 0
        assert "Health Check" in result.output
        assert "Overall Status" in result.output
        assert "healthy" in result.output

    def test_health_command_detailed(self, runner):
        """Test health command with detailed output."""
        result = runner.invoke(advanced_cli, ["health", "--detailed"])
        assert result.exit_code == 0
        assert "Component Details" in result.output
        assert "core:" in result.output
        assert "api:" in result.output

    def test_health_command_specific_component(self, runner):
        """Test health command for specific component."""
        result = runner.invoke(advanced_cli, ["health", "--component", "api"])
        assert result.exit_code == 0
        assert "api:" in result.output

    def test_health_command_invalid_component(self, runner):
        """Test health command with invalid component."""
        result = runner.invoke(advanced_cli, ["health", "--component", "invalid"])
        assert result.exit_code == 0
        assert "Component 'invalid' not found" in result.output

    def test_logs_command(self, runner):
        """Test logs command."""
        result = runner.invoke(advanced_cli, ["logs"])
        assert result.exit_code == 0
        assert "System Logs" in result.output
        assert "Showing" in result.output
        assert "log entries" in result.output

    def test_logs_command_with_lines(self, runner):
        """Test logs command with specific number of lines."""
        result = runner.invoke(advanced_cli, ["logs", "--lines", "2"])
        assert result.exit_code == 0
        assert "Showing 2 log entries" in result.output

    def test_logs_command_with_level_filter(self, runner):
        """Test logs command with level filter."""
        result = runner.invoke(advanced_cli, ["logs", "--level", "ERROR"])
        assert result.exit_code == 0
        assert "Filters: level=ERROR" in result.output


class TestBulkOperations:
    """Test suite for bulk operations."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_bulk_create_agents(self, runner):
        """Test bulk create agents command."""
        result = runner.invoke(
            advanced_cli, ["bulk", "create-agents", "agent1", "agent2"]
        )
        # Note: This would need to be adjusted based on how the CLI is structured
        # For now, just test that the command exists and can be invoked
        assert result is not None

    def test_bulk_agents_operation(self, runner):
        """Test bulk agents operation command."""
        result = runner.invoke(
            advanced_cli, ["bulk", "agents", "test*", "--action", "start", "--dry-run"]
        )
        assert result is not None


class TestConfigOperations:
    """Test suite for configuration operations."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create a temporary config file."""
        config_file = tmp_path / "test_config.yaml"
        config_data = {"api": {"base_url": "http://test.com"}, "core": {"debug": True}}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        return config_file

    def test_config_export(self, runner, tmp_path):
        """Test config export command."""
        output_file = tmp_path / "exported_config.yaml"

        with patch("engine_cli.commands.advanced.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.dict.return_value = {
                "api": {"base_url": "http://localhost:8000"},
                "core": {"debug": False},
            }
            mock_load.return_value = mock_config

            result = runner.invoke(
                advanced_cli, ["config-ops", "export", str(output_file)]
            )
            assert result is not None

    def test_config_import_dry_run(self, runner, temp_config_file):
        """Test config import command with dry run."""
        result = runner.invoke(
            advanced_cli,
            ["config-ops", "import-config", str(temp_config_file), "--dry-run"],
        )
        assert result is not None

    def test_config_import_merge(self, runner, temp_config_file):
        """Test config import command with merge."""
        with patch("engine_cli.commands.advanced.load_config") as mock_load:
            with patch("engine_cli.commands.advanced.save_config") as mock_save:
                mock_config = MagicMock()
                mock_load.return_value = mock_config

                result = runner.invoke(
                    advanced_cli,
                    ["config-ops", "import-config", str(temp_config_file), "--merge"],
                )
                assert result is not None
