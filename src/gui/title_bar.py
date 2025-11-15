from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QIcon, QMouseEvent
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMenu, QToolButton, QWidget

from ..utils import get_resource_path


class TitleBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setAutoFillBackground(True)
        self.initial_pos = None

        # Advanced options
        self.force_clean = False
        self.keep_videos = False
        self.ignore_id_limit = False
        self.dangerous_clean_no_id = False

        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        # Title
        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setStyleSheet(
            """
                font-size: 14pt;
                font-weight: bold;
                border: none;
                margin-left: 60px;
                padding-bottom: 2px;
                color: #4B5D92;
            """
        )

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)

        title_bar_layout.addWidget(self.title)

        # BUTTONS
        self.min_button = QToolButton(self)
        self.close_button = QToolButton(self)

        # Set icons
        min_icon = QIcon()
        min_icon.addFile(get_resource_path('assets/min.svg'))
        self.min_button.setIcon(min_icon)

        close_icon = QIcon()
        close_icon.addFile(get_resource_path('assets/close.svg'))
        self.close_button.setIcon(close_icon)

        # Connect clicks
        if window := self.window():
            self.min_button.clicked.connect(window.showMinimized)
            self.close_button.clicked.connect(window.close)

        # Other button settings
        for button in [
            self.min_button,
            self.close_button,
        ]:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(30, 30))
            button.setStyleSheet("""
                QToolButton {
                    border: none;
                }
            """)
            title_bar_layout.addWidget(button)

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)

        # Force clean
        force_clean_action = QAction('Force clean (ignore processed)', self)
        force_clean_action.setCheckable(True)
        force_clean_action.setChecked(self.force_clean)
        force_clean_action.toggled.connect(self.on_force_clean_toggled)
        menu.addAction(force_clean_action)

        # Keep videos
        keep_videos_action = QAction('Keep videos', self)
        keep_videos_action.setCheckable(True)
        keep_videos_action.setChecked(self.keep_videos)
        keep_videos_action.toggled.connect(self.on_keep_videos_toggled)
        menu.addAction(keep_videos_action)

        # Ignore id limit
        ignore_id_limit_action = QAction('Ignore id limit', self)
        ignore_id_limit_action.setCheckable(True)
        ignore_id_limit_action.setChecked(self.ignore_id_limit)
        ignore_id_limit_action.toggled.connect(self.on_ignore_id_limit_toggled)
        menu.addAction(ignore_id_limit_action)

        # Dangerous clean no id
        dangerous_clean_no_id_action = QAction('Dangerously clean folders with no id', self)
        dangerous_clean_no_id_action.setCheckable(True)
        dangerous_clean_no_id_action.setChecked(self.dangerous_clean_no_id)
        dangerous_clean_no_id_action.toggled.connect(self.on_dangerous_clean_no_id_toggled)
        menu.addAction(dangerous_clean_no_id_action)

        main_window = self.window()
        if not main_window:
            menu.exec(event.globalPos())
            return

        # Calculate centered position
        menu_width = menu.sizeHint().width()
        target_x = main_window.x() + (main_window.width() - menu_width) / 2
        target_y = main_window.y() + self.height()

        point = QPoint(int(target_x), int(target_y))
        menu.exec(point)

    def on_force_clean_toggled(self, checked: bool):
        self.force_clean = checked

    def on_keep_videos_toggled(self, checked: bool):
        self.keep_videos = checked

    def on_ignore_id_limit_toggled(self, checked: bool):
        self.ignore_id_limit = checked

    def on_dangerous_clean_no_id_toggled(self, checked: bool):
        self.dangerous_clean_no_id = checked

    # WINDOW DRAGGING
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            if window := self.window():
                window.move(
                    window.x() + delta.x(),
                    window.y() + delta.y(),
                )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()
