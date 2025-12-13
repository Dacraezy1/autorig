import os
from pathlib import Path
import subprocess
from rich.console import Console
from rich.progress import Progress
from .config import RigConfig
from .installers.base import get_system_installer

console = Console()

class AutoRig:
    def __init__(self, config_path: str):
        self.config = RigConfig.load(config_path)

    def apply(self):
        console.rule(f"[bold green]AutoRig: {self.config.name}")
        
        # 1. System Packages
        if self.config.system and self.config.system.packages:
            installer = get_system_installer()
            console.print("[bold]Checking system packages...[/bold]")
            installer.install(self.config.system.packages)
        
        # 2. Git Repositories
        if self.config.git and self.config.git.repositories:
            self._handle_git_repos()

        # 3. Dotfiles
        if self.config.dotfiles:
            self._handle_dotfiles()

        console.rule("[bold green]Rig Setup Complete!")

    def _handle_git_repos(self):
        console.print("[bold]Processing Git repositories...[/bold]")
        for repo in self.config.git.repositories:
            target_path = Path(os.path.expanduser(repo.path))
            if target_path.exists():
                console.print(f"  [yellow]Skipping existing:[/yellow] {repo.path}")
                continue
            
            console.print(f"  [green]Cloning:[/green] {repo.url} -> {repo.path}")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    ["git", "clone", "-b", repo.branch, repo.url, str(target_path)],
                    check=True,
                    stdout=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                console.print(f"  [red]Failed to clone:[/red] {repo.url}")

    def _handle_dotfiles(self):
        console.print("[bold]Linking dotfiles...[/bold]")
        for dot in self.config.dotfiles:
            source = Path(dot.source).resolve()
            target = Path(os.path.expanduser(dot.target))
            
            if not source.exists():
                console.print(f"  [red]Source missing:[/red] {source}")
                continue
            
            if target.exists() or target.is_symlink():
                console.print(f"  [yellow]Target exists (skipping):[/yellow] {target}")
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.symlink(source, target)
                console.print(f"  [green]Linked:[/green] {source.name} -> {target}")
            except OSError as e:
                console.print(f"  [red]Error linking {target}:[/red] {e}")
