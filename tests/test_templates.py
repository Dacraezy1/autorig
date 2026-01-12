"""Tests for the template system."""

import pytest
import tempfile
import yaml
import click
from pathlib import Path
from unittest.mock import patch
from autorig.templates import TemplateManager


class TestTemplateManager:
    """Test the TemplateManager class."""

    def test_list_templates(self):
        """Test listing available templates."""
        with patch("autorig.templates.console.print") as mock_print:
            TemplateManager.list_templates()
            mock_print.assert_called()

    def test_get_valid_template(self):
        """Test getting a valid template."""
        config = TemplateManager.get_template("python")

        assert config["name"] == "Python Development Environment"
        assert "system" in config
        assert "packages" in config["system"]
        assert "git" in config
        assert "dotfiles" in config
        assert "scripts" in config
        assert "variables" in config

    def test_get_template_python(self):
        """Test Python template specifically."""
        config = TemplateManager.get_template("python")

        # Check Python-specific packages
        packages = config["system"]["packages"]
        assert "python3" in packages
        assert "python3-pip" in packages
        assert "python3-venv" in packages

        # Check Python-specific scripts
        scripts = config["scripts"]
        script_commands = [s["command"] for s in scripts]
        assert any("venv" in cmd for cmd in script_commands)
        assert any("black" in cmd for cmd in script_commands)
        assert any("flake8" in cmd for cmd in script_commands)

    def test_get_template_web(self):
        """Test Web development template."""
        config = TemplateManager.get_template("web")

        packages = config["system"]["packages"]
        assert "nodejs" in packages
        assert "npm" in packages

        scripts = config["scripts"]
        script_commands = [s["command"] for s in scripts]
        assert any("create-react-app" in cmd for cmd in script_commands)
        assert any("@vue/cli" in cmd for cmd in script_commands)

    def test_get_template_golang(self):
        """Test Go development template."""
        config = TemplateManager.get_template("golang")

        scripts = config["scripts"]
        script_commands = [s["command"] for s in scripts]
        assert any("go.dev" in cmd for cmd in script_commands)
        assert any("golangci-lint" in cmd for cmd in script_commands)

    def test_get_template_rust(self):
        """Test Rust development template."""
        config = TemplateManager.get_template("rust")

        packages = config["system"]["packages"]
        assert "build-essential" in packages

        scripts = config["scripts"]
        script_commands = [s["command"] for s in scripts]
        assert any("rustup.rs" in cmd for cmd in script_commands)
        assert any("cargo-watch" in cmd for cmd in script_commands)

    def test_get_template_data_science(self):
        """Test Data Science template."""
        config = TemplateManager.get_template("data-science")

        packages = config["system"]["packages"]
        assert "python3-dev" in packages

        scripts = config["scripts"]
        script_commands = [s["command"] for s in scripts]
        assert any("jupyter" in cmd for cmd in script_commands)
        assert any("pandas" in cmd for cmd in script_commands)
        assert any("matplotlib" in cmd for cmd in script_commands)

    def test_get_template_minimal(self):
        """Test Minimal template."""
        config = TemplateManager.get_template("minimal")

        packages = config["system"]["packages"]
        assert "git" in packages
        assert "vim" in packages
        assert "tmux" in packages

        # Should have minimal setup
        dotfiles = config["dotfiles"]
        dotfile_targets = [d["target"] for d in dotfiles]
        assert "~/.gitconfig" in dotfile_targets
        assert "~/.vimrc" in dotfile_targets
        assert "~/.tmux.conf" in dotfile_targets

    def test_get_invalid_template(self):
        """Test getting an invalid template."""
        with pytest.raises(ValueError, match="Template 'invalid' not found"):
            TemplateManager.get_template("invalid")

    def test_create_config_from_template(self):
        """Test creating a configuration from template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_config.yaml"

            with patch("typer.confirm", return_value=True):
                TemplateManager.create_config_from_template("python", str(output_path))

            assert output_path.exists()

            # Load and verify the created config
            with open(output_path) as f:
                config = yaml.safe_load(f)

            assert config["name"] == "Python Development Environment"
            assert "system" in config
            assert "packages" in config["system"]

    def test_create_config_with_variables(self):
        """Test creating config with custom variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_config.yaml"

            variables = {"email": "custom@example.com", "python_version": "3.12"}

            with patch("typer.confirm", return_value=True):
                TemplateManager.create_config_from_template(
                    "python", str(output_path), variables
                )

            with open(output_path) as f:
                config = yaml.safe_load(f)

            assert config["variables"]["email"] == "custom@example.com"
            assert config["variables"]["python_version"] == "3.12"

    def test_create_config_overwrite_protection(self):
        """Test that existing files are protected by default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_config.yaml"

            # Create an existing file
            output_path.write_text("existing content")

            with patch("typer.confirm", return_value=False):
                TemplateManager.create_config_from_template("minimal", str(output_path))

            # File should remain unchanged
            assert output_path.read_text() == "existing content"

    def test_show_template_preview(self):
        """Test showing template preview."""
        with patch("autorig.templates.console.print") as mock_print:
            TemplateManager.show_template_preview("python")
            mock_print.assert_called()

    def test_show_invalid_template_preview(self):
        """Test preview of invalid template."""
        with pytest.raises(click.exceptions.Exit):
            TemplateManager.show_template_preview("nonexistent")


class TestTemplateValidation:
    """Test template validation and structure."""

    def test_all_templates_have_required_fields(self):
        """Test that all templates have required fields."""
        for template_name in TemplateManager.TEMPLATES:
            template = TemplateManager.TEMPLATES[template_name]

            assert "name" in template
            assert "description" in template
            assert "config" in template

            config = template["config"]
            assert "name" in config
            assert "variables" in config
            assert "system" in config
            assert "dotfiles" in config
            assert "scripts" in config

    def test_all_templates_have_descriptions(self):
        """Test that all templates have descriptions."""
        for template_name, template in TemplateManager.TEMPLATES.items():
            assert (
                len(template["description"]) > 10
            ), f"{template_name} description too short"

    def test_template_variables(self):
        """Test that templates have sensible default variables."""
        for template_name in TemplateManager.TEMPLATES:
            if template_name == "minimal":
                continue  # Minimal template is intentionally basic

            config = TemplateManager.get_template(template_name)
            variables = config["variables"]

            # Most templates should have these common variables
            if template_name in ["python", "web", "golang", "rust", "data-science"]:
                assert "email" in variables, f"{template_name} missing email variable"
                assert (
                    "@" in variables["email"]
                ), f"{template_name} email not a valid email"


class TestTemplateIntegration:
    """Test template integration with the broader system."""

    def test_template_config_validates(self):
        """Test that template configs are valid."""
        from autorig.config import RigConfig

        with tempfile.TemporaryDirectory() as temp_dir:
            for template_name in TemplateManager.TEMPLATES:
                # Create temp config file
                config_path = Path(temp_dir) / f"{template_name}.yaml"

                with patch("typer.confirm", return_value=True):
                    TemplateManager.create_config_from_template(
                        template_name, str(config_path)
                    )

                # Try to load with RigConfig
                try:
                    RigConfig.from_yaml(str(config_path))
                except Exception as e:
                    pytest.fail(f"Template '{template_name}' failed validation: {e}")

    def test_template_scripts_are_safe(self):
        """Test that template scripts don't contain obviously dangerous commands."""
        dangerous_patterns = [
            "rm -rf /",
            "sudo rm",
            ":(){ :|:& };:",  # fork bomb
            "dd if=",
            "mkfs.",
            "format",
        ]

        for template_name in TemplateManager.TEMPLATES:
            config = TemplateManager.get_template(template_name)
            scripts = config["scripts"]

            for script in scripts:
                command = script["command"]
                for pattern in dangerous_patterns:
                    assert (
                        pattern not in command
                    ), f"Dangerous pattern '{pattern}' in {template_name} template"

    def test_template_packages_are_common(self):
        """Test that templates use reasonably common packages."""
        # This is a basic sanity check - templates shouldn't use obscure packages
        for template_name in TemplateManager.TEMPLATES:
            config = TemplateManager.get_template(template_name)
            packages = config["system"]["packages"]

            for package in packages:
                # Basic sanity check - packages should be alphanumeric with common separators
                assert all(
                    c.isalnum() or c in "-._+" for c in package
                ), f"Invalid package name: {package}"
