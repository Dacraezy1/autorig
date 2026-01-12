from typing import List, Optional
from rich.console import Console
from autorig.installers.base import SystemInstaller
from autorig.notifications import ProgressTracker
from autorig.state import OperationTracker
from logging import Logger

console = Console()


class PackageService:
    def __init__(
        self,
        installer: SystemInstaller,
        logger: Logger,
        progress_tracker: ProgressTracker,
        dry_run: bool = False,
    ):
        self.installer = installer
        self.logger = logger
        self.progress_tracker = progress_tracker
        self.dry_run = dry_run

    def install_packages(
        self, packages: List[str], tracker: Optional[OperationTracker] = None
    ):
        if not packages:
            return

        console.print(f"[bold]Installing {len(packages)} system packages...[/bold]")
        self.logger.info(f"Installing {len(packages)} system packages")

        if self.dry_run:
            console.print(
                f"[yellow]DRY RUN: Would install: {', '.join(packages)}[/yellow]"
            )
            for pkg in packages:
                if tracker:
                    tracker.record_change("would_install_package", pkg)
                self.progress_tracker.update_progress(f"Dry run: {pkg}")
            return

        try:
            success_count = 0
            failures = []
            for pkg in packages:
                if self.installer.install([pkg]):
                    success_count += 1
                    if tracker:
                        tracker.record_change(
                            "installed_package", pkg, status="success"
                        )
                    self.progress_tracker.update_progress(f"Installed: {pkg}")
                else:
                    failures.append(pkg)
                    if tracker:
                        tracker.record_change("installed_package", pkg, status="failed")
                    self.progress_tracker.update_progress(f"Failed: {pkg}")

            if success_count == len(packages):
                console.print("[green]System packages installed successfully.[/green]")
                self.logger.info(f"Successfully installed packages: {packages}")
            else:
                console.print(
                    f"[yellow]Partially successful: {success_count}/{len(packages)} packages installed.[/yellow]"
                )
                if failures:
                    console.print(
                        f"[yellow]Failed packages: {', '.join(failures)}[/yellow]"
                    )
                self.logger.warning(
                    f"Only {success_count}/{len(packages)} packages installed: {packages}"
                )
        except Exception as e:
            console.print(f"[red]Error during package installation: {e}[/red]")
            self.logger.error(f"Package installation error: {e}")
            raise
