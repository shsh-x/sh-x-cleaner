from enum import Enum
from pathlib import Path
from typing import TypedDict


class OSUGameModes(Enum):
    """Enum describing the game modes."""
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3


class CleanerParams(TypedDict):
    user_images: dict[str, str | Path] | None
    delete_images: bool
    delete_modes: list[OSUGameModes]
    force_clean: bool
    keep_videos: bool
    ignore_id_limit: bool
    dangerous_clean_no_id: bool
