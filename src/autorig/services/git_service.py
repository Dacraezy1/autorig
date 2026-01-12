import asyncio
import os
import subprocess
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from autorig.config import GitRepo
from autorig.notifications import ProgressTracker
from autorig.state import OperationTracker
from logging import Logger

console = Console()

class GitService:
    def __init__(
        self,
        logger: Logger,
        progress_tracker: ProgressTracker,
        dry_run: bool = False,
        verbose: bool = False
    ):
        self.logger = logger
        self.progress_tracker = progress_tracker
        self.dry_run = dry_run
        self.verbose = verbose

    async def process_repositories(self, repos: List[GitRepo], tracker: Optional[OperationTracker] = None):
        if not repos:
            self.logger.debug("No git repositories to process")
            return

        console.print(f"[bold]Processing {len(repos)} git repositories...[/bold]")
        self.logger.info(f"Processing {len(repos)} git repositories")

        tasks = []
        for i, repo in enumerate(repos, 1):
            tasks.append(self._clone_or_update_repo(repo, i, len(repos), tracker))

        await asyncio.gather(*tasks)

    async def _clone_or_update_repo(
        self, repo: GitRepo, index: int, total: int, tracker: Optional[OperationTracker] = None
    ):
        try:
            target_path = Path(os.path.expanduser(repo.path))

            # Security check for path traversal
            expanded_path = os.path.expanduser(repo.path)
            if ".." in expanded_path or expanded_path.startswith("/tmp"):
                console.print(
                    f"[red]Security error: Invalid repository path: {repo.path}[/red]"
                )
                self.logger.error(
                    f"Security error: Invalid repository path: {repo.path}"
                )
                if tracker:
                    tracker.record_change(
                        "security_error",
                        repo.path,
                        error="path_traversal",
                        url=repo.url,
                    )
                self.progress_tracker.update_progress(f"Security error: {repo.url}")
                return

            console.print(
                f"[dim]Processing repository {index}/{total}: {repo.url}[/dim]"
            )
            self.logger.debug(f"Processing repository {index}/{total}: {repo.url}")

            if target_path.exists():
                await self._update_repo(repo, target_path, tracker)
            else:
                await self._clone_repo(repo, target_path, tracker)

        except Exception as e:
            console.print(f"[red]Error processing repository {repo.url}: {e}[/red]")
            self.logger.error(f"Error processing repository {repo.url}: {e}")
            if tracker:
                tracker.record_change(
                    "process_repo_error", repo.path, url=repo.url, error=str(e)
                )
            self.progress_tracker.update_progress(f"Error: {repo.url}")

    async def _update_repo(self, repo: GitRepo, target_path: Path, tracker: Optional[OperationTracker]):
        if (target_path / ".git").exists():
            console.print(
                f"[yellow]Path exists, updating:[/yellow] {repo.path}"
            )
            self.logger.info(f"Repository exists, updating: {repo.url}")
            if self.dry_run:
                console.print(
                    f"[yellow]DRY RUN: Would pull in {target_path}[/yellow]"
                )
                if tracker:
                    tracker.record_change(
                        "would_pull_repo", repo.path, url=repo.url
                    )
                self.progress_tracker.update_progress(
                    f"Dry run: update {repo.url}"
                )
                return

            try:
                process = await asyncio.create_subprocess_exec(
                    "git",
                    "-C",
                    str(target_path),
                    "pull",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    console.print(f"[green]Updated {repo.url}[/green]")
                    if self.verbose and stdout:
                        console.print(
                            f"[dim]Git output: {stdout.decode()}[/dim]"
                        )
                    self.logger.info(f"Updated git repo: {repo.url}")
                    if tracker:
                        tracker.record_change(
                            "updated_repo", repo.path, url=repo.url
                        )
                    self.progress_tracker.update_progress(
                        f"Updated: {repo.url}"
                    )
                else:
                    raise subprocess.CalledProcessError(
                        process.returncode or 1,
                        ["git", "pull"],
                        output=stdout.decode(),
                        stderr=stderr.decode(),
                    )

            except subprocess.CalledProcessError as e:
                console.print(f"[red]Failed to update {repo.url}: {e}[/red]")
                if e.stderr:
                    console.print(f"[red]Git error: {e.stderr}[/red]")
                self.logger.error(f"Failed to update {repo.url}: {e}")
                if tracker:
                    tracker.record_change(
                        "updated_repo",
                        repo.path,
                        url=repo.url,
                        status="failed",
                        error=str(e),
                    )
                self.progress_tracker.update_progress(f"Failed: {repo.url}")
        else:
            console.print(
                f"[yellow]Path exists but is not a git repository: {repo.path}[/yellow]"
            )
            self.logger.warning(
                f"Path exists but is not a git repository: {repo.path}"
            )
            if tracker:
                tracker.record_change(
                    "invalid_repo_path",
                    repo.path,
                    url=repo.url,
                    error="not_git_repo",
                )
            self.progress_tracker.update_progress(f"Non-git path: {repo.path}")

    async def _clone_repo(self, repo: GitRepo, target_path: Path, tracker: Optional[OperationTracker]):
        console.print(f"Cloning {repo.url} to {repo.path}...")
        self.logger.info(f"Cloning repository: {repo.url} to {repo.path}")
        if self.dry_run:
            console.print(f"[yellow]DRY RUN: Would clone {repo.url}[/yellow]")
            if tracker:
                tracker.record_change("would_clone_repo", repo.path, url=repo.url)
            self.progress_tracker.update_progress(f"Dry run: clone {repo.url}")
            return

        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "clone",
                "-b",
                repo.branch or "main",
                repo.url,
                str(target_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                console.print(f"[green]Cloned {repo.url}[/green]")
                if self.verbose and stdout:
                    console.print(f"[dim]Git output: {stdout.decode()}[/dim]")
                self.logger.info(f"Cloned git repo: {repo.url}")
                if tracker:
                    tracker.record_change("git_cloned", repo.path, url=repo.url)
                self.progress_tracker.update_progress(f"Cloned: {repo.url}")
            else:
                raise subprocess.CalledProcessError(
                    process.returncode or 1,
                    ["git", "clone"],
                    output=stdout.decode(),
                    stderr=stderr.decode(),
                )

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to clone {repo.url}: {e}[/red]")
            if e.stderr:
                console.print(f"[red]Git error: {e.stderr}[/red]")
            self.logger.error(f"Failed to clone {repo.url}: {e}")
            if tracker:
                tracker.record_change(
                    "git_cloned",
                    repo.path,
                    url=repo.url,
                    status="failed",
                    error=str(e),
                )
            self.progress_tracker.update_progress(f"Failed: {repo.url}")

    async def sync_repos(self, repos: List[GitRepo]):
        if not repos:
            console.print("No repositories defined to sync.")
            return

        console.print(f"[bold]Syncing {len(repos)} git repositories...[/bold]")

        async def _sync_one_repo(repo):
            target_path = Path(os.path.expanduser(repo.path))
            if target_path.exists() and (target_path / ".git").exists():
                console.print(f"Syncing {repo.path}...")
                if self.dry_run:
                    console.print(f"[yellow]DRY RUN: Would push {target_path}[/yellow]")
                    return

                try:
                    # Check for uncommitted changes just to inform
                    status_proc = await asyncio.create_subprocess_exec(
                        "git",
                        "-C",
                        str(target_path),
                        "status",
                        "--porcelain",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, _ = await status_proc.communicate()

                    if stdout.strip():
                        console.print(
                            f"[yellow]Warning: {repo.path} has uncommitted changes.[/yellow]"
                        )

                    push_proc = await asyncio.create_subprocess_exec(
                        "git",
                        "-C",
                        str(target_path),
                        "push",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    _, stderr = await push_proc.communicate()

                    if push_proc.returncode == 0:
                        console.print(f"[green]Pushed {repo.path}[/green]")
                        self.logger.info(f"Pushed git repo: {repo.path}")
                    else:
                        console.print(
                            f"[red]Failed to push {repo.path}: {stderr.decode()}[/red]"
                        )
                        self.logger.error(
                            f"Failed to push {repo.path}: {stderr.decode()}"
                        )
                except Exception as e:
                    console.print(f"[red]Error syncing {repo.path}: {e}[/red]")
                    self.logger.error(f"Error syncing {repo.path}: {e}")
            else:
                console.print(f"[yellow]Skipping {repo.path}: Not a git repo[/yellow]")

        await asyncio.gather(*[_sync_one_repo(repo) for repo in repos])
