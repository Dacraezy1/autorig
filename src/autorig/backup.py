import json
import os
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

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
        safe_name = (
            "".join(c for c in self.config.name if c.isalnum() or c in (" ", "_", "-"))
            .strip()
            .replace(" ", "_")
        )
        filename = f"{safe_name}_{timestamp}.tar.gz"
        filepath = self.backup_dir / filename

        console.print(f"[bold]Creating backup snapshot:[/bold] {filepath}")

        # Create a manifest of what's being backed up
        manifest: Dict[str, Any] = {
            "config_name": self.config.name,
            "timestamp": timestamp,
            "backup_type": "full",
            "dotfiles": [],
        }

        count = 0
        with tarfile.open(filepath, "w:gz") as tar:
            for df in self.config.dotfiles:
                target = Path(os.path.expanduser(df.target))
                if target.exists():
                    # Store relative to root in the tar - check for path traversal
                    arcname = str(target).lstrip(os.sep)
                    # Validate that the arcname doesn't contain dangerous patterns
                    if ".." in arcname or arcname.startswith("/") or ":" in arcname:
                        console.print(
                            f"[yellow]Skipping dangerous path: {target}[/yellow]"
                        )
                        continue
                    tar.add(target, arcname=arcname)

                    # Add to manifest
                    manifest["dotfiles"].append(
                        {
                            "source": df.source,
                            "target": df.target,
                            "exists": True,
                            "is_symlink": target.is_symlink(),
                            "original_path": (
                                str(target.resolve())
                                if target.is_symlink()
                                else str(target)
                            ),
                        }
                    )
                    count += 1

            # Add manifest to the archive using in-memory data
            import io

            manifest_data = json.dumps(manifest, indent=2).encode("utf-8")
            manifest_info = tarfile.TarInfo("manifest.json")
            manifest_info.size = len(manifest_data)
            tar.addfile(manifest_info, io.BytesIO(manifest_data))

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
                    if ".." in member.name or member.name.startswith("/"):
                        raise ValueError(f"Dangerous path in archive: {member.name}")
        except tarfile.ReadError:
            raise ValueError(f"Invalid tar archive: {path}")

        console.print(f"[bold]Restoring from snapshot:[/bold] {path}")

        # Use a safer extraction method
        with tarfile.open(path, "r:gz") as tar:
            # Extract manifest first to get information about what was backed up
            manifest_member = tar.getmember("manifest.json")
            if manifest_member:
                manifest_file = tar.extractfile(manifest_member)
                if manifest_file:
                    # Extract files with safety checks
                    for member in tar.getmembers():
                        # Skip the manifest file itself
                        if member.name == "manifest.json":
                            continue

                        # Security check for each member
                        if ".." in member.name or member.name.startswith("/"):
                            console.print(
                                f"[red]Skipping dangerous file in archive: {member.name}[/red]"
                            )
                            continue

                        # Extract with safety
                        if sys.version_info >= (3, 12):
                            tar.extract(
                                member,
                                path="/",
                                filter="data",
                            )
                        else:
                            tar.extract(
                                member,
                                path="/",
                            )

        console.print(f"[green]Restored files from {path}[/green]")

    def restore_from_manifest(self, snapshot_path: str, manifest_data: dict[str, Any]):
        """
        Restore files based on the manifest data.
        This provides more granular control over restoration process.
        """
        path = Path(snapshot_path)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {path}")

        try:
            with tarfile.open(path, "r:gz") as tar:
                # Extract only the files listed in the manifest
                for dotfile_info in manifest_data.get("dotfiles", []):
                    target_path_str = dotfile_info.get("target")
                    if not target_path_str:
                        continue

                    target_path = Path(os.path.expanduser(target_path_str))
                    archive_name = str(target_path).lstrip(os.sep)

                    # Security validation
                    if ".." in archive_name or archive_name.startswith("/"):
                        console.print(
                            f"[red]Skipping dangerous path: {archive_name}[/red]"
                        )
                        continue

                    try:
                        member = tar.getmember(archive_name)
                        # Extract to a safe location first
                        tar.extract(
                            member,
                            path="/",
                            filter="data" if sys.version_info >= (3, 12) else None,
                        )
                        console.print(f"[green]Restored: {target_path}[/green]")
                    except KeyError:
                        console.print(
                            f"[yellow]File not found in archive: {archive_name}[/yellow]"
                        )
                    except Exception as e:
                        console.print(
                            f"[red]Failed to restore {target_path}: {e}[/red]"
                        )

            console.print("[green]Restored files based on manifest[/green]")
        except tarfile.ReadError:
            raise ValueError(f"Invalid tar archive: {path}")

    def get_latest_snapshot(self) -> Path:
        snapshots = list(self.backup_dir.glob("*.tar.gz"))
        if not snapshots:
            raise FileNotFoundError("No backups found.")
        # Sort by name (which contains timestamp YYYYMMDD-HHMMSS) descending
        latest = sorted(snapshots, key=lambda p: p.name, reverse=True)[0]
        return latest
