"""Engine CLI - Command Line Interface for AI Agent Orchestration."""

from typing import TYPE_CHECKING

import click

# Import Rich formatting
from engine_cli.formatting import error as error_msg
from engine_cli.formatting import header, info, print_table, separator
from engine_cli.formatting import success as success_msg
from engine_cli.formatting import table

# Import interactive mode
from engine_cli.interactive import start_interactive

# Import engine core components for type checking
if TYPE_CHECKING:
    # Type checking imports handled individually in methods
    pass


@click.group()
@click.version_option("1.1.0", prog_name="Engine CLI")
def cli():
    """Engine Framework CLI - AI Agent Orchestration System."""


@cli.command()
def version():
    """Show version information."""
    try:
        from engine_core import __version__ as core_version  # type: ignore
    except ImportError:
        core_version = "Not available"

    header("Engine Framework Versions")

    # Create version table
    version_table = table("Component Versions", ["Component", "Version"])
    version_table.add_row("Engine CLI", "1.1.0")
    version_table.add_row("Engine Core", core_version)
    print_table(version_table)


@cli.command()
def status():
    """Show system status."""
    header("System Status")

    # Check CLI status
    success_msg("Engine CLI is running")

    # Check core availability
    try:
        import engine_core  # noqa: F401

        success_msg("Engine Core is available")
        core_available = True
    except ImportError:
        error_msg("Engine Core is not available")
        core_available = False

    if core_available:
        # Check individual modules with lazy loading using public APIs
        status_checks = {}

        try:
            from engine_core import AgentBuilder  # type: ignore  # noqa: F401

            status_checks["Agent module"] = True
        except ImportError:
            status_checks["Agent module"] = False

        try:
            from engine_core import TeamBuilder  # type: ignore  # noqa: F401

            status_checks["Team module"] = True
        except ImportError:
            status_checks["Team module"] = False

        try:
            from engine_core import WorkflowBuilder  # type: ignore  # noqa: F401

            status_checks["Workflow module"] = True
        except ImportError:
            status_checks["Workflow module"] = False

        # Display status summary
        from engine_cli.formatting import status_summary

        status_summary(status_checks)


@cli.command()
def interactive():
    """Start interactive CLI mode with auto-complete and history."""
    header("Starting Interactive Mode")
    info("Launching interactive CLI...")
    separator()
    start_interactive()


# Agent commands group
@cli.group()
def agent():
    """Agent management commands."""


# Import and add agent commands directly
try:
    from engine_cli.commands.agent import cli as agent_cli

    # Add all commands from agent module to the agent group
    for cmd_name, cmd_obj in agent_cli.commands.items():
        agent.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @agent.command(name="error_agent")
    def error_cmd():  # noqa: F811
        """Agent commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821  # noqa: F821


# Team commands group
@cli.group()
def team():
    """Team management commands."""


# Import and add team commands directly
try:
    from engine_cli.commands.team import cli as team_cli

    # Add the entire team CLI group as a subgroup instead of individual command
    cli.add_command(team_cli, name="team")

except ImportError as e:  # noqa: F841

    @team.command(name="error_team")
    def error_cmd():  # noqa: F811
        """Team commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Workflow commands group
@cli.group()
def workflow():
    """Workflow management commands."""


# Import and add workflow commands directly
try:
    from engine_cli.commands.workflow import cli as workflow_cli

    # Add all commands from workflow module to the workflow group
    for cmd_name, cmd_obj in workflow_cli.commands.items():
        workflow.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @workflow.command(name="error_workflow")
    def error_cmd():  # noqa: F811
        """Workflow commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Tool commands group
@cli.group()
def tool():
    """Tool management commands."""


# Import and add tool commands directly
try:
    from engine_cli.commands.tool import cli as tool_cli

    # Add all commands from tool module to the tool group
    for cmd_name, cmd_obj in tool_cli.commands.items():
        tool.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @tool.command(name="error_tool")
    def error_cmd():  # noqa: F811
        """Tool commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Protocol commands group
@cli.group()
def protocol():
    """Protocol management commands."""


# Import and add protocol commands directly
try:
    from engine_cli.commands.protocol import cli as protocol_cli

    # Add all commands from protocol module to the protocol group
    for cmd_name, cmd_obj in protocol_cli.commands.items():
        protocol.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @protocol.command(name="error_protocol")
    def error_cmd():  # noqa: F811
        """Protocol commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Book commands group
@cli.group()
def book():
    """Book management commands."""


# Import and add book commands directly
try:
    from engine_cli.commands.book import cli as book_cli

    # Add all commands from book module to the book group
    for cmd_name, cmd_obj in book_cli.commands.items():
        book.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @book.command(name="error_book")
    def error_cmd():  # noqa: F811
        """Book commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Project commands group
@cli.group()
def project():
    """Project management commands."""


# Import and add project commands directly
try:
    from engine_cli.commands.project import cli as project_cli

    # Add all commands from project module to the project group
    for cmd_name, cmd_obj in project_cli.commands.items():
        project.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @project.command(name="error_project")
    def error_cmd():  # noqa: F811
        """Project commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Examples commands group
@cli.group()
def examples():
    """Examples management commands."""


# Import and add examples commands directly
try:
    from engine_cli.commands.examples import cli as examples_cli

    # Add all commands from examples module to the examples group
    for cmd_name, cmd_obj in examples_cli.commands.items():
        examples.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @examples.command(name="error_examples")
    def error_cmd():  # noqa: F811
        """Examples commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Config commands group
@cli.group()
def config():
    """Configuration management commands."""


# Import and add config commands directly
try:
    from engine_cli.commands.config import cli as config_cli

    # Add all commands from config module to the config group
    for cmd_name, cmd_obj in config_cli.commands.items():
        config.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @config.command(name="error_config")
    def error_cmd():  # noqa: F811
        """Config commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Advanced commands group
@cli.group()
def advanced():
    """Advanced operations and utilities."""


# Import and add advanced commands directly
try:
    from engine_cli.commands.advanced import cli as advanced_cli

    # Add all commands from advanced module to the advanced group
    for cmd_name, cmd_obj in advanced_cli.commands.items():
        advanced.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @advanced.command(name="error_advanced")
    def error_cmd():  # noqa: F811
        """Advanced commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


# Monitoring commands group
@cli.group()
def monitoring():
    """Monitoring and observability commands."""


# Import and add monitoring commands directly
try:
    from engine_cli.commands.monitoring import cli as monitoring_cli

    # Add all commands from monitoring module to the monitoring group
    for cmd_name, cmd_obj in monitoring_cli.commands.items():
        monitoring.add_command(cmd_obj)

except ImportError as e:  # noqa: F841

    @monitoring.command(name="error_monitoring")
    def error_cmd():  # noqa: F811
        """Monitoring commands not available."""
        error_msg(f"Commands not available: {e}")  # noqa: F821


if __name__ == "__main__":
    cli()
