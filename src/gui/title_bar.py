from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QAction, QColor, QContextMenuEvent, QIcon, QMouseEvent
from PyQt6.QtWidgets import (QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
                             QMenu, QToolButton, QWidget)

from ..utils import get_resource_path


class TitleBar(QWidget):
    """
    A custom title bar widget that provides window controls (minimize, close),
    a title label, window dragging functionality, and a right-click context menu
    for advanced options.
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setAutoFillBackground(True)
        self.initial_pos = None

        # These attributes store the state of the advanced options.
        # They are toggled by the context menu actions.
        self.force_clean = False
        self.keep_videos = False
        self.ignore_id_limit = False
        self.dangerous_clean_no_id = False

        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        # --- Title Label ---
        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setStyleSheet(
            """
                font-size: 14pt; font-weight: bold; border: none;
                margin-left: 60px; padding-bottom: 2px; color: #4B5D92;
            """
        )
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)
        title_bar_layout.addWidget(self.title)

        # --- Window Control Buttons ---
        self.min_button = QToolButton(self)
        self.close_button = QToolButton(self)

        min_icon = QIcon(get_resource_path('assets/min.svg'))
        self.min_button.setIcon(min_icon)
        close_icon = QIcon(get_resource_path('assets/close.svg'))
        self.close_button.setIcon(close_icon)

        if window := self.window():
            self.min_button.clicked.connect(window.showMinimized)
            self.close_button.clicked.connect(window.close)

        for button in [self.min_button, self.close_button]:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(30, 30))
            button.setStyleSheet("QToolButton { border: none; }")
            title_bar_layout.addWidget(button)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """
        This event is triggered on a right-click. It builds and displays the
        advanced options menu.
        """
        # We only want the menu to appear when clicking on the title, not the buttons.
        if not self.title.geometry().contains(event.pos()):
            return

        menu = QMenu(self)

        # These flags are essential for custom styling. They remove the native OS
        # window frame and background, preventing visual glitches (like black corners)
        # when using border-radius in the stylesheet.
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # This effect is intentionally left commented out but is kept here for
        # historical/debugging purposes. It was part of a previous attempt to
        # create a shadow, which now is handled purely by QSS.
        # shadow = QGraphicsDropShadowEffect(menu)
        # shadow.setBlurRadius(5) ...
        # menu.setGraphicsEffect(shadow)

        # --- Menu Actions ---
        force_clean_action = QAction('Force clean (ignore processed)', self)
        force_clean_action.setCheckable(True)
        force_clean_action.setChecked(self.force_clean)
        force_clean_action.toggled.connect(self.on_force_clean_toggled)
        menu.addAction(force_clean_action)

        keep_videos_action = QAction('Keep videos', self)
        keep_videos_action.setCheckable(True)
        keep_videos_action.setChecked(self.keep_videos)
        keep_videos_action.toggled.connect(self.on_keep_videos_toggled)
        menu.addAction(keep_videos_action)

        ignore_id_limit_action = QAction('Ignore 8 digits ID limit', self)
        ignore_id_limit_action.setCheckable(True)
        ignore_id_limit_action.setChecked(self.ignore_id_limit)
        ignore_id_limit_action.toggled.connect(self.on_ignore_id_limit_toggled)
        menu.addAction(ignore_id_limit_action)

        dangerous_clean_no_id_action = QAction('Dangerous clean (process folders with no ID)', self)
        dangerous_clean_no_id_action.setCheckable(True)
        dangerous_clean_no_id_action.setChecked(self.dangerous_clean_no_id)
        dangerous_clean_no_id_action.toggled.connect(self.on_dangerous_clean_no_id_toggled)
        menu.addAction(dangerous_clean_no_id_action)

        # --- Positioning and Displaying the Menu ---
        main_window = self.window()
        if not main_window:
            menu.exec(event.globalPos()) # Fallback to cursor position
            return

        # Calculate the correct centered position below the title bar.
        menu_width = menu.sizeHint().width()
        target_x = main_window.x() + (main_window.width() - menu_width) / 2
        target_y = main_window.y() + self.height()
        point = QPoint(int(target_x), int(target_y))
        
        menu.exec(point)

    # --- Action Handlers ---
    def on_force_clean_toggled(self, checked: bool): self.force_clean = checked
    def on_keep_videos_toggled(self, checked: bool): self.keep_videos = checked
    def on_ignore_id_limit_toggled(self, checked: bool): self.ignore_id_limit = checked
    def on_dangerous_clean_no_id_toggled(self, checked: bool): self.dangerous_clean_no_id = checked

    # --- Window Dragging Logic ---
    def mousePressEvent(self, event: QMouseEvent):
        """Captures the initial mouse position when the user clicks."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Moves the main window based on the mouse drag."""
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            if window := self.window():
                window.move(window.x() + delta.x(), window.y() + delta.y())
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Resets the initial position when the mouse is released."""
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()
