"""Tests for enhanced CLI utilities."""

import pytest
from unittest.mock import patch
from autorig.cli_utils import (
    ErrorHandler,
    EnhancedProgressTracker,
    InfoDisplay,
    CommandTimer,
    format_duration,
    validate_config_exists,
)
import tempfile
import time


class TestErrorHandler:
    """Test the ErrorHandler class."""
    
    def test_format_error_basic(self):
        """Test basic error formatting."""
        error = ValueError("Test error message")
        panel = ErrorHandler.format_error(error)
        
        assert "ValueError" in str(panel.renderable)
        assert "Test error message" in str(panel.renderable)
        assert "Suggestions:" in str(panel.renderable)
    
    def test_format_error_with_traceback(self):
        """Test error formatting with traceback."""
        error = RuntimeError("Runtime error")
        panel = ErrorHandler.format_error(error, show_traceback=True)
        
        assert "RuntimeError" in str(panel.renderable)
        assert "Traceback:" in str(panel.renderable)
    
    def test_format_error_known_type(self):
        """Test formatting for known error types."""
        error = FileNotFoundError("File not found")
        panel = ErrorHandler.format_error(error)
        
        assert "FileNotFoundError" in str(panel.renderable)
        assert "Check if the configuration file exists" in str(panel.renderable)
    
    def test_show_success(self):
        """Test success message formatting."""
        panel = ErrorHandler.show_success("Operation completed", "Details here")
        
        assert "Operation completed" in str(panel.renderable)
        assert "Details here" in str(panel.renderable)
        assert "✅ Success" in str(panel.title)
    
    def test_show_warning(self):
        """Test warning message formatting."""
        panel = ErrorHandler.show_warning("Warning message", "Warning details")
        
        assert "Warning message" in str(panel.renderable)
        assert "Warning details" in str(panel.renderable)
        assert "⚠️ Warning" in str(panel.title)


class TestEnhancedProgressTracker:
    """Test the EnhancedProgressTracker class."""
    
    def test_context_manager(self):
        """Test progress tracker as context manager."""
        with EnhancedProgressTracker() as tracker:
            assert tracker.progress is not None
            task_id = tracker.add_task("Test task", total=10)
            assert task_id is not None
            tracker.update(task_id, advance=5)
            tracker.complete(task_id)
    
    def test_add_task(self):
        """Test adding tasks."""
        with EnhancedProgressTracker() as tracker:
            task_id = tracker.add_task("Test task", total=100)
            assert task_id is not None
    
    def test_eta_disabled(self):
        """Test tracker with ETA disabled."""
        tracker = EnhancedProgressTracker(show_eta=False)
        assert tracker.show_eta is False


class TestInfoDisplay:
    """Test the InfoDisplay class."""
    
    def test_show_summary(self):
        """Test summary display."""
        data = {
            "Name": "Test Config",
            "Packages": 5,
            "Repositories": 2
        }
        
        with patch('autorig.cli_utils.console.print') as mock_print:
            InfoDisplay.show_summary("Test Summary", data)
            mock_print.assert_called()
    
    def test_show_operation_summary(self):
        """Test operation summary display."""
        operations = [
            {"name": "Op1", "success": True, "status": "Completed", "details": "Success"},
            {"name": "Op2", "success": False, "status": "Failed", "details": "Error"},
        ]
        
        with patch('autorig.cli_utils.console.print') as mock_print:
            InfoDisplay.show_operation_summary(operations)
            mock_print.assert_called()
    
    def test_show_configuration_preview(self):
        """Test configuration preview."""
        config_data = {
            "system": {"packages": ["git", "vim"]},
            "git": {"repositories": []},
            "dotfiles": [{"source": "test", "target": "~/.test"}],
            "scripts": [],
            "hooks": {}
        }
        
        with patch('autorig.cli_utils.console.print') as mock_print:
            InfoDisplay.show_configuration_preview(config_data)
            mock_print.assert_called()


class TestCommandTimer:
    """Test the CommandTimer class."""
    
    def test_timer_context_manager(self):
        """Test timer as context manager."""
        with patch('autorig.cli_utils.console.print') as mock_print:
            with CommandTimer("Test operation"):
                time.sleep(0.01)  # Small delay to ensure measurable time
            
            # Check that print was called with timing info
            mock_print.assert_called()
            call_args = str(mock_print.call_args)
            assert "Test operation completed" in call_args
            assert "ms" in call_args or "s" in call_args


class TestFormatDuration:
    """Test the format_duration function."""
    
    def test_format_milliseconds(self):
        """Test formatting sub-second durations."""
        duration = format_duration(0.5)
        assert "500ms" in duration
    
    def test_format_seconds(self):
        """Test formatting seconds."""
        duration = format_duration(5.5)
        assert "5.5s" in duration
    
    def test_format_minutes(self):
        """Test formatting minutes."""
        duration = format_duration(125)  # 2 minutes 5 seconds
        assert "2m" in duration and "5s" in duration
    
    def test_format_hours(self):
        """Test formatting hours."""
        duration = format_duration(3665)  # 1 hour 1 minute 5 seconds
        assert "1h" in duration and "1m" in duration


class TestValidateConfigExists:
    """Test the validate_config_exists function."""
    
    def test_existing_file(self):
        """Test with an existing file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name
        
        try:
            result = validate_config_exists(temp_path)
            assert result.exists()
            assert result.is_file()
        finally:
            import os
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Test with a non-existent file."""
        with pytest.raises(FileNotFoundError):
            validate_config_exists("/nonexistent/path/config.yaml")
    
    def test_directory_instead_of_file(self):
        """Test with a directory instead of a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Configuration path is not a file"):
                validate_config_exists(temp_dir)
    
    def test_unreadable_file(self):
        """Test with an unreadable file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name
        
        try:
            import os
            os.chmod(temp_path, 0o000)  # Remove all permissions
            
            with pytest.raises(PermissionError):
                validate_config_exists(temp_path)
        finally:
            os.chmod(temp_path, 0o644)  # Restore permissions
            os.unlink(temp_path)


class TestErrorScenarios:
    """Test various error scenarios."""
    
    def test_import_error_in_formatter(self):
        """Test ErrorHandler with import-related errors."""
        error = ImportError("No module named 'test'")
        panel = ErrorHandler.format_error(error)
        
        assert "ImportError" in str(panel.renderable)
        assert "No module named 'test'" in str(panel.renderable)
    
    def test_permission_error_with_details(self):
        """Test PermissionError formatting."""
        error = PermissionError("Permission denied: /etc/config")
        panel = ErrorHandler.format_error(error)
        
        assert "PermissionError" in str(panel.renderable)
        assert "sudo" in str(panel.renderable) or "permissions" in str(panel.renderable)
    
    def test_connection_error(self):
        """Test network connection error."""
        error = ConnectionError("Failed to connect")
        panel = ErrorHandler.format_error(error)
        
        assert "ConnectionError" in str(panel.renderable)
        assert "internet connection" in str(panel.renderable).lower()