import os
import shutil
import subprocess
import difflib
from datetime import datetime
from pathlib import Path
from rich.console import Console
from .config import RigConfig
from .installers.base import get_system_installer
from .backup import BackupManager
from .templating import TemplateRenderer
from .logger import setup_logging

console = Console()

class AutoRig:
    def __init__(self, config_path: str, dry_run: bool = False):
        self.config_path = config_path
        self.config = RigConfig.from_yaml(config_path)
        self.installer = get_system_installer()
        self.dry_run = dry_run
        self.backup_manager = BackupManager(self.config)
        self.renderer = None
        self.logger = setup_logging()

    def apply(self):
        mode = "[DRY RUN] " if self.dry_run else ""
        console.print(f"[bold green]{mode}Applying configuration: {self.config.name}[/bold green]")
        self.logger.info(f"Starting apply: {self.config.name} (dry_run={self.dry_run})")
        
        self._install_system_packages()
        self._process_git_repos()
        self._link_dotfiles()
        self._run_scripts()
        
        console.print("[bold green]✨ Rig setup complete![/bold green]")

    def _install_system_packages(self):
        packages = self.config.system.packages
        if packages:
            console.print(f"[bold]Installing {len(packages)} system packages...[/bold]")
            if self.dry_run:
                console.print(f"[yellow]DRY RUN: Would install: {', '.join(packages)}[/yellow]")
                return

            if self.installer.install(packages):
                console.print("[green]System packages installed successfully.[/green]")
                self.logger.info(f"Installed packages: {packages}")
            else:
                console.print("[red]Failed to install some system packages.[/red]")
                self.logger.error("Package installation failed")

    def _process_git_repos(self):
        repos = self.config.git.repositories
        if not repos:
            return
            
        console.print(f"[bold]Processing {len(repos)} git repositories...[/bold]")
        for repo in repos:
            target_path = Path(os.path.expanduser(repo.path))
            if target_path.exists():
                console.print(f"[yellow]Path exists, updating:[/yellow] {repo.path}")
                if self.dry_run:
                    console.print(f"[yellow]DRY RUN: Would pull in {target_path}[/yellow]")
                    continue

                try:
                    subprocess.run(["git", "-C", str(target_path), "pull"], check=True)
                    console.print(f"[green]Updated {repo.url}[/green]")
                    self.logger.info(f"Updated git repo: {repo.url}")
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Failed to update {repo.url}: {e}[/red]")
                    self.logger.error(f"Failed to update {repo.url}: {e}")
                continue
            
            console.print(f"Cloning {repo.url} to {repo.path}...")
            if self.dry_run:
                console.print(f"[yellow]DRY RUN: Would clone {repo.url}[/yellow]")
                continue

            try:
                subprocess.run(
                    ["git", "clone", "-b", repo.branch, repo.url, str(target_path)],
                    check=True
                )
                console.print(f"[green]Cloned {repo.url}[/green]")
                self.logger.info(f"Cloned git repo: {repo.url}")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Failed to clone {repo.url}: {e}[/red]")
                self.logger.error(f"Failed to clone {repo.url}: {e}")

    def _link_dotfiles(self):
        dotfiles = self.config.dotfiles
        if not dotfiles:
            return

        console.print(f"[bold]Linking {len(dotfiles)} dotfiles...[/bold]")
        config_dir = Path(self.config_path).parent.absolute()
        self.renderer = TemplateRenderer(config_dir)
        
        for df in dotfiles:
            # Resolve source relative to config file location
            source = (config_dir / os.path.expanduser(df.source)).resolve()
            target = Path(os.path.expanduser(df.target))
            
            if not source.exists():
                console.print(f"[red]Source file not found:[/red] {source}")
                continue
                
            if target.exists() or target.is_symlink():
                # Backup existing
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup = Path(f"{target}.{timestamp}.bak")
                console.print(f"[yellow]Backing up existing {target} to {backup}[/yellow]")
                self.logger.info(f"Backing up {target} to {backup}")
                
                if not self.dry_run:
                    if target.is_symlink():
                        target.unlink()
                    else:
                        shutil.move(str(target), str(backup))
            
            # Ensure parent dir exists
            if not self.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
            
            if self.dry_run:
                console.print(f"[yellow]DRY RUN: Would link {target} -> {source}[/yellow]")
                continue

            # Check for template
            if source.suffix == '.j2':
                try:
                    # Render relative path from config_dir
                    rel_source = source.relative_to(config_dir)
                    self.renderer.render(str(rel_source), self.config.variables, target)
                    console.print(f"[green]Rendered {target} from {source}[/green]")
                    self.logger.info(f"Rendered template {source} to {target}")
                except Exception as e:
                    console.print(f"[red]Failed to render {target}: {e}[/red]")
                    self.logger.error(f"Template render failed for {target}: {e}")
                continue

            try:
                target.symlink_to(source)
                console.print(f"[green]Linked {target} -> {source}[/green]")
                self.logger.info(f"Linked {target} -> {source}")
            except Exception as e:
                console.print(f"[red]Failed to link {target}: {e}[/red]")
                self.logger.error(f"Link failed for {target}: {e}")

    def _run_scripts(self):
        scripts = self.config.scripts
        if not scripts:
            return

        console.print(f"[bold]Running {len(scripts)} post-install scripts...[/bold]")
        for script in scripts:
            desc = script.description or script.command
            console.print(f"Running: {desc}")
            
            cwd = os.path.expanduser(script.cwd) if script.cwd else None
            
            if self.dry_run:
                console.print(f"[yellow]DRY RUN: Would execute: {script.command}[/yellow]")
                continue
            
            try:
                subprocess.run(script.command, shell=True, check=True, cwd=cwd)
                console.print(f"[green]✓ Completed: {desc}[/green]")
                self.logger.info(f"Script completed: {desc}")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]✗ Failed: {desc} ({e})[/red]")
                self.logger.error(f"Script failed: {desc} - {e}")

    def clean(self):
        mode = "[DRY RUN] " if self.dry_run else ""
        console.print(f"[bold red]{mode}Cleaning configuration: {self.config.name}[/bold red]")
        
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
                        console.print(f"[yellow]Skipping {target}: Points elsewhere[/yellow]")
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
            console.print(f"\n[bold]Dotfiles:[/bold]")
            for df in self.config.dotfiles:
                target = Path(os.path.expanduser(df.target))
                source = (config_dir / os.path.expanduser(df.source)).resolve()
                
                if source.suffix == '.j2':
                    if target.exists() and not target.is_symlink():
                        console.print(f"  [green]✓[/green] {df.target} (Template Rendered)")
                    elif target.exists():
                        console.print(f"  [yellow]![/yellow] {df.target} (Type Mismatch)")
                    else:
                        console.print(f"  [red]✗[/red] {df.target} (Missing)")
                else:
                    if target.is_symlink() and target.resolve() == source:
                        console.print(f"  [green]✓[/green] {df.target}")
                    elif target.exists():
                        console.print(f"  [yellow]![/yellow] {df.target} (File/Link Mismatch)")
                    else:
                        console.print(f"  [red]✗[/red] {df.target} (Missing)")

        # Git
        if self.config.git.repositories:
            console.print(f"\n[bold]Repositories:[/bold]")
            for repo in self.config.git.repositories:
                path = Path(os.path.expanduser(repo.path))
                if path.exists() and (path / ".git").exists():
                    console.print(f"  [green]✓[/green] {repo.path}")
                else:
                    console.print(f"  [red]✗[/red] {repo.path} (Missing)")

    def diff(self):
        console.print(f"[bold]Configuration Diff: {self.config.name}[/bold]")
        config_dir = Path(self.config_path).parent.absolute()
        self.renderer = TemplateRenderer(config_dir)

        for df in self.config.dotfiles:
            target = Path(os.path.expanduser(df.target))
            source = (config_dir / os.path.expanduser(df.source)).resolve()
            
            if not target.exists():
                console.print(f"\n[bold green]New File:[/bold green] {target}")
                continue
            
            try:
                # Get source content
                if source.suffix == '.j2':
                    rel_source = source.relative_to(config_dir)
                    source_content = self.renderer.render_string(str(rel_source), self.config.variables).splitlines()
                else:
                    source_content = source.read_text().splitlines()
                
                # Get target content
                target_content = target.read_text().splitlines()
                
                # Generate diff
                diff_lines = list(difflib.unified_diff(
                    target_content,
                    source_content,
                    fromfile=str(target),
                    tofile=str(source),
                    lineterm=""
                ))
                
                if diff_lines:
                    console.print(f"\n[bold yellow]Changes for {target}:[/bold yellow]")
                    for line in diff_lines:
                        color = "red" if line.startswith("-") else "green" if line.startswith("+") else "white"
                        console.print(f"[{color}]{line}[/{color}]")
            
            except Exception as e:
                console.print(f"[red]Could not diff {target}: {e}[/red]")

    def rollback(self):
        """Rollback to the most recent backup."""
        try:
            latest = self.backup_manager.get_latest_snapshot()
            console.print(f"[bold]Rolling back to latest snapshot:[/bold] {latest.name}")
            self.restore(str(latest))
        except FileNotFoundError as e:
            console.print(f"[red]{e}[/red]")

    def watch(self):
        """Monitor config file for changes."""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        import time

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
                    
                    console.print(f"\n[bold yellow]Configuration changed. Applying...[/bold yellow]")
                    # Reload config
                    try:
                        self.rigger.config = RigConfig.from_yaml(self.rigger.config_path)
                        self.rigger.apply()
                    except Exception as e:
                        console.print(f"[red]Error applying changes:[/red] {e}")

        config_path = Path(self.config_path).absolute()
        event_handler = ConfigHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=str(config_path.parent), recursive=False)
        observer.start()
        
        console.print(f"[bold green]Watching {config_path} for changes... (Press Ctrl+C to stop)[/bold green]")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    @staticmethod
    def create_default_config(path: str):
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

    def sync_repos(self):
        repos = self.config.git.repositories
        if not repos:
            console.print("No repositories defined to sync.")
            return
            
        console.print(f"[bold]Syncing {len(repos)} git repositories...[/bold]")
        for repo in repos:
            target_path = Path(os.path.expanduser(repo.path))
            if target_path.exists() and (target_path / ".git").exists():
                console.print(f"Syncing {repo.path}...")
                if self.dry_run:
                    console.print(f"[yellow]DRY RUN: Would push {target_path}[/yellow]")
                    continue

                try:
                    # Check for uncommitted changes just to inform
                    status = subprocess.run(["git", "-C", str(target_path), "status", "--porcelain"], capture_output=True, text=True)
                    if status.stdout.strip():
                        console.print(f"[yellow]Warning: {repo.path} has uncommitted changes.[/yellow]")

                    subprocess.run(["git", "-C", str(target_path), "push"], check=True)
                    console.print(f"[green]Pushed {repo.path}[/green]")
                    self.logger.info(f"Pushed git repo: {repo.path}")
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Failed to push {repo.path}: {e}[/red]")
                    self.logger.error(f"Failed to push {repo.path}: {e}")
            else:
                console.print(f"[yellow]Skipping {repo.path}: Not a git repo[/yellow]")