from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QTextStream
from PySide2.QtGui import QFontDatabase, QIcon
from hichess_gui import HichessGui
from dialogs import SettingsDialog
import logging
import sys

import resources
import qbreezercc


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    breeze = QFile(":qbreeze/dark.qss")
    main = QFile(":/style/styles.css")

    breezeQss = ""
    mainQss = ""

    QFontDatabase.addApplicationFont(":/font/bahnschrift.ttf")
    app.setWindowIcon(QIcon(":/images/chessboard.png"))

    if breeze.open(QFile.ReadOnly):
        textstream = QTextStream(breeze)
        breezeQss = textstream.readAll()
    if main.open(QFile.ReadOnly):
        textstream = QTextStream(main)
        mainQss = textstream.readAll()

    app.setStyleSheet(f"{breezeQss}{mainQss}")

    settingsDialog = SettingsDialog("", "")
    status = settingsDialog.exec_()

    if status == SettingsDialog.Accepted:
        window = HichessGui(username=settingsDialog.newUsername, enginePath=settingsDialog.newEnginePath)
        window.setMinimumSize(800, 800)
        window.showMaximized()

    sys.exit(app.exec_())
