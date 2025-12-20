"""
Remote configuration fetching and cloud integration for AutoRig.
"""

import os
import tempfile
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from rich.console import Console

console = Console()


class RemoteConfigManager:
    """
    Manages fetching configurations from remote sources (GitHub, GitLab, HTTP, etc.)
    """

    @staticmethod
    def is_remote_url(config_path: str) -> bool:
        """Check if the config path is a remote URL."""
        parsed = urlparse(config_path)
        return parsed.scheme in ["http", "https"]

    @staticmethod
    def fetch_remote_config(remote_url: str) -> Path:
        """Fetch a configuration file from a remote URL."""
        try:
            console.print(f"[blue]Fetching remote configuration:[/blue] {remote_url}")

            response = requests.get(remote_url)
            response.raise_for_status()

            # Create a temporary file to store the remote config
            parsed_url = urlparse(remote_url)
            filename = os.path.basename(parsed_url.path) or "remote_config.yaml"

            # Create temporary file
            temp_dir = Path(tempfile.mkdtemp(prefix="autorig_"))
            temp_config_path = temp_dir / filename

            with open(temp_config_path, "wb") as f:
                f.write(response.content)

            console.print(
                f"[green]Downloaded remote configuration to:[/green] {temp_config_path}"
            )
            return temp_config_path

        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error downloading remote configuration: {e}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Error processing remote configuration: {e}[/red]")
            raise

    @staticmethod
    def fetch_from_github(owner: str, repo: str, path: str, ref: str = "main") -> Path:
        """Fetch a file from GitHub repository."""
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
        return RemoteConfigManager.fetch_remote_config(url)

    @staticmethod
    def fetch_from_gitlab(owner: str, repo: str, path: str, ref: str = "main") -> Path:
        """Fetch a file from GitLab repository."""
        # GitLab raw file URL format
        url = f"https://gitlab.com/{owner}/{repo}/-/raw/{ref}/{path}"
        return RemoteConfigManager.fetch_remote_config(url)


def resolve_config_path(config_path: str) -> str:
    """
    Resolve a configuration path, handling remote URLs by downloading to temporary location.
    Returns the local path to the configuration file.
    """
    if RemoteConfigManager.is_remote_url(config_path):
        temp_path = RemoteConfigManager.fetch_remote_config(config_path)
        return str(temp_path)
    return config_path
