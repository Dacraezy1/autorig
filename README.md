# AutoRig 🚀 v1.0.0 - Major Release

**AutoRig** is a robust, data-driven system configuration and dotfile manager written in Python. It automates the setup of a development environment by installing system packages, managing git repositories, linking dotfiles, and running custom scripts. v1.0.0 introduces a comprehensive set of new features making it the most advanced configuration management tool available.

[![License](https://img.shields.io/github/license/Dacraezy1/autorig.svg)](https://github.com/Dacraezy1/autorig/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-informational.svg)](https://github.com/Dacraezy1/autorig)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)](https://github.com/Dacraezy1/autorig/releases/latest)

## ✨ Features

- **📦 System Package Management**: Automatically detects your OS (Linux/macOS/Windows) and package manager (`apt`, `dnf`, `yum`, `pacman`, `zypper`, `xbps`, `apk`, `brew`, `port`, `winget`, `choco`, `scoop`) to install specified packages.
- **🔗 Advanced Dotfile Management**: Safely manages your configuration files with advanced features:
  - **🎨 Jinja2 Templating**: Renders templates (`.j2`) with custom variables for dynamic configurations.
  - **💾 Automated Backups**: Creates full tarball snapshots of your dotfiles and provides easy restore capabilities.
  - **🛡️ Safe Operation**: Automatically backs up existing files with timestamps (e.g., `.bashrc.20231027-103000.bak`) and prevents unwanted overwrites.
- **🐙 Git Repository Management**: Clone repositories if missing, or pull updates if they exist.
- **⚡ Async & Parallel Execution**: Core operations now run asynchronously with parallel execution for git repositories, significantly speeding up applying configurations and syncing.
- **🐳 DevContainer Export**: Generate VS Code DevContainer configurations (`Dockerfile` + `devcontainer.json`) directly from your `rig.yaml`, automatically including your dotfiles.
- **⚡ Custom Script Execution**: Execute post-install shell commands (e.g., installing plugins, setting shell defaults).
- **🎭 Pre/Post Hooks System**: Execute custom scripts before and after major operations (system, git, dotfiles, scripts). Supports `pre_system`, `post_system`, `pre_git`, `post_git`, `pre_dotfiles`, `post_dotfiles`, `pre_scripts`, and `post_scripts` hooks.
- **🛡️ Dry Run Mode**: Preview all actions without making any changes to your system.
- **🔍 Inspection Tools**: View status, differences, and current state before applying changes.
- **🧹 Cleanup Utilities**: Easily remove symlinks created by the tool.
- **📝 Comprehensive Logging**: Detailed execution logs stored in `~/.autorig/logs/` for troubleshooting.
- **🔔 Notification System**: Desktop notifications for long-running operations on supported platforms (macOS, Linux, Windows).
- **📊 Progress Indicators**: Visual progress indicators and detailed logging with real-time tracking.
- **👀 Watch Mode**: Automatically apply changes when you save your configuration file.
- **🔐 Environment Integration**: Supports environment variable expansion (e.g., `${GITHUB_TOKEN}`) within configuration files.
- **🎯 Enhanced Profile Detection**: Automatic environment detection with expanded variables (VM, CI/CD, hardware specs, etc.) and intelligent recommendations.
- **🔌 Plugin Architecture**: Extensible plugin system for custom functionality.
- **🔧 Enhanced CLI**: More intuitive options and help text with `-n` (dry-run), `-v` (verbose), `-f` (force), `-p` (profile), `-d` (detailed detection), and `-o` (output) flags.
- **🛡️ Improved Security**: Enhanced validation and security checks for commands and file paths, now integrated into async execution paths for safer parallel operations.
- **🔄 Error Recovery & Rollback**: Automatic state tracking with rollback capabilities to revert changes on failure.
- **📈 Monitoring & Reporting**: Real-time resource monitoring and status reporting with system resource usage tracking.
- **📋 Configuration Schema Validation**: JSON schema validation for configuration files to catch errors early.

## 📋 Requirements

- **Operating Systems**: Linux, macOS, or Windows
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

Detect the current environment profile:

```bash
autorig detect
```

### Main Commands

#### Apply Configuration
Apply your configuration (install packages, link files, etc.):

```bash
autorig apply rig.yaml
```

Apply with a remote configuration:

```bash
autorig apply https://example.com/config.yaml
autorig apply github:username/repo/path/to/config.yaml  # GitHub shortcut
autorig apply github:username/repo/path/to/config.yaml@branch  # Specific branch
autorig apply gitlab:username/repo/path/to/config.yaml  # GitLab shortcut
```

Apply with a specific profile:

```bash
autorig apply rig.yaml --profile linux-x86_64-desktop
```

Preview actions without making changes:

```bash
autorig apply rig.yaml --dry-run
```

More verbose output:

```bash
autorig apply rig.yaml --verbose
```

Force operations that might overwrite existing files:

```bash
autorig apply rig.yaml --force
```

#### Sync Git Repositories
Push local changes in your configured git repositories to their remotes:

```bash
autorig sync rig.yaml
```

With dry run:

```bash
autorig sync rig.yaml --dry-run
```

#### Export DevContainer
Generate a VS Code DevContainer setup from your configuration:

```bash
autorig export devcontainer --config rig.yaml --output .
```

This will create a `.devcontainer` directory containing:
- `devcontainer.json`: Configured with your extensions and settings.
- `Dockerfile`: Based on a standard base image, installing your system packages.
- `dotfiles/`: A copy of your dotfiles to be automatically installed in the container.

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

#### Run Plugins
Execute specific plugins:

```bash
autorig run-plugins rig.yaml python-dev
```
See the [Plugins](#-plugins) section for available plugins and configuration.

#### Status Reporting
Generate comprehensive status reports for your configurations:

```bash
autorig report rig.yaml
autorig report rig.yaml --verbose  # Show detailed information
autorig report rig.yaml --output report.json  # Save to JSON file
```

#### Remote Configurations
Work with configurations hosted remotely:

```bash
# Direct URL
autorig apply https://example.com/config.yaml

# GitHub shortcut (downloads from raw GitHub content)
autorig apply github:username/repo/path/to/config.yaml
autorig apply github:username/repo/path/to/config.yaml@main  # Specific branch/tag

# GitLab shortcut (downloads from raw GitLab content)
autorig apply gitlab:username/repo/path/to/config.yaml

# Using the dedicated remote command
autorig remote https://example.com/config.yaml apply
autorig remote github:username/repo/path/to/config.yaml validate
autorig remote gitlab:username/repo/path/to/config.yaml status
```

#### Profile Detection
Detect and show the current system environment profile:

```bash
autorig detect
autorig detect --verbose  # Show detailed environment information
autorig detect --detailed  # Show comprehensive environment details with recommendations
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

# Pre/post hooks for different operations
hooks:
  pre_system:
    - command: "echo 'Starting system package installation'"
      description: "Log system installation start"
  post_system:
    - command: "sudo apt autoremove -y"
      description: "Clean up after package installation"
      when: "post"
  pre_dotfiles:
    - command: "mkdir -p ~/.backup"
      description: "Create backup directory"
  post_dotfiles:
    - command: "chmod 600 ~/.ssh/*"  # Secure SSH files after linking
      description: "Secure SSH files"
      when: "post"

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

# Pre/post hooks for different operations
hooks:
  # Execute before any system operations
  pre_system:
    - command: "echo 'Starting AutoRig system configuration on $(date)' > /tmp/autorig.log"
      description: "Log start time"
    - command: "free -h | grep '^Mem:' > /tmp/memory_usage.txt"
      description: "Record available memory"
  # Execute after system package installation
  post_system:
    - command: "sudo apt autoremove -y && sudo apt autoclean"
      description: "Clean up package cache"
    - command: "echo 'System packages installed at $(date)' >> /tmp/autorig.log"
      description: "Log completion time"
  # Execute before git operations
  pre_git:
    - command: "mkdir -p ~/Projects"
      description: "Create projects directory"
  # Execute after git operations
  post_git:
    - command: "chmod -R 700 ~/Projects/private"
      description: "Secure private projects"
  # Execute before dotfiles linking
  pre_dotfiles:
    - command: "mkdir -p ~/.config ~/.ssh ~/Documents"
      description: "Create necessary directories"
  # Execute after dotfiles linking
  post_dotfiles:
    - command: "chmod 600 ~/.ssh/*"
      description: "Secure SSH files"
    - command: "chmod 700 ~/.ssh"
      description: "Secure SSH directory"
  # Execute before running custom scripts
  pre_scripts:
    - command: "source ~/.zshrc || true"
      description: "Load shell environment"
  # Execute after running custom scripts
  post_scripts:
    - command: "echo 'Configuration applied successfully at $(date)' >> /tmp/autorig.log"
      description: "Log successful completion"

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

### Profile-Based Configuration Example
```yaml
name: "Development Environment with Profiles"

variables:
  email: "developer@example.com"
  username: "dev"

# Default system packages
system:
  packages:
    - git
    - vim
    - curl

# Profile-specific configurations
profiles:
  # Configuration for Linux desktop systems
  linux-x86_64-desktop:
    system:
      packages:
        - git
        - vim
        - curl
        - docker
        - docker-compose
        - code  # VS Code
        - flameshot  # Screenshot tool
    dotfiles:
      - source: "linux/.vimrc"
        target: "~/.vimrc"
      - source: "desktop/.Xresources"
        target: "~/.Xresources"

  # Configuration for macOS systems
  darwin-x86_64:
    system:
      packages:
        - git
        - vim
        - curl
        - rectangle  # Window management
        - iterm2
        - docker
    dotfiles:
      - source: "macos/.vimrc"
        target: "~/.vimrc"
      - source: "macos/.bash_profile"
        target: "~/.bash_profile"

  # Configuration for WSL (Windows Subsystem for Linux)
  linux-x86_64-wsl:
    system:
      packages:
        - git
        - vim
        - curl
        - docker.io
    dotfiles:
      - source: "wsl/.vimrc"
        target: "~/.vimrc"
      - source: "wsl/.wsl.conf"
        target: "/etc/wsl.conf"

scripts:
  - command: "echo 'Configuration applied for profile-dependent setup'"
    description: "Confirmation script"
```

## 🔌 Plugins

AutoRig supports a plugin architecture to extend its functionality.

### Python Dev Plugin (`python-dev`)
Sets up a Python development environment with a virtual environment and packages.

**Configuration Variables:**
- `python_version`: Version string (e.g., "3.9") - *currently informational in default plugin*
- `python_venv`: Name/Path of the virtual environment directory (default: `.venv`)
- `skip_venv`: Set to `true` to skip virtual environment creation
- `python_packages`: List of pip packages to install in the virtual environment

**Example Usage in `rig.yaml`:**
```yaml
variables:
  python_venv: ".dev_env"
  python_packages:
    - black
    - pytest
    - requests
```

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📖 Documentation

For detailed documentation, check out our [Documentation](docs/) directory.

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues and Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Dacraezy1/autorig/issues) on GitHub.