import os
import shutil
import subprocess
import difflib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from .config import RigConfig
from .installers.base import get_system_installer
from .backup import BackupManager
from .templating import TemplateRenderer
from .logger import setup_logging
from .plugins import plugin_manager

console = Console()

class AutoRig:
    def __init__(self, config_path: str, dry_run: bool = False, verbose: bool = False, force: bool = False, profile: Optional[str] = None):
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
            console.print(f"[bold red]Unexpected error loading configuration:[/bold red] {e}")
            raise

        self.installer = get_system_installer()
        self.dry_run = dry_run
        self.verbose = verbose
        self.force = force
        self.backup_manager = BackupManager(self.config)
        self.renderer = None
        self.logger = setup_logging(verbose=verbose)

    def apply(self):
        mode = "[DRY RUN] " if self.dry_run else ""
        console.print(f"[bold green]{mode}Applying configuration: {self.config.name}[/bold green]")
        self.logger.info(f"Starting apply: {self.config.name} (dry_run={self.dry_run})")

        # Create a progress display
        with console.status("[bold green]Applying configuration...[/bold green]") as status:
            self.logger.debug("Starting system package installation")
            status.update("[bold blue]Installing system packages...[/bold blue]")
            self._install_system_packages()

            self.logger.debug("Starting git repository processing")
            status.update("[bold blue]Processing git repositories...[/bold blue]")
            self._process_git_repos()

            self.logger.debug("Starting dotfile linking")
            status.update("[bold blue]Linking dotfiles...[/bold blue]")
            self._link_dotfiles()

            self.logger.debug("Starting script execution")
            status.update("[bold blue]Running custom scripts...[/bold blue]")
            self._run_scripts()

        console.print("[bold green]✨ Rig setup complete![/bold green]")
        self.logger.info("Configuration application completed successfully")

    def _install_system_packages(self):
        packages = self.config.system.packages
        if packages:
            console.print(f"[bold]Installing {len(packages)} system packages...[/bold]")
            self.logger.info(f"Installing {len(packages)} system packages")
            if self.dry_run:
                console.print(f"[yellow]DRY RUN: Would install: {', '.join(packages)}[/yellow]")
                return

            try:
                if self.installer.install(packages):
                    console.print("[green]System packages installed successfully.[/green]")
                    self.logger.info(f"Successfully installed packages: {packages}")
                else:
                    console.print("[red]Failed to install some system packages.[/red]")
                    self.logger.error(f"Failed to install some system packages: {packages}")
            except Exception as e:
                console.print(f"[red]Error during package installation: {e}[/red]")
                self.logger.error(f"Package installation error: {e}")

    def _process_git_repos(self):
        repos = self.config.git.repositories
        if not repos:
            self.logger.debug("No git repositories to process")
            return

        console.print(f"[bold]Processing {len(repos)} git repositories...[/bold]")
        self.logger.info(f"Processing {len(repos)} git repositories")

        for i, repo in enumerate(repos, 1):
            try:
                target_path = Path(os.path.expanduser(repo.path))

                # Security check for path traversal
                expanded_path = os.path.expanduser(repo.path)
                if '..' in expanded_path or expanded_path.startswith('/tmp'):
                    console.print(f"[red]Security error: Invalid repository path: {repo.path}[/red]")
                    self.logger.error(f"Security error: Invalid repository path: {repo.path}")
                    continue

                console.print(f"[dim]Processing repository {i}/{len(repos)}: {repo.url}[/dim]")
                self.logger.debug(f"Processing repository {i}/{len(repos)}: {repo.url}")

                if target_path.exists():
                    if (target_path / ".git").exists():
                        console.print(f"[yellow]Path exists, updating:[/yellow] {repo.path}")
                        self.logger.info(f"Repository exists, updating: {repo.url}")
                        if self.dry_run:
                            console.print(f"[yellow]DRY RUN: Would pull in {target_path}[/yellow]")
                            continue

                        try:
                            result = subprocess.run(
                                ["git", "-C", str(target_path), "pull"],
                                check=True,
                                capture_output=True,
                                text=True
                            )
                            console.print(f"[green]Updated {repo.url}[/green]")
                            if self.verbose and result.stdout:
                                console.print(f"[dim]Git output: {result.stdout}[/dim]")
                            self.logger.info(f"Updated git repo: {repo.url}")
                        except subprocess.CalledProcessError as e:
                            console.print(f"[red]Failed to update {repo.url}: {e}[/red]")
                            if e.stderr:
                                console.print(f"[red]Git error: {e.stderr}[/red]")
                            self.logger.error(f"Failed to update {repo.url}: {e}")
                    else:
                        console.print(f"[yellow]Path exists but is not a git repository: {repo.path}[/yellow]")
                        self.logger.warning(f"Path exists but is not a git repository: {repo.path}")
                    continue

                console.print(f"Cloning {repo.url} to {repo.path}...")
                self.logger.info(f"Cloning repository: {repo.url} to {repo.path}")
                if self.dry_run:
                    console.print(f"[yellow]DRY RUN: Would clone {repo.url}[/yellow]")
                    continue

                # Ensure parent directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    result = subprocess.run(
                        ["git", "clone", "-b", repo.branch, repo.url, str(target_path)],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    console.print(f"[green]Cloned {repo.url}[/green]")
                    if self.verbose and result.stdout:
                        console.print(f"[dim]Git output: {result.stdout}[/dim]")
                    self.logger.info(f"Cloned git repo: {repo.url}")
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Failed to clone {repo.url}: {e}[/red]")
                    if e.stderr:
                        console.print(f"[red]Git error: {e.stderr}[/red]")
                    self.logger.error(f"Failed to clone {repo.url}: {e}")

            except Exception as e:
                console.print(f"[red]Error processing repository {repo.url}: {e}[/red]")
                self.logger.error(f"Error processing repository {repo.url}: {e}")

    def _link_dotfiles(self):
        dotfiles = self.config.dotfiles
        if not dotfiles:
            self.logger.debug("No dotfiles to link")
            return

        console.print(f"[bold]Linking {len(dotfiles)} dotfiles...[/bold]")
        self.logger.info(f"Linking {len(dotfiles)} dotfiles")
        config_dir = Path(self.config_path).parent.absolute()
        self.renderer = TemplateRenderer(config_dir)

        for i, df in enumerate(dotfiles, 1):
            try:
                console.print(f"[dim]Processing dotfile {i}/{len(dotfiles)}: {df.target}[/dim]")
                self.logger.debug(f"Processing dotfile {i}/{len(dotfiles)}: {df.target}")

                # Resolve source relative to config file location
                source = (config_dir / os.path.expanduser(df.source)).resolve()
                target = Path(os.path.expanduser(df.target))

                # Security check: ensure source is within config directory
                try:
                    source.relative_to(config_dir)
                except ValueError:
                    console.print(f"[red]Security error: Source path outside config directory: {source}[/red]")
                    self.logger.error(f"Security error: Source path outside config directory: {source}")
                    continue

                if not source.exists():
                    console.print(f"[red]Source file not found:[/red] {source}")
                    self.logger.warning(f"Source file not found: {source}")
                    continue

                if target.exists() or target.is_symlink():
                    if not self.force:
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
                    else:
                        console.print(f"[yellow]Force mode: removing existing {target}[/yellow]")
                        self.logger.info(f"Force mode: removing existing {target}")
                        if not self.dry_run:
                            if target.is_symlink():
                                target.unlink()
                            else:
                                target.unlink() if target.is_file() else shutil.rmtree(target)

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

            except Exception as e:
                console.print(f"[red]Error processing dotfile {df.source} -> {df.target}: {e}[/red]")
                self.logger.error(f"Error processing dotfile {df.source} -> {df.target}: {e}")

    def _run_scripts(self):
        scripts = self.config.scripts
        if not scripts:
            self.logger.debug("No scripts to run")
            return

        console.print(f"[bold]Running {len(scripts)} post-install scripts...[/bold]")
        self.logger.info(f"Running {len(scripts)} post-install scripts")

        for i, script in enumerate(scripts, 1):
            desc = script.description or script.command
            console.print(f"[dim]Running script {i}/{len(scripts)}: {desc}[/dim]")
            self.logger.debug(f"Running script {i}/{len(scripts)}: {desc}")

            # Validate script command before execution for security
            if not self._is_safe_command(script.command):
                console.print(f"[red]✗ Unsafe command blocked: {script.command}[/red]")
                self.logger.error(f"Unsafe command blocked: {script.command}")
                continue

            cwd = os.path.expanduser(script.cwd) if script.cwd else None

            if self.dry_run:
                console.print(f"[yellow]DRY RUN: Would execute: {script.command}[/yellow]")
                continue

            try:
                result = subprocess.run(script.command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
                console.print(f"[green]✓ Completed: {desc}[/green]")
                if result.stdout:
                    if self.verbose:
                        console.print(f"[dim]Output: {result.stdout}[/dim]")
                    else:
                        console.print(f"[dim]Output: {result.stdout[:200]}...[/dim]" if len(result.stdout) > 200 else f"[dim]Output: {result.stdout}[/dim]")
                self.logger.info(f"Script completed: {desc}")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]✗ Failed: {desc} ({e})[/red]")
                if e.stderr:
                    console.print(f"[red]Error: {e.stderr}[/red]")
                self.logger.error(f"Script failed: {desc} - {e}")

    def _is_safe_command(self, command: str) -> bool:
        """
        Perform basic security checks on a command before execution
        """
        # Check for dangerous patterns that could indicate command injection
        dangerous_patterns = [
            r'\|\|',  # command chaining
            r'&&',    # command chaining
            r';',     # command separation
            r'\$\(\(', # arithmetic expansion
            r'`',     # command substitution
            r'\$\(.*\)', # command substitution
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return False
        return True

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
            console.print("[blue]Configuration includes packages, repositories, dotfiles, and scripts.[/blue]")

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

    def run_plugins(self, plugin_names: List[str]):
        """Run specific plugins."""
        console.print(f"[bold]Running plugins: {', '.join(plugin_names)}[/bold]")

        for plugin_name in plugin_names:
            try:
                success = plugin_manager.run_plugin(plugin_name, self.config, self.dry_run, self.verbose)
                if success:
                    console.print(f"[green]Plugin {plugin_name} completed successfully[/green]")
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
            console.print(f"[bold]Running all plugins: {', '.join(available_plugins)}[/bold]")
            plugin_manager.run_all_plugins(self.config, self.dry_run, self.verbose)
        else:
            console.print("[yellow]No plugins registered[/yellow]")