"""System monitoring commands."""
import typer
from rich.console import Console

app = typer.Typer(help="System monitoring")
console = Console()


@app.command()
def status():
    """Show system status."""
    console.print("[green]✓[/green] Engine CLI is running")
    console.print("[yellow]⚠[/yellow] Full monitoring not yet implemented")
