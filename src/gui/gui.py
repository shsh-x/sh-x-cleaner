import os
from enum import Enum
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QFileDialog,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)

from ..app.cleaner import CleanerParams
from ..app.osu_parser import OSUGameModes
from ..utils import get_resource_path
from .cleaner_qworker import CleanerWorkerThread
from .title_bar import TitleBar

font_path = get_resource_path("assets/Exo2.ttf")

class BackgroundModes(Enum):
    """Enum описывающий настройки работы с фонами"""
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
        """Инициализирует компоненты GUI"""
        # Виджет всего окна
        self.central_widget = QWidget(self)
        centra_widget_layout = QVBoxLayout()
        centra_widget_layout.setContentsMargins(0, 0, 0, 0)
        centra_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.central_widget.setLayout(centra_widget_layout)
        self.central_widget.setStyleSheet("")
        self.setCentralWidget(self.central_widget)

        # Добавляем тайтл (ОН В ОТДЕЛЬНОМ КЛАССЕ)
        self.title_bar = TitleBar(self)
        centra_widget_layout.addWidget(self.title_bar)

        # Основной лэйаут приложения
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        centra_widget_layout.addLayout(self.main_layout)

        # Фреймы
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

        # Прогресс бар
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
        if self.keep_var.isChecked():
            user_images = None
            delete_images = False
        elif self.white_var.isChecked():
            user_images = {
                ".png": get_resource_path("assets/white.png"),
                ".jpg": get_resource_path("assets/white.jpg")
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
        self.progress.setMaximum(len(folders))
        self.progress.setValue(0)

        self.start_button.setEnabled(False)

        self.worker_thread = CleanerWorkerThread(
            Path(songs_folder), self.pick_params(), folders
        )
        self.worker_thread.progress.connect(self.__update_progress)
        self.worker_thread.finished.connect(self.__on_cleaning_finished)
        self.worker_thread.error_occured.connect(self.__on_cleaning_error)
        self.worker_thread.start()

    def __update_progress(self, folder_id: int):
        self.progress.setValue(self.progress.value() + 1)
        self.progress.setFormat(str(folder_id))

    def __on_cleaning_finished(self):
        QMessageBox.information(
            self,
            "Done!",
            "Everything's clean. Check the size of your songs folder lol"
        )
        self.close()

    def __on_cleaning_error(self, exception: Exception):
        QMessageBox.critical(
            self,
            "An error occured",
            f"An error occurred (for more info look terminal):\n{exception}"
        )
        self.close()
