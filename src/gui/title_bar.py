from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QMouseEvent, QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget


class TitleBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.initial_pos = None

        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        # Иконка
        self.icon = QLabel(self)
        icon = QIcon('assets/icon.ico')
        self.icon.setPixmap(icon.pixmap(QSize(16, 16)))  # Set the size of the icon here
        title_bar_layout.addWidget(self.icon)


        # Тайтл
        
        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setStyleSheet(
            """
                text-transform: uppercase;
                font-size: 8pt;
                font-weight: bold;
                border: none;
                margin-right: 20px;
            """
        )

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)

        title_bar_layout.addWidget(self.title)

        # КНОМПОЧКИ

        self.min_button = QToolButton(self)
        self.close_button = QToolButton(self)
        # Ставим иконки, если получен стиль
        if style := self.style():
            # Иконка для кномпочки сворачивания
            min_icon = QIcon()
            min_icon.addFile('assets/min.svg')
            self.min_button.setIcon(min_icon)


            # Иконка для кномпочки закрытия
            close_icon = QIcon()
            close_icon.addFile('assets/close.svg')
            self.close_button.setIcon(close_icon)

        # Коннектим клики, если есть окно
        if window := self.window():
            self.min_button.clicked.connect(window.showMinimized)
            self.close_button.clicked.connect(window.close)

        # Остальные настройки кномпочек
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

    # ДВИГОЕМ ОКНО
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