from PySide2.QtWidgets import QApplication
from hichess_gui import HiChessGui
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HiChessGui()
    window.showMaximized()
    sys.exit(app.exec_())