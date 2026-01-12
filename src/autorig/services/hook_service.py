import os
import subprocess
import shlex
import re
from typing import List, Optional
from rich.console import Console
from autorig.config import Script
from autorig.notifications import ProgressTracker
from autorig.state import OperationTracker
from logging import Logger

console = Console()


class HookService:
    def __init__(
        self,
        logger: Logger,
        progress_tracker: ProgressTracker,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        self.logger = logger
        self.progress_tracker = progress_tracker
        self.dry_run = dry_run
        self.verbose = verbose

    def run_hooks(self, hooks: List[Script]):
        """Run hooks (pre/post actions for different stages)."""
        if not hooks:
            return

        console.print(f"[bold]Running {len(hooks)} hook(s)...[/bold]")
        self.logger.info(f"Running {len(hooks)} hook(s)")

        for i, hook in enumerate(hooks, 1):
            desc = hook.description or hook.command
            console.print(f"[dim]Running hook {i}/{len(hooks)}: {desc}[/dim]")
            self.logger.debug(f"Running hook {i}/{len(hooks)}: {desc}")

            # Validate hook command before execution for security
            if not self._is_safe_command(hook.command):
                console.print(f"[red]✗ Unsafe command blocked: {hook.command}[/red]")
                self.logger.error(f"Unsafe command blocked: {hook.command}")
                continue

            cwd = os.path.expanduser(hook.cwd) if hook.cwd else None

            if self.dry_run:
                console.print(
                    f"[yellow]DRY RUN: Would execute hook: {hook.command}[/yellow]"
                )
                continue

            try:
                result = self._run_command_safely(hook.command, cwd=cwd)
                console.print(f"[green]✓ Hook completed: {desc}[/green]")
                if result.stdout:
                    if self.verbose:
                        console.print(f"[dim]Output: {result.stdout}[/dim]")
                    else:
                        console.print(
                            f"[dim]Output: {result.stdout[:200]}...[/dim]"
                            if len(result.stdout) > 200
                            else f"[dim]Output: {result.stdout}[/dim]"
                        )
                self.logger.info(f"Hook completed: {desc}")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]✗ Hook failed: {desc} ({e})[/red]")
                if e.stderr:
                    console.print(f"[red]Error: {e.stderr}[/red]")
                self.logger.error(f"Hook failed: {desc} - {e}")

    def run_scripts(
        self, scripts: List[Script], tracker: Optional[OperationTracker] = None
    ):
        if not scripts:
            self.logger.debug("No scripts to run")
            return

        console.print(f"[bold]Running {len(scripts)} post-install scripts...[/bold]")
        self.logger.info(f"Running {len(scripts)} post-install scripts")

        for i, script in enumerate(scripts, 1):
            desc = script.description or script.command
            console.print(f"[dim]Running script {i}/{len(scripts)}: {desc}[/dim]")
            self.logger.debug(f"Running script {i}/{len(scripts)}: {desc}")

            # Validate script command before execution for security
            if not self._is_safe_command(script.command):
                console.print(f"[red]✗ Unsafe command blocked: {script.command}[/red]")
                self.logger.error(f"Unsafe command blocked: {script.command}")
                if tracker:
                    tracker.record_change(
                        "blocked_unsafe_script", script.command, description=desc
                    )
                self.progress_tracker.update_progress(f"Blocked unsafe script: {desc}")
                continue

            cwd = os.path.expanduser(script.cwd) if script.cwd else None

            if self.dry_run:
                console.print(
                    f"[yellow]DRY RUN: Would execute: {script.command}[/yellow]"
                )
                if tracker:
                    tracker.record_change(
                        "would_execute_script",
                        script.command,
                        description=desc,
                        cwd=cwd,
                    )
                self.progress_tracker.update_progress(f"Dry run: {desc}")
                continue

            try:
                result = self._run_command_safely(script.command, cwd=cwd)
                console.print(f"[green]✓ Completed: {desc}[/green]")
                if result.stdout:
                    if self.verbose:
                        console.print(f"[dim]Output: {result.stdout}[/dim]")
                    else:
                        console.print(
                            f"[dim]Output: {result.stdout[:200]}...[/dim]"
                            if len(result.stdout) > 200
                            else f"[dim]Output: {result.stdout}[/dim]"
                        )
                self.logger.info(f"Script completed: {desc}")
                if tracker:
                    tracker.record_change(
                        "executed_script",
                        script.command,
                        description=desc,
                        status="success",
                        output=result.stdout[:500] if result.stdout else "",
                    )
                self.progress_tracker.update_progress(f"Completed: {desc}")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]✗ Failed: {desc} ({e})[/red]")
                if e.stderr:
                    console.print(f"[red]Error: {e.stderr}[/red]")
                self.logger.error(f"Script failed: {desc} - {e}")
                if tracker:
                    tracker.record_change(
                        "executed_script",
                        script.command,
                        description=desc,
                        status="failed",
                        error=str(e),
                        stderr=e.stderr if e.stderr else "",
                    )
                self.progress_tracker.update_progress(f"Failed: {desc}")

    def _run_command_safely(
        self, command: str, cwd: Optional[str] = None, capture_output: bool = True
    ):
        """
        Execute a command safely, avoiding shell=True when possible.
        """
        # Check for shell features that require shell=True
        shell_metachars = {"|", ">", "<", "&", ";", "$"}
        needs_shell = any(char in command for char in shell_metachars)

        if needs_shell:
            self.logger.debug(f"Command requires shell execution: {command}")
            return subprocess.run(
                command,
                shell=True,
                check=True,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
            )
        else:
            try:
                args = shlex.split(command)
                return subprocess.run(
                    args,
                    shell=False,
                    check=True,
                    cwd=cwd,
                    capture_output=capture_output,
                    text=True,
                )
            except ValueError as e:
                # Fallback if shlex fails to split (e.g. unbalanced quotes)
                self.logger.warning(
                    f"shlex split failed, falling back to shell=True: {e}"
                )
                return subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    cwd=cwd,
                    capture_output=capture_output,
                    text=True,
                )

    def _is_safe_command(self, command: str) -> bool:
        """
        Perform comprehensive security checks on a command before execution
        """
        # Check for dangerous patterns that could indicate command injection
        dangerous_patterns = [
            r"\|\|",  # command chaining
            r"&&",  # command chaining
            r";",  # command separation
            r"\$\(\( ",  # arithmetic expansion
            r"`",  # command substitution
            r"\$\(.*\)",  # command substitution
            r"eval\s",  # eval command
            r"exec\s",  # exec command
            r"source\s",  # source command
            r"bash\s+-c",  # bash command execution
            r"sh\s+-c",  # sh command execution
            r"python.*-c",  # python command execution
            r"perl.*-e",  # perl command execution
            r"ruby.*-e",  # ruby command execution
            r"import\s+os|import\s+sys|import\s+subprocess",  # Python imports in command
            r"rm\s+-rf",  # dangerous removal
            r"mv\s+/.*\s+/",  # dangerous move to system directories
            r"cp\s+/.*\s+/",  # dangerous copy to system directories
        ]

        # Convert to lowercase for broader pattern matching
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                self.logger.warning(
                    f"Blocked command with dangerous pattern: {pattern}"
                )
                return False

        # Additional validation: check for dangerous paths
        dangerous_paths = ["/etc", "/root", "/boot", "/sys", "/proc"]
        parts = command.split()
        for part in parts:
            # Remove quotes and normalize
            clean_part = part.strip("'\"")
            if any(clean_part.startswith(path) for path in dangerous_paths):
                self.logger.warning(
                    f"Blocked command with dangerous path: {clean_part}"
                )
                return False

        return True
