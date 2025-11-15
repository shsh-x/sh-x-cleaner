import os
from enum import Enum
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QFileDialog,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)

from ..app.types import CleanerParams
from ..app.osu_parser import OSUGameModes
from ..app.version import REPO_RELEASE_URL, check_for_updates
from ..utils import get_resource_path
from .cleaner_qworker import CleanerWorkerThread
from .title_bar import TitleBar

# Load the font globally for the application.
font_path = get_resource_path("assets/Exo2.ttf")


class BackgroundModes(Enum):
    """Defines the available options for handling beatmap backgrounds."""
    KEEP = "Keep"
    WHITE = "White"
    CUSTOM = "Custom"
    DELETE = "Delete"


class SHXCleanerApp(QMainWindow):
    """The main application window."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("sh(x)cleaner")
        self.setWindowIcon(QIcon(get_resource_path("assets/icon.ico")))
        
        # A frameless window allows for a custom title bar and rounded corners.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # This attribute is crucial for enabling transparency, which allows
        # the border-radius set in the QSS to render correctly without artifacts.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.init_components()

        self.center_window(320, 250)
        self.setStyleSheet(f"QWidget {{ font-family: {font_family};}}")

    def init_components(self):
        """Initializes and lays out all GUI components."""
        # The central widget is the main container for all other widgets.
        # It's given an object name so it can be styled with an ID selector in QSS.
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("centralWidget")
        centra_widget_layout = QVBoxLayout()
        centra_widget_layout.setContentsMargins(0, 0, 0, 0)
        centra_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.central_widget.setLayout(centra_widget_layout)
        self.setCentralWidget(self.central_widget)

        # The custom title bar replaces the default OS one.
        self.title_bar = TitleBar(self)
        centra_widget_layout.addWidget(self.title_bar)

        # This is the main layout for the user-interactive parts of the app.
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        centra_widget_layout.addLayout(self.main_layout)

        # --- UI Sections (Delete Modes, Backgrounds) ---
        self.top_frame = QHBoxLayout()
        self.main_layout.addLayout(self.top_frame)

        self.left_frame = QVBoxLayout()
        self.top_frame.addLayout(self.left_frame)

        self.right_frame = QVBoxLayout()
        self.top_frame.addLayout(self.right_frame)

        # --- "Delete modes" Section ---
        self.delete_modes_label = QLabel("Delete modes")
        self.delete_modes_label.setStyleSheet("font-size: 15px; margin-bottom: 4px;")
        self.delete_modes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_frame.addWidget(self.delete_modes_label)

        self.delete_modes_group = QButtonGroup()
        self.delete_modes_group.setExclusive(False) # Allow multiple modes to be selected
        self.osu_var = QPushButton("Osu!")
        self.taiko_var = QPushButton("Taiko")
        self.catch_var = QPushButton("Catch")
        self.mania_var = QPushButton("Mania")

        for button in [self.osu_var, self.taiko_var, self.catch_var, self.mania_var]:
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 18px; padding-top: 4px; padding-bottom: 6px;
                    border-radius: 4px; background-color: #EDEDF4;
                }
                QPushButton:hover { background-color: #E9E9F1; }
                QPushButton:checked { background-color: #D6E3FF; color: #001B3E; }
                QPushButton:checked::hover { background-color: #D2DFFB; color: #001B3E; }
            """)
            self.delete_modes_group.addButton(button)
            self.left_frame.addWidget(button)

        # --- "Backgrounds" Section ---
        self.backgrounds_label = QLabel("Backgrounds")
        self.backgrounds_label.setStyleSheet("font-size: 15px; margin-bottom: 4px;")
        self.backgrounds_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_frame.addWidget(self.backgrounds_label)

        self.backgrounds_group = QButtonGroup()
        self.backgrounds_group.setExclusive(True) # Only one background option can be active
        self.keep_var = QPushButton("Keep")
        self.white_var = QPushButton("White")
        self.custom_var = QPushButton("Custom")
        self.delete_var = QPushButton("Delete")

        for button in [self.keep_var, self.white_var, self.custom_var, self.delete_var]:
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 18px; padding-top: 4px; padding-bottom: 6px;
                    border-radius: 4px; background-color: #EDEDF4;
                }
                QPushButton:hover { background-color: #E9E9F1; }
                QPushButton:checked { background-color: #D6E3FF; color: #001B3E; }
                QPushButton:checked::hover { background-color: #D2DFFB; color: #001B3E; }
            """)
            self.backgrounds_group.addButton(button)
            self.right_frame.addWidget(button)

        # --- Progress Bar and Start Button ---
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 30px; border-radius: 4px; font-size: 17px;
                text-align: center; font-weight: 500;
            }
            QProgressBar::chunk { border-radius: 4px; background-color: #BED1FA; }
        """)
        self.main_layout.addWidget(self.progress)

        self.start_button = QPushButton("Clean it up!")
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 16px; padding: 10px 20px; border: none;
                border-radius: 4px; background-color: #D6E3FF; color: #001B3E;
            }
            QPushButton:hover { background-color: #D2DFFB; }
        """)
        self.start_button.clicked.connect(self.start_cleaning)
        self.main_layout.addWidget(self.start_button)

    def showEvent(self, event):
        """When the window is first shown, trigger the update check."""
        super().showEvent(event)
        # Use a single shot timer to ensure the main event loop has started
        # before we potentially block on a network request.
        QTimer.singleShot(0, self.check_updates)

    def check_updates(self):
        """Checks for a new version on GitHub and prompts the user if one is found."""
        is_update_available, latest_version = check_for_updates()
        if not is_update_available:
            return

        mbox_result = QMessageBox.information(
            self, "Update available",
            f"A new version is available: {latest_version}\n"
            "Do you want to open the release page?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if mbox_result == QMessageBox.StandardButton.Yes:
            import webbrowser
            webbrowser.open(REPO_RELEASE_URL)

    def center_window(self, width, height):
        """Centers the application window on the primary screen."""
        if not (screen := QApplication.primaryScreen()):
            return
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def pick_params(self) -> CleanerParams:
        """Collects all user-selected settings from the UI into a dictionary."""
        user_images: dict[str, str | Path] | None = None
        delete_images: bool = False

        # --- Background Options ---
        if self.white_var.isChecked():
            user_images = {
                ".png": get_resource_path("assets/white.png"),
                ".jpg": get_resource_path("assets/white.jpg"),
                ".jpeg": get_resource_path("assets/white.jpg")
            }
        elif self.delete_var.isChecked():
            delete_images = True
        elif self.custom_var.isChecked():
            user_images = {}
            png_file, _ = QFileDialog.getOpenFileName(self, "Select PNG Image", "", "PNG Files (*.png)")
            if png_file:
                user_images['.png'] = png_file
            jpg_file, _ = QFileDialog.getOpenFileName(self, "Select JPEG Image", "", "JPEG Files (*.jpg *.jpeg)")
            if jpg_file:
                user_images['.jpg'] = jpg_file
                user_images['.jpeg'] = jpg_file
            if not user_images:
                user_images = None # If user cancels both dialogs, do nothing.

        # --- Game Mode Options ---
        delete_modes: list[OSUGameModes] = []
        if self.osu_var.isChecked(): delete_modes.append(OSUGameModes.OSU)
        if self.taiko_var.isChecked(): delete_modes.append(OSUGameModes.TAIKO)
        if self.catch_var.isChecked(): delete_modes.append(OSUGameModes.CATCH)
        if self.mania_var.isChecked(): delete_modes.append(OSUGameModes.MANIA)

        # --- Combine all parameters ---
        return {
            "user_images": user_images,
            "delete_images": delete_images,
            "delete_modes": delete_modes,
            "force_clean": self.title_bar.force_clean,
            "keep_videos": self.title_bar.keep_videos,
            "ignore_id_limit": self.title_bar.ignore_id_limit,
            "dangerous_clean_no_id": self.title_bar.dangerous_clean_no_id,
        }

    def start_cleaning(self):
        """
        The main entry point for the cleaning process. It handles file dialogs,
        gathers parameters, and starts the background worker thread.
        """
        osu_exe_path_str, _ = QFileDialog.getOpenFileName(
            self, "Select osu!.exe", "", "osu! executable (osu!.exe)"
        )
        if not osu_exe_path_str:
            return # User cancelled the dialog.

        osu_exe_path = Path(osu_exe_path_str)
        if osu_exe_path.name.lower() != "osu!.exe":
            QMessageBox.critical(self, "Error", "You must select the osu!.exe file.")
            return

        songs_folder_path = osu_exe_path.parent / "Songs"
        if not songs_folder_path.is_dir():
            QMessageBox.critical(
                self, "Error",
                "Could not find the 'Songs' folder in the same directory as osu!.exe."
            )
            return

        params = self.pick_params()
        # A simple safeguard against accidentally deleting all difficulties.
        if len(params['delete_modes']) == 4:
            QMessageBox.critical(
                self, "Error",
                "You can delete your songs folder manually if you want to."
            )
            return

        folders = [f for f in songs_folder_path.iterdir() if f.is_dir()]
        self.progress.setMaximum(len(folders))
        self.progress.setValue(0)
        self.start_button.setEnabled(False)

        # The CleanerWorkerThread runs the actual cleaning logic in the background
        # to prevent the GUI from freezing.
        self.worker_thread = CleanerWorkerThread(
            songs_folder_path.resolve(), params, folders
        )
        self.worker_thread.progress.connect(self.__update_progress)
        self.worker_thread.finished.connect(self.__on_cleaning_finished)
        self.worker_thread.error_occured.connect(self.__on_cleaning_error)
        self.worker_thread.start()

    def __update_progress(self, folder_id: int):
        """Updates the progress bar. Connected to the worker's 'progress' signal."""
        self.progress.setValue(self.progress.value() + 1)
        # A folder_id of -1 is a signal for a skipped or invalid folder.
        if folder_id != -1:
            self.progress.setFormat(str(folder_id))

    def __on_cleaning_finished(self):
        """Called when the worker thread successfully finishes."""
        QMessageBox.information(
            self, "Done!",
            "Everything's clean. Check the size of your songs folder lol"
        )
        self.close()

    def __on_cleaning_error(self, msg: str):
        """Called if the worker thread encounters an unhandled exception."""
        QMessageBox.critical(
            self, "An error occurred",
            f"An error occurred (for more info look terminal):\n{msg}"
        )
        self.close()
