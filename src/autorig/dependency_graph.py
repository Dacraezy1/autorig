"""Dependency graph visualization for AutoRig configurations."""

import json
from pathlib import Path
from typing import Dict, List

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from .config import RigConfig

console = Console()


class DependencyAnalyzer:
    """Analyzes and visualizes dependencies in AutoRig configurations."""

    def __init__(self, config: RigConfig):
        self.config = config
        self.dependencies = self._analyze_dependencies()

    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze dependencies between different configuration components."""
        deps: Dict[str, List[str]] = {
            "system": [],
            "git": [],
            "dotfiles": [],
            "scripts": [],
            "hooks": [],
        }

        # System packages dependencies
        if self.config.system.packages:
            deps["system"].extend(
                [f"package:{pkg}" for pkg in self.config.system.packages]
            )

        # Git repositories dependencies
        if self.config.git.repositories:
            deps["git"].extend(
                [f"repo:{repo.path}" for repo in self.config.git.repositories]
            )

        # Dotfiles dependencies
        if self.config.dotfiles:
            deps["dotfiles"].extend([df.source for df in self.config.dotfiles])

        # Scripts dependencies
        if self.config.scripts:
            deps["scripts"].extend(
                [
                    script.description or f"script:{i}"
                    for i, script in enumerate(self.config.scripts)
                ]
            )

        # Hooks dependencies
        hooks_deps = []
        if self.config.hooks.pre_system:
            hooks_deps.extend(
                [
                    f"pre_system:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.pre_system)
                ]
            )
        if self.config.hooks.post_system:
            hooks_deps.extend(
                [
                    f"post_system:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.post_system)
                ]
            )
        if self.config.hooks.pre_git:
            hooks_deps.extend(
                [
                    f"pre_git:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.pre_git)
                ]
            )
        if self.config.hooks.post_git:
            hooks_deps.extend(
                [
                    f"post_git:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.post_git)
                ]
            )
        if self.config.hooks.pre_dotfiles:
            hooks_deps.extend(
                [
                    f"pre_dotfiles:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.pre_dotfiles)
                ]
            )
        if self.config.hooks.post_dotfiles:
            hooks_deps.extend(
                [
                    f"post_dotfiles:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.post_dotfiles)
                ]
            )
        if self.config.hooks.pre_scripts:
            hooks_deps.extend(
                [
                    f"pre_scripts:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.pre_scripts)
                ]
            )
        if self.config.hooks.post_scripts:
            hooks_deps.extend(
                [
                    f"post_scripts:{hook.description or i}"
                    for i, hook in enumerate(self.config.hooks.post_scripts)
                ]
            )

        deps["hooks"] = hooks_deps
        return deps

    def generate_tree_view(self) -> Tree:
        """Generate a tree view of the configuration dependencies."""
        tree = Tree(f"[bold blue]{self.config.name}[/bold blue]")

        # Add main components
        system_node = tree.add("[green]System Packages[/green]")
        for dep in self.dependencies.get("system", []):
            system_node.add(f"[dim]{dep}[/dim]")

        git_node = tree.add("[green]Git Repositories[/green]")
        for dep in self.dependencies.get("git", []):
            git_node.add(f"[dim]{dep}[/dim]")

        dotfiles_node = tree.add("[green]Dotfiles[/green]")
        for dep in self.dependencies.get("dotfiles", []):
            dotfiles_node.add(f"[dim]{dep}[/dim]")

        scripts_node = tree.add("[green]Scripts[/green]")
        for dep in self.dependencies.get("scripts", []):
            scripts_node.add(f"[dim]{dep}[/dim]")

        hooks_node = tree.add("[green]Hooks[/green]")
        for dep in self.dependencies.get("hooks", []):
            hooks_node.add(f"[dim]{dep}[/dim]")

        return tree

    def generate_mermaid_graph(self) -> str:
        """Generate a Mermaid.js compatible graph."""
        lines = ["graph TD"]

        # Add main config node
        config_id = self._sanitize_id(self.config.name)
        lines.append(f"    {config_id}[{self.config.name}]")

        # Add component nodes and connections
        components = ["system", "git", "dotfiles", "scripts", "hooks"]
        for component in components:
            if self.dependencies.get(component, []):
                comp_id = self._sanitize_id(component)
                lines.append(f"    {comp_id}[{component.title()}]")
                lines.append(f"    {config_id} --> {comp_id}")

                # Add dependencies
                for i, dep in enumerate(self.dependencies[component]):
                    dep_id = f"{comp_id}_{i}"
                    lines.append(f"    {dep_id}[{dep}]")
                    lines.append(f"    {comp_id} --> {dep_id}")

        return "\n".join(lines)

    def _sanitize_id(self, text: str) -> str:
        """Sanitize text to be a valid Mermaid ID."""
        return "".join(c if c.isalnum() else "_" for c in text)

    def export_to_file(self, filepath: str, format: str = "json") -> None:
        """Export dependency graph to a file."""
        path = Path(filepath)

        if format == "json":
            data = {"config_name": self.config.name, "dependencies": self.dependencies}
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        elif format == "mermaid":
            with open(path, "w") as f:
                f.write(self.generate_mermaid_graph())
        else:
            raise ValueError(f"Unsupported format: {format}")

    def print_summary(self) -> None:
        """Print a summary of the dependency analysis."""
        table = Table(title="Dependency Analysis Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Dependencies", style="magenta")
        table.add_column("Count", style="green")

        for component, deps in self.dependencies.items():
            table.add_row(
                component.title(),
                ", ".join(deps[:3]) + ("..." if len(deps) > 3 else ""),
                str(len(deps)) if deps else "None",
            )

        console.print(table)
