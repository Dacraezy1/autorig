import shutil
import subprocess
from typing import List
from .base import SystemInstaller


class AlpineInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        if not shutil.which("apk"):
            # apk not found
            return False

        cmd = ["sudo", "apk", "add"]

        try:
            subprocess.run(cmd + packages, check=True)
            return True
        except subprocess.CalledProcessError:
            return False