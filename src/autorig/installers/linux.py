import shutil
import subprocess
from typing import List
from .base import SystemInstaller


class LinuxInstaller(SystemInstaller):
    def install(self, packages: List[str]) -> bool:
        manager = self._get_manager()
        if not manager:
            return False

        cmd = []
        if manager == "apt-get":
            cmd = ["sudo", "apt-get", "install", "-y"]
        elif manager == "dnf":
            cmd = ["sudo", "dnf", "install", "-y"]
        elif manager == "yum":
            cmd = ["sudo", "yum", "install", "-y"]
        elif manager == "zypper":
            cmd = ["sudo", "zypper", "install", "-y"]
        elif manager == "pacman":
            cmd = ["sudo", "pacman", "-S", "--noconfirm"]
        elif manager == "xbps":
            cmd = ["sudo", "xbps-install", "-Sy"]
        elif manager == "apk":  # Also support Alpine through this installer
            cmd = ["sudo", "apk", "add"]

        try:
            subprocess.run(cmd + packages, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _get_manager(self):
        for mgr in ["apt-get", "dnf", "yum", "zypper", "pacman", "xbps", "apk"]:
            if shutil.which(mgr):
                return mgr
        return None
