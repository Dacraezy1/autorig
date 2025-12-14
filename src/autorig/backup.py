import tarfile
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from .config import RigConfig

console = Console()

class BackupManager:
    def __init__(self, config: RigConfig, backup_dir: str = "~/.autorig/backups"):
        self.config = config
        self.backup_dir = Path(os.path.expanduser(backup_dir))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_name = "".join(c for c in self.config.name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        filename = f"{safe_name}_{timestamp}.tar.gz"
        filepath = self.backup_dir / filename
        
        console.print(f"[bold]Creating backup snapshot:[/bold] {filepath}")
        
        count = 0
        with tarfile.open(filepath, "w:gz") as tar:
            for df in self.config.dotfiles:
                target = Path(os.path.expanduser(df.target))
                if target.exists():
                    # Store relative to root in the tar
                    arcname = str(target).lstrip(os.sep)
                    tar.add(target, arcname=arcname)
                    count += 1
        
        console.print(f"[green]Backed up {count} files to {filepath}[/green]")
        return filepath

    def restore_snapshot(self, snapshot_path: str):
        path = Path(snapshot_path)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {path}")
            
        console.print(f"[bold]Restoring from snapshot:[/bold] {path}")
        with tarfile.open(path, "r:gz") as tar:
            # Extract relative paths starting from root to restore absolute locations
            tar.extractall(path="/")
            
        console.print(f"[green]Restored files from {path}[/green]")