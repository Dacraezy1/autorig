"""
Environment detection and profiles functionality for AutoRig.
"""

import os
import platform
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml  # type: ignore[import-untyped]


class EnvironmentDetector:
    """
    Detects the current environment and system characteristics with caching.
    """

    _cached_info: Optional[Dict[str, Any]] = None

    def __init__(self, use_cache: bool = True):
        if use_cache and EnvironmentDetector._cached_info is not None:
            self.env_info = EnvironmentDetector._cached_info
        else:
            self.env_info = self._collect_environment_info()
            if use_cache:
                EnvironmentDetector._cached_info = self.env_info

    def _collect_environment_info(self) -> Dict[str, Any]:
        """Collect information about the current environment."""
        return {
            "os": platform.system().lower(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "node": socket.gethostname(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "shell": os.environ.get("SHELL", ""),
            "user": os.environ.get("USER", os.environ.get("USERNAME", "")),
            "home": os.path.expanduser("~"),
            "is_wsl": self._is_wsl(),
            "is_docker": self._is_docker(),
            "is_vm": self._is_vm(),
            "is_ci": self._is_ci(),
            "desktop_environment": os.environ.get("XDG_CURRENT_DESKTOP", ""),
            "display_server": os.environ.get("XDG_SESSION_TYPE", ""),
            "session_type": os.environ.get("XDG_SESSION_TYPE", ""),
            "wayland_display": os.environ.get("WAYLAND_DISPLAY", ""),
            "term": os.environ.get("TERM", ""),
            "term_program": os.environ.get("TERM_PROGRAM", ""),
            "editor": os.environ.get("EDITOR", os.environ.get("VISUAL", "vi")),
            "language": os.environ.get("LANG", ""),
            "timezone": os.environ.get("TZ", ""),
            "display": os.environ.get("DISPLAY", ""),
            "packages_installed": self._get_installed_packages(),
            "gpu_info": self._get_gpu_info(),
            "memory_gb": self._get_memory_gb(),
            "cpu_cores": self._get_cpu_cores(),
            "disk_space_gb": self._get_disk_space_gb(),
        }

    def _is_vm(self) -> bool:
        """Check if running inside a virtual machine."""
        try:
            # Check for common VM indicators in DMI
            import subprocess

            result = subprocess.run(
                ["systemd-detect-virt"], capture_output=True, text=True, check=True
            )
            if result.stdout.strip() != "none":
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback method: check for VM indicators in other ways
            try:
                with open("/sys/class/dmi/id/product_name", "r") as f:
                    product_name = f.read().strip().lower()
                    vm_indicators = [
                        "vmware",
                        "virtualbox",
                        "qemu",
                        "kvm",
                        "parallels",
                        "bochs",
                    ]
                    if any(indicator in product_name for indicator in vm_indicators):
                        return True
            except FileNotFoundError:
                pass
        return False

    def _is_ci(self) -> bool:
        """Check if running in a CI/CD environment."""
        ci_vars = [
            "CI",
            "CONTINUOUS_INTEGRATION",
            "BUILD_NUMBER",
            "GITHUB_ACTIONS",
            "TRAVIS",
            "CIRCLECI",
            "JENKINS_URL",
            "GITLAB_CI",
            "TEAMCITY_VERSION",
        ]
        return any(os.environ.get(var) for var in ci_vars)

    def _get_installed_packages(self) -> List[str]:
        """Get a list of installed packages (best effort)."""
        try:
            if self.env_info["os"] == "linux":
                # Try different package managers
                for cmd in [
                    ["dpkg", "-l"],
                    ["rpm", "-qa"],
                    ["pacman", "-Q"],
                    ["brew", "list"],
                ]:
                    try:
                        result = subprocess.run(
                            cmd, capture_output=True, text=True, check=True
                        )
                        packages = result.stdout.split("\n")
                        # Filter and clean package names
                        packages = [
                            pkg.split()[0] if pkg.split() else ""
                            for pkg in packages
                            if pkg.startswith(("ii", "rc")) or pkg.strip()
                        ]
                        return [pkg for pkg in packages if pkg]
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            elif self.env_info["os"] == "darwin":
                try:
                    result = subprocess.run(
                        ["brew", "list"], capture_output=True, text=True, check=True
                    )
                    return [
                        pkg.strip() for pkg in result.stdout.split("\n") if pkg.strip()
                    ]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        except Exception:
            pass
        return []

    def _get_gpu_info(self) -> str:
        """Get GPU information."""
        try:
            if self.env_info["os"] == "linux":
                result = subprocess.run(
                    ["lspci"], capture_output=True, text=True, check=True
                )
                for line in result.stdout.split("\n"):
                    if (
                        "vga" in line.lower()
                        or "3d" in line.lower()
                        or "display" in line.lower()
                    ):
                        return line.strip().split(":")[-1].strip()
            elif self.env_info["os"] == "darwin":
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                for line in result.stdout.split("\n"):
                    if "chip" in line.lower() or "processor" in line.lower():
                        return line.strip()
        except Exception:
            pass
        return "Unknown"

    def _get_memory_gb(self) -> float:
        """Get total system memory in GB."""
        try:
            if self.env_info["os"] == "linux":
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            # Format: MemTotal:       16342348 kB
                            parts = line.split()
                            kb = int(parts[1])
                            return round(kb / 1024 / 1024, 2)  # Convert to GB
            elif self.env_info["os"] == "darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                bytes_size = int(result.stdout.strip())
                return round(bytes_size / 1024 / 1024 / 1024, 2)  # Convert to GB
        except Exception:
            pass
        return 0.0

    def _get_cpu_cores(self) -> int:
        """Get number of CPU cores."""
        try:
            import multiprocessing

            return multiprocessing.cpu_count()
        except Exception:
            return 0

    def _get_disk_space_gb(self) -> float:
        """Get available disk space in GB."""
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")
            return round(free / 1024 / 1024 / 1024, 2)  # Convert to GB
        except Exception:
            return 0.0

    def _is_wsl(self) -> bool:
        """Check if running under Windows Subsystem for Linux."""
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except FileNotFoundError:
            return False

    def _is_docker(self) -> bool:
        """Check if running inside a Docker container."""
        # Check for .dockerenv file
        if Path("/.dockerenv").exists():
            return True

        # Check for docker cgroup
        try:
            with open("/proc/1/cgroup", "r") as f:
                return "docker" in f.read()
        except FileNotFoundError:
            return False

    def get_profile_name(self) -> str:
        """Generate a profile name based on environment characteristics."""
        os_name = self.env_info["os"]
        machine = self.env_info["machine"]
        node = self.env_info["node"]

        # Create a profile name like "linux-x86_64-workstation"
        profile_parts = [os_name, machine]

        # Add more specific identifiers if available
        if "laptop" in node.lower() or "thinkpad" in node.lower():
            profile_parts.append("laptop")
        elif "desktop" in node.lower() or "tower" in node.lower():
            profile_parts.append("desktop")
        elif self.env_info.get("is_wsl"):
            profile_parts.append("wsl")
        elif self.env_info.get("is_docker"):
            profile_parts.append("docker")

        return "-".join(profile_parts)

    def matches_profile(self, profile_spec: Dict[str, Any]) -> bool:
        """
        Check if the current environment matches a profile specification.

        Profile spec can contain:
        - 'os': 'linux', 'darwin', 'windows'
        - 'platform': partial match for platform string
        - 'machine': architecture (x86_64, arm64, etc.)
        - 'hostname': match for hostname
        - 'shell': match for shell
        - 'conditions': custom conditions
        """
        if "os" in profile_spec and profile_spec["os"] != self.env_info["os"]:
            return False

        if (
            "platform" in profile_spec
            and profile_spec["platform"] not in self.env_info["platform"]
        ):
            return False

        if (
            "machine" in profile_spec
            and profile_spec["machine"] != self.env_info["machine"]
        ):
            return False

        if (
            "hostname" in profile_spec
            and profile_spec["hostname"] != self.env_info["node"]
        ):
            return False

        if (
            "shell" in profile_spec
            and profile_spec["shell"] not in self.env_info["shell"]
        ):
            return False

        # Check custom conditions
        if "conditions" in profile_spec:
            for condition in profile_spec["conditions"]:
                if not self._evaluate_condition(condition):
                    return False

        return True

    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a custom condition."""
        # Simple condition evaluation
        if condition == "is_wsl":
            return self.env_info.get("is_wsl", False)
        elif condition == "is_docker":
            return self.env_info.get("is_docker", False)
        elif condition.startswith("env:"):
            # Check environment variable
            env_var = condition[4:]  # Remove 'env:' prefix
            key, expected = env_var.split("=", 1) if "=" in env_var else (env_var, "1")
            return os.environ.get(key, "") == expected
        return False


def load_profile_config(
    config_path: str, profile: Optional[str] = None
) -> Dict[str, Any]:
    """
    Load a configuration file with profile-specific overrides.

    If a profile is specified or auto-detected, it will try to load:
    - rig.yaml (base config)
    - rig-{profile}.yaml (profile-specific config)
    - rig.local.yaml (local overrides, not committed)

    Profile-specific config overrides base config.
    """
    detector = EnvironmentDetector()

    # Determine profile to use
    if not profile:
        profile = detector.get_profile_name()

    # List of config files to try, in order of precedence (last wins)
    config_files = [
        config_path,  # Base config
        config_path.replace(".yaml", f"-{profile}.yaml"),  # Profile-specific
        config_path.replace(".yaml", ".local.yaml"),  # Local overrides
    ]

    final_config: Dict[str, Any] = {}

    for config_file in config_files:
        config_path_obj = Path(config_file)
        if config_path_obj.exists():
            with open(config_path_obj, "r") as f:
                content = f.read()

            # Expand environment variables in the content
            try:
                content = os.path.expandvars(content)
            except Exception as e:
                raise ValueError(
                    f"Error expanding environment variables in config: {e}"
                )

            try:
                config_data = yaml.safe_load(content) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in configuration file: {e}")

            # First merge the base configuration from this file
            final_config = _deep_merge(final_config, config_data)

            # Then apply profile-specific sections if they exist
            if (
                profile
                and "profiles" in config_data
                and profile in config_data["profiles"]
            ):
                profile_config = config_data["profiles"][profile]
                # Merge profile config with base config
                final_config = _deep_merge(final_config, profile_config)

    return final_config


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result
