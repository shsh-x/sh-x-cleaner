import sys

from PyQt6.QtWidgets import QApplication

from src.gui.gui import SHXCleanerApp

app = QApplication(sys.argv)
window = SHXCleanerApp()
window.show()
sys.exit(app.exec())
