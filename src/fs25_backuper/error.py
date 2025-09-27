class BackuperError(Exception):
    """Base exception for fs25_backuper"""

    pass


class ConfigurationError(BackuperError):
    """Raised when there's an error in configuration"""

    pass


class DownloadError(BackuperError):
    """Raised when download fails"""

    pass


class AuthenticationError(BackuperError):
    """Raised when authentication fails"""

    pass


class UploadError(BackuperError):
    """Raised when upload fails"""

    pass
