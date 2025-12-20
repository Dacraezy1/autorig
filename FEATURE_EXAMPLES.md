# AutoRig v1.0.0 Feature Examples

This file demonstrates the new features added in AutoRig v1.0.0.

## 🔗 Hooks System

### Complete Configuration Example
```yaml
name: "Advanced Developer Setup"

variables:
  email: "user@example.com"
  username: "developer"
  theme: "dracula"

system:
  packages:
    - git
    - vim
    - curl
    - htop
    - nodejs
    - python3
    - docker

git:
  repositories:
    - url: "https://github.com/ohmyzsh/ohmyzsh.git"
      path: "~/.oh-my-zsh"
      branch: "master"

dotfiles:
  - source: "shell/.zshrc"
    target: "~/.zshrc"
  - source: "editor/.vimrc"
    target: "~/.vimrc"
  - source: "git/gitconfig.j2"
    target: "~/.gitconfig"

# NEW: Pre/Post Hooks System
hooks:
  # Execute before system package installation
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
  - command: "sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\" \"\" --unattended"
    description: "Install Oh My Zsh"
  - command: "npm install -g typescript"
    description: "Install TypeScript globally"
```

## 🌐 Remote Configuration Usage

### Using Direct URLs
```bash
# Apply configuration from a direct URL
autorig apply https://raw.githubusercontent.com/username/repo/main/config.yaml

# Validate a remote configuration
autorig validate https://example.com/config.yaml
```

### Using GitHub Shortcuts
```bash
# Apply configuration from GitHub
autorig apply github:username/repository/path/to/config.yaml

# Use a specific branch/tag
autorig apply github:username/repository/path/to/config.yaml@development

# Validate and apply with profile
autorig apply github:company/configs/engineering-laptop.yaml@main --profile linux-workstation
```

### Using GitLab Shortcuts
```bash
# Apply configuration from GitLab
autorig apply gitlab:group/project/path/to/config.yaml

# Use the remote command for other operations
autorig remote gitlab:group/project/path/to/config.yaml status
autorig remote github:username/repo/config.yaml diff
```

## 📊 Monitoring and Reporting

### Generate Status Reports
```bash
# Basic status report
autorig report config.yaml

# Verbose report with more details
autorig report config.yaml --verbose

# Save report to JSON file
autorig report config.yaml --output report.json

# With profile selection
autorig report config.yaml --profile work-desktop --output work-report.json
```

### Enhanced Detection
```bash
# Basic detection
autorig detect

# Verbose detection
autorig detect --verbose

# Detailed detection with recommendations
autorig detect --detailed
```

## 🔔 Enhanced Notification and Progress Tracking

All operations now include:
- Desktop notifications for long-running operations
- Detailed progress tracking with percentage indicators
- Real-time resource monitoring
- Automatic state tracking for rollback capability

### Example of Enhanced Output
```bash
$ autorig apply config.yaml
[green]Applying configuration: Advanced Developer Setup[/green]
[blue]Running pre-system hooks...[/blue] (25% complete)
[blue]Installing system packages...[/blue] (35% complete)
[blue]Running post-system hooks...[/blue] (50% complete)
[blue]Processing git repositories...[/blue] (65% complete)
[green]✨ Rig setup complete![/green]
```

## 🔒 Enhanced Security Validation

The new security system blocks:
- Command chaining (`||`, `&&`, `;`)
- Command substitution (`$()`, backticks)
- Dangerous commands (`eval`, `exec`, `source`)
- Shell execution patterns (`bash -c`, `sh -c`)
- Access to system directories (`/etc`, `/root`, etc.)

## 🔄 Error Recovery & Rollback

If any operation fails, AutoRig:
- Automatically tracks operation state
- Preserves original file backups
- Provides rollback capability
- Logs detailed error information