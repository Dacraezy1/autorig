from unittest.mock import patch, MagicMock
from src.autorig.installers.base import get_system_installer
from src.autorig.installers.windows import WindowsInstaller


def test_windows_installer_selection():
    """Test that Windows installer is selected on Windows platform"""
    with patch("platform.system", return_value="Windows"):
        installer = get_system_installer()
        assert isinstance(installer, WindowsInstaller)


def test_windows_installer_install_with_winget():
    """Test Windows installer with winget package manager"""
    installer = WindowsInstaller()

    with patch("src.autorig.installers.windows.shutil.which", return_value=True):
        with patch("src.autorig.installers.windows.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()
            result = installer.install(["package1", "package2"])

            # Check that subprocess was called with the correct command
            assert mock_run.called
            args, kwargs = mock_run.call_args
            assert args[0][:3] == ["winget", "install", "--silent"]
            assert result is True


def test_windows_installer_install_with_choco():
    """Test Windows installer with chocolatey package manager"""
    installer = WindowsInstaller()

    with patch(
        "src.autorig.installers.windows.shutil.which", side_effect=[None, True]
    ):  # winget not found, choco found
        with patch("src.autorig.installers.windows.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()
            result = installer.install(["package1", "package2"])

            # Check that subprocess was called with the correct command
            assert mock_run.called
            args, kwargs = mock_run.call_args
            assert args[0][:2] == ["choco", "install"]
            assert result is True


def test_windows_installer_install_with_scoop():
    """Test Windows installer with scoop package manager"""
    installer = WindowsInstaller()

    # Mock that winget and choco are not found, but scoop is
    def which_side_effect(cmd):
        return cmd == "scoop"

    with patch(
        "src.autorig.installers.windows.shutil.which", side_effect=which_side_effect
    ):
        with patch("src.autorig.installers.windows.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()
            result = installer.install(["package1", "package2"])

            # Check that subprocess was called with the correct command
            assert mock_run.called
            args, kwargs = mock_run.call_args
            assert args[0][:2] == ["scoop", "install"]
            assert result is True


def test_windows_installer_no_package_manager():
    """Test Windows installer when no package manager is found"""
    installer = WindowsInstaller()

    with patch("src.autorig.installers.windows.shutil.which", return_value=None):
        result = installer.install(["package1", "package2"])
        assert result is False
