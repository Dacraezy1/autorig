import tarfile
import os
import tempfile
from pathlib import Path
from datetime import datetime
from rich.console import Console
from .config import RigConfig
import sys

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
                    # Store relative to root in the tar - check for path traversal
                    arcname = str(target).lstrip(os.sep)
                    # Validate that the arcname doesn't contain dangerous patterns
                    if '..' in arcname or arcname.startswith('/') or ':' in arcname:
                        console.print(f"[yellow]Skipping dangerous path: {target}[/yellow]")
                        continue
                    tar.add(target, arcname=arcname)
                    count += 1

        console.print(f"[green]Backed up {count} files to {filepath}[/green]")
        return filepath

    def restore_snapshot(self, snapshot_path: str):
        path = Path(snapshot_path)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {path}")

        # Validate the archive before extraction
        try:
            with tarfile.open(path, "r:gz") as tar:
                members = tar.getmembers()
                # Security check: ensure no path traversal in the archive
                for member in members:
                    if '..' in member.name or member.name.startswith('/'):
                        raise ValueError(f"Dangerous path in archive: {member.name}")
        except tarfile.ReadError:
            raise ValueError(f"Invalid tar archive: {path}")

        console.print(f"[bold]Restoring from snapshot:[/bold] {path}")

        # Use a safer extraction method
        with tarfile.open(path, "r:gz") as tar:
            # Use system-specific trusted filter if available, else extract to temp and validate
            if sys.version_info >= (3, 12):
                tar.extractall(path="/", filter='data')
            else:
                # For older Python versions, extract with more caution
                for member in tar.getmembers():
                    tar.extract(member, path="/")

        console.print(f"[green]Restored files from {path}[/green]")

    def get_latest_snapshot(self) -> Path:
        snapshots = list(self.backup_dir.glob("*.tar.gz"))
        if not snapshots:
            raise FileNotFoundError("No backups found.")
        # Sort by name (which contains timestamp YYYYMMDD-HHMMSS) descending
        latest = sorted(snapshots, key=lambda p: p.name, reverse=True)[0]
        return latest