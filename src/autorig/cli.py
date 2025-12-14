import typer
from rich.console import Console
from .core import AutoRig

app = typer.Typer()
console = Console()

@app.command()
def apply(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate actions without making changes")
):
    """
    Apply a rig configuration to the local machine.
    """
    try:
        rig = AutoRig(config, dry_run=dry_run)
        rig.apply()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def clean(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate actions without making changes")
):
    """
    Remove symlinks created by the configuration.
    """
    try:
        rig = AutoRig(config, dry_run=dry_run)
        rig.clean()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def validate(config: str = typer.Argument(..., help="Path to rig.yaml config file")):
    """
    Validate a rig configuration file.
    """
    try:
        AutoRig(config)
        console.print(f"[bold green]Configuration file '{config}' is valid.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error validating configuration:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def backup(config: str = typer.Argument(..., help="Path to rig.yaml config file")):
    """
    Create a full backup archive of all dotfiles defined in the config.
    """
    try:
        rig = AutoRig(config)
        rig.backup()
    except Exception as e:
        console.print(f"[bold red]Error creating backup:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def restore(
    config: str = typer.Argument(..., help="Path to rig.yaml config file"),
    snapshot: str = typer.Argument(..., help="Path to the backup tarball to restore")
):
    """
    Restore dotfiles from a backup snapshot.
    """
    try:
        rig = AutoRig(config)
        rig.restore(snapshot)
    except Exception as e:
        console.print(f"[bold red]Error restoring backup:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def status(config: str = typer.Argument(..., help="Path to rig.yaml config file")):
    """
    Show the status of dotfiles and repositories.
    """
    try:
        rig = AutoRig(config)
        rig.status()
    except Exception as e:
        console.print(f"[bold red]Error checking status:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def diff(config: str = typer.Argument(..., help="Path to rig.yaml config file")):
    """
    Show differences between current system state and configuration.
    """
    try:
        rig = AutoRig(config)
        rig.diff()
    except Exception as e:
        console.print(f"[bold red]Error checking diff:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def rollback(config: str = typer.Argument(..., help="Path to rig.yaml config file")):
    """
    Rollback to the most recent backup snapshot.
    """
    try:
        rig = AutoRig(config)
        rig.rollback()
    except Exception as e:
        console.print(f"[bold red]Error rolling back:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def watch(config: str = typer.Argument(..., help="Path to rig.yaml config file")):
    """
    Monitor the config file and automatically apply changes when saved.
    """
    try:
        rig = AutoRig(config)
        rig.watch()
    except Exception as e:
        console.print(f"[bold red]Error watching config:[/bold red] {e}")
        raise typer.Exit(code=1)

def main():
    app()

if __name__ == "__main__":
    main()
