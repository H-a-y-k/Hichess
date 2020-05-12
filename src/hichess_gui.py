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
from PySide2.QtCore import Qt, Slot, QEvent
from PySide2.QtGui import QPixmap

import hichess.hichess as hichess
import chess
from stockfish import Stockfish
import random

import client
import dialogs


class HichessGui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.client = None

        self.scene = QtWidgets.QStackedWidget()
        self.boardWidget = hichess.BoardWidget(flipped=False, sides=hichess.BOTH_SIDES)
        self.boardWidget.setBoardPixmap(defaultPixmap=QPixmap(":/images/chessboard.png"),
                                        flippedPixmap=QPixmap(":/images/flipped_chessboard.png"))
        self.real_board = self.boardWidget.board

        self.setCentralWidget(self.scene)
        self.setupMainMenuScene()
        self.setupGameScene()
        self.installEventFilter(self)

    def setupMainMenuScene(self):
        menuScene = QtWidgets.QWidget()

        pveButton = QtWidgets.QPushButton("Against the Computer")
        offlinePvpButton = QtWidgets.QPushButton("Offline Pvp")
        onlinePvpButton = QtWidgets.QPushButton("Online PvP")
        exitButton = QtWidgets.QPushButton("Exit")

        pveButton.clicked.connect(self.playPve)
        offlinePvpButton.clicked.connect(self.playOfflinePvp)
        onlinePvpButton.clicked.connect(self.playOnlinePvp)
        exitButton.clicked.connect(self.close)

        menuSceneLayout = QtWidgets.QVBoxLayout()
        menuSceneLayout.addWidget(pveButton)
        menuSceneLayout.addWidget(offlinePvpButton)
        menuSceneLayout.addWidget(onlinePvpButton)
        menuSceneLayout.addWidget(exitButton)
        menuScene.setLayout(menuSceneLayout)

        self.scene.addWidget(menuScene)

    def setupGameScene(self):
        gameSceneWidget = QtWidgets.QWidget()

        informationWidget = QtWidgets.QWidget()

        gameSceneLayout = QtWidgets.QHBoxLayout()
        gameSceneLayout.addWidget(self.boardWidget)
        gameSceneLayout.addWidget(informationWidget)
        gameSceneLayout.setContentsMargins(0, 0, 0, 0)
        gameSceneWidget.setLayout(gameSceneLayout)
        self.scene.addWidget(gameSceneWidget)

    @Slot()
    def playPve(self):
        pveDialog = dialogs.PveDialog(self)
        res = pveDialog.exec_()

        if res == QtWidgets.QDialog.Accepted:
            SKILL_LEVLES = [0, 4, 8, 12, 14, 16, 18, 20]
            variant, timeControl, level, color = pveDialog.data.values()

            ####
            self.boardWidget.setFen(pveDialog.fromPositionLineEdit.text())

            if color == "random":
                color = random.choice["white", "black"]
            if color == "white":
                self.boardWidget.accessibleSides = hichess.ONLY_WHITE_SIDE
            elif color == "black":
                self.boardWidget.accessibleSides = hichess.ONLY_BLACK_SIDE
                self.boardWidget.flip()

            stockfish = Stockfish()
            stockfish.set_skill_level(SKILL_LEVLES[pveDialog.data["level"]])

            Slot()
            def onMoveMade():
                stockfish.set_fen_position(self.boardWidget.board.fen())
                if not chess.COLOR_NAMES[self.boardWidget.board.turn] == color:
                    self.boardWidget.push(chess.Move.from_uci(stockfish.get_best_move()))

            self.boardWidget.moveMade.connect(onMoveMade)
            self.scene.setCurrentIndex(1)
            onMoveMade()

    @Slot()
    def playOfflinePvp(self):
        self.scene.setCurrentIndex(1)

    @Slot()
    def playOnlinePvp(self):
        loginDialog = dialogs.LoginDialog(self)
        loginDialog.loginRejected.connect(loginDialog.reject)
        loginDialog.loginAccepted.connect(self.connectToServer)
        loginDialog.exec_()

    @Slot()
    def startGame(self, packet: client.Packet):
        self.scene.setCurrentIndex(1)

        if packet.contentType == client.WHITE_PLAYER_DATA:
            self.boardWidget.accessibleSides = hichess.ONLY_WHITE_SIDE
            self.boardWidget.synchronize()
        elif packet.contentType == client.BLACK_PLAYER_DATA:
            self.boardWidget.accessibleSides = hichess.ONLY_BLACK_SIDE
            self.boardWidget.synchronize()
            self.boardWidget.flip()

    @Slot()
    def connectToServer(self, username):
        if self.client is not None:
            self.client.webClient.close()

        self.client = client.Client(username, self)
        self.client.gameStarted.connect(self.startGame)
        self.client.moveMade.connect(lambda move: self.boardWidget.movePieceAt(chess.Move.from_uci(move).from_square,
                                                                               chess.Move.from_uci(move).to_square))
        self.boardWidget.moveMade.connect(lambda move: self.client.sendPacket(client.MOVE, move))

        self.setWindowTitle(username)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Left:
                if self.boardWidget.board.move_stack:
                    self.boardWidget.pop()
            if event.key() == Qt.Key_Right:
                if self.boardWidget.pop_stack:
                    self.boardWidget.unpop()
            return True
        return super().eventFilter(watched, event)
