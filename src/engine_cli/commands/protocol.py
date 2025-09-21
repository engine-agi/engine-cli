"""Protocol management commands."""
import typer
from rich.console import Console

app = typer.Typer(help="Manage protocols")
console = Console()


@app.command()
def list():
    """List all protocols."""
    console.print("[yellow]⚠[/yellow] Protocol listing not yet implemented")
