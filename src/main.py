from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QTextStream
from hichess_gui import HichessGui
import logging
import sys

import resources

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = HichessGui()
    f = QFile(":/style/styles.css")
    ts = QTextStream(f)
    if f.open(QFile.ReadOnly):
        a = str(ts.readAll())
        app.setStyleSheet(a)
    window.setMinimumSize(800, 800)
    window.showMaximized()
    sys.exit(app.exec_())
