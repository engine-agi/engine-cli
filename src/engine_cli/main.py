"""Engine CLI - Command Line Interface for AI Agent Orchestration."""
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine_cli.commands import agent, team, workflow, tool, protocol, book, project, examples, monitoring

# Initialize Typer app
app = typer.Typer(
    name="engine",
    help="Engine Framework CLI - AI Agent Orchestration System",
    add_completion=True,
)

# Initialize Rich console for beautiful output
console = Console()

# Add command groups
try:
    app.add_typer(agent.app, name="agent", help="Manage AI agents")
except:
    pass

try:
    app.add_typer(team.app, name="team", help="Manage agent teams")
except:
    pass

try:
    app.add_typer(workflow.app, name="workflow", help="Manage workflows")
except:
    pass

try:
    app.add_typer(tool.app, name="tool", help="Manage tools and integrations")
except:
    pass

try:
    app.add_typer(protocol.app, name="protocol", help="Manage protocols")
except:
    pass

try:
    app.add_typer(book.app, name="book", help="Manage memory systems")
except:
    pass

try:
    app.add_typer(project.app, name="project", help="Manage projects")
except:
    pass

try:
    app.add_typer(examples.app, name="examples", help="Example commands")
except:
    pass

try:
    app.add_typer(monitoring.app, name="monitoring", help="System monitoring")
except:
    pass


@app.callback()
def callback():
    """Engine Framework CLI - AI Agent Orchestration System."""


@app.command()
def version():
    """Show version information."""
    from engine_core import __version__ as core_version

    table = Table(title="Engine Framework Versions")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="magenta")

    table.add_row("Engine CLI", "1.0.0")
    table.add_row("Engine Core", core_version)

    console.print(table)


@app.command()
def status():
    """Show system status."""
    console.print("[green]✓[/green] Engine CLI is running")
    console.print("[green]✓[/green] Engine Core is available")

    try:
        from engine_core.core.agents import agent as agent_module
        console.print("[green]✓[/green] Agent module loaded")
    except ImportError:
        console.print("[red]✗[/red] Agent module not available")

    try:
        from engine_core.core.teams import team as team_module
        console.print("[green]✓[/green] Team module loaded")
    except ImportError:
        console.print("[red]✗[/red] Team module not available")

    try:
        from engine_core.core.workflows import workflow as workflow_module
        console.print("[green]✓[/green] Workflow module loaded")
    except ImportError:
        console.print("[red]✗[/red] Workflow module not available")


if __name__ == "__main__":
    app()
