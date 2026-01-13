"""Low-level git operations module."""

import asyncio
from pathlib import Path
from typing import Optional, Tuple
from logging import Logger


class GitOperations:
    """Handles low-level git operations."""

    def __init__(self, logger: Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run

    async def clone(
        self, url: str, path: Path, branch: str = "main"
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Clone a git repository.

        Returns:
            Tuple of (success, stdout, stderr)
        """
        self.logger.info(f"Cloning repository: {url} to {path}")

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "clone",
                "-b",
                branch,
                url,
                str(path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            if success:
                self.logger.info(f"Successfully cloned: {url}")
            else:
                self.logger.error(f"Failed to clone {url}: {stderr.decode()}")

            return success, stdout.decode(), stderr.decode()
        except Exception as e:
            self.logger.error(f"Exception cloning {url}: {e}")
            return False, "", str(e)

    async def pull(self, path: Path) -> Tuple[bool, str, Optional[str]]:
        """
        Pull latest changes in a git repository.

        Returns:
            Tuple of (success, stdout, stderr)
        """
        self.logger.info(f"Pulling in repository: {path}")

        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                str(path),
                "pull",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            if success:
                self.logger.info(f"Successfully pulled: {path}")
            else:
                self.logger.error(f"Failed to pull {path}: {stderr.decode()}")

            return success, stdout.decode(), stderr.decode()
        except Exception as e:
            self.logger.error(f"Exception pulling {path}: {e}")
            return False, "", str(e)

    async def push(self, path: Path) -> Tuple[bool, Optional[str]]:
        """
        Push changes to remote repository.

        Returns:
            Tuple of (success, stderr)
        """
        self.logger.info(f"Pushing from repository: {path}")

        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                str(path),
                "push",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()

            success = process.returncode == 0
            if success:
                self.logger.info(f"Successfully pushed: {path}")
            else:
                self.logger.error(f"Failed to push {path}: {stderr.decode()}")

            return success, stderr.decode()
        except Exception as e:
            self.logger.error(f"Exception pushing {path}: {e}")
            return False, str(e)

    async def get_status(self, path: Path) -> str:
        """
        Get git status in porcelain format.

        Returns:
            Status output string
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                str(path),
                "status",
                "--porcelain",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            return stdout.decode()
        except Exception as e:
            self.logger.error(f"Exception getting status {path}: {e}")
            return ""

    def is_git_repo(self, path: Path) -> bool:
        """Check if path is a git repository."""
        return (path / ".git").exists()

    def validate_path(self, path: str) -> bool:
        """
        Validate git repository path for security.

        Returns:
            True if path is safe, False otherwise
        """
        expanded_path = path
        if ".." in expanded_path or expanded_path.startswith("/tmp"):
            self.logger.error(f"Invalid repository path: {path}")
            return False
        return True
