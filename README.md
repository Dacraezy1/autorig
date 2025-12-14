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
- **👀 Watch Mode**: Automatically apply changes when you save `rig.yaml`.
- **🔐 Secrets**: Supports environment variable expansion (e.g., `${GITHUB_TOKEN}`) within the configuration file, processed via `os.path.expandvars`.
- **✅ Robust Testing**: Features a comprehensive suite of unit tests ensuring reliability and maintainability.

## Requirements

- **OS**: Linux or macOS
- **Python**: 3.9+
- **Git**: Installed on the system

## Installation

```bash
pip install .
```

## Usage

### Quick Start

Generate a default configuration file:

```bash
autorig bootstrap
```

### Applying a Configuration

To apply your configuration (install packages, link files, etc.):

```bash
autorig apply rig.yaml
```

To preview what will happen without making changes:

```bash
autorig apply rig.yaml --dry-run
```

### Syncing Repositories

Push local changes in your configured git repositories to their remotes:

```bash
autorig sync rig.yaml
```

### Checking Status & Diff

View the status of your links and repositories:

```bash
autorig status rig.yaml
```

See the difference between your current system files and the configuration (including rendered templates):

```bash
autorig diff rig.yaml
```

### Backup & Restore

Create a full compressed snapshot of your current dotfiles:

```bash
autorig backup rig.yaml
```

Restore files from a specific snapshot:

```bash
autorig restore rig.yaml ~/.autorig/backups/My_Setup_20231027-103000.tar.gz
```

Quickly rollback to the most recent snapshot:

```bash
autorig rollback rig.yaml
```

### Watch Mode

Automatically apply configuration whenever you save the file:

```bash
autorig watch rig.yaml
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

Create a YAML file to define your setup. You can use variables for Jinja2 templating.

```yaml
name: "My Developer Setup"

# Variables available in .j2 templates
variables:
  email: "user@example.com"
  theme: "dracula"

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
  # If source ends in .j2, it is rendered as a Jinja2 template using 'variables'
  # Example: gitconfig.j2 containing "email = {{ email }}"
  - source: "git/gitconfig.j2"
    target: "~/.gitconfig"

scripts:
  - command: "~/.fzf/install --all"
    description: "Install FZF bindings"
```