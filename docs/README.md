# AutoRig Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Commands](#commands)
6. [Hooks System](#hooks-system)
7. [Security](#security)
8. [Monitoring & Reporting](#monitoring--reporting)
9. [Troubleshooting](#troubleshooting)

## Introduction

AutoRig is a robust, data-driven system configuration and dotfile manager written in Python. It automates the setup of a development environment by installing system packages, managing git repositories, linking dotfiles, and running custom scripts.

## Features

### Core Features
- System package management across multiple platforms
- Advanced dotfile management with Jinja2 templating
- Git repository management (clone/update)
- Custom script execution
- Dry run mode for safe testing
- Backup and restore capabilities
- Watch mode for automatic updates

### Enhanced Features (v0.3+)
- **Pre/Post Hooks System**: Execute custom scripts before and after major operations
- **Notification System**: Desktop notifications for long-running operations
- **Enhanced Profile Detection**: Expanded environment detection with hardware specs
- **Error Recovery & Rollback**: Automatic state tracking with rollback capabilities
- **Monitoring & Reporting**: Real-time resource monitoring and status reporting
- **Configuration Schema Validation**: JSON schema validation for configuration files
- **Improved Security**: Enhanced validation patterns and path restrictions

## Installation

### Prerequisites
- Python 3.9+
- Git

### From Source
```bash
git clone https://github.com/Dacraezy1/autorig.git
cd autorig
pip install -e .
```

### Using pipx
```bash
pipx install git+https://github.com/Dacraezy1/autorig.git
```

## Configuration

### Basic Structure
```yaml
name: "My Developer Setup"
variables: { }  # Variables for Jinja2 templates

system:
  packages: [ ]  # System packages to install

git:
  repositories: [ ]  # Git repos to manage

dotfiles: [ ]  # Dotfiles to link

hooks: { }  # Pre/post operation hooks

scripts: [ ]  # Custom scripts to execute
```

### Variables
Variables are available for use in Jinja2 templates:

```yaml
variables:
  email: "user@example.com"
  username: "developer"
  theme: "dracula"
```

### Hooks System
Hooks allow you to run scripts before and after major operations:

```yaml
hooks:
  pre_system:
    - command: "echo 'Starting package installation'"
      description: "Log start time"
  post_system:
    - command: "sudo apt autoremove -y"
      description: "Clean up packages"
  pre_git:
    - command: "mkdir -p ~/Projects"
      description: "Create project directory"
  post_git:
    - command: "chmod -R 700 ~/Projects/private"
      description: "Secure private projects"
  pre_dotfiles:
    - command: "mkdir -p ~/.config"
      description: "Create config directory"
  post_dotfiles:
    - command: "chmod 600 ~/.ssh/*"
      description: "Secure SSH files"
  pre_scripts:
    - command: "source ~/.zshrc || true"
      description: "Load shell environment"
  post_scripts:
    - command: "echo 'Setup complete!'"
      description: "Completion notification"
```

## Commands

### Main Commands
- `autorig apply <config>` - Apply a configuration
- `autorig clean <config>` - Remove symlinks
- `autorig validate <config>` - Validate configuration
- `autorig backup <config>` - Create backup
- `autorig restore <config> <snapshot>` - Restore from backup
- `autorig status <config>` - Show status
- `autorig diff <config>` - Show differences
- `autorig rollback <config>` - Rollback to latest backup
- `autorig watch <config>` - Watch mode
- `autorig sync <config>` - Sync repositories
- `autorig run-plugins <config> <plugins>` - Run plugins
- `autorig report <config>` - Generate status report
- `autorig detect` - Detect environment profile

### Options
- `-n, --dry-run` - Simulate actions without changes
- `-v, --verbose` - Enable verbose output
- `-f, --force` - Force operations that might overwrite files
- `-p, --profile` - Use specific profile configuration
- `-d, --detailed` - Show detailed information (detect command)
- `-o, --output` - Output file for reports

## Security

AutoRig implements several security measures:

1. **Path Traversal Prevention**: Checks for `../` patterns in paths
2. **Command Injection Prevention**: Validates command patterns:
   - `||`, `&&`, `;` (command chaining)
   - `$((...))`, `` `...` ``, `$({...})` (command substitution)
   - `eval`, `exec`, `source` commands
   - `bash -c`, `sh -c`, etc.
   - Dangerous paths like `/etc`, `/root`, etc.

3. **Safe Extraction**: Uses secure extraction methods for archives
4. **Restricted Paths**: Prevents access to system directories

## Monitoring & Reporting

### Resource Monitoring
AutoRig monitors system resources during operations:
- CPU usage
- Memory usage
- Disk usage
- Network I/O

### Status Reports
Generate detailed reports:
```bash
autorig report rig.yaml --output report.json
```

Reports include:
- Configuration summary
- System resource usage
- Operation statistics

## Troubleshooting

### Common Issues

#### Permission Errors
- Run with appropriate privileges (sudo) for system operations
- Check file permissions for dotfiles

#### Path Issues
- Ensure paths don't contain `../` patterns
- Use `~` for home directory

#### Git Repository Conflicts
- Clean up conflicting repositories before running AutoRig
- Use `--force` option carefully

#### Script Failures
- Check script syntax and permissions
- Use dry-run mode to preview actions

### Logs
Logs are stored in `~/.autorig/logs/` with timestamps.

### Rollbacks
If operations fail, AutoRig attempts to rollback automatically.
Manually rollback with:
```bash
autorig rollback rig.yaml
```

## Profile-Based Configuration

AutoRig can detect system profiles and apply specific configurations:

```yaml
profiles:
  linux-x86_64-desktop:
    system:
      packages:
        - docker
        - code
  darwin-x86_64:
    system:
      packages:
        - rectangle
        - iterm2
```

The system automatically detects profiles like:
- `linux-x86_64-desktop`
- `darwin-x86_64`
- `linux-x86_64-wsl`
- `linux-aarch64` (ARM systems)