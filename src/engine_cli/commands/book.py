"""Book management commands."""
import typer
from rich.console import Console

app = typer.Typer(help="Manage memory systems")
console = Console()


@app.command()
def list():
    """List all books."""
    console.print("[yellow]⚠[/yellow] Book listing not yet implemented")
