"""
Monitoring and status reporting for AutoRig operations.
"""

import psutil
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from .config import RigConfig


@dataclass
class SystemResourceUsage:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    timestamp: datetime


class ResourceMonitor:
    """
    Monitors system resources during AutoRig operations.
    """

    def __init__(self):
        self.initial_network = psutil.net_io_counters()
        self.initial_network_sent = self.initial_network.bytes_sent
        self.initial_network_recv = self.initial_network.bytes_recv
        self.resource_history: List[SystemResourceUsage] = []

    def get_current_usage(self) -> SystemResourceUsage:
        """Get current system resource usage."""
        net_current = psutil.net_io_counters()
        return SystemResourceUsage(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage("/").percent,
            network_sent=net_current.bytes_sent - self.initial_network_sent,
            network_recv=net_current.bytes_recv - self.initial_network_recv,
            timestamp=datetime.now(),
        )

    def start_monitoring(self):
        """Start resource monitoring."""
        self.resource_history.append(self.get_current_usage())

    def get_average_usage(self) -> SystemResourceUsage:
        """Get average resource usage since monitoring started."""
        if not self.resource_history:
            return self.get_current_usage()

        avg_cpu = sum([r.cpu_percent for r in self.resource_history]) / len(
            self.resource_history
        )
        avg_memory = sum([r.memory_percent for r in self.resource_history]) / len(
            self.resource_history
        )
        avg_disk = sum([r.disk_percent for r in self.resource_history]) / len(
            self.resource_history
        )
        total_sent = max([r.network_sent for r in self.resource_history])
        total_recv = max([r.network_recv for r in self.resource_history])

        return SystemResourceUsage(
            cpu_percent=avg_cpu,
            memory_percent=avg_memory,
            disk_percent=avg_disk,
            network_sent=total_sent,
            network_recv=total_recv,
            timestamp=datetime.now(),
        )


class StatusReporter:
    """
    Generates status reports for AutoRig operations.
    """

    def __init__(self, config: RigConfig, console: Console):
        self.config = config
        self.console = console
        self.resource_monitor = ResourceMonitor()

    def report_status(self, show_resources: bool = True, show_config: bool = True):
        """Generate and display a status report."""
        table = Table(title=f"AutoRig Status Report: {self.config.name}")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")

        # Configuration status
        if show_config:
            table.add_row("Configuration", "Loaded", f"Name: {self.config.name}")
            table.add_row(
                "System Packages",
                str(len(self.config.system.packages)),
                f"Packages: {', '.join(self.config.system.packages[:5])}{'...' if len(self.config.system.packages) > 5 else ''}",
            )
            table.add_row(
                "Git Repositories",
                str(len(self.config.git.repositories)),
                f"Repos: {len(self.config.git.repositories)}",
            )
            table.add_row(
                "Dotfiles",
                str(len(self.config.dotfiles)),
                f"Files: {len(self.config.dotfiles)}",
            )
            table.add_row(
                "Scripts",
                str(len(self.config.scripts)),
                f"Scripts: {len(self.config.scripts)}",
            )

        # System resources
        if show_resources:
            usage = self.resource_monitor.get_average_usage()
            table.add_row("CPU Usage", f"{usage.cpu_percent:.1f}%", "Average usage")
            table.add_row(
                "Memory Usage", f"{usage.memory_percent:.1f}%", "Current usage"
            )
            table.add_row("Disk Usage", f"{usage.disk_percent:.1f}%", "Root partition")
            table.add_row(
                "Network Out",
                f"{usage.network_sent:,} bytes",
                "Since monitoring started",
            )
            table.add_row(
                "Network In",
                f"{usage.network_recv:,} bytes",
                "Since monitoring started",
            )

        self.console.print(table)

    def generate_detailed_report(self) -> Dict[str, Any]:
        """Generate a detailed status report as a dictionary."""
        usage = self.resource_monitor.get_average_usage()

        report = {
            "config_name": self.config.name,
            "timestamp": datetime.now().isoformat(),
            "system_resources": {
                "cpu_percent": usage.cpu_percent,
                "memory_percent": usage.memory_percent,
                "disk_percent": usage.disk_percent,
                "network_sent_bytes": usage.network_sent,
                "network_recv_bytes": usage.network_recv,
            },
            "configuration_summary": {
                "system_packages_count": len(self.config.system.packages),
                "git_repositories_count": len(self.config.git.repositories),
                "dotfiles_count": len(self.config.dotfiles),
                "scripts_count": len(self.config.scripts),
                "hooks_count": (
                    len(self.config.hooks.pre_system)
                    + len(self.config.hooks.post_system)
                    + len(self.config.hooks.pre_git)
                    + len(self.config.hooks.post_git)
                    + len(self.config.hooks.pre_dotfiles)
                    + len(self.config.hooks.post_dotfiles)
                    + len(self.config.hooks.pre_scripts)
                    + len(self.config.hooks.post_scripts)
                ),
            },
        }

        return report

    def save_report(self, output_path: str = None):
        """Save the status report to a file."""
        import json

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"autorig_report_{timestamp}.json"

        report = self.generate_detailed_report()

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        self.console.print(f"[green]Status report saved to: {output_path}[/green]")


class OperationMonitor:
    """
    Monitors ongoing AutoRig operations with real-time feedback.
    """

    def __init__(self, config: RigConfig, console: Console):
        self.config = config
        self.console = console
        self.status_reporter = StatusReporter(config, console)
        self.start_time = time.time()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        )

    def start_operation(self, operation_name: str):
        """Start monitoring an operation."""
        self.start_time = time.time()
        self.console.print(
            f"[bold blue]Starting operation:[/bold blue] {operation_name}"
        )
        self.status_reporter.resource_monitor.start_monitoring()

    def report_progress(
        self, operation: str, current: int, total: int, description: str = ""
    ):
        """Report progress of an operation."""
        percent = (current / total) * 100 if total > 0 else 0
        self.console.print(
            f"[cyan]{operation}:[/cyan] {current}/{total} ({percent:.1f}%) - {description}"
        )

    def get_operation_duration(self) -> float:
        """Get the duration of the current operation in seconds."""
        return time.time() - self.start_time

    def finish_operation(self, operation_name: str):
        """Finish monitoring an operation and show final report."""
        duration = self.get_operation_duration()
        self.console.print(
            f"[green]Operation '{operation_name}' completed in {duration:.2f} seconds[/green]"
        )

        # Show final status report
        self.status_reporter.report_status()
