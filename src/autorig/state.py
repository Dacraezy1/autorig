"""
State management for AutoRig operations with error recovery and rollback capabilities.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from .config import RigConfig


class StateManager:
    """
    Manages the state of AutoRig operations with error recovery capabilities.
    """

    def __init__(self, config: RigConfig, state_dir: str = "~/.autorig/state"):
        self.config = config
        self.state_dir = Path(os.path.expanduser(state_dir))
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = (
            self.state_dir / f"{self._sanitize_filename(config.name)}.json"
        )

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize the config name to be a valid filename."""
        return (
            "".join(c for c in name if c.isalnum() or c in (" ", "_", "-"))
            .strip()
            .replace(" ", "_")
        )

    def save_state(self, operation: str, state_data: Dict[str, Any]):
        """Save the current state of an operation."""
        state = {
            "config_name": self.config.name,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "data": state_data,
        }

        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load the current state if it exists."""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return None

    def clear_state(self):
        """Clear the current state file."""
        if self.state_file.exists():
            self.state_file.unlink()

    def create_rollback_point(self, operation: str, changes: List[Dict[str, Any]]):
        """Create a rollback point for an operation."""
        rollback_file = (
            self.state_dir
            / f"{self._sanitize_filename(self.config.name)}_rollback_{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        rollback_data = {
            "operation": operation,
            "config_name": self.config.name,
            "timestamp": datetime.now().isoformat(),
            "changes": changes,
        }

        with open(rollback_file, "w") as f:
            json.dump(rollback_data, f, indent=2)

        return rollback_file

    def get_latest_rollback(self, operation: str) -> Optional[Path]:
        """Get the latest rollback file for an operation."""
        rollback_files = list(
            self.state_dir.glob(
                f"{self._sanitize_filename(self.config.name)}_rollback_{operation}_*.json"
            )
        )
        if not rollback_files:
            return None
        return sorted(rollback_files, key=lambda x: x.name)[-1]

    def rollback_operation(self, rollback_file: Path):
        """Execute rollback based on a rollback file."""
        if not rollback_file.exists():
            raise FileNotFoundError(f"Rollback file not found: {rollback_file}")

        with open(rollback_file, "r") as f:
            rollback_data = json.load(f)

        changes = rollback_data.get("changes", [])
        operation = rollback_data.get("operation", "")

        print(f"Rolling back operation: {operation}")

        for change in changes:
            action = change.get("action", "")
            path = change.get("path", "")
            previous_state = change.get("previous_state", {})

            if action == "created_symlink":
                target_path = Path(os.path.expanduser(path))
                if target_path.is_symlink():
                    target_path.unlink()
                    print(f"Removed symlink: {path}")
            elif action == "modified_file":
                target_path = Path(os.path.expanduser(path))
                if previous_state.get("exists", False):
                    backup_path = Path(
                        os.path.expanduser(previous_state.get("backup_path", ""))
                    )
                    if backup_path.exists():
                        if target_path.exists():
                            target_path.unlink()
                        backup_path.rename(target_path)
                        print(f"Restored file from backup: {path}")
            elif action == "installed_package":
                # This would need to call the installer to remove the package
                # For now, just log the action
                print(f"Would rollback package installation: {path}")
            elif action == "git_cloned":
                repo_path = Path(os.path.expanduser(path))
                if repo_path.exists():
                    import shutil

                    shutil.rmtree(repo_path)
                    print(f"Removed cloned repository: {path}")


class OperationTracker:
    """
    Tracks ongoing operations and manages rollbacks.
    """

    def __init__(self, state_manager: StateManager, operation_name: str):
        self.state_manager = state_manager
        self.operation_name = operation_name
        self.changes: List[Dict[str, Any]] = []

    def record_change(self, action: str, path: str, **details):
        """Record a change made during an operation."""
        change = {
            "action": action,
            "path": path,
            "timestamp": datetime.now().isoformat(),
            **details,
        }
        self.changes.append(change)

    def save_rollback_point(self):
        """Save the current set of changes as a rollback point."""
        return self.state_manager.create_rollback_point(
            self.operation_name, self.changes
        )

    def complete_operation(self):
        """Complete the operation and clear the temporary state."""
        # Create final rollback point
        self.save_rollback_point()
        # Clear temporary state
        self.state_manager.clear_state()

    def rollback_operation(self):
        """Rollback the operation."""
        latest_rollback = self.state_manager.get_latest_rollback(self.operation_name)
        if latest_rollback:
            self.state_manager.rollback_operation(latest_rollback)
