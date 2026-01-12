"""
Enhanced CLI utilities for AutoRig with better progress indicators and error handling.
"""

import os
import traceback
from typing import Any, Dict, List, Optional
from pathlib import Path
import shutil
import time
from datetime import datetime
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    TaskID,
)
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich import box
import typer

console = Console()


class EnhancedProgressTracker:
    """Enhanced progress tracker with rich UI components."""

    def __init__(self, show_eta: bool = True, show_percentage: bool = True):
        self.show_eta = show_eta
        self.show_percentage = show_percentage
        self.progress = None
        self.current_task = None
        self.tasks: Dict[str, TaskID] = {}

    def __enter__(self):
        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ]

        if self.show_percentage:
            columns.append(BarColumn())
            columns.append(TaskProgressColumn())

        if self.show_eta:
            columns.append(TimeElapsedColumn())
            columns.append(TimeRemainingColumn())

        columns.append(MofNCompleteColumn())

        self.progress = Progress(*columns, console=console)
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()

    def add_task(
        self, description: str, total: int = 100, **kwargs
    ) -> Optional[TaskID]:
        """Add a new progress task."""
        if not self.progress:
            return None
        task_id = self.progress.add_task(description, total=total, **kwargs)
        self.tasks[description] = task_id
        return task_id

    def update(
        self,
        task_id: TaskID,
        advance: int = 1,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Update a progress task."""
        if self.progress and task_id:
            self.progress.update(
                task_id, advance=advance, description=description, **kwargs
            )

    def complete(self, task_id: TaskID):
        """Mark a task as complete."""
        if self.progress and task_id:
            self.progress.update(task_id, completed=self.progress.tasks[task_id].total)


class ErrorHandler:
    """Enhanced error handling with actionable suggestions."""

    ERROR_SUGGESTIONS = {
        "FileNotFoundError": [
            "Check if the configuration file exists",
            "Verify the file path is correct",
            "Ensure you have read permissions for the file",
        ],
        "PermissionError": [
            "Try running with sudo (if appropriate)",
            "Check file/directory permissions",
            "Verify you have write access to the target location",
        ],
        "ConnectionError": [
            "Check your internet connection",
            "Verify the URL or repository is accessible",
            "Try again in a few moments",
        ],
        "ValidationError": [
            "Check your YAML syntax",
            "Verify all required fields are present",
            "Run 'autorig validate <config>' to check configuration",
        ],
        "ConfigError": [
            "Review your configuration file",
            "Check for typos in field names",
            "Ensure all lists and objects are properly formatted",
        ],
        "InstallError": [
            "Check if package manager is available",
            "Verify package names are correct for your system",
            "Try installing packages manually first",
        ],
    }

    @classmethod
    def format_error(cls, error: Exception, show_traceback: bool = False) -> Panel:
        """Format an error with helpful suggestions."""
        error_type = type(error).__name__
        error_message = str(error)

        # Build suggestion list
        suggestions = cls.ERROR_SUGGESTIONS.get(
            error_type,
            [
                "Check the error message above",
                "Run with --verbose for more details",
                "Consult the documentation for help",
            ],
        )

        # Create error content
        error_content = f"[bold red]Error Type:[/bold red] {error_type}\n"
        error_content += f"[bold red]Message:[/bold red] {error_message}\n"

        if show_traceback:
            tb_lines = traceback.format_exc().split("\n")
            error_content += "\n[bold red]Traceback:[/bold red]\n"
            for line in tb_lines[-10:]:  # Last 10 lines of traceback
                if line.strip():
                    error_content += f"[dim]{line}[/dim]\n"

        # Add suggestions
        error_content += "\n[bold yellow]Suggestions:[/bold yellow]\n"
        for i, suggestion in enumerate(suggestions, 1):
            error_content += f"  {i}. {suggestion}\n"

        return Panel(
            error_content,
            title="[bold red]❌ Error Occurred[/bold red]",
            border_style="red",
            padding=(1, 2),
        )

    @classmethod
    def show_success(cls, message: str, details: Optional[str] = None) -> Panel:
        """Show a success message."""
        content = f"[bold green]✓[/bold green] {message}"
        if details:
            content += f"\n[dim]{details}[/dim]"

        return Panel(
            content,
            title="[bold green]✅ Success[/bold green]",
            border_style="green",
            padding=(1, 2),
        )

    @classmethod
    def show_warning(cls, message: str, details: Optional[str] = None) -> Panel:
        """Show a warning message."""
        content = f"[bold yellow]⚠[/bold yellow] {message}"
        if details:
            content += f"\n[dim]{details}[/dim]"

        return Panel(
            content,
            title="[bold yellow]⚠️ Warning[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )


class InfoDisplay:
    """Enhanced information display utilities."""

    @staticmethod
    def show_summary(title: str, data: Dict[str, Any]) -> None:
        """Display a summary table."""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        for key, value in data.items():
            table.add_row(key, str(value))

        console.print(table)

    @staticmethod
    def show_operation_summary(operations: List[Dict[str, Any]]) -> None:
        """Display operation summary with status indicators."""
        table = Table(title="Operation Summary", box=box.ROUNDED)
        table.add_column("Operation", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="dim")

        for op in operations:
            status_icon = "✅" if op.get("success", False) else "❌"
            status_text = f"{status_icon} {op.get('status', 'Unknown')}"

            table.add_row(op.get("name", "Unknown"), status_text, op.get("details", ""))

        console.print(table)

    @staticmethod
    def show_configuration_preview(config_data: Dict[str, Any]) -> None:
        """Show a preview of the configuration."""
        console.print(Rule("Configuration Preview", style="bold blue"))

        sections = [
            ("System Packages", len(config_data.get("system", {}).get("packages", []))),
            (
                "Git Repositories",
                len(config_data.get("git", {}).get("repositories", [])),
            ),
            ("Dotfiles", len(config_data.get("dotfiles", []))),
            ("Scripts", len(config_data.get("scripts", []))),
            (
                "Hooks",
                len(config_data.get("hooks", {})) if config_data.get("hooks") else 0,
            ),
        ]

        for section_name, count in sections:
            if count > 0:
                console.print(f"• {section_name}: {count} items")

        console.print(Rule(style="bold blue"))


def confirm_action(message: str, default: bool = False) -> bool:
    """Enhanced confirmation prompt."""
    return typer.confirm(message, default=default, show_default=True, prompt_suffix=" ")


def validate_config_exists(config_path: str) -> Path:
    """Validate that a configuration file exists and is accessible."""
    path = Path(config_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Configuration path is not a file: {path}")

    if not os.access(path, os.R_OK):
        raise PermissionError(f"Cannot read configuration file: {path}")

    return path


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining = seconds % 60
        return f"{minutes}m {remaining:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def create_spinner_task(progress, description: str) -> str:
    """Create a spinner task for indeterminate progress."""
    return progress.add_task(description, total=None)


class CommandTimer:
    """Context manager for timing command execution."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        console.print(
            f"[dim]⏱️  {self.operation_name} completed in {format_duration(duration)}[/dim]"
        )
