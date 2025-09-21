"""Tool management commands."""
import typer
from rich.console import Console

app = typer.Typer(help="Manage tools and integrations")
console = Console()


@app.command()
def list():
    """List all tools."""
    console.print("[yellow]⚠[/yellow] Tool listing not yet implemented")
