import traceback
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from ..app.cleaner import Cleaner, CleanerParams
from ..exceptions import CleanError, OSUParsingError


class CleanerWorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error_occured = pyqtSignal(str)

    def __init__(
        self,
        songs_folder: Path,
        params: CleanerParams,
        folders: list[Path]
    ):
        super().__init__()
        self.cleaner = Cleaner(
            songs_folder,
            params,
            lambda folder_id: self.progress.emit(folder_id)
        )
        self.folders = folders

    def run(self):
        try:
            self.cleaner.start_clean(self.folders)
            self.finished.emit()
        except (CleanError, OSUParsingError) as e:
            base_ex = e.base_exception
            print(e)
            traceback.print_exception(
                type(base_ex), base_ex, base_ex.__traceback__
            )
            self.error_occured.emit(str(e))
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            self.error_occured.emit(str(e))
