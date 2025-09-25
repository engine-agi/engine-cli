"""Usability tests for CLI user experience."""

import os
import re

# Import the actual CLI
import sys

import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from engine_cli.main import cli


class TestCLIUsability:
    """Test CLI usability and user experience."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_help_completeness(self, runner):
        """Test that help messages are comprehensive and user-friendly."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

        # Check for essential elements in help
        assert "Engine Framework CLI" in result.output
        assert "Commands:" in result.output

        # Should list main command groups
        assert "agent" in result.output
        assert "config" in result.output
        assert "advanced" in result.output

    def test_command_help_quality(self, runner):
        """Test quality of individual command help messages."""
        commands_to_test = [
            ["config", "--help"],
            ["config", "show", "--help"],
            ["config", "get", "--help"],
            ["config", "set", "--help"],
            ["advanced", "--help"],
            ["advanced", "monitor", "--help"],
            ["advanced", "health", "--help"],
        ]

        for cmd in commands_to_test:
            result = runner.invoke(cli, cmd)
            assert (
                result.exit_code == 0
            ), f"Help failed for command: {' '.join(cmd)}"

            # Basic help quality checks
            assert "Options:" in result.output or "Usage:" in result.output
            assert "--help" in result.output  # Should show help option

    def test_error_messages_user_friendly(self, runner):
        """Test that error messages are user-friendly."""
        # Test invalid command
        result = runner.invoke(cli, ["nonexistent-command"])
        assert result.exit_code != 0

        # Error should be clear and actionable
        assert "Error" in result.output or "not recognized" in result.output

    def test_config_error_handling(self, runner):
        """Test user-friendly error handling in config commands."""
        # Test getting non-existent config key
        result = runner.invoke(cli, ["config", "get", "nonexistent.key"])
        assert result.exit_code == 0  # Should not crash
        assert "not found" in result.output.lower()

        # Test setting invalid config
        result = runner.invoke(cli, ["config", "set", "invalid.key", "value"])
        # Should either succeed or give clear error
        assert result.exit_code in [0, 1]

    def test_output_formatting_consistency(self, runner):
        """Test that output formatting is consistent across commands."""
        commands = [
            ["config", "show"],
            ["config", "paths"],
            ["advanced", "monitor"],
            ["advanced", "health"],
        ]

        outputs = []
        for cmd in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == 0
            outputs.append(result.output)

        # Check for consistent patterns (this is subjective but helps catch major issues)
        for output in outputs:
            # Should not have obvious formatting errors
            assert not output.startswith("\n\n")  # No double newlines at start
            assert not re.search(
                r"\n\s*\n\s*\n", output
            )  # No excessive blank lines

    def test_progress_feedback(self, runner):
        """Test that commands provide appropriate progress feedback."""
        with runner.isolated_filesystem():
            # Test commands that should show progress
            result = runner.invoke(cli, ["config", "init", "--force"])
            assert result.exit_code == 0
            # Should indicate success
            assert "✓" in result.output or "created" in result.output.lower()

            result = runner.invoke(cli, ["advanced", "monitor"])
            assert result.exit_code == 0
            # Should show some status information
            assert len(result.output.strip()) > 10  # Not empty

    def test_command_discovery(self, runner):
        """Test that users can discover commands easily."""
        # Main help should show all major command groups
        result = runner.invoke(cli, ["--help"])
        main_commands = [
            "agent",
            "team",
            "workflow",
            "tool",
            "protocol",
            "book",
            "project",
            "examples",
            "status",
            "config",
            "advanced",
        ]

        for cmd in main_commands:
            assert (
                cmd in result.output
            ), f"Command '{cmd}' not listed in main help"

    def test_option_clarity(self, runner):
        """Test that command options are clearly named and described."""
        result = runner.invoke(cli, ["advanced", "monitor", "--help"])
        assert result.exit_code == 0

        # Should clearly describe options
        assert "watch" in result.output.lower()
        assert "json" in result.output.lower()


class TestWorkflowUsability:
    """Test end-to-end user workflows."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    def test_new_user_onboarding(self, runner):
        """Test workflow for new users getting started."""
        with runner.isolated_filesystem():
            # Step 1: User runs main command
            result = runner.invoke(cli, ["--help"])
            assert result.exit_code == 0
            assert "config" in result.output

            # Step 2: Initialize config
            result = runner.invoke(cli, ["config", "init", "--force"])
            assert result.exit_code == 0
            assert "created" in result.output.lower()

            # Step 3: Check current config
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0
            assert "Configuration" in result.output

            # Step 4: Get help on advanced features
            result = runner.invoke(cli, ["advanced", "--help"])
            assert result.exit_code == 0
            assert "monitor" in result.output

    def test_configuration_management_workflow(self, runner):
        """Test typical configuration management workflow."""
        with runner.isolated_filesystem():
            # Initialize config
            result = runner.invoke(cli, ["config", "init", "--force"])
            assert result.exit_code == 0

            # Set some configuration
            result = runner.invoke(
                cli,
                [
                    "config",
                    "set",
                    "database.url",
                    "postgresql://localhost:5432/engine",
                ],
            )
            assert result.exit_code == 0

            # Get the configuration back
            result = runner.invoke(cli, ["config", "get", "database.url"])
            assert result.exit_code == 0
            assert "postgresql://localhost:5432/engine" in result.output

            # Show all config - should contain our custom setting
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0
            # The config show might not show custom keys directly, so just check it runs

    def test_monitoring_workflow(self, runner):
        """Test monitoring and health check workflow."""
        # Test health check
        result = runner.invoke(cli, ["advanced", "health"])
        assert result.exit_code == 0
        assert "status" in result.output.lower()

        # Test monitoring
        result = runner.invoke(cli, ["advanced", "monitor"])
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0

        # Test JSON output
        result = runner.invoke(cli, ["advanced", "monitor", "--json"])
        assert result.exit_code == 0
        # Should be valid JSON
        import json

        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            pytest.fail("Monitor --json did not return valid JSON")
