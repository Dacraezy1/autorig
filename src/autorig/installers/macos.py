import shutil
import subprocess
from typing import List
from .base import SystemInstaller

class MacOSInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        if not shutil.which("brew"):
            # Homebrew not found
            return False
            
        cmd = ["brew", "install"]
        
        try:
            subprocess.run(cmd + packages, check=True)
            return True
        except subprocess.CalledProcessError:
            return False