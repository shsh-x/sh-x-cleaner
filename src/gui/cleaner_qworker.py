import traceback
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from ..app.cleaner import Cleaner, CleanerParams
from ..exceptions import CleanError, OSUParsingError


class CleanerWorkerThread(QThread):
    """
    A dedicated QThread to run the cleaning process in the background.

    This is crucial for preventing the main GUI from freezing while the application
    is performing intensive file I/O operations. It communicates its status back
    to the main thread using Qt's signal and slot mechanism.
    """
    # --- Signals ---
    # Emitted for each folder processed, carrying the beatmap ID (or -1 for skips).
    progress = pyqtSignal(int)
    # Emitted once when the entire cleaning process completes successfully.
    finished = pyqtSignal()
    # Emitted if any exception occurs during the cleaning process.
    error_occured = pyqtSignal(str)

    def __init__(
        self,
        songs_folder: Path,
        params: CleanerParams,
        folders: list[Path]
    ):
        super().__init__()
        # The lambda function here is a simple way to connect the Cleaner's
        # progress callback directly to this thread's `progress` signal.
        self.cleaner = Cleaner(
            songs_folder,
            params,
            lambda folder_id: self.progress.emit(folder_id)
        )
        self.folders = folders

    def run(self):
        """
        The main entry point for the thread's execution. This method is called
        when `thread.start()` is invoked.
        """
        try:
            self.cleaner.start_clean(self.folders)
            self.finished.emit()
        except (CleanError, OSUParsingError) as e:
            # For our custom, expected errors, print the formatted message
            # and also the traceback of the original underlying exception.
            base_ex = e.base_exception
            print(e)
            traceback.print_exception(type(base_ex), base_ex, base_ex.__traceback__)
            self.error_occured.emit(str(e))
        except Exception as e:
            # For any other unexpected errors, print the full traceback.
            traceback.print_exception(type(e), e, e.__traceback__)
            self.error_occured.emit(str(e))
