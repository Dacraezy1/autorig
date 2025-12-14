# AutoRig Examples

This directory contains example configuration files for different use cases.

## Available Examples

### basic-dev.yaml
A basic development environment with essential tools:
- Git, Vim, Curl, Wget, Htop
- Node.js, Python, Docker
- Oh My Zsh shell setup
- Basic dotfiles configuration

### python-dev.yaml
A comprehensive Python development environment:
- Python 3.10 with virtual environments
- Essential Python packages (black, flake8, isort, mypy, pytest, pipenv)
- Shell customization (Oh My Zsh, Powerlevel10k)
- Editor configuration (Vim/Neovim)
- Git configuration

### web-dev.yaml
A web development environment:
- Node.js and npm/yarn
- Essential web development tools
- Linters and formatters (ESLint, Prettier)
- Shell and editor configuration

### minimal.yaml
A minimal configuration to demonstrate basic functionality:
- Essential packages only
- Single dotfile
- Simple confirmation script

## How to Use

1. Copy one of the examples to your working directory
2. Customize it to your needs
3. Run `autorig apply <your-config-file>.yaml`

For example:
```bash
cp examples/python-dev.yaml ~/my-python-config.yaml
# Edit my-python-config.yaml to match your preferences
autorig apply ~/my-python-config.yaml
```

## Creating Your Own Configurations

Use these examples as a starting point for your own configurations. You can:

- Modify existing examples
- Combine elements from different examples
- Add your own packages, repositories, and dotfiles
- Use Jinja2 templates for dynamic configurations