class AutoRigError(Exception):
    """Base exception for AutoRig."""

    pass


class ConfigError(AutoRigError):
    """Raised when configuration is invalid."""

    pass


class InstallError(AutoRigError):
    """Raised when installation fails."""

    pass
