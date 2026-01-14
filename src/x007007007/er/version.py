"""Version utilities for ER Diagram Converter."""

from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    """
    Get package version from installed metadata.
    
    Returns:
        str: Package version string, or "unknown" if not installed
    """
    try:
        return version("x007007007-er")
    except PackageNotFoundError:
        return "unknown"


__version__ = get_version()
