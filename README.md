# AutoRig 🚀

**AutoRig** is a robust, data-driven system configuration and dotfile manager written in Python. It automates the setup of a development environment by installing system packages, managing git repositories, linking dotfiles, and running custom scripts.

[![License](https://img.shields.io/github/license/Dacraezy1/autorig.svg)](https://github.com/Dacraezy1/autorig/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-informational.svg)](https://github.com/Dacraezy1/autorig)

## ✨ Features

- **📦 System Package Management**: Automatically detects your OS (Linux/macOS) and package manager (`apt`, `dnf`, `pacman`, `brew`) to install specified packages.
- **🔗 Advanced Dotfile Management**: Safely manages your configuration files with advanced features:
  - **🎨 Jinja2 Templating**: Renders templates (`.j2`) with custom variables for dynamic configurations.
  - **💾 Automated Backups**: Creates full tarball snapshots of your dotfiles and provides easy restore capabilities.
  - **🛡️ Safe Operation**: Automatically backs up existing files with timestamps (e.g., `.bashrc.20231027-103000.bak`) and prevents unwanted overwrites.
- **🐙 Git Repository Management**: Clone repositories if missing, or pull updates if they exist.
- **⚡ Custom Script Execution**: Execute post-install shell commands (e.g., installing plugins, setting shell defaults).
- **🛡️ Dry Run Mode**: Preview all actions without making any changes to your system.
- **🔍 Inspection Tools**: View status, differences, and current state before applying changes.
- **🧹 Cleanup Utilities**: Easily remove symlinks created by the tool.
- **📝 Comprehensive Logging**: Detailed execution logs stored in `~/.autorig/logs/` for troubleshooting.
- **👀 Watch Mode**: Automatically apply changes when you save your configuration file.
- **🔐 Environment Integration**: Supports environment variable expansion (e.g., `${GITHUB_TOKEN}`) within configuration files.

## 📋 Requirements

- **Operating Systems**: Linux or macOS
- **Python Version**: 3.9 or higher
- **Git**: Installed and available in your system PATH

## 🚀 Installation

### From Source
```bash
git clone https://github.com/Dacraezy1/autorig.git
cd autorig
pip install -e .
```

### Using pipx (Recommended)
```bash
pipx install git+https://github.com/Dacraezy1/autorig.git
```

### Install Local Development Version
```bash
# Inside the cloned repository
pip install -e .
```

## 🔧 Usage

### Quick Start

Generate a default configuration file:

```bash
autorig bootstrap
```

### Main Commands

#### Apply Configuration
Apply your configuration (install packages, link files, etc.):

```bash
autorig apply rig.yaml
```

Preview actions without making changes:

```bash
autorig apply rig.yaml --dry-run
```

#### Sync Git Repositories
Push local changes in your configured git repositories to their remotes:

```bash
autorig sync rig.yaml
```

#### Status & Inspection
View the status of your links and repositories:

```bash
autorig status rig.yaml
```

See differences between current system files and configuration (including rendered templates):

```bash
autorig diff rig.yaml
```

#### Backup & Restore
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

#### Watch Mode
Automatically apply configuration when you save the file:

```bash
autorig watch rig.yaml
```

#### Cleanup
Remove symlinks created by the configuration:

```bash
autorig clean rig.yaml
```

#### Validation
Check if your YAML file is valid:

```bash
autorig validate rig.yaml
```

## ⚙️ Configuration (`rig.yaml`)

Create a YAML file to define your development environment setup. You can use variables for Jinja2 templating.

### Basic Configuration Example
```yaml
name: "My Developer Setup"

# Variables available in .j2 templates
variables:
  email: "user@example.com"
  username: "developer"
  theme: "dracula"
  editor: "nvim"

system:
  packages:
    # Essential tools
    - git
    - vim
    - curl
    - wget
    - htop
    - tmux
    # Development tools
    - nodejs
    - python3
    - docker

git:
  repositories:
    - url: "https://github.com/junegunn/fzf.git"
      path: "~/.fzf"
      branch: "master"
    - url: "https://github.com/ohmyzsh/ohmyzsh.git"
      path: "~/.oh-my-zsh"
      branch: "master"

dotfiles:
  # 'source' is relative to the location of rig.yaml
  # 'target' is where the symlink will be created
  - source: "shell/.zshrc"
    target: "~/.zshrc"
  - source: "shell/.bashrc"
    target: "~/.bashrc"
  - source: "editor/.vimrc"
    target: "~/.vimrc"
  # If source ends in .j2, it is rendered as a Jinja2 template using 'variables'
  # Example: gitconfig.j2 containing "email = {{ email }}"
  - source: "git/gitconfig.j2"
    target: "~/.gitconfig"
  - source: "tmux/tmux.conf"
    target: "~/.tmux.conf"

scripts:
  - command: "~/.fzf/install --all"
    description: "Install FZF bindings"
  - command: "git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.powerlevel10k"
    description: "Install Powerlevel10k Zsh theme"
    condition: "zsh"
  - command: "pip3 install --user powerline-status"
    description: "Install Powerline for status bar"
```

### Advanced Configuration Example
```yaml
name: "Developer Workstation Setup"

variables:
  email: "developer@example.com"
  git_user: "John Doe"
  theme_color: "gruvbox"
  editor: "nvim"

system:
  packages:
    # System utilities
    - git
    - curl
    - wget
    - htop
    - tmux
    - zsh

    # Development
    - nodejs
    - python3
    - python3-pip
    - docker
    - docker-compose
    - make
    - gcc

    # Text editing
    - vim
    - neovim
    - jq

    # Network tools
    - nmap
    - ncdu
    - tree

git:
  repositories:
    - url: "https://github.com/ohmyzsh/ohmyzsh.git"
      path: "~/.oh-my-zsh"
      branch: "master"
    - url: "https://github.com/romkatv/powerlevel10k.git"
      path: "~/.powerlevel10k"
      branch: "master"
    - url: "https://github.com/junegunn/fzf.git"
      path: "~/.fzh"
      branch: "master"

dotfiles:
  # Shell configuration
  - source: "shell/.zshrc"
    target: "~/.zshrc"

  # Vim configuration
  - source: "editor/.vimrc"
    target: "~/.vimrc"
  - source: "editor/nvim/init.vim"
    target: "~/.config/nvim/init.vim"

  # Git configuration (with templating)
  - source: "git/.gitconfig.j2"
    target: "~/.gitconfig"

  # Terminal configuration
  - source: "terminal/alacritty.yml"
    target: "~/.config/alacritty/alacritty.yml"
  - source: "terminal/kitty.conf"
    target: "~/.config/kitty/kitty.conf"

scripts:
  # Install Oh My Zsh
  - command: "sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\" \"\" --unattended"
    description: "Install Oh My Zsh"
    condition: "!test -d ~/.oh-my-zsh"

  # Install FZF
  - command: "~/.fzf/install --all"
    description: "Install FZF key bindings and fuzzy completion"

  # Install Python tools
  - command: "pip3 install --user black flake8 isort mypy"
    description: "Install Python development tools"

  # Configure Git globally
  - command: "git config --global user.email \"${email}\""
    description: "Configure Git email"
  - command: "git config --global user.name \"${git_user}\""
    description: "Configure Git username"
```

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📖 Documentation

For detailed documentation, check out our [Documentation](docs/) directory.

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues and Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Dacraezy1/autorig/issues) on GitHub.