"""
Additional tests for AutoRig CLI and integration testing
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml

from autorig.cli import app
from autorig.core import AutoRig
from autorig.config import RigConfig


def test_full_integration():
    """Test a full integration scenario."""
    # Create a temporary config file with all new features
    config_data = {
        "name": "Test Integration Config",
        "variables": {"test_var": "test_value"},
        "system": {"packages": ["git"]},  # Use a package that's likely installed
        "git": {"repositories": []},
        "dotfiles": [],
        "scripts": [],
        "hooks": {
            "pre_system": [
                {
                    "command": "echo 'pre-system test'",
                    "description": "Pre-system hook test",
                }
            ],
            "post_system": [
                {
                    "command": "echo 'post-system test'",
                    "description": "Post-system hook test",
                }
            ],
        },
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.yaml"

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Test that we can create a RigConfig from this file
        config = RigConfig.from_yaml(str(config_path))
        assert config.name == "Test Integration Config"
        assert len(config.hooks.pre_system) == 1
        assert len(config.hooks.post_system) == 1
        assert config.hooks.pre_system[0].command == "echo 'pre-system test'"

        # Test that we can create an AutoRig instance
        rig = AutoRig(
            str(config_path), dry_run=True
        )  # Use dry-run to avoid actual changes
        assert rig.config.name == "Test Integration Config"


@patch("autorig.profiles.EnvironmentDetector._collect_environment_info")
@patch("subprocess.run")
def test_autorig_with_new_features(mock_subprocess, mock_env_info):
    """Test AutoRig with mocked subprocess for new features."""
    # Mock environment info to avoid platform issues
    mock_env_info.return_value = {
        "os": "linux",
        "platform": "linux",
        "machine": "x86_64",
        "node": "test",
        "release": "test",
        "version": "test",
        "architecture": "64bit",
        "python_version": "3.9",
        "shell": "/bin/bash",
        "user": "testuser",
        "home": "/home/testuser",
        "is_wsl": False,
        "is_docker": False,
        "desktop_environment": "",
        "display_server": "",
        "session_type": "",
        "wayland_display": "",
        "term": "xterm",
        "term_program": "",
        "editor": "vim",
        "language": "en_US.UTF-8",
        "timezone": "",
        "display": "",
        "packages_installed": [],
        "gpu_info": "test",
        "memory_gb": 8.0,
        "cpu_cores": 4,
        "disk_space_gb": 100.0,
    }

    # Mock successful subprocess calls
    mock_result = Mock()
    mock_result.stdout = "mock output"
    mock_result.stderr = ""
    mock_result.returncode = 0
    mock_subprocess.return_value = mock_result

    # Create a config with hooks
    config_data = {
        "name": "Test Mock Config",
        "system": {"packages": []},
        "git": {"repositories": []},
        "dotfiles": [],
        "scripts": [],
        "hooks": {
            "pre_system": [{"command": "echo 'test'", "description": "test hook"}]
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()

        try:
            # Test with dry-run to avoid actual changes
            rig = AutoRig(f.name, dry_run=True, verbose=True)

            # Apply should work with all new features
            # Since we're in dry-run mode, this shouldn't make actual changes
            # but should process all the new features correctly
            rig.apply()

            # Verify that no actual system operations were attempted in dry-run
            # (this is just to make sure the code path works)
            assert rig.config.name == "Test Mock Config"
            assert len(rig.config.hooks.pre_system) == 1
        finally:
            os.unlink(f.name)


def test_schema_validation_integration():
    """Test schema validation with the new hooks feature."""
    # This test ensures that the schema validation includes the new hooks field
    config_data = {
        "name": "Schema Test Config",
        "variables": {},
        "system": {"packages": []},
        "git": {"repositories": []},
        "dotfiles": [],
        "scripts": [],
        "hooks": {
            "pre_system": [],
            "post_system": [],
            "pre_git": [],
            "post_git": [],
            "pre_dotfiles": [],
            "post_dotfiles": [],
            "pre_scripts": [],
            "post_scripts": [],
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()

        try:
            # This should work without schema validation errors
            config = RigConfig.from_yaml(f.name)
            assert config.name == "Schema Test Config"
            # Verify hooks are properly loaded
            assert hasattr(config, "hooks")
        finally:
            os.unlink(f.name)


def test_config_validation_with_new_fields():
    """Test that new fields are properly included in validation."""
    config_data = {
        "name": "Validation Test",
        "hooks": {"pre_system": [{"command": "test", "description": "test"}]},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()

        try:
            # Should validate successfully with new hooks field
            config = RigConfig.from_yaml(f.name)
            assert len(config.hooks.pre_system) == 1
            assert config.hooks.pre_system[0].command == "test"
        finally:
            os.unlink(f.name)


@patch("autorig.installers.base.get_system_installer")
def test_autorig_with_notifications_and_tracking(mock_installer):
    """Test AutoRig with new notification and tracking features."""
    # Mock the installer to return a mock installer that doesn't do anything
    mock_inst = Mock()
    mock_inst.install.return_value = True
    mock_installer.return_value = mock_inst

    config_data = {
        "name": "Test Notifications",
        "system": {"packages": ["git"]},
        "git": {"repositories": []},
        "dotfiles": [],
        "scripts": [],
        "hooks": {"pre_system": [{"command": "echo 'test'", "description": "test"}]},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()

        try:
            # Test with dry run to prevent actual changes
            rig = AutoRig(f.name, dry_run=True, verbose=True)
            assert hasattr(rig, "notification_manager")
            assert hasattr(rig, "progress_tracker")
            assert hasattr(rig, "state_manager")
        finally:
            os.unlink(f.name)


def test_secure_command_validation():
    """Test the enhanced security validation."""
    # Test that dangerous commands are blocked
    from autorig.core import AutoRig

    config_data = {
        "name": "Security Test",
        "system": {"packages": []},
        "git": {"repositories": []},
        "dotfiles": [],
        "scripts": [{"command": "echo safe command", "description": "safe"}],
        "hooks": {"pre_system": [{"command": "echo safe hook", "description": "safe"}]},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()

        try:
            rig = AutoRig(f.name)
            # Test the validation function directly
            assert rig._is_safe_command("echo hello") == True
            assert rig._is_safe_command("echo hello; rm -rf /") == False
            assert rig._is_safe_command("echo hello && rm -rf /") == False
            assert rig._is_safe_command("echo hello || rm -rf /") == False
            assert rig._is_safe_command("eval 'rm -rf /'") == False
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__])
