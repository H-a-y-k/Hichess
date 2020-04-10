from PySide2.QtWidgets import QApplication
from hichess_gui import HichessGui
import logging
import sys


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = HichessGui()
    window.showMaximized()
    sys.exit(app.exec_())
