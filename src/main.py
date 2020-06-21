from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QTextStream
from PySide2.QtGui import QFontDatabase
from hichess_gui import HichessGui
from dialogs import SignInDialog, InvalidUsername
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

    if breeze.open(QFile.ReadOnly):
        textstream = QTextStream(breeze)
        breezeQss = textstream.readAll()
    if main.open(QFile.ReadOnly):
        textstream = QTextStream(main)
        mainQss = textstream.readAll()

    app.setStyleSheet(f"{breezeQss}{mainQss}")

    loginDialog = SignInDialog()
    status = loginDialog.exec_()

    if status == SignInDialog.Accepted and loginDialog.validator.regExp().exactMatch(loginDialog.username):
        window = HichessGui(username=loginDialog.username)

        window.setMinimumSize(800, 800)
        window.showMaximized()
    else:
        raise InvalidUsername

    sys.exit(app.exec_())
