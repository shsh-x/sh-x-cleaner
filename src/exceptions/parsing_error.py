from pathlib import Path


class OSUParsingError(Exception):
    def __init__(
        self,
        base_exception: Exception,
        file: Path
    ):
        msg = (f"File: {file}\n{base_exception}")
        super().__init__(msg)
        self.base_exception = base_exception
        self.file = file
