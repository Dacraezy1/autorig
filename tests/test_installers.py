from unittest.mock import patch
from autorig.installers.linux import LinuxInstaller
from autorig.installers.macos import MacOSInstaller


@patch("autorig.installers.linux.shutil.which")
@patch("autorig.installers.linux.subprocess.run")
def test_linux_installer_apt(mock_run, mock_which):
    # Setup
    mock_which.side_effect = lambda x: "/usr/bin/apt-get" if x == "apt-get" else None
    installer = LinuxInstaller()

    # Execute
    result = installer.install(["vim", "git"])

    # Verify
    assert result is True
    mock_run.assert_called_once_with(
        ["sudo", "apt-get", "install", "-y", "vim", "git"], check=True
    )


@patch("autorig.installers.linux.shutil.which")
@patch("autorig.installers.linux.subprocess.run")
def test_linux_installer_pacman(mock_run, mock_which):
    # Setup
    mock_which.side_effect = lambda x: "/usr/bin/pacman" if x == "pacman" else None
    installer = LinuxInstaller()

    # Execute
    result = installer.install(["vim"])

    # Verify
    assert result is True
    mock_run.assert_called_once_with(
        ["sudo", "pacman", "-S", "--noconfirm", "vim"], check=True
    )


@patch("autorig.installers.linux.shutil.which")
def test_linux_installer_none(mock_which):
    mock_which.return_value = None
    installer = LinuxInstaller()
    result = installer.install(["vim"])
    assert result is False


@patch("autorig.installers.macos.shutil.which")
@patch("autorig.installers.macos.subprocess.run")
def test_macos_installer(mock_run, mock_which):
    # Setup
    mock_which.return_value = "/usr/local/bin/brew"
    installer = MacOSInstaller()

    # Execute
    result = installer.install(["wget"])

    # Verify
    assert result is True
    mock_run.assert_called_once_with(["brew", "install", "wget"], check=True)


@patch("autorig.installers.macos.shutil.which")
def test_macos_installer_fail(mock_which):
    mock_which.return_value = None
    installer = MacOSInstaller()
    result = installer.install(["wget"])
    assert result is False
