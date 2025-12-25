import os
import json
import shutil
from pathlib import Path
from ..config import RigConfig
from ..templating import TemplateRenderer


class DevContainerExporter:
    """
    Exports the current configuration to a VS Code DevContainer setup.
    """

    def __init__(self, config: RigConfig, config_path: str, output_dir: str):
        self.config = config
        self.config_path = config_path
        self.output_dir = Path(output_dir)
        self.devcontainer_dir = self.output_dir / ".devcontainer"
        self.dotfiles_src_dir = self.devcontainer_dir / "dotfiles"

        # Determine the directory where the original config lives, for resolving relative paths
        self.original_config_dir = Path(config_path).parent.absolute()
        self.renderer = TemplateRenderer(self.original_config_dir)

    def export(self):
        """Generates the .devcontainer folder and contents."""
        self.devcontainer_dir.mkdir(parents=True, exist_ok=True)

        # 1. Prepare dotfiles (render and copy to build context)
        self._prepare_dotfiles()

        # 2. Generate Dockerfile
        self._create_dockerfile()

        # 3. Generate devcontainer.json
        self._create_devcontainer_json()

        print(f"Exported DevContainer to {self.devcontainer_dir}")

    def _prepare_dotfiles(self):
        """
        Copies referenced dotfiles to .devcontainer/dotfiles/, preserving relative structure.
        Renders Jinja2 templates to static files.
        """
        if self.dotfiles_src_dir.exists():
            shutil.rmtree(self.dotfiles_src_dir)
        self.dotfiles_src_dir.mkdir()

        for df in self.config.dotfiles:
            # Source path (original file)
            source_abs = (
                self.original_config_dir / os.path.expanduser(df.source)
            ).resolve()

            # Target path (where it goes in the system, e.g. ~/.config/nvim/init.vim)
            target_expanded = os.path.expanduser(df.target)

            # We want to map "~/" to "dotfiles/"
            # e.g. "~/.bashrc" -> "dotfiles/.bashrc"
            # e.g. "/etc/conf" -> "dotfiles/etc/conf" (might be tricky, stick to home for now)

            if target_expanded.startswith(str(Path.home())):
                # Strip home dir prefix
                rel_path = str(Path(target_expanded).relative_to(Path.home()))
            elif target_expanded.startswith("~"):
                rel_path = target_expanded[2:]
            else:
                # Absolute path elsewhere, place in root of dotfiles for manual handling or skip
                # For simplicity, we'll try to mirror it under dotfiles/root/...
                rel_path = target_expanded.lstrip("/")

            dest_path = self.dotfiles_src_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if not source_abs.exists():
                print(f"Warning: Source file {source_abs} not found. Skipping.")
                continue

            if source_abs.suffix == ".j2":
                # Render to destination
                try:
                    rel_source = source_abs.relative_to(self.original_config_dir)
                    self.renderer.render(
                        str(rel_source), self.config.variables, dest_path
                    )
                except Exception as e:
                    print(f"Error rendering {source_abs}: {e}")
            else:
                # Copy file
                if source_abs.is_dir():
                    shutil.copytree(source_abs, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_abs, dest_path)

    def _create_dockerfile(self):
        packages = " ".join(self.config.system.packages)

        dockerfile_content = [
            "FROM mcr.microsoft.com/devcontainers/base:ubuntu",
            "",
            "USER root",
            "",
            "# Install system packages",
            "RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \\",
            f"    && apt-get -y install --no-install-recommends {packages}",
            "",
            "# Clean up",
            "RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*",
            "",
        ]

        # Git Repos
        if self.config.git.repositories:
            dockerfile_content.append("# Clone Git repositories")
            # We assume cloning into /workspaces or home.
            # If path is ~, we map to /home/vscode
            for repo in self.config.git.repositories:
                target_path = repo.path.replace("~", "/home/vscode").replace(
                    "$HOME", "/home/vscode"
                )
                # Ensure parent dir exists
                parent_dir = str(Path(target_path).parent)
                dockerfile_content.append(f"RUN mkdir -p {parent_dir} \\")
                dockerfile_content.append(
                    f"    && git clone -b {repo.branch or 'main'} {repo.url} {target_path} \\"
                )
                dockerfile_content.append(
                    f"    && chown -R vscode:vscode {target_path}"
                )
            dockerfile_content.append("")

        # Copy Dotfiles
        # We copy everything from dotfiles/ to /home/vscode/
        # Check if we have anything to copy
        if any(self.dotfiles_src_dir.iterdir()):
            dockerfile_content.append("# Apply Dotfiles")
            dockerfile_content.append("COPY dotfiles/ /home/vscode/")
            dockerfile_content.append("RUN chown -R vscode:vscode /home/vscode")
            dockerfile_content.append("")

        # Scripts
        # We run them as vscode user usually, but some might need root.
        # For safety/simplicity in export, we'll run them as vscode if they look like user scripts.
        if self.config.scripts:
            dockerfile_content.append("# Custom Scripts")
            dockerfile_content.append("USER vscode")
            for script in self.config.scripts:
                # Minimal escaping. This is best-effort.
                cmd = script.command.replace('"', '"')
                dockerfile_content.append(f"RUN {cmd}")
            dockerfile_content.append(
                "USER root"
            )  # Revert to root for end of file if needed
            dockerfile_content.append("")

        with open(self.devcontainer_dir / "Dockerfile", "w") as f:
            f.write("\n".join(dockerfile_content))

    def _create_devcontainer_json(self):
        content = {
            "name": self.config.name,
            "build": {"dockerfile": "Dockerfile", "context": "."},
            "features": {
                "ghcr.io/devcontainers/features/common-utils:2": {
                    "installZsh": "true",
                    "username": "vscode",
                    "uid": "1000",
                    "gid": "1000",
                    "upgradePackages": "true",
                }
            },
            "remoteUser": "vscode",
        }

        with open(self.devcontainer_dir / "devcontainer.json", "w") as f:
            json.dump(content, f, indent=4)
