import shutil
import subprocess
from typing import List
from .base import SystemInstaller


class WindowsInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        # Check for package managers: winget, choco, scoop
        if shutil.which("winget"):
            # winget: Modern package manager from Microsoft
            cmd = [
                "winget",
                "install",
                "--silent",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ]
        elif shutil.which("choco"):
            # Chocolatey: Popular Windows package manager
            cmd = ["choco", "install", "-y"]
        elif shutil.which("scoop"):
            # Scoop: Windows command-line installer
            cmd = ["scoop", "install"]
        else:
            return False

        success = True
        for package in packages:
            try:
                result = subprocess.run(
                    cmd + [package], check=True, capture_output=True, text=True
                )
                if result.stderr and "error" in result.stderr.lower():
                    success = False
                    continue
            except subprocess.CalledProcessError:
                success = False
                continue

        return success
