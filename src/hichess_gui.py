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

from functools import partial

import client
import dialogs
import control_panel
import chatwidget


class HichessGui(QtWidgets.QMainWindow):
    def __init__(self, username: str):
        super(HichessGui, self).__init__()

        self.username = username
        self.client = client.Client(self.username, self)

        self.scene = QtWidgets.QStackedWidget()
        self.boardWidget = hichess.BoardWidget(flipped=False, sides=hichess.BOTH_SIDES)
        self.boardWidget.setBoardPixmap(defaultPixmap=QPixmap(":/images/chessboard.png"),
                                        flippedPixmap=QPixmap(":/images/flipped_chessboard.png"))
        self.boardWidget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        ))
        self.boardWidget.setFocusPolicy(Qt.StrongFocus)

        self.boardWidget.moveMade.connect(self.updateMoveTable)

        self.controlPanelWidget = control_panel.GameControlPanel(self.username, self.username)
        self.controlPanelWidget.flipButton.clicked.connect(self.flip)
        self.controlPanelWidget.toStartFenButton.clicked.connect(self.toStartFen)
        self.controlPanelWidget.previousMoveButton.clicked.connect(self.previousMove)
        self.controlPanelWidget.nextMoveButton.clicked.connect(self.nextMove)
        self.controlPanelWidget.toCurrentFenButton.clicked.connect(self.toCurrentFen)

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

    @Slot()
    def updateMoveTable(self, move):
        item = self.controlPanelWidget.addMove(move)
        self.controlPanelWidget.moveTable.setCurrentCell(item.row(), item.column())

    @Slot()
    def flip(self):
        self.boardWidget.flip()
        self.controlPanelWidget.swapNames()

    @Slot()
    def toStartFen(self):
        while self.boardWidget.board.move_stack:
            self.previousMove()

    @Slot()
    def toCurrentFen(self):
        while self.boardWidget.popStack:
            self.nextMove()

    @Slot()
    def previousMove(self):
        if self.boardWidget.board.move_stack:
            self.boardWidget.pop()
            if not self.boardWidget.blockBoardOnPop:
                self.controlPanelWidget.popMove()
            else:
                self.controlPanelWidget.toPreviousCell()

    @Slot()
    def nextMove(self):
        if self.boardWidget.popStack:
            move = self.boardWidget.unpop()
            if not self.boardWidget.blockBoardOnPop:
                self.updateMoveTable(move)
            else:
                self.controlPanelWidget.toNextCell()

    def setupGameScene(self):
        gameSceneWidget = QtWidgets.QWidget()

        gameSceneLayout = QtWidgets.QHBoxLayout()
        gameSceneLayout.addWidget(self.boardWidget)
        gameSceneLayout.addWidget(self.controlPanelWidget)
        gameSceneLayout.setContentsMargins(0, 0, 0, 0)
        gameSceneWidget.setLayout(gameSceneLayout)

        self.scene.addWidget(gameSceneWidget)

    @Slot()
    def playPve(self):
        pveDialog = dialogs.PveDialog(self)
        res = pveDialog.exec_()

        if res == QtWidgets.QDialog.Accepted:
            self.boardWidget.blockBoardOnPop = True

            SKILL_LEVELS = [0, 4, 8, 12, 14, 16, 18, 20]
            fen, level, color = pveDialog.data.values()
            self.controlPanelWidget.firstName.setText(f"Stockfish {SKILL_LEVELS[level]}")

            # fen
            self.boardWidget.setFen(pveDialog.chooseVariantSection.fromPositionLineEdit.text())

            # level
            stockfish = Stockfish()
            stockfish.set_skill_level(SKILL_LEVELS[level])

            Slot(str)
            def onMoveMade(move):
                stockfish.set_fen_position(self.boardWidget.board.fen())
                if self.boardWidget.board.turn != color:
                    self.boardWidget.push(chess.Move.from_uci(stockfish.get_best_move()))

            self.boardWidget.moveMade.connect(onMoveMade)

            # color
            if color == chess.WHITE:
                self.boardWidget.accessibleSides = hichess.ONLY_WHITE_SIDE
            elif color == chess.BLACK:
                self.boardWidget.accessibleSides = hichess.ONLY_BLACK_SIDE
                self.boardWidget.flip()

            stockfish.set_fen_position(self.boardWidget.board.fen())
            if self.boardWidget.board.turn != color:
                self.boardWidget.push(chess.Move.from_uci(stockfish.get_best_move()))

            self.scene.setCurrentIndex(1)

    @Slot()
    def playOfflinePvp(self):
        self.boardWidget.blockBoardOnPop = False
        self.scene.setCurrentIndex(1)

    @Slot()
    def playOnlinePvp(self):
        if not dialogs.LoginDialog.validator.validate(self.username, 0):
            loginDialog = dialogs.LoginDialog(self)
            status = loginDialog.exec_()
            if not status == dialogs.LoginDialog.Accepted:
                self.username = loginDialog.username
            else:
                raise dialogs.InvalidLogin()

        waitDialog = QtWidgets.QDialog(self)

        waitLabel = QtWidgets.QLabel("Waiting for player...")
        waitLabel.setAlignment(Qt.AlignCenter)
        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.clicked.connect(waitDialog.reject)

        waitDialogLayout = QtWidgets.QVBoxLayout()
        waitDialogLayout.addWidget(waitLabel)
        waitDialogLayout.addWidget(cancelButton)
        waitDialog.setLayout(waitDialogLayout)

        self.client.gameStarted.connect(waitDialog.accept)
        self.client.gameStarted.connect(self.startGame)
        self.client.startConnectionWithServer()
        self.searchForGame()

        waitDialog.exec_()

    @Slot()
    def startGame(self, packet: client.Packet):
        self.boardWidget.blockBoardOnPop = True
        self.scene.setCurrentIndex(1)

        opponentUsername = packet.payload

        self.controlPanelWidget.firstName.setText(opponentUsername)
        self.controlPanelWidget.secondName.setText(self.username)

        if packet.contentType == client.WHITE_PLAYER_DATA:
            self.boardWidget.accessibleSides = hichess.ONLY_WHITE_SIDE
            self.boardWidget.synchronize()
        elif packet.contentType == client.BLACK_PLAYER_DATA:
            self.boardWidget.accessibleSides = hichess.ONLY_BLACK_SIDE
            self.boardWidget.flip()

        cw = chatwidget.ChatWidget()
        self.addDockWidget(Qt.LeftDockWidgetArea, cw)
        cw.messageToBeSent.connect(partial(self.client.sendPacket, client.MESSAGE))
        self.client.messageReceived.connect(partial(cw.showMessage, chatwidget.OPPONENT))
        self.client.serverMessageReceived.connect(partial(cw.showMessage, chatwidget.SERVER))

    @Slot(str)
    def onClientMoveMade(self, move):
        if not self.boardWidget.popStack:
            self.boardWidget.makeMove(chess.Move.from_uci(move))
            self.updateMoveTable(move)
        else:
            self.boardWidget.popStack.appendleft(chess.Move.from_uci(move))
            self.controlPanelWidget.addMove(not self.boardWidget.board.turn, move)

    def searchForGame(self):
        self.client.moveMade.connect(self.onClientMoveMade)
        self.boardWidget.moveMade.connect(partial(self.client.sendPacket, client.MOVE))

        self.setWindowTitle(self.username)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Left:
                if self.boardWidget.board.move_stack:
                    self.controlPanelWidget.previousMoveButton.click()
            if event.key() == Qt.Key_Right:
                if self.boardWidget.popStack:
                    self.controlPanelWidget.nextMoveButton.click()
            return True
        return super().eventFilter(watched, event)
