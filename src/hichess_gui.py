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
from PySide2.QtGui import QRegExpValidator, QPixmap

import hichess.hichess as hichess
import chess
import client


class LoginDialog(QtWidgets.QDialog):
    loginAccepted = Signal(str)
    loginRejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        titleLabel = QtWidgets.QLabel("LOGIN")
        titleLabel.setMinimumHeight(35)

        self.usernameLineEdit = QtWidgets.QLineEdit()
        self.usernameLineEdit.setPlaceholderText("Username (a-zA-Z0-9_)")
        nameRx = QRegExp("[A-Za-z0-9_]{6,15}")
        self.usernameLineEdit.setValidator(QRegExpValidator(nameRx))
        self.usernameLineEdit.setMinimumHeight(35)

        rememberMeCheckBox = QtWidgets.QCheckBox("Remember me")
        rememberMeCheckBox.setMinimumHeight(35)

        loginButton = QtWidgets.QPushButton("Login")
        loginButton.clicked.connect(self.loginButtonClicked)
        loginButton.setDefault(True)
        loginButton.setMinimumHeight(35)

        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.clicked.connect(self.loginRejected.emit)
        cancelButton.setMinimumHeight(35)

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
        self.chessBoard = hichess.BoardWidget(flipped=False, sides=hichess.BOTH_SIDES)
        self.chessBoard.setBoardPixmap(defaultPixmap=QPixmap(":/images/chessboard.png"),
                                       flippedPixmap=QPixmap(":/images/flipped_chessboard.png"))

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

        informationWidget = QtWidgets.QWidget()

        gameSceneLayout = QtWidgets.QHBoxLayout()
        gameSceneLayout.addWidget(self.chessBoard)
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
    def startGame(self, packet: client.Packet):
        self.scene.setCurrentIndex(1)

        if packet.contentType == client.WHITE_PLAYER_DATA:
            self.chessBoard.accessibleSides = hichess.ONLY_WHITE_SIDE
        elif packet.contentType == client.BLACK_PLAYER_DATA:
            self.chessBoard.accessibleSides = hichess.ONLY_BLACK_SIDE
            self.chessBoard.flip()

    @Slot()
    def connectToServer(self, username):
        if self.client is not None:
            self.client.webClient.close()

        self.client = client.Client(username, self)
        self.client.gameStarted.connect(self.startGame)
        self.client.moveMade.connect(lambda move: self.chessBoard.movePieceAt(chess.Move.from_uci(move).from_square,
                                                                              chess.Move.from_uci(move).to_square))
        self.chessBoard.moveMade.connect(lambda move: self.client.sendPacket(client.MOVE, move))

        self.setWindowTitle(username)
