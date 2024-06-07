import os
from enum import Enum
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QProgressBar, QPushButton, QSizePolicy,
                             QSpacerItem, QVBoxLayout, QWidget)

from ..app.cleaner import Cleaner, CleanerParams
from ..app.osu_parser import OSUGameModes
from ..utils import get_resource_path


class BackgroundModes(Enum):
    """Enum описывающий настройки работы с фонами"""
    KEEP = "Keep"
    WHITE = "White"
    DELETE = "Delete"
    CUSTOM = "Custom"


class CleanerWorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

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
        self.cleaner.start_clean(self.folders)
        self.finished.emit()


class SHXCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("sh(x)cleaner")
        icon = QIcon(get_resource_path("assets/icon.ico"))
        self.setWindowIcon(icon)

        self.init_components()
        self.center_window(320, 250)

    def init_components(self):
        """Инициализирует компоненты GUI"""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Фреймы
        self.top_frame = QHBoxLayout()
        self.main_layout.addLayout(self.top_frame)

        self.left_frame = QVBoxLayout()
        self.top_frame.addLayout(self.left_frame)

        self.right_frame = QVBoxLayout()
        self.top_frame.addLayout(self.right_frame)

        # Режимы игры
        self.osu_var = QCheckBox("Osu!")
        self.taiko_var = QCheckBox("Taiko")
        self.catch_var = QCheckBox("Catch")
        self.mania_var = QCheckBox("Mania")

        for checkbox in [
            self.osu_var,
            self.taiko_var,
            self.catch_var,
            self.mania_var
        ]:
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    margin-bottom: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
            self.left_frame.addWidget(checkbox)

        # Параметры работы с фонами
        self.bgs_var = QComboBox()
        self.bgs_var.addItems([mode.value for mode in BackgroundModes])
        self.bgs_var.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        self.bgs_label = QLabel("BGs:")
        self.bgs_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                margin-bottom: 5px;
            }
        """)
        self.right_frame.addWidget(self.bgs_label)
        self.right_frame.addWidget(self.bgs_var)
        self.right_frame.addSpacerItem(QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        ))

        # Прогресс бар
        self.progress_label = QLabel("Progress:")
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        self.main_layout.addWidget(self.progress_label)

        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 30px;
                border: 2px solid #3d3d3d;
                border-radius: 10px;
                font-size: 14px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 8px;
            }
        """)
        self.main_layout.addWidget(self.progress)

        # D e s t r o y   e v e r y t h i n g
        self.start_button = QPushButton("Destroy everything")
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.start_button.clicked.connect(self.start_cleaning)
        self.main_layout.addWidget(self.start_button)

    def center_window(self, width, height):
        """Центрирует окно приложения на экране"""
        if not (screen := QApplication.primaryScreen()):
            return

        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def pick_params(self) -> CleanerParams:
        """Собирает параметры очистки из GUI"""
        user_images: dict[str, str] | None = None
        delete_images: bool = False
        delete_modes: list[OSUGameModes] = []

        # Параметры работы с фоном
        bgs_option = BackgroundModes(self.bgs_var.currentText())
        if bgs_option == BackgroundModes.KEEP:
            user_images = None
            delete_images = False
        elif bgs_option == BackgroundModes.WHITE:
            user_images = {
                ".png": get_resource_path("assets/white.png"),
                ".jpg": get_resource_path("assets/white.jpg")
            }
            delete_images = False
        elif bgs_option == BackgroundModes.DELETE:
            user_images = None
            delete_images = True
        elif bgs_option == BackgroundModes.CUSTOM:
            user_images = {}
            delete_images = False

            png_file, _ = QFileDialog.getOpenFileName(
                self, "Select PNG Image", None, "PNG Files (*.png)"
            )
            if png_file:
                user_images['.png'] = png_file
            jpg_file, _ = QFileDialog.getOpenFileName(
                self, "Select JPG Image", "", "JPG Files (*.jpg)"
            )
            if jpg_file:
                user_images['.jpg'] = jpg_file

            if not user_images:
                user_images = None

        # Параметры работы с режимами игры
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
            "delete_modes": delete_modes
        }

    def start_cleaning(self):
        """Выполняет итоговую подготовку и запускает очистку карт"""
        songs_folder = QFileDialog.getExistingDirectory(
            self, "Select Songs Folder"
        )
        if not songs_folder:
            QMessageBox.critical(self, "Fatal error", "Why you...")
            return

        # Получаем все вложенные папки
        folders = [
            Path(songs_folder, f) for f in os.listdir(songs_folder)
            if Path(songs_folder, f).is_dir()
        ]
        self.progress.setMaximum(len(folders) * 2)
        self.progress.setValue(0)

        self.start_button.setEnabled(False)

        self.worker_thread = CleanerWorkerThread(
            Path(songs_folder), self.pick_params(), folders
        )
        self.worker_thread.progress.connect(self.__update_progress)
        self.worker_thread.finished.connect(self.__on_cleaning_finished)
        self.worker_thread.start()

    def __update_progress(self, folder_id):
        self.progress.setValue(self.progress.value() + 1)
        self.progress_label.setText(f"Cleaning {folder_id}...")

    def __on_cleaning_finished(self):
        QMessageBox.information(
            self,
            "Info",
            "Everything's clean. Check the size of your songs folder lol"
        )
        self.close()
