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

def main():
    app()

if __name__ == "__main__":
    main()
