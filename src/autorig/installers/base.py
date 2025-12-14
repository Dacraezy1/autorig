from abc import ABC, abstractmethod
from typing import List
import subprocess
import shutil
from rich.console import Console

console = Console()

class BaseInstaller(ABC):
    """Abstract base class for system package installers."""

    @abstractmethod
    def install(self, packages: List[str]) -> bool:
        """Installs the given list of packages. Returns True on success."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if this package manager is available on the current system."""
        pass

class AptInstaller(BaseInstaller):
    """Installer for Debian/Ubuntu based systems."""
    def is_available(self) -> bool:
        return shutil.which("apt-get") is not None

    def install(self, packages: List[str]) -> bool:
        if not packages:
            return True
        console.print(f"[cyan]Installing with apt:[/cyan] {', '.join(packages)}")
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(
                ["sudo", "apt-get", "install", "-y"] + packages,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

class DnfInstaller(BaseInstaller):
    """Installer for Fedora/RHEL based systems."""
    def is_available(self) -> bool:
        return shutil.which("dnf") is not None

    def install(self, packages: List[str]) -> bool:
        if not packages:
            return True
        console.print(f"[cyan]Installing with dnf:[/cyan] {', '.join(packages)}")
        try:
            subprocess.run(["sudo", "dnf", "install", "-y"] + packages, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

class PacmanInstaller(BaseInstaller):
    """Installer for Arch Linux based systems."""
    def is_available(self) -> bool:
        return shutil.which("pacman") is not None

    def install(self, packages: List[str]) -> bool:
        if not packages:
            return True
        console.print(f"[cyan]Installing with pacman:[/cyan] {', '.join(packages)}")
        try:
            # -Syu might be too aggressive for a simple install, just -S --noconfirm
            subprocess.run(
                ["sudo", "pacman", "-S", "--noconfirm", "--needed"] + packages,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

class YayInstaller(BaseInstaller):
    """Installer for Arch Linux systems using the yay AUR helper."""
    def is_available(self) -> bool:
        return shutil.which("yay") is not None

    def install(self, packages: List[str]) -> bool:
        if not packages:
            return True
        console.print(f"[cyan]Installing with yay:[/cyan] {', '.join(packages)}")
        try:
            # yay handles sudo internally
            subprocess.run(["yay", "-S", "--noconfirm", "--needed"] + packages, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

def get_system_installer() -> BaseInstaller:
    """Detects and returns the appropriate installer for the current system."""
    # Check for yay before pacman to prefer AUR helper if available
    installers = [AptInstaller(), DnfInstaller(), YayInstaller(), PacmanInstaller()]
    for installer in installers:
        if installer.is_available():
            return installer
    raise RuntimeError("No supported package manager found (checked: apt, dnf, yay, pacman)")
