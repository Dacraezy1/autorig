import typer
from rich.console import Console
from .core import AutoRig

app = typer.Typer()
console = Console()

@app.command()
def apply(config: str = typer.Argument(..., help="Path to rig.yaml config file")):
    """
    Apply a rig configuration to the local machine.
    """
    try:
        rig = AutoRig(config)
        rig.apply()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

def main():
    app()

if __name__ == "__main__":
    main()
