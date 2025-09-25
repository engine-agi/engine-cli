import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner():
    return CliRunner()


class TestExamplesCLICommands:
    """Test CLI commands for examples management"""

    def test_hello_command(self, cli_runner):
        """Test hello command"""
        from engine_cli.commands.examples import hello

        result = cli_runner.invoke(hello)

        assert result.exit_code == 0
        assert "Hello from Engine CLI!" in result.output
        assert "This is a basic example command" in result.output

    def test_list_command_default_level(self, cli_runner):
        """Test list command with default level"""
        from engine_cli.commands.examples import list

        result = cli_runner.invoke(list)

        assert result.exit_code == 0
        assert (
            "Examples listing for level 'beginner' not yet implemented" in result.output
        )

    def test_list_command_beginner_level(self, cli_runner):
        """Test list command with beginner level"""
        from engine_cli.commands.examples import list

        result = cli_runner.invoke(list, ["--level", "beginner"])

        assert result.exit_code == 0
        assert (
            "Examples listing for level 'beginner' not yet implemented" in result.output
        )

    def test_list_command_intermediate_level(self, cli_runner):
        """Test list command with intermediate level"""
        from engine_cli.commands.examples import list

        result = cli_runner.invoke(list, ["--level", "intermediate"])

        assert result.exit_code == 0
        assert (
            "Examples listing for level 'intermediate' not yet implemented"
            in result.output
        )

    def test_list_command_advanced_level(self, cli_runner):
        """Test list command with advanced level"""
        from engine_cli.commands.examples import list

        result = cli_runner.invoke(list, ["--level", "advanced"])

        assert result.exit_code == 0
        assert (
            "Examples listing for level 'advanced' not yet implemented" in result.output
        )

    def test_list_command_invalid_level(self, cli_runner):
        """Test list command with invalid level"""
        from engine_cli.commands.examples import list

        result = cli_runner.invoke(list, ["--level", "invalid"])

        # Click should handle invalid choice and show error
        assert result.exit_code != 0 or "Invalid value for" in result.output

    def test_run_command(self, cli_runner):
        """Test run command"""
        from engine_cli.commands.examples import run

        result = cli_runner.invoke(run, ["basic_agent"])

        assert result.exit_code == 0
        assert "Running example 'basic_agent' not yet implemented" in result.output

    def test_run_command_with_spaces(self, cli_runner):
        """Test run command with name containing spaces"""
        from engine_cli.commands.examples import run

        result = cli_runner.invoke(run, ["my example name"])

        assert result.exit_code == 0
        assert "Running example 'my example name' not yet implemented" in result.output

    def test_create_command_basic(self, cli_runner):
        """Test create command without output directory"""
        from engine_cli.commands.examples import create

        result = cli_runner.invoke(create, ["new_example"])

        assert result.exit_code == 0
        assert "Creating example 'new_example' not yet implemented" in result.output
        assert "Would create example in current directory" in result.output

    def test_create_command_with_output(self, cli_runner):
        """Test create command with output directory"""
        from engine_cli.commands.examples import create

        result = cli_runner.invoke(create, ["new_example", "--output", "/tmp/examples"])

        assert result.exit_code == 0
        assert "Creating example 'new_example' not yet implemented" in result.output
        assert "Would create example in: /tmp/examples" in result.output

    def test_create_command_with_relative_output(self, cli_runner):
        """Test create command with relative output directory"""
        from engine_cli.commands.examples import create

        result = cli_runner.invoke(
            create, ["new_example", "--output", "examples/my_project"]
        )

        assert result.exit_code == 0
        assert "Creating example 'new_example' not yet implemented" in result.output
        assert "Would create example in: examples/my_project" in result.output

    def test_templates_command(self, cli_runner):
        """Test templates command"""
        from engine_cli.commands.examples import templates

        result = cli_runner.invoke(templates)

        assert result.exit_code == 0
        assert "Example templates listing not yet implemented" in result.output
        assert "Available templates:" in result.output
        assert "basic-agent: Simple agent example" in result.output
        assert "team-coordination: Multi-agent team example" in result.output
        assert "workflow-automation: Workflow orchestration example" in result.output
        assert "tool-integration: External tool integration example" in result.output

    def test_hello_command_error_handling(self, cli_runner):
        """Test hello command error handling"""
        from engine_cli.commands.examples import hello

        result = cli_runner.invoke(hello)
        assert result.exit_code == 0
        # Error handling is basic - just ensures command doesn't crash

    def test_list_command_error_handling(self, cli_runner):
        """Test list command error handling"""
        from engine_cli.commands.examples import list

        result = cli_runner.invoke(list)
        assert result.exit_code == 0
        # Error handling is basic - just ensures command doesn't crash

    def test_run_command_error_handling(self, cli_runner):
        """Test run command error handling"""
        from engine_cli.commands.examples import run

        result = cli_runner.invoke(run, ["test"])
        assert result.exit_code == 0
        # Error handling is basic - just ensures command doesn't crash

    def test_create_command_error_handling(self, cli_runner):
        """Test create command error handling"""
        from engine_cli.commands.examples import create

        result = cli_runner.invoke(create, ["test"])
        assert result.exit_code == 0
        # Error handling is basic - just ensures command doesn't crash

    def test_templates_command_error_handling(self, cli_runner):
        """Test templates command error handling"""
        from engine_cli.commands.examples import templates

        result = cli_runner.invoke(templates)
        assert result.exit_code == 0
        # Error handling is basic - just ensures command doesn't crash

    def test_cli_group_exists(self, cli_runner):
        """Test that the CLI group exists and can be invoked"""
        from engine_cli.commands.examples import cli

        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Example commands" in result.output
        assert "hello" in result.output
        assert "list" in result.output
        assert "run" in result.output
        assert "create" in result.output
        assert "templates" in result.output

    def test_hello_command_help(self, cli_runner):
        """Test hello command help"""
        from engine_cli.commands.examples import hello

        result = cli_runner.invoke(hello, ["--help"])

        assert result.exit_code == 0
        assert "Say hello" in result.output

    def test_list_command_help(self, cli_runner):
        """Test list command help"""
        from engine_cli.commands.examples import list

        result = cli_runner.invoke(list, ["--help"])

        assert result.exit_code == 0
        assert "List available examples" in result.output
        assert "--level" in result.output

    def test_run_command_help(self, cli_runner):
        """Test run command help"""
        from engine_cli.commands.examples import run

        result = cli_runner.invoke(run, ["--help"])

        assert result.exit_code == 0
        assert "Run a specific example" in result.output

    def test_create_command_help(self, cli_runner):
        """Test create command help"""
        from engine_cli.commands.examples import create

        result = cli_runner.invoke(create, ["--help"])

        assert result.exit_code == 0
        assert "Create a new example project" in result.output
        assert "--output" in result.output

    def test_templates_command_help(self, cli_runner):
        """Test templates command help"""
        from engine_cli.commands.examples import templates

        result = cli_runner.invoke(templates, ["--help"])

        assert result.exit_code == 0
        assert "List available example templates" in result.output


if __name__ == "__main__":
    pytest.main([__file__])
