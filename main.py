import sys

from PyQt6.QtWidgets import QApplication

from src.gui.app_theme import set_theme
from src.gui.gui import SHXCleanerApp

app = QApplication(sys.argv)
set_theme(app)

window = SHXCleanerApp()
window.show()
sys.exit(app.exec())
