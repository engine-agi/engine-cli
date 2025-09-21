"""Project management commands."""
import typer
from rich.console import Console

app = typer.Typer(help="Manage projects")
console = Console()


@app.command()
def create(name: str = typer.Option(..., "--name", help="Project name")):
    """Create a new project."""
    console.print(f"[yellow]⚠[/yellow] Project creation not yet implemented")
    console.print(f"Would create project '{name}'")


@app.command()
def list():
    """List all projects."""
    console.print("[yellow]⚠[/yellow] Project listing not yet implemented")
