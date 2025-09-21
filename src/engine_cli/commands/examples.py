"""Example commands."""
import typer
from rich.console import Console

app = typer.Typer(help="Example commands")
console = Console()


@app.command()
def hello():
    """Say hello."""
    console.print("[green]Hello from Engine CLI![/green]")
    console.print("This is a basic example command.")


@app.command()
def list():
    """List available examples."""
    console.print("[yellow]⚠[/yellow] Examples listing not yet implemented")
