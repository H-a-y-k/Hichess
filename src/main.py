from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QTextStream
from hichess_gui import HichessGui
from dialogs import LoginDialog, InvalidLogin
import logging
import sys

import resources
import qbreezercc


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)

    loginDialog = LoginDialog()
    status = loginDialog.exec_()

    if status == LoginDialog.Accepted and loginDialog.validator.regExp().exactMatch(loginDialog.username):
        window = HichessGui(username=loginDialog.username)

        breeze = QFile(":qbreeze/dark.qss")
        main = QFile(":/style/styles.css")

        breezeQss = ""
        mainQss = ""

        if breeze.open(QFile.ReadOnly):
            textstream = QTextStream(breeze)
            breezeQss = textstream.readAll()
        if main.open(QFile.ReadOnly):
            textstream = QTextStream(main)
            mainQss = textstream.readAll()

        app.setStyleSheet(f"{breezeQss}{mainQss}")
        window.setMinimumSize(800, 800)
        window.showMaximized()
    else:
        raise InvalidLogin()

    sys.exit(app.exec_())
