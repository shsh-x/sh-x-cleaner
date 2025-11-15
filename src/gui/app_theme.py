from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


def set_theme(app: QApplication):
    """
    Sets the global visual theme for the entire application.
    This function defines a central color palette and applies a global
    stylesheet (QSS) to ensure a consistent look and feel.
    """
    # 1. Define the Color Palette
    # Using a QPalette is a robust way to define theme colors. QSS can then
    # reference these colors using `palette(role-name)`, making it easy to
    # change the theme from one place.
    palette = QPalette()
    
    # General Window
    palette.setColor(QPalette.ColorRole.Window, QColor('#F9F9FF'))          # Main background color.
    palette.setColor(QPalette.ColorRole.WindowText, QColor('#2E3036'))      # Default text color.
    
    # Buttons
    palette.setColor(QPalette.ColorRole.Button, QColor('#D6E3FF'))          # Background of checked/main action buttons.
    palette.setColor(QPalette.ColorRole.ButtonText, QColor('#001B3E'))      # Text on checked/main action buttons.
    
    # Progress Bar
    palette.setColor(QPalette.ColorRole.Base, QColor('#E2E2E9'))            # Background of the progress bar.
    palette.setColor(QPalette.ColorRole.Highlight, QColor('#BED1FA'))       # Color of the progress bar's chunk and highlights.
    palette.setColor(QPalette.ColorRole.Text, QColor('#5A77AB'))            # Color of the beatmap ID text in the progress bar.
    
    # Context Menu
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor('#F0F0F8'))     # Background of the context menu.
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor('#2E3036'))     # Text color for menu items.
    
    app.setPalette(palette)

    # 2. Apply Global Stylesheet (QSS)
    app.setStyleSheet("""
        /* Global reset: remove the dotted focus outline on all widgets. */
        *:focus { 
            outline: none; 
        }

        /* Main Window Styling */
        /* The main window itself is made transparent to allow the rounded corners to show. */
        QMainWindow {
            border-radius: 10px;
        }
        /* The actual visible content and border are applied to the central widget. */
        #centralWidget {
            background-color: palette(window);
            border: 1px solid palette(highlight);
            border-radius: 10px;
        }
        /* The title bar's top corners must also be rounded to match the main window. */
        TitleBar {
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }

        /* Context Menu Styling */
        QMenu {
            background-color: palette(tooltip-base);
            border: 1px solid palette(highlight);
            border-radius: 5px;
        }
        /* The indicator is the checkmark icon. This gives it space from the left edge. */
        QMenu::indicator {
            width: 13px;
            height: 13px;
            margin-left: 8px;
        }
        /* A menu item contains the indicator and the text. This padding adds space
           between the indicator and the text. */
        QMenu::item {
            padding: 5px 25px 5px 2px;
            background-color: transparent;
            color: palette(tooltip-text);
        }
        /* Style for the currently hovered/selected item. */
        QMenu::item:selected {
            background-color: palette(highlight);
            color: palette(button-text);
            border-radius: 3px;
        }
    """)
