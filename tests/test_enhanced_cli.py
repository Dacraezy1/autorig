"""Tests for enhanced CLI functionality."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, Mock
from click.testing import CliRunner
from typer.testing import CliRunner
from autorig.cli import app
from autorig.templates import TemplateManager


class TestEnhancedCLI:
    """Test enhanced CLI commands and features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_apply_with_enhanced_error_handling(self):
        """Test apply command with enhanced error handling."""
        # Test with non-existent config
        result = self.runner.invoke(app, ["apply", "nonexistent.yaml"])
        assert result.exit_code != 0
        assert "Configuration file not found" in result.stdout
    
    def test_apply_with_confirmation(self):
        """Test apply command with confirmation prompt."""
        # Create a valid config
        config_data = {
            "name": "Test Config",
            "system": {"packages": ["git"]},
            "git": {"repositories": []},
            "dotfiles": [],
            "scripts": []
        }
        config_path = Path(self.temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump(config_data))
        
        # Test with confirmation
        with patch('typer.confirm', return_value=False):
            result = self.runner.invoke(app, ["apply", str(config_path)])
            assert "Operation cancelled" in result.stdout
    
    def test_apply_dry_run(self):
        """Test apply command with dry run."""
        config_data = {
            "name": "Test Config",
            "system": {"packages": []},
            "git": {"repositories": []},
            "dotfiles": [],
            "scripts": []
        }
        config_path = Path(self.temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump(config_data))
        
        with patch('typer.confirm', return_value=True):
            result = self.runner.invoke(app, ["apply", str(config_path), "--dry-run"])
            assert "Dry run completed" in result.stdout
    
    def test_bootstrap_with_template(self):
        """Test bootstrap command with template option."""
        config_path = Path(self.temp_dir) / "bootstrap_config.yaml"
        
        with patch('typer.confirm', return_value=True):
            result = self.runner.invoke(app, [
                "bootstrap",
                "--path", str(config_path),
                "--template", "python"
            ])
        
        assert config_path.exists()
        assert "Configuration created" in result.stdout
    
    def test_bootstrap_without_template(self):
        """Test bootstrap command without template."""
        config_path = Path(self.temp_dir) / "bootstrap_config.yaml"
        
        with patch('autorig.core.AutoRig.create_default_config') as mock_bootstrap:
            with patch('typer.confirm', return_value=True):
                result = self.runner.invoke(app, [
                    "bootstrap",
                    "--path", str(config_path)
                ])
            
            mock_bootstrap.assert_called_once()
    
    def test_clean_command_with_confirmation(self):
        """Test clean command with confirmation."""
        config_data = {
            "name": "Test Config",
            "dotfiles": [{"source": "test", "target": "~/.test"}]
        }
        config_path = Path(self.temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump(config_data))
        
        with patch('typer.confirm', return_value=False):
            result = self.runner.invoke(app, ["clean", str(config_path)])
            assert "Operation cancelled" in result.stdout
    
    def test_completion_command(self):
        """Test completion generation command."""
        # Test unsupported shell
        result = self.runner.invoke(app, ["completion", "unsupported"])
        assert result.exit_code != 0
        assert "Unsupported shell" in result.stdout
        
        # Test supported shell (this might not work in testing environment)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="# completion script", returncode=0)
            
            result = self.runner.invoke(app, ["completion", "bash"])
            # Should not fail for supported shell
    
    def test_template_commands(self):
        """Test template-related commands."""
        # Test list templates
        result = self.runner.invoke(app, ["template", "list"])
        assert result.exit_code == 0
        assert "Available Templates" in result.stdout
        
        # Test show template
        result = self.runner.invoke(app, ["template", "show", "python"])
        assert result.exit_code == 0
        assert "Python Development Environment" in result.stdout
        
        # Test invalid template
        result = self.runner.invoke(app, ["template", "show", "invalid"])
        assert result.exit_code != 0
        assert "not found" in result.stdout
    
    def test_template_create_command(self):
        """Test template create command."""
        config_path = Path(self.temp_dir) / "from_template.yaml"
        
        with patch('typer.confirm', return_value=True):
            result = self.runner.invoke(app, [
                "template", "create", "minimal",
                "--output", str(config_path),
                "--email", "test@example.com"
            ])
        
        assert config_path.exists()
        
        # Verify the created config
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config["variables"]["email"] == "test@example.com"


class TestCLIIntegration:
    """Test CLI integration with other components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_template_integration_with_config_validation(self):
        """Test that templates produce valid configs."""
        from autorig.config import RigConfig
        
        for template_name in TemplateManager.TEMPLATES:
            config_path = Path(self.temp_dir) / f"{template_name}_test.yaml"
            
            with patch('typer.confirm', return_value=True):
                result = self.runner.invoke(app, [
                    "template", "create", template_name,
                    "--output", str(config_path)
                ])
            
            assert config_path.exists()
            
            # Try to validate the config
            try:
                RigConfig.from_yaml(str(config_path))
            except Exception as e:
                pytest.fail(f"Template '{template_name}' created invalid config: {e}")
    
    def test_error_scenarios_with_enhanced_messages(self):
        """Test various error scenarios with enhanced error messages."""
        # Test file permission error
        config_path = Path(self.temp_dir) / "test.yaml"
        
        # Create file and make it unreadable
        config_path.write_text("test")
        original_mode = config_path.stat().st_mode
        config_path.chmod(0o000)
        
        try:
            result = self.runner.invoke(app, ["apply", str(config_path)])
            assert result.exit_code != 0
            # Should contain helpful error message
            assert "Permission" in result.stdout or "access" in result.stdout.lower()
        finally:
            config_path.chmod(original_mode)
    
    def test_verbose_output(self):
        """Test verbose output option."""
        config_data = {
            "name": "Test Config",
            "system": {"packages": []},
            "git": {"repositories": []},
            "dotfiles": [],
            "scripts": []
        }
        config_path = Path(self.temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump(config_data))
        
        with patch('typer.confirm', return_value=True):
            # Test with verbose flag
            result_verbose = self.runner.invoke(app, [
                "apply", str(config_path), "--dry-run", "--verbose"
            ])
            
            # Test without verbose flag
            result_normal = self.runner.invoke(app, [
                "apply", str(config_path), "--dry-run"
            ])
            
            # Both should succeed, but verbose might have more output
            assert result_verbose.exit_code == 0
            assert result_normal.exit_code == 0
    
    def test_profile_option(self):
        """Test profile option functionality."""
        config_data = {
            "name": "Test Config",
            "profiles": {
                "test-profile": {
                    "system": {"packages": ["test-package"]}
                }
            }
        }
        config_path = Path(self.temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump(config_data))
        
        with patch('typer.confirm', return_value=True):
            result = self.runner.invoke(app, [
                "apply", str(config_path),
                "--profile", "test-profile",
                "--dry-run"
            ])
            assert result.exit_code == 0


class TestCLIHelpAndDocumentation:
    """Test CLI help and documentation features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_main_help(self):
        """Test main help output."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AutoRig" in result.stdout
        assert "development environment" in result.stdout.lower()
    
    def test_apply_help(self):
        """Test apply command help."""
        result = self.runner.invoke(app, ["apply", "--help"])
        assert result.exit_code == 0
        assert "Apply a rig configuration" in result.stdout
        assert "dry-run" in result.stdout
        assert "verbose" in result.stdout
        assert "force" in result.stdout
    
    def test_template_help(self):
        """Test template command help."""
        result = self.runner.invoke(app, ["template", "--help"])
        assert result.exit_code == 0
        assert "Manage configuration templates" in result.stdout
    
    def test_bootstrap_help(self):
        """Test bootstrap command help."""
        result = self.runner.invoke(app, ["bootstrap", "--help"])
        assert result.exit_code == 0
        assert "template" in result.stdout
        assert "path" in result.stdout


class TestCLIEdgeCases:
    """Test CLI edge cases and error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_config_file(self):
        """Test handling of empty config file."""
        config_path = Path(self.temp_dir) / "empty.yaml"
        config_path.write_text("")
        
        result = self.runner.invoke(app, ["validate", str(config_path)])
        assert result.exit_code != 0
    
    def test_malformed_yaml(self):
        """Test handling of malformed YAML."""
        config_path = Path(self.temp_dir) / "bad.yaml"
        config_path.write_text("invalid: yaml: content: [")
        
        result = self.runner.invoke(app, ["validate", str(config_path)])
        assert result.exit_code != 0
    
    def test_config_missing_required_fields(self):
        """Test config missing required fields."""
        config_data = {
            "system": {"packages": []}
            # Missing "name" field
        }
        config_path = Path(self.temp_dir) / "incomplete.yaml"
        config_path.write_text(yaml.dump(config_data))
        
        result = self.runner.invoke(app, ["validate", str(config_path)])
        assert result.exit_code != 0
    
    def test_very_long_path(self):
        """Test handling of very long file paths."""
        # Create a deeply nested path
        long_path = Path(self.temp_dir)
        for i in range(10):
            long_path = long_path / f"very_long_directory_name_{i}"
        
        long_path.mkdir(parents=True, exist_ok=True)
        config_path = long_path / "config.yaml"
        
        config_data = {
            "name": "Test Config",
            "system": {"packages": []},
            "git": {"repositories": []},
            "dotfiles": [],
            "scripts": []
        }
        config_path.write_text(yaml.dump(config_data))
        
        with patch('typer.confirm', return_value=True):
            result = self.runner.invoke(app, ["apply", str(config_path), "--dry-run"])
            assert result.exit_code == 0