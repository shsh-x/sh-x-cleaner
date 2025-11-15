import sys
from pathlib import Path


def get_resource_path(resource_name: str) -> str:
    """
    Gets the resource path. Returns the path to the bundled resource
    or a relative path from the executable.
    """
    # pylint: disable=no-member
    parent = getattr(sys, "_MEIPASS", Path(".").resolve())  # type: ignore
    return str(Path(parent, resource_name))
