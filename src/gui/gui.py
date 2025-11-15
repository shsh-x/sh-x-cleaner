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

font_path = get_resource_path("assets/Exo2.ttf")


class BackgroundModes(Enum):
    """Enum describing the background replacement modes."""
    KEEP = "Keep"
    WHITE = "White"
    CUSTOM = "Custom"
    DELETE = "Delete"


class SHXCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("sh(x)cleaner")
        icon = QIcon(get_resource_path("assets/icon.ico"))
        self.setWindowIcon(icon)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.init_components()

        self.center_window(320, 250)
        self.setStyleSheet(f"QWidget {{ font-family: {font_family};}}")

    def init_components(self):
        """Initializes the GUI components."""
        # Main window widget
        self.central_widget = QWidget(self)
        centra_widget_layout = QVBoxLayout()
        centra_widget_layout.setContentsMargins(0, 0, 0, 0)
        centra_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.central_widget.setLayout(centra_widget_layout)
        self.central_widget.setStyleSheet("")
        self.setCentralWidget(self.central_widget)

        # Add the custom title bar
        self.title_bar = TitleBar(self)
        centra_widget_layout.addWidget(self.title_bar)

        # Main application layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        centra_widget_layout.addLayout(self.main_layout)

        # Frames
        self.top_frame = QHBoxLayout()
        self.main_layout.addLayout(self.top_frame)

        self.left_frame = QVBoxLayout()
        self.top_frame.addLayout(self.left_frame)

        self.right_frame = QVBoxLayout()
        self.top_frame.addLayout(self.right_frame)

        # Delete modes
        self.delete_modes_label = QLabel("Delete modes")
        self.delete_modes_label.setStyleSheet(
            "font-size: 15px; margin-bottom: 4px;"
        )
        self.delete_modes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_frame.addWidget(self.delete_modes_label)

        self.delete_modes_group = QButtonGroup()
        self.delete_modes_group.setExclusive(False)
        self.osu_var = QPushButton("Osu!")
        self.taiko_var = QPushButton("Taiko")
        self.catch_var = QPushButton("Catch")
        self.mania_var = QPushButton("Mania")

        for button in [
            self.osu_var,
            self.taiko_var,
            self.catch_var,
            self.mania_var
        ]:
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding-top: 4px;
                    padding-bottom: 6px;
                    border-radius: 4px;
                    background-color: #EDEDF4;
                }
                QPushButton:hover {background-color: #E9E9F1}
                QPushButton:checked {
                    background-color: #D6E3FF;
                    color: #001B3E;
                }
                QPushButton:checked::hover {
                    background-color: #D2DFFB;
                    color: #001B3E;
                }
            """)
            self.delete_modes_group.addButton(button)
            self.left_frame.addWidget(button)

        # Backgrounds
        self.backgrounds_label = QLabel("Backgrounds")
        self.backgrounds_label.setStyleSheet(
            "font-size: 15px; margin-bottom: 4px;")
        self.backgrounds_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_frame.addWidget(self.backgrounds_label)

        self.backgrounds_group = QButtonGroup()
        self.backgrounds_group.setExclusive(True)
        self.keep_var = QPushButton("Keep")
        self.white_var = QPushButton("White")
        self.custom_var = QPushButton("Custom")
        self.delete_var = QPushButton("Delete")

        for button in [
            self.keep_var,
            self.white_var,
            self.custom_var,
            self.delete_var
        ]:
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding-top: 4px;
                    padding-bottom: 6px;
                    border-radius: 4px;
                    background-color: #EDEDF4;
                }
                QPushButton:hover {background-color: #E9E9F1}
                QPushButton:checked {
                    background-color: #D6E3FF;
                    color: #001B3E;
                }
                QPushButton:checked::hover {
                    background-color: #D2DFFB;
                    color: #001B3E;
                }
            """)
            self.backgrounds_group.addButton(button)
            self.right_frame.addWidget(button)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 30px;
                border-radius: 4px;
                font-size: 17px;
                text-align: center;
                font-weight: 500;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background-color: #BED1FA;
            }
        """)
        self.main_layout.addWidget(self.progress)
        # D e s t r o y   e v e r y t h i n g
        self.start_button = QPushButton("Destroy everything")
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                background-color: #D6E3FF;
                color: #001B3E;
            }
            QPushButton:hover {
                background-color: #D2DFFB;
            }
        """)
        self.start_button.clicked.connect(self.start_cleaning)
        self.main_layout.addWidget(self.start_button)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.check_updates)

    def check_updates(self):
        is_update_available, latest_version = check_for_updates()
        if not is_update_available:
            return

        mbox_result = QMessageBox.information(
            self,
            "Update available",
            (
                f"A new version is available: {latest_version}\n"
                "Do you want to open the release page?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if mbox_result != QMessageBox.StandardButton.Yes:
            return

        import webbrowser
        webbrowser.open(REPO_RELEASE_URL)

    def center_window(self, width, height):
        """Centers the application window on the screen."""
        if not (screen := QApplication.primaryScreen()):
            return

        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def pick_params(self) -> CleanerParams:
        """Gathers the cleaning parameters from the GUI."""
        user_images: dict[str, str] | None = None
        delete_images: bool = False
        delete_modes: list[OSUGameModes] = []

        # Background options
        if self.keep_var.isChecked():
            user_images = None
            delete_images = False
        elif self.white_var.isChecked():
            user_images = {
                ".png": get_resource_path("assets/white.png"),
                ".jpg": get_resource_path("assets/white.jpg"),
                ".jpeg": get_resource_path("assets/white.jpg")
            }
            delete_images = False
        elif self.delete_var.isChecked():
            user_images = None
            delete_images = True
        elif self.custom_var.isChecked():
            user_images = {}
            delete_images = False

            png_file, _ = QFileDialog.getOpenFileName(
                self, "Select PNG Image", None, "PNG Files (*.png)"
            )
            if png_file:
                user_images['.png'] = png_file
            jpg_file, _ = QFileDialog.getOpenFileName(
                self, "Select JPEG Image", "", "JPEG Files (*.jpg *.jpeg)"
            )
            if jpg_file:
                user_images['.jpg'] = jpg_file
                user_images['.jpeg'] = jpg_file

            if not user_images:
                user_images = None

        # Game mode options
        if self.osu_var.isChecked():
            delete_modes.append(OSUGameModes.OSU)
        if self.taiko_var.isChecked():
            delete_modes.append(OSUGameModes.TAIKO)
        if self.catch_var.isChecked():
            delete_modes.append(OSUGameModes.CATCH)
        if self.mania_var.isChecked():
            delete_modes.append(OSUGameModes.MANIA)

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
        """Performs final preparations and starts the cleaning process."""
        osu_exe_path_str, _ = QFileDialog.getOpenFileName(
            self, "Select osu!.exe", "", "osu! executable (osu!.exe)"
        )
        if not osu_exe_path_str:
            return

        osu_exe_path = Path(osu_exe_path_str)
        if osu_exe_path.name.lower() != "osu!.exe":
            QMessageBox.critical(
                self, "Error", "You must select the osu!.exe file."
            )
            return

        songs_folder_path = osu_exe_path.parent.joinpath("Songs")
        if not songs_folder_path.is_dir():
            QMessageBox.critical(
                self,
                "Error",
                "Could not find the 'Songs' folder in the same directory as osu!.exe."
            )
            return

        params = self.pick_params()
        if len(params['delete_modes']) == 4:
            QMessageBox.critical(
                self,
                "Error",
                "You can delete your songs folder manually if you want to."
            )
            return

        # Get all subfolders
        folders = [f for f in songs_folder_path.iterdir() if f.is_dir()]
        self.progress.setMaximum(len(folders))
        self.progress.setValue(0)

        self.start_button.setEnabled(False)

        self.worker_thread = CleanerWorkerThread(
            songs_folder_path.resolve(), params, folders
        )
        self.worker_thread.progress.connect(self.__update_progress)
        self.worker_thread.finished.connect(self.__on_cleaning_finished)
        self.worker_thread.error_occured.connect(self.__on_cleaning_error)
        self.worker_thread.start()

    def __update_progress(self, folder_id: int):
        self.progress.setValue(self.progress.value() + 1)
        # Don't set the beatmap ID in the progress bar if the ID is -1
        if folder_id != -1:
            self.progress.setFormat(str(folder_id))

    def __on_cleaning_finished(self):
        QMessageBox.information(
            self,
            "Done!",
            "Everything's clean. Check the size of your songs folder lol"
        )
        self.close()

    def __on_cleaning_error(self, msg: str):
        QMessageBox.critical(
            self,
            "An error occurred",
            f"An error occurred (for more info look terminal):\n{msg}"
        )
        self.close()
