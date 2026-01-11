from abc import ABC, abstractmethod
from typing import List
import platform


class SystemInstaller(ABC):
    @abstractmethod
    def install(self, packages: List[str]) -> bool:
        pass

    @abstractmethod
    def uninstall(self, packages: List[str]) -> bool:
        pass


class NoOpInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        # Fallback for unsupported OS
        return True

    def uninstall(self, packages: List[str]) -> bool:
        return True


def get_system_installer() -> SystemInstaller:
    system = platform.system().lower()
    if system == "linux":
        # Check for specific distros
        from .linux import LinuxInstaller
        from .alpine import AlpineInstaller

        # Check for Alpine first (uses apk)
        if _is_alpine():
            return AlpineInstaller()
        else:
            return LinuxInstaller()
    elif system == "darwin":
        from .macos import MacOSInstaller

        return MacOSInstaller()
    elif system == "windows":
        from .windows import WindowsInstaller

        return WindowsInstaller()
    return NoOpInstaller()


def _is_alpine() -> bool:
    """Check if the system is Alpine Linux."""
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read().lower()
            return "alpine" in content
    except FileNotFoundError:
        return False
