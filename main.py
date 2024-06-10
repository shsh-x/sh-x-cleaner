import sys

from PyQt6.QtWidgets import QApplication

from src.gui import SHXCleanerApp
from src.gui.app_theme import set_theme

app = QApplication(sys.argv)
set_theme(app)

window = SHXCleanerApp()
window.show()
sys.exit(app.exec())
