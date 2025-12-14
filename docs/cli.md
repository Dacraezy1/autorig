# Command Line Interface

This document details all AutoRig command line interface options.

## Global Options

All commands support these global options:

- `-h`, `--help`: Show help message and exit

## Command Reference

### `apply`

Apply a rig configuration to the local machine.

```bash
autorig apply [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--dry-run, -n`: Simulate actions without making changes
- `--verbose, -v`: Enable verbose output
- `--force, -f`: Force operations that might overwrite existing files

**Examples:**
```bash
# Apply configuration
autorig apply rig.yaml

# Preview what would happen
autorig apply rig.yaml --dry-run

# Apply with verbose output
autorig apply rig.yaml --verbose

# Force operations
autorig apply rig.yaml --force
```

**What it does:**
1. Install system packages
2. Process git repositories (clone/update)
3. Link dotfiles (with template processing)
4. Execute custom scripts

### `clean`

Remove symlinks created by the configuration.

```bash
autorig clean [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--dry-run, -n`: Simulate actions without making changes
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Remove symlinks
autorig clean rig.yaml

# Preview what would be removed
autorig clean rig.yaml --dry-run
```

### `validate`

Validate a rig configuration file.

```bash
autorig validate [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Validate configuration
autorig validate rig.yaml

# Validate with detailed output
autorig validate rig.yaml --verbose
```

### `backup`

Create a full backup archive of all dotfiles defined in the config.

```bash
autorig backup [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Create backup
autorig backup rig.yaml
```

### `restore`

Restore dotfiles from a backup snapshot.

```bash
autorig restore [OPTIONS] CONFIG_FILE SNAPSHOT_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file
- `SNAPSHOT_FILE`: Path to the backup tarball to restore

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Restore from backup
autorig restore rig.yaml ~/.autorig/backups/My_Setup_20231027-103000.tar.gz
```

### `status`

Show the status of dotfiles and repositories.

```bash
autorig status [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Show configuration status
autorig status rig.yaml
```

### `diff`

Show differences between current system state and configuration.

```bash
autorig diff [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Show differences
autorig diff rig.yaml
```

### `rollback`

Rollback to the most recent backup snapshot.

```bash
autorig rollback [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Rollback to latest backup
autorig rollback rig.yaml
```

### `watch`

Monitor the config file and automatically apply changes when saved.

```bash
autorig watch [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Watch config for changes
autorig watch rig.yaml
```

### `sync`

Push local changes in git repositories to remotes.

```bash
autorig sync [OPTIONS] CONFIG_FILE
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file

**Options:**
- `--dry-run, -n`: Simulate actions without making changes
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Sync repositories
autorig sync rig.yaml

# Preview sync operations
autorig sync rig.yaml --dry-run
```

### `bootstrap`

Generate a default rig.yaml configuration file.

```bash
autorig bootstrap [OPTIONS] [PATH]
```

**Arguments:**
- `PATH`: Path to generate the config file (defaults to "rig.yaml")

**Options:**
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Create default config
autorig bootstrap

# Create config at specific location
autorig bootstrap myconfig.yaml
```

### `run-plugins`

Run specific plugins defined in the configuration.

```bash
autorig run-plugins [OPTIONS] CONFIG_FILE PLUGIN_NAMES...
```

**Arguments:**
- `CONFIG_FILE`: Path to rig.yaml config file
- `PLUGIN_NAMES`: Names of plugins to run

**Options:**
- `--dry-run, -n`: Simulate actions without making changes
- `--verbose, -v`: Enable verbose output

**Examples:**
```bash
# Run specific plugins
autorig run-plugins rig.yaml python-dev

# Run multiple plugins
autorig run-plugins rig.yaml python-dev nodejs-dev
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Command line usage error
- `3`: Configuration error