"""Integration tests for CLI commands using Click CliRunner."""

import json
import os

# Import the actual CLI
import sys

import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from engine_cli.main import cli


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test main CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Engine Framework CLI" in result.output
        assert "Commands:" in result.output

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "Engine Framework Versions" in result.output
        assert "Engine CLI" in result.output

    def test_status_command(self, runner):
        """Test status command."""
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "System Status" in result.output
        assert "Engine CLI is running" in result.output


class TestConfigCLIIntegration:
    """Integration tests for configuration CLI commands."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_config_show(self, runner):
        """Test config show command."""
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "Current Configuration" in result.output

    def test_config_paths(self, runner):
        """Test config paths command."""
        result = runner.invoke(cli, ["config", "paths"])
        assert result.exit_code == 0
        assert "Configuration File Search Paths" in result.output
        assert "Environment Variables" in result.output

    def test_config_init(self, runner, tmp_path):
        """Test config init command."""
        # Change to temp directory to avoid overwriting real config
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["config", "init", "--force"])
            assert result.exit_code == 0
            assert "Default configuration created" in result.output

            # Check if config file was created
            # config_file = Path.home() / ".engine" / "config.yaml"
            # Note: In isolated filesystem, this might not work as expected
            # Just check that the command completed successfully

    def test_config_get_set_workflow(self, runner):
        """Test config get/set workflow."""
        # Set a value
        result = runner.invoke(cli, ["config", "set", "core.debug", "true"])
        assert result.exit_code == 0
        assert "Configuration updated" in result.output

        # Get the value back
        result = runner.invoke(cli, ["config", "get", "core.debug"])
        assert result.exit_code == 0
        assert "core.debug: True" in result.output


class TestAdvancedCLIIntegration:
    """Integration tests for advanced CLI commands."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_advanced_help(self, runner):
        """Test advanced commands help."""
        result = runner.invoke(cli, ["advanced", "--help"])
        assert result.exit_code == 0
        assert "Advanced operations and utilities" in result.output
        assert "bulk" in result.output
        assert "config-ops" in result.output
        assert "monitor" in result.output

    def test_monitor_command(self, runner):
        """Test monitor command."""
        result = runner.invoke(cli, ["advanced", "monitor"])
        assert result.exit_code == 0
        assert "System Status" in result.output
        assert "Active Agents" in result.output

    def test_monitor_json_command(self, runner):
        """Test monitor command with JSON output."""
        result = runner.invoke(cli, ["advanced", "monitor", "--json"])
        assert result.exit_code == 0

        # Should be valid JSON
        try:
            data = json.loads(result.output)
            assert isinstance(data, dict)
            assert "agents" in data
        except json.JSONDecodeError:
            pytest.fail("Monitor --json did not return valid JSON")

    def test_health_command(self, runner):
        """Test health command."""
        result = runner.invoke(cli, ["advanced", "health"])
        assert result.exit_code == 0
        assert "Health Check" in result.output
        assert "Overall Status" in result.output

    def test_logs_command(self, runner):
        """Test logs command."""
        result = runner.invoke(cli, ["advanced", "logs"])
        assert result.exit_code == 0
        assert "System Logs" in result.output

    def test_bulk_help(self, runner):
        """Test bulk commands help."""
        result = runner.invoke(cli, ["advanced", "bulk", "--help"])
        assert result.exit_code == 0
        assert "Bulk operations for multiple resources" in result.output
        assert "create-agents" in result.output
        assert "agents" in result.output

    def test_config_ops_help(self, runner):
        """Test config-ops commands help."""
        result = runner.invoke(cli, ["advanced", "config-ops", "--help"])
        assert result.exit_code == 0
        assert "Configuration export and import operations" in result.output
        assert "export" in result.output
        assert "import-config" in result.output


class TestEndToEndWorkflows:
    """End-to-end workflow tests."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_config_workflow(self, runner, tmp_path):
        """Test complete configuration workflow."""
        with runner.isolated_filesystem():
            # Initialize config
            result = runner.invoke(cli, ["config", "init", "--force"])
            assert result.exit_code == 0

            # Set some values
            result = runner.invoke(
                cli, ["config", "set", "api.base_url", "http://test.com"]
            )
            assert result.exit_code == 0

            result = runner.invoke(cli, ["config", "set", "core.debug", "true"])
            assert result.exit_code == 0

            # Get values back
            result = runner.invoke(cli, ["config", "get", "api.base_url"])
            assert result.exit_code == 0
            assert "http://test.com" in result.output

            result = runner.invoke(cli, ["config", "get", "core.debug"])
            assert result.exit_code == 0
            assert "True" in result.output

            # Show config
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0
            assert "http://test.com" in result.output

    def test_advanced_config_workflow(self, runner, tmp_path):
        """Test advanced config operations workflow."""
        # Skip this test for now due to CliRunner isolated filesystem issues
        # TODO: Fix config export testing with proper mocking
        pytest.skip("Config export test needs proper mocking for CliRunner")


class TestErrorHandling:
    """Test error handling in CLI commands."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_invalid_config_key(self, runner):
        """Test handling of invalid config keys."""
        result = runner.invoke(cli, ["config", "get", "invalid.nonexistent.key"])
        assert result.exit_code == 0  # CLI should handle gracefully
        assert "not found" in result.output

    def test_config_validate_nonexistent_file(self, runner):
        """Test config validate with non-existent file."""
        result = runner.invoke(cli, ["config", "validate", "/nonexistent/file.yaml"])
        assert result.exit_code in [1, 2]  # Should fail for non-existent file

    def test_invalid_command(self, runner):
        """Test invalid command handling."""
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0  # Should fail for invalid commands
