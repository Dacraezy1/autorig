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
        rig = AutoRig(
            config, dry_run=dry_run, verbose=verbose, force=force, profile=profile
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
        rig = AutoRig(config, dry_run=dry_run, verbose=verbose, profile=profile)
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
        AutoRig(config, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, dry_run=dry_run, verbose=verbose, profile=profile)
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
        rig = AutoRig(config, dry_run=dry_run, verbose=verbose, profile=profile)
        rig.run_plugins(plugins)
    except Exception as e:
        console.print(f"[bold red]Error running plugins:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(
    help="Detect and show the current system environment profile.",
    short_help="Show environment profile",
)
def detect(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """
    Detect and show the current system environment profile.
    """
    from .profiles import EnvironmentDetector

    try:
        detector = EnvironmentDetector()
        profile_name = detector.get_profile_name()
        console.print(f"[bold green]Detected profile:[/bold green] {profile_name}")

        if verbose:
            console.print("\n[bold]Environment details:[/bold]")
            for key, value in detector.env_info.items():
                console.print(f"  [cyan]{key}:[/cyan] {value}")

    except Exception as e:
        console.print(f"[bold red]Error detecting environment:[/bold red] {e}")
        raise typer.Exit(code=1)


def main():
    app()


if __name__ == "__main__":
    main()
