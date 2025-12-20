from typing import List
import typer
from rich.console import Console
from .core import AutoRig

app = typer.Typer(
    help="""
    AutoRig - A declarative development environment bootstrapper

    Automate the setup of your development environment by installing system packages,
    managing git repositories, linking dotfiles, and running custom scripts.
    """,
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()


@app.command(
    help="Apply a rig configuration to the local machine.",
    short_help="Apply a rig configuration",
)
def apply(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Simulate actions without making changes"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force operations that might overwrite existing files",
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Apply a rig configuration to the local machine.

    This command will:
    - Install system packages using the appropriate package manager
    - Clone or update git repositories
    - Link dotfiles with optional Jinja2 templating
    - Execute custom post-install scripts
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(
            local_config_path,
            dry_run=dry_run,
            verbose=verbose,
            force=force,
            profile=profile,
        )
        rig.apply()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Remove symlinks created by the configuration.", short_help="Remove symlinks"
)
def clean(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Simulate actions without making changes"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Remove symlinks created by the configuration.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(
            local_config_path, dry_run=dry_run, verbose=verbose, profile=profile
        )
        rig.clean()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Validate a rig configuration file.", short_help="Validate configuration"
)
def validate(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Validate a rig configuration file.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        AutoRig(local_config_path, verbose=verbose, profile=profile)
        console.print(
            f"[bold green]Configuration file '{config}' is valid.[/bold green]"
        )
    except Exception as e:
        console.print(f"[bold red]Error validating configuration:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Create a full backup archive of all dotfiles defined in the config.",
    short_help="Backup dotfiles",
)
def backup(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Create a full backup archive of all dotfiles defined in the config.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(local_config_path, verbose=verbose, profile=profile)
        rig.backup()
    except Exception as e:
        console.print(f"[bold red]Error creating backup:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Restore dotfiles from a backup snapshot.", short_help="Restore from backup"
)
def restore(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    snapshot: str = typer.Argument(..., help="Path to the backup tarball to restore"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Restore dotfiles from a backup snapshot.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(local_config_path, verbose=verbose, profile=profile)
        rig.restore(snapshot)
    except Exception as e:
        console.print(f"[bold red]Error restoring backup:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Show the status of dotfiles and repositories.", short_help="Show status"
)
def status(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Show the status of dotfiles and repositories.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(local_config_path, verbose=verbose, profile=profile)
        rig.status()
    except Exception as e:
        console.print(f"[bold red]Error checking status:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Show differences between current system state and configuration.",
    short_help="Show diff",
)
def diff(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Show differences between current system state and configuration.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(local_config_path, verbose=verbose, profile=profile)
        rig.diff()
    except Exception as e:
        console.print(f"[bold red]Error checking diff:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Rollback to the most recent backup snapshot.",
    short_help="Rollback to latest backup",
)
def rollback(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Rollback to the most recent backup snapshot.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(local_config_path, verbose=verbose, profile=profile)
        rig.rollback()
    except Exception as e:
        console.print(f"[bold red]Error rolling back:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Monitor the config file and automatically apply changes when saved.",
    short_help="Watch config file",
)
def watch(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Monitor the config file and automatically apply changes when saved.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(local_config_path, verbose=verbose, profile=profile)
        rig.watch()
    except Exception as e:
        console.print(f"[bold red]Error watching config:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Generate a default rig.yaml configuration file.",
    short_help="Create default config",
)
def bootstrap(
    path: str = typer.Argument("rig.yaml", help="Path to generate the config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Generate a default rig.yaml configuration file.
    """
    try:
        AutoRig.create_default_config(path, verbose=verbose)
    except Exception as e:
        console.print(f"[bold red]Error bootstrapping:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Push local changes in git repositories to remotes.",
    short_help="Sync git repositories",
)
def sync(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Simulate actions without making changes"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Push local changes in git repositories to remotes.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(
            local_config_path, dry_run=dry_run, verbose=verbose, profile=profile
        )
        rig.sync_repos()
    except Exception as e:
        console.print(f"[bold red]Error syncing repos:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Run specific plugins defined in the configuration.",
    short_help="Run specific plugins",
)
def run_plugins(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    plugins: List[str] = typer.Argument(..., help="Names of plugins to run"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Simulate actions without making changes"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Run specific plugins defined in the configuration.
    """
    try:
        from .remote import resolve_config_path

        local_config_path = resolve_config_path(config)
        rig = AutoRig(
            local_config_path, dry_run=dry_run, verbose=verbose, profile=profile
        )
        rig.run_plugins(plugins)
    except Exception as e:
        console.print(f"[bold red]Error running plugins:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Detect and show the current system environment profile.",
    short_help="Show environment profile",
)
def detect(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed environment information"
    ),
):
    """
    Detect and show the current system environment profile.
    """
    from .profiles import EnvironmentDetector

    try:
        detector = EnvironmentDetector()
        profile_name = detector.get_profile_name()
        console.print(f"[bold green]Detected profile:[/bold green] {profile_name}")

        if verbose or detailed:
            console.print("\n[bold]Environment details:[/bold]")
            for key, value in detector.env_info.items():
                console.print(f"  [cyan]{key}:[/cyan] {value}")

        if detailed:
            console.print("\n[bold]Recommendations based on environment:[/bold]")
            # Provide recommendations based on detected environment
            if detector.env_info.get("is_wsl", False):
                console.print(
                    "  [yellow]WSL detected:[/yellow] Consider installing Windows-specific tools via WSL interop"
                )
            if detector.env_info.get("is_docker", False):
                console.print(
                    "  [yellow]Docker container detected:[/yellow] Some system operations may be limited"
                )
            if detector.env_info.get("is_vm", False):
                console.print(
                    "  [yellow]Virtual machine detected:[/yellow] Graphics acceleration may be limited"
                )
            if detector.env_info.get("is_ci", False):
                console.print(
                    "  [yellow]CI/CD environment detected:[/yellow] Non-interactive mode recommended"
                )
            if detector.env_info.get("memory_gb", 0) < 4:
                console.print(
                    "  [yellow]Low memory detected:[/yellow] Consider lighter-weight packages"
                )
            if detector.env_info.get("cpu_cores", 0) < 2:
                console.print(
                    "  [yellow]Limited CPU cores:[/yellow] Some parallel operations may be slow"
                )

    except Exception as e:
        console.print(f"[bold red]Error detecting environment:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Generate a status report for the current configuration.",
    short_help="Generate status report",
)
def report(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
    output: str = typer.Option(
        None, "--output", "-o", help="Output file for the report (JSON format)"
    ),
):
    """
    Generate a status report for the current configuration.
    """
    try:
        from .core import AutoRig
        from .monitoring import StatusReporter
        from .remote import resolve_config_path

        # Resolve remote config path if needed
        local_config_path = resolve_config_path(config)

        # Create a rig instance to access the config
        rig = AutoRig(local_config_path, verbose=verbose, profile=profile)

        # Create and show the status report
        reporter = StatusReporter(rig.config, console)
        reporter.report_status(show_resources=not verbose, show_config=True)

        # Save to file if requested
        if output:
            reporter.save_report(output)

    except Exception as e:
        console.print(f"[bold red]Error generating report:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Download and work with remote configurations (GitHub, GitLab, HTTP).",
    short_help="Work with remote configs",
)
def remote(
    url: str = typer.Argument(..., help="URL to remote configuration file"),
    command: str = typer.Argument(
        "apply", help="Command to execute (apply, validate, status, etc.)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Simulate actions without making changes"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force operations that might overwrite existing files",
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """
    Download and work with remote configurations (GitHub, GitLab, HTTP).
    """
    try:
        from .remote import RemoteConfigManager
        import os

        console.print(f"[blue]Fetching remote configuration:[/blue] {url}")

        # Handle special GitHub/GitLab shortcuts
        if url.startswith("github:"):
            # Format: github:owner/repo/path/to/config.yaml[@ref]
            parts = url[7:].split("/")  # Remove 'github:' prefix
            if len(parts) >= 3:
                owner = parts[0]
                repo = parts[1]
                path_parts = parts[2:]

                # Check if there's a @ref at the end
                path = "/".join(path_parts)
                ref = "main"  # default
                if "@" in path:
                    path, ref = path.rsplit("@", 1)

                local_path = RemoteConfigManager.fetch_from_github(
                    owner, repo, path, ref
                )
            else:
                raise ValueError(
                    "Invalid GitHub URL format. Use: github:owner/repo/path/to/file[@ref]"
                )
        elif url.startswith("gitlab:"):
            # Format: gitlab:owner/repo/path/to/config.yaml[@ref]
            parts = url[7:].split("/")  # Remove 'gitlab:' prefix
            if len(parts) >= 3:
                owner = parts[0]
                repo = parts[1]
                path_parts = parts[2:]

                # Check if there's a @ref at the end
                path = "/".join(path_parts)
                ref = "main"  # default
                if "@" in path:
                    path, ref = path.rsplit("@", 1)

                local_path = RemoteConfigManager.fetch_from_gitlab(
                    owner, repo, path, ref
                )
        else:
            local_path = RemoteConfigManager.fetch_remote_config(url)

        # Execute the requested command
        from .core import AutoRig

        if command == "apply":
            rig = AutoRig(
                str(local_path),
                dry_run=dry_run,
                verbose=verbose,
                force=force,
                profile=profile,
            )
            rig.apply()
        elif command == "validate":
            AutoRig(str(local_path), verbose=verbose, profile=profile)
            console.print(
                f"[bold green]Configuration file '{url}' is valid.[/bold green]"
            )
        elif command == "status":
            rig = AutoRig(str(local_path), verbose=verbose, profile=profile)
            rig.status()
        elif command == "diff":
            rig = AutoRig(str(local_path), verbose=verbose, profile=profile)
            rig.diff()
        else:
            console.print(f"[red]Unsupported command: {command}[/red]")
            raise typer.Exit(code=1)

        # Clean up temporary file after successful operation
        try:
            os.remove(local_path)
            console.print("[green]Cleaned up temporary configuration file[/green]")
        except OSError:
            pass  # Don't fail if cleanup fails

    except Exception as e:
        console.print(f"[bold red]Error with remote config:[/bold red] {e}")
        raise typer.Exit(code=1)


def main():
    app()


if __name__ == "__main__":
    main()
