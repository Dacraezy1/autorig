# AutoRig

**AutoRig** is a robust, data-driven system configuration and dotfile manager written in Python. It automates the setup of a development environment by installing system packages, managing git repositories, linking dotfiles, and running custom scripts.

## Features

- **📦 System Packages**: Automatically detects your OS (Linux/macOS) and package manager (`apt`, `dnf`, `pacman`, `brew`) to install specified packages.
- **🔗 Dotfile Management**: Safely symlinks configuration files.
  - **🎨 Templating**: Renders Jinja2 templates (`.j2`) with custom variables.
  - **💾 Snapshots**: Create full tarball backups of your dotfiles and restore them later.
  - Automatically backs up existing files with timestamps (e.g., `.bashrc.20231027-103000.bak`).
  - Prevents overwriting unless necessary.
- **🐙 Git Operations**: Clones repositories if missing, or pulls updates if they exist.
- **⚡ Custom Scripts**: Execute post-install shell commands (e.g., installing plugins, setting shell defaults).
- **🛡️ Dry Run Mode**: Preview actions without making any changes to your system.
- **🔍 Diff & Status**: Inspect changes and current state before applying.
- **🧹 Clean Mode**: Easily remove symlinks created by the tool.
- **📝 Logging**: Detailed execution logs stored in `~/.autorig/logs/`.

## Installation

Requires Python 3.8+.

```bash
pip install .
```

## Usage

### Applying a Configuration

To apply your configuration (install packages, link files, etc.):

```bash
autorig apply rig.yaml
```

To preview what will happen without making changes:

```bash
autorig apply rig.yaml --dry-run
```

### Cleaning Up

To remove symlinks created by the configuration:

```bash
autorig clean rig.yaml
```

### Validating Config

To check if your YAML file is valid:

```bash
autorig validate rig.yaml
```

## Configuration (`rig.yaml`)

Create a YAML file to define your setup:

```yaml
name: "My Developer Setup"

system:
  packages:
    - vim
    - git
    - zsh
    - tmux

git:
  repositories:
    - url: "https://github.com/junegunn/fzf.git"
      path: "~/.fzf"
      branch: "master"

dotfiles:
  # 'source' is relative to the location of rig.yaml
  # 'target' is where the symlink will be created
  - source: "zsh/.zshrc"
    target: "~/.zshrc"
  - source: "vim/.vimrc"
    target: "~/.vimrc"

scripts:
  - command: "~/.fzf/install --all"
    description: "Install FZF bindings"
```