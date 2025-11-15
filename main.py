import sys

from PyQt6.QtWidgets import QApplication

from src.gui import SHXCleanerApp
from src.gui.app_theme import set_theme

# This is the main entry point of the application.

# 1. Every PyQt application must create a QApplication instance.
app = QApplication(sys.argv)

# 2. Set the global visual theme (colors, styles) for the entire app.
set_theme(app)

# 3. Create an instance of our main window.
window = SHXCleanerApp()

# 4. Show the main window.
window.show()

# 5. Start the application's event loop. This call is blocking and will
#    exit only when the application is closed.
sys.exit(app.exec())
