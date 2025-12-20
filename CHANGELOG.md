# Changelog

All notable changes to AutoRig will be documented in this file.

## [1.0.0] - 2025-01-20

### Major Release - Complete Rewrite with Advanced Features

This is a major release that introduces a comprehensive set of new features and improvements, transforming AutoRig into a more powerful and robust system configuration manager.

### Added

#### Core Features
- **Pre/Post Hooks System**: Execute custom scripts before and after major operations (system, git, dotfiles, scripts). Supports `pre_system`, `post_system`, `pre_git`, `post_git`, `pre_dotfiles`, `post_dotfiles`, `pre_scripts`, and `post_scripts` hooks.
- **Notification System**: Desktop notifications for long-running operations on supported platforms (macOS, Linux, Windows) with customizable alert settings.
- **Enhanced Profile Detection**: Expanded environment detection including VM, CI/CD detection, hardware specs (memory, CPU cores, disk space, GPU), session type, terminal info, and intelligent recommendations.
- **Error Recovery & Rollback**: Automatic state tracking with rollback capabilities to revert changes on failure, including operation tracking and state preservation.
- **Monitoring & Reporting**: Real-time resource monitoring (CPU, memory, disk, network) and detailed status reporting with system resource usage tracking.
- **Configuration Schema Validation**: JSON schema validation for configuration files to catch errors early with comprehensive validation rules.
- **Cloud Integration & Remote Config Fetching**: Support for remote configurations via HTTP, GitHub, and GitLab with direct URL support and special syntax (e.g., `github:username/repo/path`).

#### Security Enhancements
- **Enhanced Command Validation**: Expanded patterns for detecting potentially dangerous commands including eval, exec, source, and shell execution commands.
- **Path Restriction Validation**: Additional validation for dangerous system paths and command patterns.
- **Secure Archive Extraction**: Safe extraction methods with path traversal prevention for backup/restore operations.

#### User Experience
- **Improved CLI Options**: Added `-d` (detailed detection) and `-o` (output) flags for enhanced functionality.
- **Progress Tracking**: Detailed progress indicators with percentage tracking and operation steps.
- **Better Logging**: Enhanced logging with configurable levels and detailed execution information.

### Changed

#### Configuration Format
- Added `hooks` section to configuration schema for pre/post operation scripts.
- Enhanced validation for all configuration fields with more comprehensive checks.
- Extended profile detection with additional environment variables and system information.

#### Architecture
- Introduced modular design with dedicated modules for notifications, monitoring, state management, and remote configurations.
- Improved error handling and exception management throughout the codebase.
- Enhanced testing infrastructure with comprehensive test coverage for new features.

### Fixed

- Improved security validation to prevent command injection and path traversal attacks.
- Fixed issues with backup/restore operations using more robust manifest tracking.
- Enhanced error recovery mechanisms to prevent partial configuration states.

### Security

- Expanded security validation patterns to include more dangerous command structures.
- Enhanced path validation to prevent access to restricted system directories.
- Improved command sanitization with more comprehensive pattern matching.

## [0.2.0] - 2024-06-15

### Added
- Cross-platform support (Linux, macOS, Windows)
- System package management for multiple package managers
- Git repository management (clone/update)
- Dotfile management with Jinja2 templating
- Backup and restore functionality
- Plugin architecture
- Dry run mode
- Watch mode
- Profile-based configurations

## [0.1.0] - 2024-01-15

### Added
- Initial release
- Basic system package installation
- Simple dotfile linking
- Configuration management