import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from rich.console import Console
from .config import RigConfig
from .installers.base import get_system_installer

console = Console()

class AutoRig:
    def __init__(self, config_path: str, dry_run: bool = False):
        self.config_path = config_path
        self.config = RigConfig.from_yaml(config_path)
        self.installer = get_system_installer()
        self.dry_run = dry_run

    def apply(self):
        mode = "[DRY RUN] " if self.dry_run else ""
        console.print(f"[bold green]{mode}Applying configuration: {self.config.name}[/bold green]")
        
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
            else:
                console.print("[red]Failed to install some system packages.[/red]")

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
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Failed to update {repo.url}: {e}[/red]")
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
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Failed to clone {repo.url}: {e}[/red]")

    def _link_dotfiles(self):
        dotfiles = self.config.dotfiles
        if not dotfiles:
            return

        console.print(f"[bold]Linking {len(dotfiles)} dotfiles...[/bold]")
        config_dir = Path(self.config_path).parent.absolute()
        
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

            try:
                target.symlink_to(source)
                console.print(f"[green]Linked {target} -> {source}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to link {target}: {e}[/red]")

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
            except subprocess.CalledProcessError as e:
                console.print(f"[red]✗ Failed: {desc} ({e})[/red]")

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