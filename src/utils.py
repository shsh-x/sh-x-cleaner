import sys
from pathlib import Path


def get_resource_path(resource_name: str) -> str:
    """
    Gets the absolute path to a resource file (like an image or font).

    This function is essential for PyInstaller compatibility. When the app is
    running as a script, it resolves paths relative to the project directory.
    When bundled into a one-file executable by PyInstaller, it resolves paths
    inside the temporary directory where PyInstaller unpacks the assets.

    `sys._MEIPASS` is a special attribute set by PyInstaller at runtime,
    containing the path to that temporary directory. `getattr` provides a safe
    fallback to the current working directory if `_MEIPASS` doesn't exist.
    """
    # pylint: disable=no-member
    base_path = getattr(sys, "_MEIPASS", Path(".").resolve())  # type: ignore
    return str(Path(base_path) / resource_name)
