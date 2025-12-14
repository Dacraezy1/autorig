# Plugins

AutoRig supports a plugin architecture that allows extending functionality without modifying core code.

## Overview

Plugins are Python classes that can extend AutoRig's functionality. They are loaded dynamically and can be registered to handle specific tasks beyond the core functionality.

## Creating Custom Plugins

### Plugin Interface

All plugins must inherit from the `Plugin` base class and implement two methods:

1. `name` property: Returns the plugin's name as a string
2. `apply` method: Contains the plugin's logic and returns a boolean indicating success

```python
from autorig.plugins import Plugin
from autorig.config import RigConfig
from typing import Dict, Any

class MyCustomPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-custom-plugin"
    
    def apply(self, config: RigConfig, dry_run: bool = False, verbose: bool = False) -> bool:
        # Access configuration values
        variables = config.variables
        
        # Your plugin logic here
        if verbose:
            print(f"Applying {self.name} plugin...")
        
        if dry_run:
            print("DRY RUN: Would execute plugin logic")
            return True
        
        try:
            # Perform plugin-specific operations
            # For example, setting up a specific development environment
            # or configuring a particular tool
            
            # Return True if successful, False otherwise
            return True
        except Exception as e:
            print(f"Error in plugin: {e}")
            return False
```

### Plugin Registration

To register a plugin, you need to import it and register it with the plugin manager:

```python
from autorig.plugins import plugin_manager
from my_plugin import MyCustomPlugin

plugin_manager.register(MyCustomPlugin())
```

## Built-in Plugins

### Python Development Plugin

The Python development plugin (`python-dev`) helps set up Python development environments.

#### Configuration

Add Python-specific variables to your configuration:

```yaml
name: "Python Development Setup"

variables:
  python_version: "3.10"
  python_venv: ".venv"
  python_packages: ["black", "flake8", "isort", "mypy"]
  skip_venv: false  # Set to true to skip virtual environment creation

system:
  packages:
    - python3
    - python3-pip
    - python3-venv

dotfiles:
  - source: ".python-version"
    target: "~/.python-version"
  - source: ".pylintrc"
    target: "~/.pylintrc"
```

#### Functionality

The Python development plugin will:

1. Create a virtual environment (if it doesn't exist)
2. Install specified Python packages
3. Optionally skip virtual environment creation based on configuration

## Using Plugins

### Running Specific Plugins

To run specific plugins:

```bash
autorig run-plugins rig.yaml my-plugin another-plugin
```

### Running All Registered Plugins

To run all registered plugins:

```bash
autorig run-plugins rig.yaml  # This runs all available plugins
```

### With Options

You can use the same options as other commands:

```bash
# Dry run
autorig run-plugins rig.yaml my-plugin --dry-run

# Verbose output
autorig run-plugins rig.yaml my-plugin --verbose
```

## Security Considerations

### Plugin Safety

- Only install plugins from trusted sources
- Review plugin code before using it
- Plugins have access to your configuration and can execute system commands

### Validation

All plugins should implement proper error handling and validation to ensure they don't break the system or configuration.

## Advanced Plugin Features

### Accessing Configuration

Plugins have access to the full configuration:

```python
def apply(self, config: RigConfig, dry_run: bool = False, verbose: bool = False) -> bool:
    # Access system packages
    packages = config.system.packages
    
    # Access git repositories
    repos = config.git.repositories
    
    # Access dotfiles
    dotfiles = config.dotfiles
    
    # Access variables
    variables = config.variables
    
    # Access scripts
    scripts = config.scripts
    
    return True
```

### Integration with Core Flow

Plugins can be integrated into the main AutoRig flow by modifying the apply function or creating custom commands. The plugin architecture is designed to be flexible while maintaining security and reliability.