"""Common utilities for AutoRig."""

import os
from pathlib import Path


def expand_path(path: str) -> Path:
    """
    Expand user home and environment variables in a path.

    Args:
        path: Path string that may contain ~ or environment variables

    Returns:
        Expanded Path object
    """
    expanded = os.path.expanduser(path)
    expanded = os.path.expandvars(expanded)
    return Path(expanded)


def validate_path(path: str) -> bool:
    """
    Validate a path for security (prevent path traversal).

    Args:
        path: Path string to validate

    Returns:
        True if path is safe, False otherwise
    """
    if "../" in path or "..\\" in path:
        return False

    dangerous_paths = [
        "/etc",
        "/root",
        "/boot",
        "/sys",
        "/proc",
        "/dev",
        "/var/log",
        "/usr/bin",
        "/usr/sbin",
        "/bin",
        "/sbin",
    ]

    expanded = str(expand_path(path))

    for dangerous in dangerous_paths:
        if expanded.startswith(dangerous) and expanded != dangerous:
            return False

    return True


def safe_open(path: str, mode: str = "r"):
    """
    Safely open a file with validation.

    Args:
        path: Path to the file
        mode: File open mode

    Returns:
        File object or None if validation fails
    """
    if not validate_path(path):
        raise ValueError(f"Invalid path detected: {path}")

    return open(expand_path(path), mode)


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory

    Returns:
        Path object for the directory
    """
    dir_path = expand_path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_home_dir() -> Path:
    """
    Get the user's home directory.

    Returns:
        Path object for home directory
    """
    return Path.home()


def get_config_dir() -> Path:
    """
    Get AutoRig's configuration directory.

    Returns:
        Path object for config directory
    """
    home = get_home_dir()
    return home / ".autorig"


def get_cache_dir() -> Path:
    """
    Get AutoRig's cache directory.

    Returns:
        Path object for cache directory
    """
    config = get_config_dir()
    cache_dir = config / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
