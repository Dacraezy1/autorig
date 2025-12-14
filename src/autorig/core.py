import os
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from .config import RigConfig
from .installers.base import get_system_installer

console = Console()

class AutoRig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = RigConfig.from_yaml(config_path)
        self.installer = get_system_installer()

    def apply(self):
        console.print(f"[bold green]Applying configuration: {self.config.name}[/bold green]")
        
        self._install_system_packages()
        self._process_git_repos()
        self._link_dotfiles()
        
        console.print("[bold green]✨ Rig setup complete![/bold green]")

    def _install_system_packages(self):
        packages = self.config.system.packages
        if packages:
            console.print(f"[bold]Installing {len(packages)} system packages...[/bold]")
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
                try:
                    subprocess.run(["git", "-C", str(target_path), "pull"], check=True)
                    console.print(f"[green]Updated {repo.url}[/green]")
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Failed to update {repo.url}: {e}[/red]")
                continue
            
            console.print(f"Cloning {repo.url} to {repo.path}...")
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
                backup = target.with_suffix(target.suffix + ".bak")
                console.print(f"[yellow]Backing up existing {target} to {backup}[/yellow]")
                if target.is_symlink():
                    target.unlink()
                else:
                    shutil.move(str(target), str(backup))
            
            # Ensure parent dir exists
            target.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                target.symlink_to(source)
                console.print(f"[green]Linked {target} -> {source}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to link {target}: {e}[/red]")