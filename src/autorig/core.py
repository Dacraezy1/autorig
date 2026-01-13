import asyncio
import difflib
import os
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .backup import BackupManager
from .config import RigConfig
from .installers.base import get_system_installer
from .logger import setup_logging
from .notifications import NotificationManager, ProgressTracker
from .plugins import plugin_manager
from .services.dotfile_service import DotfileService
from .services.git_service import GitService
from .services.hook_service import HookService
from .services.package_service import PackageService
from .state import OperationTracker, StateManager
from .templating import TemplateRenderer

console = Console()


class AutoRig:
    def __init__(
        self,
        config_path: str,
        dry_run: bool = False,
        verbose: bool = False,
        force: bool = False,
        profile: Optional[str] = None,
    ):
        self.config_path = config_path
        try:
            self.config = RigConfig.from_yaml(config_path, profile)
        except FileNotFoundError as e:
            console.print(f"[bold red]Configuration file not found:[/bold red] {e}")
            raise
        except ValueError as e:
            console.print(f"[bold red]Configuration validation error:[/bold red] {e}")
            raise
        except Exception as e:
            console.print(
                f"[bold red]Unexpected error loading configuration:[/bold red] {e}"
            )
            raise

        self.installer = get_system_installer()
        self.dry_run = dry_run
        self.verbose = verbose
        self.force = force
        self.backup_manager = BackupManager(self.config)
        self.logger = setup_logging(verbose=verbose)
        self.notification_manager = NotificationManager()
        self.progress_tracker = ProgressTracker(self.notification_manager)
        self.state_manager = StateManager(self.config)
        config_dir = Path(self.config_path).parent.absolute()
        self.renderer = TemplateRenderer(config_dir)

        # Initialize Services
        self.package_service = PackageService(
            self.installer, self.logger, self.progress_tracker, self.dry_run
        )
        self.git_service = GitService(
            self.logger, self.progress_tracker, self.dry_run, self.verbose
        )
        self.dotfile_service = DotfileService(
            self.config_path,
            self.renderer,
            self.logger,
            self.progress_tracker,
            self.dry_run,
            self.force,
        )
        self.hook_service = HookService(
            self.logger, self.progress_tracker, self.dry_run, self.verbose
        )

    async def apply(self):
        mode = "[DRY RUN] " if self.dry_run else ""
        console.print(
            f"[bold green]{mode}Applying configuration: {self.config.name}[/bold green]"
        )
        self.logger.info(f"Starting apply: {self.config.name} (dry_run={self.dry_run})")

        # Calculate total steps for progress tracking
        total_steps = 12  # Each major step counts as one
        if self.config.hooks.pre_system:
            total_steps += len(self.config.hooks.pre_system)
        if self.config.hooks.post_system:
            total_steps += len(self.config.hooks.post_system)
        if self.config.system.packages:
            total_steps += len(self.config.system.packages)
        if self.config.hooks.pre_git:
            total_steps += len(self.config.hooks.pre_git)
        if self.config.git.repositories:
            total_steps += len(self.config.git.repositories)
        if self.config.hooks.post_git:
            total_steps += len(self.config.hooks.post_git)
        if self.config.hooks.pre_dotfiles:
            total_steps += len(self.config.hooks.pre_dotfiles)
        if self.config.dotfiles:
            total_steps += len(self.config.dotfiles)
        if self.config.hooks.post_dotfiles:
            total_steps += len(self.config.hooks.post_dotfiles)
        if self.config.hooks.pre_scripts:
            total_steps += len(self.config.hooks.pre_scripts)
        if self.config.scripts:
            total_steps += len(self.config.scripts)
        if self.config.hooks.post_scripts:
            total_steps += len(self.config.hooks.post_scripts)

        self.progress_tracker.start_operation("Configuration Apply", total_steps)

        # Create operation tracker for error recovery
        tracker = OperationTracker(self.state_manager, "apply")

        # Create a progress display
        with console.status(
            "[bold green]Applying configuration...[/bold green]"
        ) as status:
            try:
                # Execute pre-system hooks
                status.update("[bold blue]Running pre-system hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.pre_system)
                self.progress_tracker.update_progress("Pre-system hooks completed")

                self.logger.debug("Starting system package installation")
                status.update("[bold blue]Installing system packages...[/bold blue]")
                self.package_service.install_packages(
                    self.config.system.packages, tracker
                )
                self.progress_tracker.update_progress("System packages installed")

                # Execute post-system hooks
                status.update("[bold blue]Running post-system hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.post_system)
                self.progress_tracker.update_progress("Post-system hooks completed")

                # Execute pre-git hooks
                status.update("[bold blue]Running pre-git hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.pre_git)
                self.progress_tracker.update_progress("Pre-git hooks completed")

                self.logger.debug("Starting git repository processing")
                status.update("[bold blue]Processing git repositories...[/bold blue]")
                await self.git_service.process_repositories(
                    self.config.git.repositories, tracker
                )
                self.progress_tracker.update_progress("Git repositories processed")

                # Execute post-git hooks
                status.update("[bold blue]Running post-git hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.post_git)
                self.progress_tracker.update_progress("Post-git hooks completed")

                # Execute pre-dotfile hooks
                status.update("[bold blue]Running pre-dotfile hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.pre_dotfiles)
                self.progress_tracker.update_progress("Pre-dotfile hooks completed")

                self.logger.debug("Starting dotfile linking")
                status.update("[bold blue]Linking dotfiles...[/bold blue]")
                self.dotfile_service.link_dotfiles(
                    self.config.dotfiles, self.config.variables, tracker
                )
                self.progress_tracker.update_progress("Dotfiles linked")

                # Execute post-dotfile hooks
                status.update("[bold blue]Running post-dotfile hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.post_dotfiles)
                self.progress_tracker.update_progress("Post-dotfile hooks completed")

                # Execute pre-script hooks
                status.update("[bold blue]Running pre-script hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.pre_scripts)
                self.progress_tracker.update_progress("Pre-script hooks completed")

                self.logger.debug("Starting script execution")
                status.update("[bold blue]Running custom scripts...[/bold blue]")
                self.hook_service.run_scripts(self.config.scripts, tracker)
                self.progress_tracker.update_progress("Custom scripts executed")

                # Execute post-script hooks
                status.update("[bold blue]Running post-script hooks...[/bold blue]")
                self.hook_service.run_hooks(self.config.hooks.post_scripts)
                self.progress_tracker.update_progress("Post-script hooks completed")

                # Complete the operation and save the rollback point
                tracker.complete_operation()
                self.progress_tracker.complete_operation()
                console.print("[bold green]✨ Rig setup complete![/bold green]")
                self.logger.info("Configuration application completed successfully")

            except Exception as e:
                self.progress_tracker.fail_operation(str(e))
                # Attempt rollback if not in dry-run mode
                if not self.dry_run:
                    console.print(
                        "[yellow]Attempting rollback due to error...[/yellow]"
                    )
                    try:
                        tracker.rollback_operation()
                    except Exception as rollback_error:
                        console.print(f"[red]Rollback failed: {rollback_error}[/red]")
                raise

    def clean(self):
        mode = "[DRY RUN] " if self.dry_run else ""
        console.print(
            f"[bold red]{mode}Cleaning configuration: {self.config.name}[/bold red]"
        )

        dotfiles = self.config.dotfiles
        if not dotfiles:
            return

        config_dir = Path(self.config_path).parent.absolute()

        for df in dotfiles:
            target = Path(os.path.expanduser(df.target))
            # Resolve what the link source should be
            source = (config_dir / os.path.expanduser(df.source)).resolve()

            if target.is_symlink():
                try:
                    # Check if the symlink actually points to our source
                    if target.resolve() == source:
                        console.print(f"Removing symlink: {target}")
                        if not self.dry_run:
                            target.unlink()
                    else:
                        console.print(
                            f"[yellow]Skipping {target}: Points elsewhere[/yellow]"
                        )
                except FileNotFoundError:
                    console.print(f"Removing broken symlink: {target}")
                    if not self.dry_run:
                        target.unlink()

    def backup(self):
        """Create a full snapshot of the current target files."""
        self.backup_manager.create_snapshot()

    def restore(self, snapshot_path: str):
        """Restore files from a backup snapshot."""
        self.backup_manager.restore_snapshot(snapshot_path)

    def status(self):
        console.print(f"[bold]Configuration Status: {self.config.name}[/bold]")

        config_dir = Path(self.config_path).parent.absolute()

        # Dotfiles
        if self.config.dotfiles:
            console.print("\n[bold]Dotfiles:[/bold]")
            for df in self.config.dotfiles:
                target = Path(os.path.expanduser(df.target))
                source = (config_dir / os.path.expanduser(df.source)).resolve()

                if source.suffix == ".j2":
                    if target.exists() and not target.is_symlink():
                        console.print(
                            f"  [green]✓[/green] {df.target} (Template Rendered)"
                        )
                    elif target.exists():
                        console.print(
                            f"  [yellow]![/yellow] {df.target} (Type Mismatch)"
                        )
                    else:
                        console.print(f"  [red]✗[/red] {df.target} (Missing)")
                else:
                    if target.is_symlink() and target.resolve() == source:
                        console.print(f"  [green]✓[/green] {df.target}")
                    elif target.exists():
                        console.print(
                            f"  [yellow]![/yellow] {df.target} (File/Link Mismatch)"
                        )
                    else:
                        console.print(f"  [red]✗[/red] {df.target} (Missing)")

        # Git
        if self.config.git.repositories:
            console.print("\n[bold]Repositories:[/bold]")
            for repo in self.config.git.repositories:
                path = Path(os.path.expanduser(repo.path))
                if path.exists() and (path / ".git").exists():
                    console.print(f"  [green]✓[/green] {repo.path}")
                else:
                    console.print(f"  [red]✗[/red] {repo.path} (Missing)")

    def diff(self):
        console.print(f"[bold]Configuration Diff: {self.config.name}[/bold]")
        config_dir = Path(self.config_path).parent.absolute()

        for df in self.config.dotfiles:
            target = Path(os.path.expanduser(df.target))
            source = (config_dir / os.path.expanduser(df.source)).resolve()

            if not target.exists():
                console.print(f"\n[bold green]New File:[/bold green] {target}")
                continue

            try:
                # Get source content
                if source.suffix == ".j2":
                    rel_source = source.relative_to(config_dir)
                    source_content = self.renderer.render_string(
                        str(rel_source), self.config.variables
                    ).splitlines()
                else:
                    source_content = source.read_text().splitlines()

                # Get target content
                target_content = target.read_text().splitlines()

                # Generate diff
                diff_lines = list(
                    difflib.unified_diff(
                        target_content,
                        source_content,
                        fromfile=str(target),
                        tofile=str(source),
                        lineterm="",
                    )
                )

                if diff_lines:
                    console.print(f"\n[bold yellow]Changes for {target}:[/bold yellow]")
                    for line in diff_lines:
                        color = (
                            "red"
                            if line.startswith("-")
                            else "green" if line.startswith("+") else "white"
                        )
                        console.print(f"[{color}]{line}[/{color}]")

            except Exception as e:
                console.print(f"[red]Could not diff {target}: {e}[/red]")

    def rollback(self):
        """Rollback to the most recent backup."""
        try:
            latest = self.backup_manager.get_latest_snapshot()
            console.print(
                f"[bold]Rolling back to latest snapshot:[/bold] {latest.name}"
            )
            self.restore(str(latest))
        except FileNotFoundError as e:
            console.print(f"[red]{e}[/red]")

    def watch(self):
        """Monitor config file for changes."""
        import time

        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

        class ConfigHandler(FileSystemEventHandler):
            def __init__(self, rigger):
                self.rigger = rigger
                self.last_run = 0

            def on_modified(self, event):
                if event.src_path == str(Path(self.rigger.config_path).absolute()):
                    # Simple debounce
                    if time.time() - self.last_run < 1:
                        return
                    self.last_run = time.time()

                    console.print(
                        "\n[bold yellow]Configuration changed. Applying...[/bold yellow]"
                    )
                    # Reload config
                    try:
                        self.rigger.config = RigConfig.from_yaml(
                            self.rigger.config_path
                        )
                        # We need to run the async apply here, but watch is sync.
                        # This is a bit tricky. For now, we wrap it.
                        asyncio.run(self.rigger.apply())
                    except Exception as e:
                        console.print(f"[red]Error applying changes:[/red] {e}")

        config_path = Path(self.config_path).absolute()
        event_handler = ConfigHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=str(config_path.parent), recursive=False)
        observer.start()

        console.print(
            f"[bold green]Watching {config_path} for changes... (Press Ctrl+C to stop)[/bold green]"
        )
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    @staticmethod
    def create_default_config(path: str, verbose: bool = False):
        if os.path.exists(path):
            raise FileExistsError(f"File {path} already exists.")

        default_config = """name: "My Developer Setup"

variables:
  email: "user@example.com"

system:
  packages:
    - git
    - vim
    - curl

git:
  repositories:
    # - url: "https://github.com/username/repo.git"
    #   path: "~/projects/repo"

dotfiles:
  # - source: ".bashrc"
  #   target: "~/.bashrc"

scripts:
  # - command: "echo 'Hello World'"
  #   description: "Test script"
"""
        with open(path, "w") as f:
            f.write(default_config)
        console.print(f"[green]Created default configuration at {path}[/green]")
        if verbose:
            console.print(
                "[blue]Configuration includes packages, repositories, dotfiles, and scripts.[/blue]"
            )

    async def sync_repos(self):
        await self.git_service.sync_repos(self.config.git.repositories)

    def run_plugins(self, plugin_names: List[str]):
        """Run specific plugins."""
        console.print(f"[bold]Running plugins: {', '.join(plugin_names)}[/bold]")

        for plugin_name in plugin_names:
            try:
                success = plugin_manager.run_plugin(
                    plugin_name, self.config, self.dry_run, self.verbose
                )
                if success:
                    console.print(
                        f"[green]Plugin {plugin_name} completed successfully[/green]"
                    )
                else:
                    console.print(f"[red]Plugin {plugin_name} failed[/red]")
            except ValueError as e:
                console.print(f"[red]Plugin {plugin_name} not found: {e}[/red]")
            except Exception as e:
                console.print(f"[red]Error running plugin {plugin_name}: {e}[/red]")

    def run_all_plugins(self):
        """Run all registered plugins."""
        available_plugins = plugin_manager.get_available_plugins()
        if available_plugins:
            console.print(
                f"[bold]Running all plugins: {', '.join(available_plugins)}[/bold]"
            )
            plugin_manager.run_all_plugins(self.config, self.dry_run, self.verbose)
        else:
            console.print("[yellow]No plugins registered[/yellow]")
