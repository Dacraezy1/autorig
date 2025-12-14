import shutil
import subprocess
from typing import List
from .base import SystemInstaller


class MacOSInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        # Check for package managers: homebrew, macports
        if shutil.which("brew"):
            # Homebrew: Popular macOS package manager
            cmd = ["brew", "install"]
        elif shutil.which("port"):
            # MacPorts: Alternative macOS package manager
            cmd = ["sudo", "port", "install"]
        else:
            return False

        try:
            subprocess.run(cmd + packages, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
