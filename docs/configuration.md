# Configuration Reference

This document provides detailed information about the AutoRig configuration file format.

## Overview

The AutoRig configuration file is a YAML file that defines your development environment. The typical filename is `rig.yaml`.

## Configuration Schema

### `name` (string, required)
The name of your setup. This is used for logging and identification purposes.

```yaml
name: "My Linux Development Environment"
```

### `variables` (object, optional)
A mapping of key-value pairs that can be used in Jinja2 templates.

```yaml
variables:
  email: "user@example.com"
  username: "developer"
  theme: "dracula"
  editor: "nvim"
```

### `system` (object, optional)

#### `packages` (array of strings)
List of system packages to install using the appropriate package manager.

**Linux:** Uses `apt`, `dnf`, `yum`, `pacman`, `zypper`, `xbps`, or `apk` depending on the distribution.
**macOS:** Uses Homebrew or MacPorts.
**Windows:** Uses `winget`, `choco`, or `scoop`.

```yaml
system:
  packages:
    - git
    - vim
    - curl
    - htop
    - nodejs
    - python3
    - docker
```

### `git` (object, optional)

#### `repositories` (array of objects)
List of git repositories to clone or update.

Each repository object has these properties:

- `url` (string): Repository URL (supports HTTPS, SSH)
- `path` (string): Local path where repository should be cloned
- `branch` (string, optional): Branch name to check out (defaults to "main")

```yaml
git:
  repositories:
    - url: "https://github.com/ohmyzsh/ohmyzsh.git"
      path: "~/.oh-my-zsh"
      branch: "master"
    - url: "git@github.com:user/repo.git"  # SSH
      path: "~/projects/myrepo"
      branch: "develop"
```

### `dotfiles` (array of objects, optional)

List of files to link as symlinks. Each object has:

- `source` (string): Path to source file (relative to config file location)
- `target` (string): Path where symlink should be created

If `source` ends with `.j2`, it will be treated as a Jinja2 template and rendered using variables.

```yaml
dotfiles:
  # Regular file linking
  - source: "shell/.zshrc"
    target: "~/.zshrc"
  - source: "editor/.vimrc"
    target: "~/.vimrc"
  
  # Template file (will be rendered with Jinja2)
  - source: "git/.gitconfig.j2"
    target: "~/.gitconfig"
```

Example template file (`git/.gitconfig.j2`):
```gitconfig
[user]
    name = {{ username }}
    email = {{ email }}

[core]
    editor = {{ editor }}
```

### `scripts` (array of objects, optional)

List of custom scripts to execute. Each object has:

- `command` (string): Shell command to execute
- `description` (string, optional): Human-readable description
- `cwd` (string, optional): Working directory for the command

```yaml
scripts:
  - command: "sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\" \"\" --unattended"
    description: "Install Oh My Zsh"
    cwd: "~"
  - command: "pip3 install --user black flake8 isort"
    description: "Install Python development tools"
```

## Security Considerations

### Path Traversal Prevention
AutoRig prevents path traversal attacks. Paths containing `../` or `..\\` will cause validation errors.

### Command Injection Prevention
The following patterns are blocked in script commands:
- `||` (command chaining)
- `&&` (command chaining)
- `;` (command separation)
- `$((...))` (arithmetic expansion)
- `` `...` `` (command substitution)
- `$(...)` (command substitution)

## Advanced Configuration Examples

### Development Environment with Multiple Tools

```yaml
name: "Full Development Setup"

variables:
  email: "developer@example.com"
  username: "dev"
  editor: "nvim"
  theme: "gruvbox"

system:
  packages:
    # System utilities
    - git
    - curl
    - wget
    - htop
    - tmux
    - zsh
    # Development tools
    - nodejs
    - python3
    - python3-pip
    - docker
    - docker-compose
    - make
    - gcc
    # Text editors
    - vim
    - neovim
    - jq

git:
  repositories:
    - url: "https://github.com/ohmyzsh/ohmyzsh.git"
      path: "~/.oh-my-zsh"
      branch: "master"
    - url: "https://github.com/romkatv/powerlevel10k.git"
      path: "~/.powerlevel10k"
      branch: "master"

dotfiles:
  # Shell configuration
  - source: "shell/.zshrc"
    target: "~/.zshrc"
  - source: "shell/.p10k.zsh"
    target: "~/.p10k.zsh"
  # Editor configuration
  - source: "editor/.vimrc"
    target: "~/.vimrc"
  - source: "editor/nvim/init.vim"
    target: "~/.config/nvim/init.vim"
  # Git configuration
  - source: "git/.gitconfig.j2"
    target: "~/.gitconfig"

scripts:
  # Install Oh My Zsh
  - command: "sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\" \"\" --unattended"
    description: "Install Oh My Zsh"
  # Install FZF
  - command: "git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install"
    description: "Install FZF"
  # Install Python tools
  - command: "pip3 install --user black flake8 isort mypy"
    description: "Install Python development tools"
```

### Minimal Configuration

```yaml
name: "Minimal Setup"

system:
  packages:
    - git
    - vim

dotfiles:
  - source: ".vimrc"
    target: "~/.vimrc"
```