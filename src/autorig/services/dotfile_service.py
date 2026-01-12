import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from rich.console import Console
from autorig.config import Dotfile
from autorig.notifications import ProgressTracker
from autorig.state import OperationTracker
from autorig.templating import TemplateRenderer
from logging import Logger

console = Console()

class DotfileService:
    def __init__(
        self,
        config_path: str,
        renderer: TemplateRenderer,
        logger: Logger,
        progress_tracker: ProgressTracker,
        dry_run: bool = False,
        force: bool = False
    ):
        self.config_path = config_path
        self.renderer = renderer
        self.logger = logger
        self.progress_tracker = progress_tracker
        self.dry_run = dry_run
        self.force = force

    def link_dotfiles(self, dotfiles: List[Dotfile], variables: Dict, tracker: Optional[OperationTracker] = None):
        if not dotfiles:
            self.logger.debug("No dotfiles to link")
            return

        console.print(f"[bold]Linking {len(dotfiles)} dotfiles...[/bold]")
        self.logger.info(f"Linking {len(dotfiles)} dotfiles")
        config_dir = Path(self.config_path).parent.absolute()

        for i, df in enumerate(dotfiles, 1):
            try:
                console.print(
                    f"[dim]Processing dotfile {i}/{len(dotfiles)}: {df.target}[/dim]"
                )
                self.logger.debug(
                    f"Processing dotfile {i}/{len(dotfiles)}: {df.target}"
                )

                # Resolve source relative to config file location
                source = (config_dir / os.path.expanduser(df.source)).resolve()
                target = Path(os.path.expanduser(df.target))

                # Security check: ensure source is within config directory
                try:
                    source.relative_to(config_dir)
                except ValueError:
                    console.print(
                        f"[red]Security error: Source path outside config directory: {source}[/red]"
                    )
                    self.logger.error(
                        f"Security error: Source path outside config directory: {source}"
                    )
                    if tracker:
                        tracker.record_change(
                            "security_error",
                            str(target),
                            error="source_outside_config",
                            source=str(source),
                        )
                    self.progress_tracker.update_progress(
                        f"Security error: {df.target}"
                    )
                    continue

                if not source.exists():
                    console.print(f"[red]Source file not found:[/red] {source}")
                    self.logger.warning(f"Source file not found: {source}")
                    if tracker:
                        tracker.record_change(
                            "missing_source", str(target), source=str(source)
                        )
                    self.progress_tracker.update_progress(f"Missing source: {source}")
                    continue

                # Handle existing file (backup or force remove)
                self._handle_existing_target(target, tracker)

                # Ensure parent dir exists
                if not self.dry_run:
                    target.parent.mkdir(parents=True, exist_ok=True)

                if self.dry_run:
                    console.print(
                        f"[yellow]DRY RUN: Would link {target} -> {source}[/yellow]"
                    )
                    if tracker:
                        tracker.record_change(
                            "would_create_symlink",
                            str(target),
                            source=str(source),
                            is_template=(source.suffix == ".j2"),
                        )
                    self.progress_tracker.update_progress(f"Dry run: {df.target}")
                    continue

                # Check for template
                if source.suffix == ".j2":
                    self._render_template(source, target, config_dir, variables, df, tracker)
                    continue

                # Link file
                self._create_symlink(source, target, df, tracker)

            except Exception as e:
                console.print(
                    f"[red]Error processing dotfile {df.source} -> {df.target}: {e}[/red]"
                )
                self.logger.error(
                    f"Error processing dotfile {df.source} -> {df.target}: {e}"
                )
                if tracker:
                    tracker.record_change(
                        "dotfile_error", df.target, source=df.source, error=str(e)
                    )
                self.progress_tracker.update_progress(f"Error: {df.target}")

    def _handle_existing_target(self, target: Path, tracker: Optional[OperationTracker]):
        original_exists = target.exists() or target.is_symlink()
        original_is_symlink = target.is_symlink()
        original_path = (
            str(target.resolve())
            if target.is_symlink()
            else str(target) if target.exists() else None
        )

        if target.exists() or target.is_symlink():
            if not self.force:
                # Backup existing
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup = Path(f"{target}.{timestamp}.bak")
                console.print(
                    f"[yellow]Backing up existing {target} to {backup}[/yellow]"
                )
                self.logger.info(f"Backing up {target} to {backup}")

                # Record the backup action
                if tracker:
                    tracker.record_change(
                        "backup_file",
                        str(target),
                        backup_path=str(backup),
                        exists=original_exists,
                        is_symlink=original_is_symlink,
                        original_path=original_path,
                    )

                if not self.dry_run:
                    if target.is_symlink():
                        target.unlink()
                    else:
                        shutil.move(str(target), str(backup))
            else:
                console.print(
                    f"[yellow]Force mode: removing existing {target}[/yellow]"
                )
                self.logger.info(f"Force mode: removing existing {target}")
                # Record the deletion action
                if tracker:
                    tracker.record_change(
                        "deleted_file",
                        str(target),
                        is_symlink=original_is_symlink,
                        original_path=original_path,
                    )

                if not self.dry_run:
                    if target.is_symlink():
                        target.unlink()
                    else:
                        (
                            target.unlink()
                            if target.is_file()
                            else shutil.rmtree(target)
                        )

    def _render_template(self, source, target, config_dir, variables, df, tracker):
        try:
            # Render relative path from config_dir
            rel_source = source.relative_to(config_dir)
            self.renderer.render(
                str(rel_source), variables, target
            )
            console.print(f"[green]Rendered {target} from {source}[/green]")
            self.logger.info(f"Rendered template {source} to {target}")
            if tracker:
                tracker.record_change(
                    "rendered_from_template",
                    str(target),
                    source=str(source),
                )
            self.progress_tracker.update_progress(f"Rendered: {df.target}")
        except Exception as e:
            console.print(f"[red]Failed to render {target}: {e}[/red]")
            self.logger.error(f"Template render failed for {target}: {e}")
            if tracker:
                tracker.record_change(
                    "failed_render",
                    str(target),
                    source=str(source),
                    error=str(e),
                )
            self.progress_tracker.update_progress(
                f"Failed render: {df.target}"
            )

    def _create_symlink(self, source, target, df, tracker):
        try:
            target.symlink_to(source)
            console.print(f"[green]Linked {target} -> {source}[/green]")
            self.logger.info(f"Linked {target} -> {source}")
            if tracker:
                tracker.record_change(
                    "created_symlink",
                    str(target),
                    source=str(source),
                )
            self.progress_tracker.update_progress(f"Linked: {df.target}")
        except Exception as e:
            console.print(f"[red]Failed to link {target}: {e}[/red]")
            self.logger.error(f"Link failed for {target}: {e}")
            if tracker:
                tracker.record_change(
                    "failed_symlink", str(target), source=str(source), error=str(e)
                )
            self.progress_tracker.update_progress(f"Failed link: {df.target}")
