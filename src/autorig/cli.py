from typing import List, Optional
from pathlib import Path
import os
import typer
from rich.console import Console
from rich.panel import Panel
from .core import AutoRig
from .cli_utils import (
    ErrorHandler, 
    EnhancedProgressTracker, 
    InfoDisplay, 
    confirm_action,
    validate_config_exists,
    format_duration,
    CommandTimer
)

app = typer.Typer(
    help="""
    AutoRig - A declarative development environment bootstrapper

    Automate the setup of your development environment by installing system packages,
    managing git repositories, linking dotfiles, and running custom scripts.
    """,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=True,
)

console = Console()


@app.command(hidden=True)
def completion(
    shell: str = typer.Argument(..., help="Shell type (bash, zsh, fish)"),
    install: bool = typer.Option(False, "--install", help="Install completion script"),
):
    """Generate shell completion script."""
    import platform
    
    if shell not in ["bash", "zsh", "fish"]:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        console.print("Supported shells: bash, zsh, fish")
        raise typer.Exit(code=1)
    
    try:
        # Generate completion script using typer's built-in functionality
        import os
        script_source = f"""
import typer
from autorig.cli import app

typer.main.get_completion(app, {shell!r})
"""
        
        if install:
            # Install based on shell and platform
            home_dir = Path.home()
            system = platform.system().lower()
            
            completion_file = None
            
            if shell == "bash":
                if system == "linux":
                    completion_file = home_dir / ".local" / "share" / "bash-completion" / "completions" / "autorig"
                else:  # macOS
                    completion_file = home_dir / ".bash_completion.d" / "autorig"
                    
            elif shell == "zsh":
                completion_file = home_dir / ".zsh" / "_autorig"
                
            elif shell == "fish":
                completion_file = home_dir / ".config" / "fish" / "completions" / "autorig.fish"
            
            if completion_file is None:
                console.print(f"[red]Unsupported platform for {shell} completion[/red]")
                raise typer.Exit(code=1)
            
            # Generate the completion script
            import subprocess
            result = subprocess.run(
                ["python3", "-c", script_source],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Create directory if needed
            completion_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write completion script
            completion_file.write_text(result.stdout)
            console.print(f"[green]✅ Completion installed to: {completion_file}[/green]")
            console.print(f"[yellow]💡 Restart your shell or run: source {completion_file}[/yellow]")
            
        else:
            # Generate and display the script
            import subprocess
            result = subprocess.run(
                ["python3", "-c", script_source],
                capture_output=True,
                text=True,
                check=True
            )
            console.print(result.stdout)
            
    except Exception as e:
        console.print(f"[red]Error generating completion: {e}[/red]")
        console.print(f"[yellow]💡 Try: eval \"$(autorig completion {shell})\"[/yellow]")
        raise typer.Exit(code=1)


def show_completion_installation_help():
    """Show help for installing shell completion."""
    console.print(Panel.fit(
        """
        [bold blue]Shell Completion Installation[/bold blue]
        
        [bold]Bash:[/bold]
          autorig completion bash --install
        
        [bold]Zsh:[/bold]
          autorig completion zsh --install
        
        [bold]Fish:[/bold]
          autorig completion fish --install
        
        Or generate the script and add it manually:
          autorig completion <shell> >> ~/.<shell>_completion.d/autorig
        """,
        title="💡 Tip",
        border_style="blue"
    ))


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
        import asyncio

        # Validate configuration exists
        config_path = validate_config_exists(config)
        
        # Show configuration preview
        if verbose:
            from .config import RigConfig
            config_data = RigConfig.from_yaml(str(config_path))
            InfoDisplay.show_configuration_preview(config_data.model_dump())
        
        # Confirm destructive operations unless in dry-run mode
        if not dry_run and not force:
            if not confirm_action(
                "This will modify your system. Do you want to continue?",
                default=False
            ):
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit(code=0)
        
        with CommandTimer("Configuration application"):
            local_config_path = resolve_config_path(config)
            rig = AutoRig(
                local_config_path,
                dry_run=dry_run,
                verbose=verbose,
                force=force,
                profile=profile,
            )
            asyncio.run(rig.apply())
            
        if dry_run:
            console.print(ErrorHandler.show_success(
                "Dry run completed successfully",
                "No changes were made to your system"
            ))
        else:
            console.print(ErrorHandler.show_success(
                "Configuration applied successfully",
                "Your development environment has been updated"
            ))
            
    except Exception as e:
        console.print(ErrorHandler.format_error(e, verbose))
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

        config_path = validate_config_exists(config)
        local_config_path = resolve_config_path(config)
        
        if not dry_run and not confirm_action(
            "This will remove symlinks created by the configuration. Continue?",
            default=False
        ):
            console.print("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit(code=0)
        
        rig = AutoRig(
            local_config_path, dry_run=dry_run, verbose=verbose, profile=profile
        )
        
        with CommandTimer("Cleanup operation"):
            rig.clean()
            
        console.print(ErrorHandler.show_success(
            "Cleanup completed successfully",
            "Symlinks have been removed"
        ))
        
    except Exception as e:
        console.print(ErrorHandler.format_error(e, verbose))
        raise typer.Exit(code=1)


@app.command(
    help="Generate a default rig.yaml configuration file.",
    short_help="Generate default config",
)
def bootstrap(
    path: str = typer.Option(
        "rig.yaml", "--path", "-p", help="Path to create configuration file"
    ),
    template: str = typer.Option(
        None, "--template", "-t", help="Use a predefined template (python, web, golang, rust, data-science, minimal)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """
    Generate a default rig.yaml configuration file.
    
    This creates a well-documented configuration file with examples
    that you can customize for your development environment.
    
    Use --template to start from a predefined template for specific development setups.
    """
    try:
        if template:
            # Use template system
            from .templates import TemplateManager
            
            if verbose:
                console.print(f"[blue]Using template: {template}[/blue]")
            
            TemplateManager.create_config_from_template(template, path)
        else:
            # Use original bootstrap
            AutoRig.create_default_config(path, verbose)
            console.print(
                f"[bold green]✅[/bold green] Configuration file created: [cyan]{path}[/cyan]"
            )
            console.print(
                "[dim]💡 Use 'autorig template list' to see available templates[/dim]"
            )
            console.print(
                "[dim]Edit the file to customize your development environment setup.[/dim]"
            )
            
    except Exception as e:
        console.print(ErrorHandler.format_error(e, verbose))
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
        import asyncio

        local_config_path = resolve_config_path(config)
        rig = AutoRig(
            local_config_path, dry_run=dry_run, verbose=verbose, profile=profile
        )
        asyncio.run(rig.sync_repos())
    except Exception as e:
        console.print(f"[bold red]Error syncing repos:[/bold red] {e}")
        raise typer.Exit(code=1)


# Template commands
template_app = typer.Typer(help="Manage configuration templates", name="template")
app.add_typer(template_app)


@template_app.command("list", help="List available configuration templates")
def list_templates():
    """List all available configuration templates."""
    from .templates import TemplateManager
    TemplateManager.list_templates()


@template_app.command("show", help="Show details of a specific template")
def show_template(
    name: str = typer.Argument(..., help="Template name to preview")
):
    """Show detailed information about a specific template."""
    from .templates import TemplateManager
    TemplateManager.show_template_preview(name)


@template_app.command("create", help="Create configuration from template")
def create_template_config(
    name: str = typer.Argument(..., help="Template name to use"),
    output: str = typer.Option(
        "rig.yaml", "--output", "-o", help="Output configuration file path"
    ),
    email: str = typer.Option(
        None, "--email", "-e", help="Email address (overrides template default)"
    ),
    editor: str = typer.Option(
        None, "--editor", help="Editor preference (overrides template default)"
    ),
):
    """Create a configuration file from a template."""
    from .templates import TemplateManager
    
    variables = {}
    if email:
        variables["email"] = email
    if editor:
        variables["editor"] = editor
    
    TemplateManager.create_config_from_template(name, output, variables)


@app.command(
    help="Generate VS Code DevContainer configuration.", short_help="Export DevContainer"
)
def export(
    format: str = typer.Argument(
        "devcontainer", help="Export format (currently only devcontainer supported)"
    ),
    config: str = typer.Option(
        "rig.yaml", "--config", "-c", help="Path to rig.yaml config file"
    ),
    output: str = typer.Option(
        ".", "--output", "-o", help="Output directory for exported files"
    ),
    profile: str = typer.Option(
        None, "--profile", "-p", help="Use a specific profile configuration"
    ),
):
    """Export configuration to different formats."""
    try:
        from .remote import resolve_config_path
        from .config import RigConfig
        from .exporters.devcontainer import DevContainerExporter

        local_config_path = resolve_config_path(config)
        exporter = DevContainerExporter(
            RigConfig.from_yaml(local_config_path, profile),
            local_config_path,
            output,
        )
        exporter.export()
    except Exception as e:
        from .cli_utils import ErrorHandler
        console.print(ErrorHandler.format_error(e))
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
    local_path = None
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
                raise ValueError(
                    "Invalid GitLab URL format. Use: gitlab:owner/repo/path/to/file[@ref]"
                )
        else:
            local_path = RemoteConfigManager.fetch_remote_config(url)
            
        if not local_path:
            raise ValueError(f"Failed to fetch remote configuration from: {url}")

        # Execute the requested command
        from .core import AutoRig
        import asyncio

        if command == "apply":
            rig = AutoRig(
                str(local_path),
                dry_run=dry_run,
                verbose=verbose,
                force=force,
                profile=profile,
            )
            asyncio.run(rig.apply())
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
            if local_path and os.path.exists(local_path):
                os.remove(local_path)
                console.print("[green]Cleaned up temporary configuration file[/green]")
        except OSError:
            pass  # Don't fail if cleanup fails

    except Exception as e:
        console.print(ErrorHandler.format_error(e, verbose))
        raise typer.Exit(code=1)





def main():
    app()


if __name__ == "__main__":
    main()
