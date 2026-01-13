"""Package manager operations module."""

import subprocess
from typing import List, Dict, Tuple, Optional
from logging import Logger


class PackageOperations:
    """Handles package manager operations."""

    def __init__(self, logger: Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run

    def get_package_manager(self) -> str:
        """Detect the system package manager."""
        try:
            if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
                return "apt"
            elif subprocess.run(["which", "dnf"], capture_output=True).returncode == 0:
                return "dnf"
            elif subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
                return "yum"
            elif (
                subprocess.run(["which", "pacman"], capture_output=True).returncode == 0
            ):
                return "pacman"
            elif (
                subprocess.run(["which", "zypper"], capture_output=True).returncode == 0
            ):
                return "zypper"
            elif subprocess.run(["which", "xbps"], capture_output=True).returncode == 0:
                return "xbps"
            elif subprocess.run(["which", "apk"], capture_output=True).returncode == 0:
                return "apk"
            elif subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
                return "brew"
            elif (
                subprocess.run(["which", "winget"], capture_output=True).returncode == 0
            ):
                return "winget"
            elif (
                subprocess.run(["which", "choco"], capture_output=True).returncode == 0
            ):
                return "choco"
            elif (
                subprocess.run(["which", "scoop"], capture_output=True).returncode == 0
            ):
                return "scoop"
            else:
                return "unknown"
        except Exception:
            return "unknown"

    def get_install_command(self, package_manager: str, package: str) -> List[str]:
        """Get the install command for a package manager."""
        commands: Dict[str, List[str]] = {
            "apt": ["sudo", "apt-get", "install", "-y", package],
            "dnf": ["sudo", "dnf", "install", "-y", package],
            "yum": ["sudo", "yum", "install", "-y", package],
            "pacman": ["sudo", "pacman", "-S", "--noconfirm", package],
            "zypper": ["sudo", "zypper", "install", "-y", package],
            "xbps": ["sudo", "xbps-install", "-S", package],
            "apk": ["sudo", "apk", "add", package],
            "brew": ["brew", "install", package],
            "winget": ["winget", "install", package],
            "choco": ["choco", "install", package, "-y"],
            "scoop": ["scoop", "install", package],
        }
        return commands.get(package_manager, [])

    def install_package(
        self, package: str, package_manager: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Install a package using the system package manager.

        Returns:
            Tuple of (success, error_message)
        """
        if package_manager is None:
            package_manager = self.get_package_manager()

        if package_manager == "unknown":
            self.logger.error("Unknown package manager")
            return False, "Unknown package manager"

        command = self.get_install_command(package_manager, package)
        if not command:
            self.logger.error(f"Unknown package manager: {package_manager}")
            return False, f"Unknown package manager: {package_manager}"

        self.logger.info(f"Installing {package} using {package_manager}")

        if self.dry_run:
            self.logger.info(f"DRY RUN: Would install {package}")
            return True, ""

        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
            self.logger.info(f"Successfully installed: {package}")
            return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or str(e)
            self.logger.error(f"Failed to install {package}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Exception installing {package}: {error_msg}")
            return False, error_msg

    def is_installed(self, package: str) -> bool:
        """Check if a package is installed."""
        try:
            result = subprocess.run(["which", package], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    def list_installed(self, package_manager: Optional[str] = None) -> List[str]:
        """List installed packages."""
        if package_manager is None:
            package_manager = self.get_package_manager()

        commands: Dict[str, List[str]] = {
            "apt": ["dpkg", "-l"],
            "dnf": ["rpm", "-qa"],
            "yum": ["rpm", "-qa"],
            "pacman": ["pacman", "-Q"],
            "zypper": ["rpm", "-qa"],
            "xbps": ["xbps-query", "-l"],
            "apk": ["apk", "info"],
            "brew": ["brew", "list"],
        }

        command = commands.get(package_manager)
        if not command:
            return []

        try:
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                packages = result.stdout.split("\n")
                return [p.strip() for p in packages if p.strip()]
            return []
        except Exception:
            return []
