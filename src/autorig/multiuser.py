"""Multi-user support for shared AutoRig configurations."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from rich.console import Console

from .config import RigConfig

console = Console()


class MultiUserManager:
    """Manages multi-user configurations and permissions."""

    def __init__(self, base_config_path: str):
        self.base_config_path = Path(base_config_path)
        self.shared_config_dir = self.base_config_path.parent / ".autorig" / "shared"
        self.user_config_dir = Path.home() / ".autorig" / "configs"

        # Ensure directories exist
        self.shared_config_dir.mkdir(parents=True, exist_ok=True)
        self.user_config_dir.mkdir(parents=True, exist_ok=True)

    def get_current_username(self) -> str:
        """Get the current username."""
        return os.environ.get("USER", os.environ.get("USERNAME", "default"))

    def get_user_config_path(self, username: Optional[str] = None) -> Path:
        """Get the config path for a specific user."""
        user = username or self.get_current_username()
        return self.user_config_dir / f"{user}.yaml"

    def create_user_config(
        self, base_config: str, username: Optional[str] = None
    ) -> RigConfig:
        """Create a user-specific configuration based on a base config."""
        user = username or self.get_current_username()
        user_config_path = self.get_user_config_path(user)

        # Load base configuration
        base_config_data = RigConfig.from_yaml(base_config)

        # Create user-specific overrides
        user_overrides = {
            "name": f"{base_config_data.name} ({user})",
            "variables": {"username": user, "user_home": str(Path.home())},
        }

        # Save user config
        with open(user_config_path, "w") as f:
            yaml.dump(user_overrides, f, default_flow_style=False, indent=2)

        console.print(f"[green]✅ User configuration created for: {user}[/green]")
        console.print(f"[dim]Location: {user_config_path}[/dim]")

        # Merge configurations
        merged_config = self._merge_configs(
            base_config_data.model_dump(), user_overrides
        )
        return RigConfig(**merged_config)

    def list_user_configs(self) -> Dict[str, Path]:
        """List all user-specific configurations."""
        user_configs = {}

        if self.user_config_dir.exists():
            for config_file in self.user_config_dir.glob("*.yaml"):
                username = config_file.stem
                user_configs[username] = config_file

        return user_configs

    def get_shared_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get a shared configuration by name."""
        shared_config_path = self.shared_config_dir / f"{config_name}.yaml"

        if not shared_config_path.exists():
            return None

        with open(shared_config_path, "r") as f:
            return yaml.safe_load(f)

    def save_shared_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Save a configuration to the shared directory."""
        shared_config_path = self.shared_config_dir / f"{config_name}.yaml"

        with open(shared_config_path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

        console.print(f"[green]✅ Shared configuration saved: {config_name}[/green]")
        console.print(f"[dim]Location: {shared_config_path}[/dim]")

    def list_shared_configs(self) -> Dict[str, Path]:
        """List all shared configurations."""
        shared_configs = {}

        if self.shared_config_dir.exists():
            for config_file in self.shared_config_dir.glob("*.yaml"):
                config_name = config_file.stem
                shared_configs[config_name] = config_file

        return shared_configs

    def _merge_configs(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def apply_config_for_user(
        self, base_config: str, username: Optional[str] = None
    ) -> RigConfig:
        """Load and merge base configuration with user-specific overrides."""
        user = username or self.get_current_username()

        # Load base configuration
        base_config_data = RigConfig.from_yaml(base_config)

        # Check for user-specific overrides
        user_config_path = self.get_user_config_path(user)

        if user_config_path.exists():
            with open(user_config_path, "r") as f:
                user_overrides = yaml.safe_load(f) or {}

            # Merge configurations
            merged = self._merge_configs(base_config_data.model_dump(), user_overrides)
            return RigConfig(**merged)

        return base_config_data

    def remove_user_config(self, username: Optional[str] = None) -> bool:
        """Remove a user-specific configuration."""
        user = username or self.get_current_username()
        user_config_path = self.get_user_config_path(user)

        if not user_config_path.exists():
            console.print(f"[yellow]No configuration found for user: {user}[/yellow]")
            return False

        user_config_path.unlink()
        console.print(f"[green]✅ User configuration removed for: {user}[/green]")
        return True

    def get_config_lock_path(self, config_name: str) -> Path:
        """Get the lock file path for a configuration."""
        return self.shared_config_dir / f"{config_name}.lock"

    def acquire_lock(self, config_name: str) -> bool:
        """Acquire a lock for a configuration."""
        lock_path = self.get_config_lock_path(config_name)

        if lock_path.exists():
            console.print(
                f"[yellow]Configuration is locked by another user: {config_name}[/yellow]"
            )
            return False

        lock_path.touch()
        return True

    def release_lock(self, config_name: str) -> None:
        """Release a lock for a configuration."""
        lock_path = self.get_config_lock_path(config_name)

        if lock_path.exists():
            lock_path.unlink()

    def print_user_info(self) -> None:
        """Print information about current user and available configs."""
        from rich.table import Table

        user = self.get_current_username()

        table = Table(title="Multi-User Information")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Current User", user)
        table.add_row("User Config Dir", str(self.user_config_dir))
        table.add_row("Shared Config Dir", str(self.shared_config_dir))

        user_configs = self.list_user_configs()
        table.add_row("User Configs", str(len(user_configs)))

        shared_configs = self.list_shared_configs()
        table.add_row("Shared Configs", str(len(shared_configs)))

        console.print(table)
