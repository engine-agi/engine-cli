"""Agent management commands."""
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List

app = typer.Typer(help="Manage AI agents")
console = Console()


@app.command()
def create(
    name: str = typer.Option(..., "--name", help="Agent name"),
    model: str = typer.Option("claude-3.5-sonnet", "--model", help="AI model to use"),
    speciality: Optional[str] = typer.Option(None, "--speciality", help="Agent speciality"),
    stack: Optional[List[str]] = typer.Option(None, "--stack", help="Technology stack (can be used multiple times)"),
):
    """Create a new AI agent."""
    try:
        from engine_core.core.agents.agent_builder import AgentBuilder

        builder = AgentBuilder()
        builder = builder.with_id(name)
        builder = builder.with_name(name)
        builder = builder.with_model(model)

        if speciality:
            builder = builder.with_speciality(speciality)

        if stack:
            builder = builder.with_stack(stack)

        agent = builder.build()

        console.print(f"[green]✓[/green] Agent '{name}' created successfully!")
        console.print(f"  Model: {model}")
        if speciality:
            console.print(f"  Speciality: {speciality}")
        if stack:
            console.print(f"  Stack: {', '.join(stack)}")

    except ImportError:
        console.print("[red]✗[/red] Engine Core not available. Please install engine-core first.")
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating agent: {e}")


@app.command()
def list():
    """List all agents."""
    try:
        # TODO: Implement agent listing from database/storage
        console.print("[yellow]⚠[/yellow] Agent listing not yet implemented")
        console.print("This will list all created agents from the database")

    except Exception as e:
        console.print(f"[red]✗[/red] Error listing agents: {e}")


@app.command()
def show(
    name: str = typer.Argument(..., help="Agent name")
):
    """Show details of a specific agent."""
    try:
        # TODO: Implement agent details retrieval
        console.print(f"[yellow]⚠[/yellow] Agent details for '{name}' not yet implemented")
        console.print("This will show detailed information about the specified agent")

    except Exception as e:
        console.print(f"[red]✗[/red] Error showing agent: {e}")


@app.command()
def delete(
    name: str = typer.Argument(..., help="Agent name"),
    force: bool = typer.Option(False, "--force", help="Force deletion without confirmation")
):
    """Delete an agent."""
    try:
        if not force:
            console.print(f"[yellow]⚠[/yellow] This will delete agent '{name}'. Use --force to confirm.")
            return

        # TODO: Implement agent deletion
        console.print(f"[yellow]⚠[/yellow] Agent deletion not yet implemented")

    except Exception as e:
        console.print(f"[red]✗[/red] Error deleting agent: {e}")
