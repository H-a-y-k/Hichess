from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QTextStream
from hichess_gui import HichessGui
from dialogs import LoginDialog, InvalidLogin
import logging
import sys

import resources


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)

    loginDialog = LoginDialog()
    status = loginDialog.exec_()

    if status == LoginDialog.Accepted and loginDialog.validator.regExp().exactMatch(loginDialog.username):
        window = HichessGui(username=loginDialog.username)

        f = QFile(":/style/styles.css")
        ts = QTextStream(f)
        if f.open(QFile.ReadOnly):
            app.setStyleSheet(ts.readAll())

        window.setMinimumSize(800, 800)
        window.showMaximized()
    else:
        raise InvalidLogin()

    sys.exit(app.exec_())
