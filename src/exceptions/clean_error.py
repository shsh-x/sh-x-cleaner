from pathlib import Path


class CleanError(Exception):
    def __init__(
        self,
        base_exception: Exception,
        folder: Path,
        file: str | None = None
    ):
        msg = (
            f"Folder: {folder}\n"
            f"File: {file}\n" if file else ""
            f"{base_exception}"
        )
        super().__init__(msg)
        self.base_exception = base_exception
        self.folder = folder
        self.file = file
