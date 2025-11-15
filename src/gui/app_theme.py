from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


def set_theme(app: QApplication):
    """Sets the global theme for the application."""
    # Set the color palette (for a fixed theme across different devices)
    palette = QPalette()
    # General
    palette.setColor(QPalette.ColorRole.Window, QColor('#F9F9FF'))          # Main background
    palette.setColor(QPalette.ColorRole.WindowText, QColor('#2E3036'))      # Text on BGs+Modes
    # Buttons
    palette.setColor(QPalette.ColorRole.Button, QColor('#D6E3FF'))          # Button background
    palette.setColor(QPalette.ColorRole.ButtonText, QColor('#001B3E'))      # Button text
    # Progress Bar
    palette.setColor(QPalette.ColorRole.Base, QColor('#E2E2E9'))            # Progressbar background
    palette.setColor(QPalette.ColorRole.Highlight, QColor('#BED1FA'))       # Progressbar chunk
    palette.setColor(QPalette.ColorRole.Text, QColor('#5A77AB'))            # ID in progressbar
    # Menu
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor('#F0F0F8'))     # Menu background
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor('#2E3036'))     # Menu item text
    app.setPalette(palette)

    # Disable the focus rectangle on elements and apply menu styles
    app.setStyleSheet("""
        *:focus { 
            outline: none; 
        }
        /* Apply rounding and border to the main window */
        QMainWindow {
            border-radius: 10px;
        }
        #centralWidget {
            background-color: palette(window);
            border: 1px solid palette(highlight);
            border-radius: 10px;
        }
        TitleBar {
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        QMenu {
            background-color: palette(tooltip-base);
            border: 1px solid palette(highlight);
            border-radius: 5px;
        }
        QMenu::indicator {
            width: 13px;
            height: 13px;
            margin-left: 8px;
        }
        QMenu::item {
            padding: 5px 25px 5px 2px;
            background-color: transparent;
            color: palette(tooltip-text);
        }
        QMenu::item:selected {
            background-color: palette(highlight);
            color: palette(button-text);
            border-radius: 3px;
        }
    """)
