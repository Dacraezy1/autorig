"""
Tests for AutoRig - testing new functionality
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from autorig.config import RigConfig, Hooks
from autorig.core import AutoRig
from autorig.remote import RemoteConfigManager, resolve_config_path
from autorig.notifications import NotificationManager, ProgressTracker
from autorig.state import StateManager, OperationTracker
from autorig.monitoring import StatusReporter, ResourceMonitor


class TestHooks:
    """Test the hooks functionality."""
    
    def test_hooks_model(self):
        """Test that the Hooks model works properly."""
        hooks = Hooks()
        assert hooks.pre_system == []
        assert hooks.post_system == []
        assert hooks.pre_git == []
        assert hooks.post_git == []
        assert hooks.pre_dotfiles == []
        assert hooks.post_dotfiles == []
        assert hooks.pre_scripts == []
        assert hooks.post_scripts == []
    
    def test_config_with_hooks(self):
        """Test that RigConfig properly includes hooks."""
        config_data = {
            "name": "Test Config",
            "hooks": {
                "pre_system": [
                    {"command": "echo 'pre'", "description": "Pre-system hook"}
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            f.flush()
            
            config = RigConfig.from_yaml(f.name)
            assert len(config.hooks.pre_system) == 1
            assert config.hooks.pre_system[0].command == "echo 'pre'"
            assert config.hooks.pre_system[0].description == "Pre-system hook"
            
            os.unlink(f.name)


class TestNotifications:
    """Test the notification functionality."""
    
    def test_notification_manager_creation(self):
        """Test that NotificationManager can be created."""
        manager = NotificationManager()
        assert manager is not None
        
    def test_progress_tracker(self):
        """Test that ProgressTracker works."""
        manager = NotificationManager()
        tracker = ProgressTracker(manager)
        
        assert tracker.notification_manager == manager
        assert tracker.total_steps == 0
        assert tracker.current_step == 0
        assert tracker.operation_name == ""


class TestStateManagement:
    """Test the state management functionality."""
    
    def test_state_manager_creation(self):
        """Test that StateManager can be created."""
        # Create a minimal config for testing
        config_data = {"name": "test"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            f.flush()
            
            config = RigConfig.from_yaml(f.name)
            manager = StateManager(config)
            
            assert manager.config == config
            assert manager.state_dir.exists()
            
            os.unlink(f.name)
    
    def test_operation_tracker(self):
        """Test that OperationTracker works."""
        # Create a minimal config for testing
        config_data = {"name": "test"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            f.flush()
            
            config = RigConfig.from_yaml(f.name)
            state_manager = StateManager(config)
            tracker = OperationTracker(state_manager, "test_operation")
            
            assert tracker.operation_name == "test_operation"
            assert tracker.changes == []
            
            # Test record_change
            tracker.record_change("test_action", "/tmp/test", extra_info="test")
            assert len(tracker.changes) == 1
            assert tracker.changes[0]["action"] == "test_action"
            assert tracker.changes[0]["path"] == "/tmp/test"
            assert tracker.changes[0]["extra_info"] == "test"
            
            os.unlink(f.name)


class TestMonitoring:
    """Test the monitoring functionality."""
    
    def test_status_reporter(self):
        """Test that StatusReporter can be created."""
        # Create a minimal config for testing
        config_data = {"name": "test"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            f.flush()
            
            config = RigConfig.from_yaml(f.name)
            from rich.console import Console
            console = Console()
            reporter = StatusReporter(config, console)
            
            assert reporter.config == config
            
            os.unlink(f.name)
    
    def test_resource_monitor(self):
        """Test that ResourceMonitor works."""
        monitor = ResourceMonitor()
        usage = monitor.get_current_usage()
        
        assert usage.cpu_percent >= 0
        assert usage.memory_percent >= 0
        assert usage.disk_percent >= 0


class TestRemote:
    """Test the remote configuration functionality."""
    
    def test_is_remote_url(self):
        """Test the is_remote_url function."""
        assert RemoteConfigManager.is_remote_url("https://example.com/config.yaml")
        assert RemoteConfigManager.is_remote_url("http://example.com/config.yaml")
        assert not RemoteConfigManager.is_remote_url("./config.yaml")
        assert not RemoteConfigManager.is_remote_url("~/config.yaml")
    
    def test_resolve_config_path_local(self):
        """Test resolve_config_path with local file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            local_path = f.name
        
        try:
            result = resolve_config_path(local_path)
            assert result == local_path
        finally:
            os.unlink(local_path)


class TestCoreEnhancements:
    """Test enhancements to the core functionality."""
    
    def test_config_with_new_features(self):
        """Test that the configuration supports all new features."""
        config_data = {
            "name": "Test Config",
            "variables": {},
            "system": {"packages": ["git", "curl"]},
            "git": {"repositories": []},
            "dotfiles": [],
            "scripts": [],
            "hooks": {
                "pre_system": [{"command": "echo 'test'", "description": "test hook"}]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            f.flush()
            
            # This should work with schema validation
            config = RigConfig.from_yaml(f.name)
            assert config.name == "Test Config"
            assert len(config.hooks.pre_system) == 1
            
            os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__])