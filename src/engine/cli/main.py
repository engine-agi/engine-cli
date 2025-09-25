#!/usr/bin/env python3
"""
Engine CLI - Command Line Interface for Engine Framework
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.theme import Theme

# Add src to path for development
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Custom theme for Engine CLI
engine_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "header": "bold magenta",
        "command": "bold blue",
    }
)

console = Console(theme=engine_theme)


@click.group()
@click.version_option(version="1.0.0", prog_name="Engine CLI")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to config file"
)
def cli(verbose, config):
    """Engine Framework Command Line Interface

    Manage AI agents, teams, workflows, and more.
    """
    if verbose:
        console.print("[info]Verbose mode enabled[/info]")


@cli.command()
def interactive():
    """Start interactive REPL mode"""
    console.print("[header]🚀 Engine Interactive Mode[/header]")
    console.print("Type 'help' for commands or 'exit' to quit")
    console.print()

    while True:
        try:
            command = console.input("[command]engine > [/command]").strip()

            if command in ["exit", "quit", "q"]:
                console.print("[success]Goodbye! 👋[/success]")
                break
            elif command in ["help", "h", "?"]:
                show_help()
            elif command:
                console.print(
                    f"[warning]Command not implemented: {command}[/warning]"
                )
            else:
                continue

        except KeyboardInterrupt:
            console.print(
                "\n[warning]Interrupted. Type 'exit' to quit.[/warning]"
            )
        except EOFError:
            console.print("\n[success]Goodbye! 👋[/success]")
            break


def show_help():
    """Show help information"""
    console.print("[header]Available Commands:[/header]")
    console.print("  [command]help[/command]     - Show this help")
    console.print("  [command]exit[/command]     - Exit interactive mode")
    console.print()
    console.print("[header]Agent Commands:[/header]")
    console.print("  [command]agent create[/command]   - Create new agent")
    console.print("  [command]agent list[/command]     - List all agents")
    console.print("  [command]agent update[/command]   - Update agent")
    console.print("  [command]agent delete[/command]   - Delete agent")
    console.print()
    console.print("[header]Team Commands:[/header]")
    console.print("  [command]team create[/command]    - Create new team")
    console.print("  [command]team list[/command]      - List all teams")
    console.print()
    console.print("[header]Workflow Commands:[/header]")
    console.print("  [command]workflow create[/command] - Create workflow")
    console.print("  [command]workflow run[/command]     - Run workflow")
    console.print("  [command]workflow status[/command]  - Check status")


@cli.command()
def version():
    """Show version information"""
    console.print("[header]Engine CLI v1.0.0[/header]")
    console.print("Part of Engine Framework")
    console.print("https://github.com/engine-agi")


def main():
    """Main entry point"""
    try:
        cli()
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        sys.exit(1)


if __name__ == "__main__":
    main()
