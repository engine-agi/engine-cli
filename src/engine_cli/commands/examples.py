"""Example commands."""

import click


@click.group()
def cli():
    """Example commands."""
    pass


@cli.command()
def hello():
    """Say hello."""
    click.echo("Hello from Engine CLI!")
    click.echo("This is a basic example command.")


@cli.command()
@click.option(
    "--level",
    type=click.Choice(["beginner", "intermediate", "advanced"]),
    default="beginner",
    help="Example difficulty level",
)
def list(level):
    """List available examples."""
    try:
        click.echo(
            f"⚠ Examples listing for level '{level}' not yet implemented"
        )
        click.echo(
            "This will list all available examples organized by difficulty level"
        )
    except Exception as e:
        click.echo(f"✗ Error listing examples: {e}")


@cli.command()
@click.argument("name")
def run(name):
    """Run a specific example."""
    try:
        click.echo(f"⚠ Running example '{name}' not yet implemented")
        click.echo("This will execute the specified example")
    except Exception as e:
        click.echo(f"✗ Error running example: {e}")


@cli.command()
@click.argument("name")
@click.option("--output", help="Output directory for the example")
def create(name, output):
    """Create a new example project."""
    try:
        click.echo(f"⚠ Creating example '{name}' not yet implemented")
        if output:
            click.echo(f"Would create example in: {output}")
        else:
            click.echo("Would create example in current directory")
    except Exception as e:
        click.echo(f"✗ Error creating example: {e}")


@cli.command()
def templates():
    """List available example templates."""
    try:
        click.echo("⚠ Example templates listing not yet implemented")
        click.echo("This will show available project templates")
        click.echo("Available templates:")
        click.echo("  - basic-agent: Simple agent example")
        click.echo("  - team-coordination: Multi-agent team example")
        click.echo("  - workflow-automation: Workflow orchestration example")
        click.echo("  - tool-integration: External tool integration example")
    except Exception as e:
        click.echo(f"✗ Error listing templates: {e}")
