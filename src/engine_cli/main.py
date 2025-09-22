"""Engine CLI - Command Line Interface for AI Agent Orchestration."""
import click
from typing import Optional, List

# Import Rich formatting
from engine_cli.formatting import header, success, error, table, print_table, key_value, info, separator

# Import interactive mode
from engine_cli.interactive import start_interactive

"""Engine CLI - Command Line Interface for AI Agent Orchestration."""
import click
from typing import Optional, List

# Import Rich formatting
from engine_cli.formatting import header, success, error, table, print_table, key_value, info, separator

# Import interactive mode
from engine_cli.interactive import start_interactive

# Import cache system
from engine_cli.cache import cli_cache

# Lazy loading imports - moved to functions to reduce startup time
_command_cache = {}


def _get_command_module(name: str):
    """Lazy load command modules with caching."""
    if name not in _command_cache:
        try:
            # Check if module has changed
            module_file = f"engine_cli/commands/{name}.py"
            if cli_cache.is_module_changed(name, module_file):
                # Module changed, clear cache entry
                if name in _command_cache:
                    del _command_cache[name]

            if name == "agent":
                from engine_cli.commands import agent
                _command_cache[name] = agent
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "team":
                from engine_cli.commands import team
                _command_cache[name] = team
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "workflow":
                from engine_cli.commands import workflow
                _command_cache[name] = workflow
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "tool":
                from engine_cli.commands import tool
                _command_cache[name] = tool
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "protocol":
                from engine_cli.commands import protocol
                _command_cache[name] = protocol
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "book":
                from engine_cli.commands import book
                _command_cache[name] = book
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "project":
                from engine_cli.commands import project
                _command_cache[name] = project
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "examples":
                from engine_cli.commands import examples
                _command_cache[name] = examples
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "monitoring":
                from engine_cli.commands import monitoring
                _command_cache[name] = monitoring
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "config":
                from engine_cli.commands import config
                _command_cache[name] = config
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
            elif name == "advanced":
                from engine_cli.commands import advanced
                _command_cache[name] = advanced
                cli_cache.set_module_hash(name, cli_cache._get_file_hash(module_file))
        except ImportError:
            _command_cache[name] = None

    return _command_cache[name]


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
    success("Engine CLI is running")

    # Check core availability
    try:
        import engine_core
        success("Engine Core is available")
        core_available = True
    except ImportError:
        error("Engine Core is not available")
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


# Lazy command registration - only load when needed
@cli.command()
@click.pass_context
def agent(ctx):
    """Agent management commands."""
    agent_module = _get_command_module("agent")
    if agent_module and hasattr(agent_module, 'cli'):
        ctx.invoke(agent_module.cli)
    else:
        error("Agent commands not available")


@cli.command()
@click.pass_context
def team(ctx):
    """Team management commands."""
    team_module = _get_command_module("team")
    if team_module and hasattr(team_module, 'cli'):
        ctx.invoke(team_module.cli)
    else:
        error("Team commands not available")


@cli.command()
@click.pass_context
def workflow(ctx):
    """Workflow management commands."""
    workflow_module = _get_command_module("workflow")
    if workflow_module and hasattr(workflow_module, 'cli'):
        ctx.invoke(workflow_module.cli)
    else:
        error("Workflow commands not available")


@cli.command()
@click.pass_context
def tool(ctx):
    """Tool management commands."""
    tool_module = _get_command_module("tool")
    if tool_module and hasattr(tool_module, 'cli'):
        ctx.invoke(tool_module.cli)
    else:
        error("Tool commands not available")


@cli.command()
@click.pass_context
def protocol(ctx):
    """Protocol management commands."""
    protocol_module = _get_command_module("protocol")
    if protocol_module and hasattr(protocol_module, 'cli'):
        ctx.invoke(protocol_module.cli)
    else:
        error("Protocol commands not available")


@cli.command()
@click.pass_context
def book(ctx):
    """Book management commands."""
    book_module = _get_command_module("book")
    if book_module and hasattr(book_module, 'cli'):
        ctx.invoke(book_module.cli)
    else:
        error("Book commands not available")


@cli.command()
@click.pass_context
def project(ctx):
    """Project management commands."""
    project_module = _get_command_module("project")
    if project_module and hasattr(project_module, 'cli'):
        ctx.invoke(project_module.cli)
    else:
        error("Project commands not available")


@cli.command()
@click.pass_context
def examples(ctx):
    """Examples management commands."""
    examples_module = _get_command_module("examples")
    if examples_module and hasattr(examples_module, 'cli'):
        ctx.invoke(examples_module.cli)
    else:
        error("Examples commands not available")


@cli.command()
@click.pass_context
def config(ctx):
    """Configuration management commands."""
    config_module = _get_command_module("config")
    if config_module and hasattr(config_module, 'cli'):
        ctx.invoke(config_module.cli)
    else:
        error("Config commands not available")


@cli.command()
@click.pass_context
def advanced(ctx):
    """Advanced operations and utilities."""
    advanced_module = _get_command_module("advanced")
    if advanced_module and hasattr(advanced_module, 'cli'):
        ctx.invoke(advanced_module.cli)
    else:
        error("Advanced commands not available")


if __name__ == "__main__":
    cli()
