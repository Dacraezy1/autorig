import pytest
import yaml


@pytest.fixture
def valid_config_data():
    return {
        "name": "Test Rig",
        "variables": {"user": "testuser"},
        "system": {"packages": ["git", "vim"]},
        "git": {
            "repositories": [
                {"url": "https://github.com/test/repo.git", "path": "~/test/repo"}
            ]
        },
        "dotfiles": [{"source": "bashrc", "target": "~/.bashrc"}],
    }


@pytest.fixture
def config_file(tmp_path, valid_config_data):
    p = tmp_path / "rig.yaml"
    with open(p, "w") as f:
        yaml.dump(valid_config_data, f)
    return str(p)
