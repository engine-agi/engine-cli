"""Team management commands."""
import typer
from rich.console import Console

app = typer.Typer(help="Manage agent teams")
console = Console()


@app.command()
def create(
    name: str = typer.Option(..., "--name", help="Team name"),
    agents: list[str] = typer.Option(None, "--agents", help="Agent IDs to include"),
):
    """Create a new team."""
    console.print(f"[yellow]⚠[/yellow] Team creation not yet implemented")
    console.print(f"Would create team '{name}' with agents: {agents}")


@app.command()
def list():
    """List all teams."""
    console.print("[yellow]⚠[/yellow] Team listing not yet implemented")
