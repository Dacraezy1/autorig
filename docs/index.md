# AutoRig Documentation

AutoRig is a powerful, declarative development environment bootstrapper written in Python. It automates the setup of your development environment by installing system packages, managing git repositories, linking dotfiles, and running custom scripts.

This project is maintained by [Dacraezy1](https://github.com/Dacraezy1) at [younesaouzal18@gmail.com](mailto:younesaouzal18@gmail.com).

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [CLI Commands](#cli-commands)
- [Plugins](#plugins)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.9+
- Git
- Operating System: Linux, macOS, or Windows

### Installing AutoRig

```bash
# From source
git clone https://github.com/Dacraezy1/autorig.git
cd autorig
pip install -e .

# Using pipx (recommended)
pipx install git+https://github.com/Dacraezy1/autorig.git

# Install local development version
pip install -e .
```

## Getting Started

### Bootstrap a Configuration

Generate a default configuration file:

```bash
autorig bootstrap
```

This creates a `rig.yaml` file with basic configuration.

### Apply Configuration

To apply your configuration:

```bash
autorig apply rig.yaml
```

To see what would happen without making changes:

```bash
autorig apply rig.yaml --dry-run
```

## Configuration

The configuration file (`rig.yaml`) defines your development environment setup using YAML format.

### Basic Structure

```yaml
name: "My Developer Setup"

variables:
  email: "user@example.com"
  username: "developer"

system:
  packages:
    - git
    - vim
    - curl

git:
  repositories:
    - url: "https://github.com/ohmyzsh/ohmyzsh.git"
      path: "~/.oh-my-zsh"
      branch: "master"

dotfiles:
  - source: ".zshrc"
    target: "~/.zshrc"
  - source: ".gitconfig.j2"
    target: "~/.gitconfig"

scripts:
  - command: "sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\" \"\" --unattended"
    description: "Install Oh My Zsh"
```

### Configuration Sections

#### `name` (required)
The name of your setup. Used for logging and identification.

#### `variables`
A key-value mapping of variables that can be used in Jinja2 templates.

#### `system`
Defines system packages to install.

- `packages`: List of package names to install using the appropriate package manager.

#### `git`
Defines git repositories to clone or update.

- `url`: Repository URL
- `path`: Local path to clone the repository
- `branch`: Branch to checkout (defaults to "main")

#### `dotfiles`
Defines dotfile linking operations.

- `source`: Path to source file (relative to config file)
- `target`: Path where symlink should be created

If `source` ends with `.j2`, it will be processed as a Jinja2 template using variables.

#### `scripts`
Defines custom scripts to execute.

- `command`: The shell command to execute
- `description`: Optional description
- `cwd`: Optional working directory

## CLI Commands

### apply
Apply a rig configuration to the local machine.

```bash
autorig apply rig.yaml
autorig apply rig.yaml --dry-run  # Preview actions
autorig apply rig.yaml --verbose  # Verbose output
autorig apply rig.yaml --force    # Force operations
```

### clean
Remove symlinks created by the configuration.

```bash
autorig clean rig.yaml
```

### validate
Validate a rig configuration file.

```bash
autorig validate rig.yaml
```

### backup
Create a full backup archive of all dotfiles defined in the config.

```bash
autorig backup rig.yaml
```

### restore
Restore dotfiles from a backup snapshot.

```bash
autorig restore rig.yaml ~/.autorig/backups/My_Setup_20231027-103000.tar.gz
```

### status
Show the status of dotfiles and repositories.

```bash
autorig status rig.yaml
```

### diff
Show differences between current system state and configuration.

```bash
autorig diff rig.yaml
```

### rollback
Rollback to the most recent backup snapshot.

```bash
autorig rollback rig.yaml
```

### watch
Monitor the config file and automatically apply changes when saved.

```bash
autorig watch rig.yaml
```

### sync
Push local changes in git repositories to remotes.

```bash
autorig sync rig.yaml
```

### bootstrap
Generate a default rig.yaml configuration file.

```bash
autorig bootstrap myconfig.yaml
```

### run-plugins
Run specific plugins defined in the configuration.

```bash
autorig run-plugins rig.yaml myplugin
```

## Plugins

AutoRig supports a plugin architecture that allows extending functionality without modifying core code.

### Creating Plugins

Plugins are Python classes that inherit from the `Plugin` base class and implement the required methods:

```python
from autorig.plugins import Plugin
from autorig.config import RigConfig

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    def apply(self, config: RigConfig, dry_run: bool = False, verbose: bool = False) -> bool:
        # Plugin logic here
        return True
```

### Using Plugins

Plugins can be registered and used through the plugin system. The Python development plugin is included by default.

## Advanced Features

### Jinja2 Templates

Dotfiles ending with `.j2` are processed as Jinja2 templates:

```gitconfig.j2
[user]
    name = {{ username }}
    email = {{ email }}
```

### Environment Variables

Environment variables can be expanded in config files using `${VAR_NAME}` syntax.

### Watch Mode

AutoRig includes a watch mode that automatically applies changes when you save the configuration:

```bash
autorig watch rig.yaml
```

### Dry Run Mode

Preview all actions without making changes to your system:

```bash
autorig apply rig.yaml --dry-run
```

## Troubleshooting

### Common Issues

1. **Permission denied errors**: Make sure AutoRig has appropriate permissions for system package installation.

2. **Path traversal security errors**: Ensure all paths in config files are properly formatted without `../` sequences.

3. **Git repository conflicts**: If a repository path exists but is not a git repository, AutoRig will warn you.

4. **Template rendering errors**: Check Jinja2 syntax in `.j2` templates.

### Logging

AutoRig logs detailed execution information to `~/.autorig/logs/autorig.log` for troubleshooting.