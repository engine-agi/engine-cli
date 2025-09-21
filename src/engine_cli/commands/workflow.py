"""Workflow management commands."""
import typer
from rich.console import Console

app = typer.Typer(help="Manage workflows")
console = Console()


@app.command()
def create(name: str = typer.Option(..., "--name", help="Workflow name")):
    """Create a new workflow."""
    console.print(f"[yellow]⚠[/yellow] Workflow creation not yet implemented")
    console.print(f"Would create workflow '{name}'")


@app.command()
def list():
    """List all workflows."""
    console.print("[yellow]⚠[/yellow] Workflow listing not yet implemented")
