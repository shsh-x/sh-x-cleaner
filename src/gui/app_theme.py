from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


def set_theme(app: QApplication):
    """Установка глобальной темы приложения"""
    # Установка палитры цветов (для фиксированной темы на разных устройствах)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.WindowText, QColor          ('#2E3036'))    # BGs+Modes (actually +title but nvm)
    palette.setColor(QPalette.ColorRole.Text, QColor                ('#5A77AB'))    # ID in progressbar
    palette.setColor(QPalette.ColorRole.ButtonText, QColor          ('#131C2B'))    # Button text
    palette.setColor(QPalette.ColorRole.Base, QColor                ('#E2E2E9'))    # Progressbar bg
    palette.setColor(QPalette.ColorRole.Window, QColor              ('#F9F9FF'))    # Background
    app.setPalette(palette)

    # Отключение Focus Rectangle на элементах
    app.setStyleSheet("*:focus { outline: none; }")
