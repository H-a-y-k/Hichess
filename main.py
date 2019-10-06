from PySide2.QtWidgets import QApplication
from hichess import HiChess
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HiChess()
    window.setWindowTitle("HiChess")
    window.showMaximized()
    sys.exit(app.exec_())