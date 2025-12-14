import pytest
import os
import tarfile
from pathlib import Path
from autorig.backup import BackupManager
from autorig.config import RigConfig, Dotfile

# Mock RigConfig to avoid loading full config
class MockConfig:
    def __init__(self, name, dotfiles):
        self.name = name
        self.dotfiles = dotfiles

def test_backup_create_and_restore(tmp_path):
    # Setup directories
    backup_dir = tmp_path / "backups"
    
    # Setup dummy dotfiles
    source_dir = tmp_path / "home"
    source_dir.mkdir()
    file1 = source_dir / ".bashrc"
    file1.write_text("alias ll='ls -l'")
    
    # Config pointing to these files
    # We use absolute paths for target
    dotfiles = [
        Dotfile(source="bashrc", target=str(file1))
    ]
    config = MockConfig(name="TestBackup", dotfiles=dotfiles)
    
    # Initialize Manager
    manager = BackupManager(config, backup_dir=str(backup_dir))
    
    # 1. Create Snapshot
    snapshot_path = manager.create_snapshot()
    
    assert snapshot_path.exists()
    assert tarfile.is_tarfile(snapshot_path)
    
    # Verify content of tar
    with tarfile.open(snapshot_path, "r:gz") as tar:
        # The path stored in tar should be the absolute path without leading slash
        expected_arcname = str(file1).lstrip(os.sep)
        assert expected_arcname in tar.getnames()
    
    # 2. Modify "original" file to simulate loss/change
    file1.write_text("corrupted content")
    
    # 3. Restore
    manager.restore_snapshot(str(snapshot_path))
    
    # Verify restoration
    assert file1.read_text() == "alias ll='ls -l'"

def test_get_latest_snapshot(tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # Create dummy snapshots
    (backup_dir / "backup_20230101-100000.tar.gz").touch()
    latest_file = (backup_dir / "backup_20230102-100000.tar.gz")
    latest_file.touch()
    
    config = MockConfig(name="Test", dotfiles=[])
    manager = BackupManager(config, backup_dir=str(backup_dir))
    
    assert manager.get_latest_snapshot() == latest_file
