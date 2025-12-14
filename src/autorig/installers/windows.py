import shutil
import subprocess
from typing import List
from .base import SystemInstaller


class WindowsInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        # Check for package managers: winget, choco, scoop
        if shutil.which("winget"):
            cmd = ["winget", "install", "--silent", "--accept-package-agreements"]
        elif shutil.which("choco"):
            cmd = ["choco", "install", "-y"]
        elif shutil.which("scoop"):
            cmd = ["scoop", "install"]
        else:
            return False

        success = True
        for package in packages:
            try:
                subprocess.run(cmd + [package], check=True)
            except subprocess.CalledProcessError:
                success = False
        
        return success