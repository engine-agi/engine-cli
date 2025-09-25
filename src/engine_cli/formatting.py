"""Rich formatting utilities for Engine CLI."""

from typing import Any, Dict, List, Optional

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

# Initialize Rich console
console = Console()


class CLIRichFormatter:
    """Rich formatting utilities for CLI output."""

    @staticmethod
    def print_success(message: str):
        """Print success message with green checkmark."""
        console.print(f"[green]✓[/green] {message}")

    @staticmethod
    def print_error(message: str):
        """Print error message with red X."""
        console.print(f"[red]✗[/red] {message}")

    @staticmethod
    def print_warning(message: str):
        """Print warning message with yellow warning sign."""
        console.print(f"[yellow]⚠[/yellow] {message}")

    @staticmethod
    def print_info(message: str):
        """Print info message with blue info sign."""
        console.print(f"[blue]ℹ[/blue] {message}")

    @staticmethod
    def print_header(title: str, subtitle: Optional[str] = None):
        """Print a formatted header."""
        if subtitle:
            panel = Panel(
                f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]",
                border_style="cyan",
                padding=(1, 2),
            )
        else:
            panel = Panel(
                f"[bold cyan]{title}[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        console.print(panel)

    @staticmethod
    def create_table(
        title: str = "",
        columns: Optional[List[str]] = None,
        show_header: bool = True,
        box_style=box.ROUNDED,
    ) -> Table:
        """Create a formatted table."""
        table = Table(
            title=title,
            show_header=show_header,
            box=box_style,
            header_style="bold cyan",
            title_style="bold magenta",
        )

        if columns:
            for col in columns:
                table.add_column(col, style="white")

        return table

    @staticmethod
    def print_table(table: Table):
        """Print a Rich table."""
        console.print(table)

    @staticmethod
    def print_key_value_pairs(
        data: Dict[str, Any], title: Optional[str] = None
    ):
        """Print key-value pairs in a nice format."""
        if title:
            CLIRichFormatter.print_header(title)

        max_key_len = max(len(str(k)) for k in data.keys()) if data else 0

        for key, value in data.items():
            key_str = f"[cyan]{str(key):<{max_key_len}}[/cyan]"
            value_str = f"[white]{value}[/white]"
            console.print(f"{key_str}: {value_str}")

    @staticmethod
    def print_list(
        items: List[str],
        title: Optional[str] = None,
        bullet: str = "•",
        style: str = "white",
    ):
        """Print a list with bullets."""
        if title:
            console.print(f"[bold cyan]{title}:[/bold cyan]")

        for item in items:
            console.print(f"[{style}]{bullet} {item}[/{style}]")

    @staticmethod
    def create_progress(description: str = "Processing...") -> Progress:
        """Create a progress bar."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        )

    @staticmethod
    def print_columns(
        items: List[str], equal: bool = True, expand: bool = False
    ):
        """Print items in columns."""
        columns = Columns(items, equal=equal, expand=expand)
        console.print(columns)

    @staticmethod
    def print_separator(char: str = "─", length: int = 50, style: str = "dim"):
        """Print a separator line."""
        console.print(f"[{style}]{char * length}[/{style}]")

    @staticmethod
    def print_status_summary(
        statuses: Dict[str, bool], title: str = "Status Summary"
    ):
        """Print a status summary with checkmarks/X marks."""
        CLIRichFormatter.print_header(title)

        for item, status in statuses.items():
            if status:
                CLIRichFormatter.print_success(f"{item}")
            else:
                CLIRichFormatter.print_error(f"{item}")

    @staticmethod
    def print_metrics(metrics: Dict[str, Any], title: str = "Metrics"):
        """Print metrics in a formatted way."""
        CLIRichFormatter.print_header(title)

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if key.lower().endswith(("count", "total", "size", "length")):
                    value_str = f"[green]{value:,}[/green]"
                elif key.lower().endswith(("rate", "percentage", "ratio")):
                    value_str = f"[yellow]{value:.2f}[/yellow]"
                elif key.lower().endswith(("time", "duration", "latency")):
                    value_str = f"[blue]{value:.3f}s[/blue]"
                else:
                    value_str = f"[white]{value}[/white]"
            else:
                value_str = f"[white]{value}[/white]"

            console.print(f"[cyan]{key}:[/cyan] {value_str}")


# Convenience functions for easy importing
def success(message: str):
    """Print success message."""
    CLIRichFormatter.print_success(message)


def error(message: str):
    """Print error message."""
    CLIRichFormatter.print_error(message)


def warning(message: str):
    """Print warning message."""
    CLIRichFormatter.print_warning(message)


def info(message: str):
    """Print info message."""
    CLIRichFormatter.print_info(message)


def header(title: str, subtitle: Optional[str] = None):
    """Print header."""
    CLIRichFormatter.print_header(title, subtitle)


def table(
    title: str = "",
    columns: Optional[List[str]] = None,
    show_header: bool = True,
    box_style=box.ROUNDED,
) -> Table:
    """Create table."""
    return CLIRichFormatter.create_table(
        title, columns, show_header, box_style
    )


def print_table(table: Table):
    """Print table."""
    CLIRichFormatter.print_table(table)


def key_value(data: Dict[str, Any], title: Optional[str] = None):
    """Print key-value pairs."""
    CLIRichFormatter.print_key_value_pairs(data, title)


def list_items(
    items: List[str],
    title: Optional[str] = None,
    bullet: str = "•",
    style: str = "white",
):
    """Print list."""
    CLIRichFormatter.print_list(items, title, bullet, style)


def progress(description: str = "Processing...") -> Progress:
    """Create progress bar."""
    return CLIRichFormatter.create_progress(description)


def columns(items: List[str], equal: bool = True, expand: bool = False):
    """Print columns."""
    CLIRichFormatter.print_columns(items, equal, expand)


def separator(char: str = "─", length: int = 50, style: str = "dim"):
    """Print separator."""
    CLIRichFormatter.print_separator(char, length, style)


def status_summary(statuses: Dict[str, bool], title: str = "Status Summary"):
    """Print status summary."""
    CLIRichFormatter.print_status_summary(statuses, title)


def metrics(data: Dict[str, Any], title: str = "Metrics"):
    """Print metrics."""
    CLIRichFormatter.print_metrics(data, title)
