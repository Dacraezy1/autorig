from abc import ABC, abstractmethod
from typing import List
import subprocess
import shutil
from rich.console import Console

console = Console()

class BaseInstaller(ABC):
    @abstractmethod
    def install(self, packages: List[str]) -> bool:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

class AptInstaller(BaseInstaller):
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

class PacmanInstaller(BaseInstaller):
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

def get_system_installer() -> BaseInstaller:
    installers = [AptInstaller(), PacmanInstaller()]
    for installer in installers:
        if installer.is_available():
            return installer
    raise RuntimeError("No supported package manager found (checked: apt, pacman)")
