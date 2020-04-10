# -*- coding: utf-8 -*-
#
# This file is part of the HiChess project.
# Copyright (C) 2019-2020 Haik Sargsian <haiksargsian6@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import PySide2.QtWidgets as QtWidgets
from PySide2.QtCore import Qt, QRegExp, Slot, Signal
from PySide2.QtGui import QRegExpValidator

import hichess.hichess as hichess
import client


class LoginDialog(QtWidgets.QDialog):
    loginAccepted = Signal(str)
    loginRejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        titleLabel = QtWidgets.QLabel("LOGIN")

        self.usernameLineEdit = QtWidgets.QLineEdit()
        self.usernameLineEdit.setPlaceholderText("Username (a-zA-Z0-9_)")
        nameRx = QRegExp("[A-Za-z0-9_]{6,15}")
        self.usernameLineEdit.setValidator(QRegExpValidator(nameRx))

        rememberMeCheckBox = QtWidgets.QCheckBox("Remember me")
        loginButton = QtWidgets.QPushButton("Login")
        loginButton.clicked.connect(self.loginButtonClicked)
        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.clicked.connect(self.loginRejected.emit)

        layout = QtWidgets.QFormLayout()
        layout.addRow(titleLabel)
        layout.addRow(self.usernameLineEdit)
        layout.addRow(rememberMeCheckBox)
        layout.addRow(cancelButton, loginButton)
        layout.setAlignment(titleLabel, Qt.AlignCenter)
        self.setLayout(layout)

    @Slot()
    def loginButtonClicked(self):
        self.loginAccepted.emit(self.usernameLineEdit.text())
        self.close()


class HichessGui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.client = None

        self.scene = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.scene)
        self.setupMainMenuScene()
        self.setupGameScene()

    def setupMainMenuScene(self):
        menuScene = QtWidgets.QWidget()
        playOfflineButton = QtWidgets.QPushButton("Play Offline")
        playOnlineButton = QtWidgets.QPushButton("Play Online")
        exitButton = QtWidgets.QPushButton("Exit")

        playOfflineButton.clicked.connect(self.playOffline)
        playOnlineButton.clicked.connect(self.playOnline)
        exitButton.clicked.connect(self.close)

        menuSceneLayout = QtWidgets.QVBoxLayout()
        menuSceneLayout.addWidget(playOfflineButton)
        menuSceneLayout.addWidget(playOnlineButton)
        menuSceneLayout.addWidget(exitButton)
        menuScene.setLayout(menuSceneLayout)

        self.scene.addWidget(menuScene)

    def setupGameScene(self):
        gameSceneWidget = QtWidgets.QWidget()
        chessBoard = hichess.BoardWidget(flipped=False)

        informationWidget = QtWidgets.QWidget()

        gameSceneLayout = QtWidgets.QHBoxLayout()
        gameSceneLayout.addWidget(chessBoard)
        gameSceneLayout.addWidget(informationWidget)
        gameSceneLayout.setContentsMargins(0, 0, 0, 0)
        gameSceneWidget.setLayout(gameSceneLayout)
        self.scene.addWidget(gameSceneWidget)

    def playOffline(self):
        self.scene.setCurrentIndex(1)

    def playOnline(self):
        loginDialog = LoginDialog()
        loginDialog.loginRejected.connect(loginDialog.reject)
        loginDialog.loginAccepted.connect(self.connectToServer)
        loginDialog.exec_()

    @Slot()
    def startGame(self, username):
        self.scene.setCurrentIndex(1)
        self.setWindowTitle(username)

    @Slot()
    def connectToServer(self, username):
        if self.client is not None:
            self.client.webClient.close()
        self.client = client.Client(username, self)
        self.client.gameStarted.connect(self.startGame)
