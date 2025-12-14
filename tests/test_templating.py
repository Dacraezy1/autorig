import pytest
from pathlib import Path
from autorig.templating import TemplateRenderer

def test_render_template(tmp_path):
    # Setup
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "test.txt.j2"
    template_file.write_text("Hello {{ name }}!")
    
    output_file = tmp_path / "output.txt"
    
    # Execute
    renderer = TemplateRenderer(template_dir)
    renderer.render("test.txt.j2", {"name": "World"}, output_file)
    
    # Verify
    assert output_file.exists()
    assert output_file.read_text() == "Hello World!"

def test_render_string(tmp_path):
    # Setup
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "config.ini.j2"
    template_file.write_text("user={{ user }}\nemail={{ email }}")
    
    # Execute
    renderer = TemplateRenderer(template_dir)
    result = renderer.render_string("config.ini.j2", {"user": "admin", "email": "admin@example.com"})
    
    # Verify
    assert "user=admin" in result
    assert "email=admin@example.com" in result
