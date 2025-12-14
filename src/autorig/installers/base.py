from abc import ABC, abstractmethod
from typing import List
import platform

class SystemInstaller(ABC):
    @abstractmethod
    def install(self, packages: List[str]) -> bool:
        pass

class NoOpInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        # Fallback for unsupported OS
        return True

def get_system_installer() -> SystemInstaller:
    system = platform.system().lower()
    if system == "linux":
        from .linux import LinuxInstaller
        return LinuxInstaller()
    return NoOpInstaller()