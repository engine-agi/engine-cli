"""Engine CLI - Command Line Interface for AI Agent Orchestration."""
import click
from typing import Optional, List
import sys
import os
import yaml
from datetime import datetime

# Import Rich formatting
from engine_cli.formatting import header, success as success_msg, error as error_msg, table, print_table, key_value, info, separator

# Import interactive mode
from engine_cli.interactive import start_interactive

# Import cache system
from engine_cli.cache import cli_cache

@click.group()
@click.version_option("1.0.1", prog_name="Engine CLI")
def cli():
    """Engine Framework CLI - AI Agent Orchestration System."""
    pass


@cli.command()
def version():
    """Show version information."""
    try:
        from engine_core import __version__ as core_version
    except ImportError:
        core_version = "Not available"

    header("Engine Framework Versions")

    # Create version table
    version_table = table("Component Versions", ["Component", "Version"])
    version_table.add_row("Engine CLI", "1.0.1")
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
        import engine_core
        success_msg("Engine Core is available")
        core_available = True
    except ImportError:
        error_msg("Engine Core is not available")
        core_available = False

    if core_available:
        # Check individual modules with lazy loading
        status_checks = {}

        try:
            from engine_core.core.agents import agent as agent_module
            status_checks["Agent module"] = True
        except ImportError:
            status_checks["Agent module"] = False

        try:
            from engine_core.core.teams import team as team_module
            status_checks["Team module"] = True
        except ImportError:
            status_checks["Team module"] = False

        try:
            from engine_core.core.workflows import workflow as workflow_module
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
    pass


# Import and add agent commands directly
try:
    from engine_cli.commands.agent import cli as agent_cli

    # Add all commands from agent module to the agent group
    for cmd_name, cmd_obj in agent_cli.commands.items():
        agent.add_command(cmd_obj)

except ImportError as e:
    @agent.command()
    def error():
        """Agent commands not available."""
        error_msg(f"Agent commands not available: {e}")


# Team commands group
@cli.group()
def team():
    """Team management commands."""
    pass


# Import and add team commands directly
try:
    from engine_cli.commands.team import cli as team_cli

    # Add the entire team CLI group as a subgroup instead of individual commands
    cli.add_command(team_cli, name="team")

except ImportError as e:
    @team.command()
    def error():
        """Team commands not available."""
        error_msg(f"Team commands not available: {e}")


# Workflow commands group
@cli.group()
def workflow():
    """Workflow management commands."""
    pass


# Import and add workflow commands directly
try:
    from engine_cli.commands.workflow import cli as workflow_cli

    # Add all commands from workflow module to the workflow group
    for cmd_name, cmd_obj in workflow_cli.commands.items():
        workflow.add_command(cmd_obj)

except ImportError as e:
    @workflow.command()
    def error():
        """Workflow commands not available."""
        error_msg(f"Workflow commands not available: {e}")


# Tool commands group
@cli.group()
def tool():
    """Tool management commands."""
    pass


# Import and add tool commands directly
try:
    from engine_cli.commands.tool import cli as tool_cli

    # Add all commands from tool module to the tool group
    for cmd_name, cmd_obj in tool_cli.commands.items():
        tool.add_command(cmd_obj)

except ImportError as e:
    @tool.command()
    def error():
        """Tool commands not available."""
        error_msg(f"Tool commands not available: {e}")


# Protocol commands group
@cli.group()
def protocol():
    """Protocol management commands."""
    pass


# Import and add protocol commands directly
try:
    from engine_cli.commands.protocol import cli as protocol_cli

    # Add all commands from protocol module to the protocol group
    for cmd_name, cmd_obj in protocol_cli.commands.items():
        protocol.add_command(cmd_obj)

except ImportError as e:
    @protocol.command()
    def error():
        """Protocol commands not available."""
        error_msg(f"Protocol commands not available: {e}")


# Book commands group
@cli.group()
def book():
    """Book management commands."""
    pass


# Import and add book commands directly
try:
    from engine_cli.commands.book import cli as book_cli

    # Add all commands from book module to the book group
    for cmd_name, cmd_obj in book_cli.commands.items():
        book.add_command(cmd_obj)

except ImportError as e:
    @book.command()
    def error():
        """Book commands not available."""
        error_msg(f"Book commands not available: {e}")


# Project commands group
@cli.group()
def project():
    """Project management commands."""
    pass


# Import and add project commands directly
try:
    from engine_cli.commands.project import cli as project_cli

    # Add all commands from project module to the project group
    for cmd_name, cmd_obj in project_cli.commands.items():
        project.add_command(cmd_obj)

except ImportError as e:
    @project.command()
    def error():
        """Project commands not available."""
        error_msg(f"Project commands not available: {e}")


# Examples commands group
@cli.group()
def examples():
    """Examples management commands."""
    pass


# Import and add examples commands directly
try:
    from engine_cli.commands.examples import cli as examples_cli

    # Add all commands from examples module to the examples group
    for cmd_name, cmd_obj in examples_cli.commands.items():
        examples.add_command(cmd_obj)

except ImportError as e:
    @examples.command()
    def error():
        """Examples commands not available."""
        error_msg(f"Examples commands not available: {e}")


# Config commands group
@cli.group()
def config():
    """Configuration management commands."""
    pass


# Import and add config commands directly
try:
    from engine_cli.commands.config import cli as config_cli

    # Add all commands from config module to the config group
    for cmd_name, cmd_obj in config_cli.commands.items():
        config.add_command(cmd_obj)

except ImportError as e:
    @config.command()
    def error():
        """Config commands not available."""
        error_msg(f"Config commands not available: {e}")


# Advanced commands group
@cli.group()
def advanced():
    """Advanced operations and utilities."""
    pass


# Import and add advanced commands directly
try:
    from engine_cli.commands.advanced import cli as advanced_cli

    # Add all commands from advanced module to the advanced group
    for cmd_name, cmd_obj in advanced_cli.commands.items():
        advanced.add_command(cmd_obj)

except ImportError as e:
    @advanced.command()
    def error():
        """Advanced commands not available."""
        error_msg(f"Advanced commands not available: {e}")


# Monitoring commands group
@cli.group()
def monitoring():
    """Monitoring and observability commands."""
    pass


# Import and add monitoring commands directly
try:
    from engine_cli.commands.monitoring import cli as monitoring_cli

    # Add all commands from monitoring module to the monitoring group
    for cmd_name, cmd_obj in monitoring_cli.commands.items():
        monitoring.add_command(cmd_obj)

except ImportError as e:
    @monitoring.command()
    def error():
        """Monitoring commands not available."""
        error_msg(f"Monitoring commands not available: {e}")


if __name__ == "__main__":
    cli()
