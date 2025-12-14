import os
import pytest
from autorig.config import RigConfig

def test_load_valid_config(config_file):
    """Test loading a standard valid configuration."""
    config = RigConfig.from_yaml(config_file)
    
    assert config.name == "Test Rig"
    assert config.variables["user"] == "testuser"
    assert "git" in config.system.packages
    assert len(config.git.repositories) == 1
    assert config.git.repositories[0].path == "~/test/repo"

def test_env_var_expansion(tmp_path):
    """Test that ${VAR} is expanded in the config."""
    content = """
    name: "Env Test"
    variables:
      home: "${HOME}"
    """
    p = tmp_path / "env_rig.yaml"
    p.write_text(content)
    
    # Ensure we test against the actual env var
    config = RigConfig.from_yaml(str(p))
    assert config.variables["home"] == os.environ.get("HOME", "")