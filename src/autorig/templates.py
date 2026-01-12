"""
Template generator for common development setups.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import typer

console = Console()


class TemplateManager:
    """Manages configuration templates for different development setups."""

    TEMPLATES: Dict[str, Dict[str, Any]] = {
        "python": {
            "name": "Python Development Environment",
            "description": "Complete Python development setup with virtual environments, linting, and testing tools",
            "config": {
                "name": "Python Development Environment",
                "variables": {
                    "python_version": "3.11",
                    "email": "developer@example.com",
                    "editor": "code",
                    "venv_name": ".venv",
                },
                "system": {
                    "packages": [
                        "python3",
                        "python3-pip",
                        "python3-venv",
                        "git",
                        "curl",
                        "wget",
                        "build-essential",
                    ]
                },
                "git": {
                    "repositories": [
                        {
                            "url": "https://github.com/pre-commit/pre-commit-hooks.git",
                            "path": "~/.pre-commit-hooks",
                            "branch": "main",
                        }
                    ]
                },
                "dotfiles": [
                    {"source": "python/.gitignore.j2", "target": "~/.gitignore"},
                    {
                        "source": "python/.pre-commit-config.yaml",
                        "target": "~/.pre-commit-config.yaml",
                    },
                ],
                "scripts": [
                    {
                        "command": "python3 -m venv {{ venv_name }}",
                        "description": "Create Python virtual environment",
                    },
                    {
                        "command": "{{ venv_name }}/bin/pip install --upgrade pip",
                        "description": "Upgrade pip in virtual environment",
                    },
                    {
                        "command": "{{ venv_name }}/bin/pip install black flake8 isort mypy pytest pre-commit",
                        "description": "Install essential Python development tools",
                    },
                    {
                        "command": "git config --global init.templateDir ~/.git-template",
                        "description": "Set global git template directory",
                    },
                ],
            },
        },
        "web": {
            "name": "Web Development Environment",
            "description": "Modern web development setup with Node.js, React/Vue tools, and browser utilities",
            "config": {
                "name": "Web Development Environment",
                "variables": {
                    "email": "developer@example.com",
                    "node_version": "18",
                    "editor": "code",
                },
                "system": {
                    "packages": [
                        "git",
                        "curl",
                        "wget",
                        "nodejs",
                        "npm",
                        "python3",
                        "python3-pip",
                    ]
                },
                "git": {
                    "repositories": [
                        {
                            "url": "https://github.com/nvm-sh/nvm.git",
                            "path": "~/.nvm",
                            "branch": "master",
                        }
                    ]
                },
                "dotfiles": [
                    {"source": "web/.gitignore.j2", "target": "~/.gitignore"},
                    {"source": "web/.npmrc", "target": "~/.npmrc"},
                ],
                "scripts": [
                    {
                        "command": "npm install -g create-react-app @vue/cli typescript ts-node nodemon",
                        "description": "Install essential web development tools",
                    },
                    {
                        "command": "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash",
                        "description": "Install Node Version Manager",
                    },
                ],
            },
        },
        "golang": {
            "name": "Go Development Environment",
            "description": "Complete Go development setup with tools, linters, and common libraries",
            "config": {
                "name": "Go Development Environment",
                "variables": {
                    "email": "developer@example.com",
                    "go_version": "1.21",
                    "editor": "code",
                },
                "system": {"packages": ["git", "curl", "wget", "build-essential"]},
                "git": {
                    "repositories": [
                        {
                            "url": "https://github.com/golang/go.git",
                            "path": "~/go",
                            "branch": "master",
                        }
                    ]
                },
                "dotfiles": [
                    {"source": "go/.gitignore.j2", "target": "~/.gitignore"},
                    {"source": "go/.golangci.yml", "target": "~/.golangci.yml"},
                ],
                "scripts": [
                    {
                        "command": "wget -q https://go.dev/dl/go{{ go_version }}.linux-amd64.tar.gz",
                        "description": "Download Go binary",
                    },
                    {
                        "command": "sudo tar -C /usr/local -xzf go{{ go_version }}.linux-amd64.tar.gz",
                        "description": "Extract Go to /usr/local",
                    },
                    {
                        "command": "echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc",
                        "description": "Add Go to PATH",
                    },
                    {
                        "command": "go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest",
                        "description": "Install Go linter",
                    },
                ],
            },
        },
        "rust": {
            "name": "Rust Development Environment",
            "description": "Rust development setup with cargo, rust-analyzer, and common tools",
            "config": {
                "name": "Rust Development Environment",
                "variables": {"email": "developer@example.com", "editor": "code"},
                "system": {
                    "packages": [
                        "git",
                        "curl",
                        "build-essential",
                        "pkg-config",
                        "libssl-dev",
                    ]
                },
                "dotfiles": [
                    {"source": "rust/.gitignore.j2", "target": "~/.gitignore"}
                ],
                "scripts": [
                    {
                        "command": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
                        "description": "Install Rust via rustup",
                    },
                    {
                        "command": "source ~/.cargo/env && cargo install cargo-watch cargo-edit rust-analyzer",
                        "description": "Install essential Rust tools",
                    },
                ],
            },
        },
        "data-science": {
            "name": "Data Science Environment",
            "description": "Python data science setup with Jupyter, pandas, numpy, and ML libraries",
            "config": {
                "name": "Data Science Environment",
                "variables": {
                    "python_version": "3.11",
                    "email": "data-scientist@example.com",
                    "editor": "code",
                },
                "system": {
                    "packages": [
                        "python3",
                        "python3-pip",
                        "python3-venv",
                        "git",
                        "curl",
                        "wget",
                        "build-essential",
                        "python3-dev",
                    ]
                },
                "git": {"repositories": []},
                "dotfiles": [
                    {"source": "data-science/.gitignore.j2", "target": "~/.gitignore"},
                    {
                        "source": "data-science/.jupyter.j2",
                        "target": "~/.jupyter/jupyter_notebook_config.py",
                    },
                ],
                "scripts": [
                    {
                        "command": "python3 -m venv ds-env",
                        "description": "Create data science virtual environment",
                    },
                    {
                        "command": "ds-env/bin/pip install --upgrade pip",
                        "description": "Upgrade pip",
                    },
                    {
                        "command": "ds-env/bin/pip install jupyter pandas numpy matplotlib seaborn scikit-learn scipy plotly dash",
                        "description": "Install core data science libraries",
                    },
                    {
                        "command": "ds-env/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
                        "description": "Install PyTorch (CPU version)",
                    },
                ],
            },
        },
        "minimal": {
            "name": "Minimal Development Setup",
            "description": "Lightweight setup with just the essential tools for basic development",
            "config": {
                "name": "Minimal Development Setup",
                "variables": {"email": "developer@example.com"},
                "system": {"packages": ["git", "curl", "wget", "vim", "tmux"]},
                "git": {"repositories": []},
                "dotfiles": [
                    {"source": "minimal/.gitconfig.j2", "target": "~/.gitconfig"},
                    {"source": "minimal/.vimrc", "target": "~/.vimrc"},
                    {"source": "minimal/.tmux.conf", "target": "~/.tmux.conf"},
                ],
                "scripts": [
                    {
                        "command": "git config --global user.email '{{ email }}'",
                        "description": "Set git email",
                    }
                ],
            },
        },
    }

    @classmethod
    def list_templates(cls) -> None:
        """Display available templates in a formatted table."""
        table = Table(title="Available Templates", box=box.ROUNDED)
        table.add_column("Template", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("Description", style="dim")

        for template_id, template_info in cls.TEMPLATES.items():
            table.add_row(
                template_id,
                template_info["name"],
                (
                    template_info["description"][:80] + "..."
                    if len(template_info["description"]) > 80
                    else template_info["description"]
                ),
            )

        console.print(table)

    @classmethod
    def get_template(cls, template_name: str) -> Dict[str, Any]:
        """Get a specific template configuration."""
        if template_name not in cls.TEMPLATES:
            available = ", ".join(cls.TEMPLATES.keys())
            raise ValueError(
                f"Template '{template_name}' not found. Available: {available}"
            )

        return cls.TEMPLATES[template_name]["config"]

    @classmethod
    def create_config_from_template(
        cls,
        template_name: str,
        output_path: str,
        variables: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create a configuration file from a template."""
        import yaml

        template_config = cls.get_template(template_name)

        # Override template variables with user-provided ones
        if variables:
            template_config["variables"].update(variables)

        output_file = Path(output_path)

        if output_file.exists():
            if not typer.confirm(
                f"File {output_file} already exists. Overwrite?", default=False
            ):
                console.print("[yellow]Operation cancelled.[/yellow]")
                return

        try:
            with open(output_file, "w") as f:
                yaml.dump(template_config, f, default_flow_style=False, indent=2)

            console.print(f"[green]✅ Configuration created: {output_file}[/green]")
            console.print(f"[blue]📝 Template used: {template_name}[/blue]")

            # Show next steps
            console.print(
                Panel.fit(
                    f"""
                [bold yellow]Next Steps:[/bold yellow]
                
                1. Review and customize the configuration:
                   [dim]cat {output_file}[/dim]
                
                2. Apply the configuration:
                   [dim]autorig apply {output_file}[/dim]
                
                3. For dry run (preview changes):
                   [dim]autorig apply {output_file} --dry-run[/dim]
                """,
                    title="💡 What's Next?",
                    border_style="blue",
                )
            )

        except Exception as e:
            console.print(f"[red]Error creating configuration: {e}[/red]")
            raise typer.Exit(code=1)

    @classmethod
    def show_template_preview(cls, template_name: str) -> None:
        """Show a preview of a template configuration."""
        import yaml

        try:
            template_config = cls.get_template(template_name)
            template_info = cls.TEMPLATES[template_name]

            console.print(f"\n[bold blue]Template: {template_info['name']}[/bold blue]")
            console.print(f"[dim]{template_info['description']}[/dim]\n")

            # Show configuration preview
            console.print("[bold yellow]Configuration Preview:[/bold yellow]")

            # Summary of what will be installed
            config = template_config

            summary_data = {
                "System Packages": len(config.get("system", {}).get("packages", [])),
                "Git Repositories": len(config.get("git", {}).get("repositories", [])),
                "Dotfiles": len(config.get("dotfiles", [])),
                "Scripts": len(config.get("scripts", [])),
                "Variables": len(config.get("variables", {})),
            }

            for key, count in summary_data.items():
                if count > 0:
                    console.print(f"  • {key}: {count}")

            # Show detailed configuration
            console.print("\n[bold yellow]Full Configuration:[/bold yellow]")
            yaml_str = yaml.dump(template_config, default_flow_style=False, indent=2)
            console.print(yaml_str)

        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[red]Error showing template: {e}[/red]")
            raise typer.Exit(code=1)
