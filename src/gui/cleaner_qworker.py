from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from ..app.cleaner import Cleaner, CleanerParams


class CleanerWorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error_occured = pyqtSignal(Exception)

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
        except Exception as e:
            self.error_occured.emit(e)
