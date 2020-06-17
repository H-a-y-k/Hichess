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
from PySide2.QtCore import Qt, Slot, QObject
from PySide2.QtGui import QPixmap, QIcon, QKeySequence
from PySide2.QtNetwork import QAbstractSocket

import hichess.hichess as hichess
import chess
from stockfish import Stockfish

from functools import partial

import client
import dialogs
import control_panel
import chatwidget

import pyperclip


class HichessGui(QtWidgets.QMainWindow):
    def __init__(self, username: str):
        super(HichessGui, self).__init__()

        self.username = username

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.boardWidget = hichess.BoardWidget(flipped=False, sides=hichess.BOTH_SIDES)
        self.boardWidget.setBoardPixmap(defaultPixmap=QPixmap(":/images/chessboard.png"),
                                        flippedPixmap=QPixmap(":/images/flipped_chessboard.png"))
        self.boardWidget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding
        ))
        self.boardWidget.setFocusPolicy(Qt.StrongFocus)

        self.boardWidget.moveMade.connect(self.updateMoveTable)
        self.boardWidget.checkmate.connect(self.onCheckmate)
        self.boardWidget.draw.connect(self.onDraw)
        self.boardWidget.gameOver.connect(self.onGameOver)

        self.stockfishEngine = None

        self.controlPanelWidget = control_panel.GameControlPanel(self.username, self.username)
        self.controlPanelWidget.setFocusPolicy(Qt.NoFocus)
        self.controlPanelWidget.flipButton.clicked.connect(self.flip)
        self.controlPanelWidget.toStartFenButton.clicked.connect(self.toStartFen)
        self.controlPanelWidget.previousMoveButton.clicked.connect(self.previousMove)
        self.controlPanelWidget.nextMoveButton.clicked.connect(self.nextMove)
        self.controlPanelWidget.toCurrentFenButton.clicked.connect(self.toCurrentFen)
        self.controlPanelWidget.moveTable.cellClicked.connect(self.onCellClicked)

        self.client = client.Client(self.username, self)

        self.client.webClient.error.connect(self.onClientErrorReceived)
        self.client.serverError.connect(self.onServerError)
        self.client.webClient.connected.connect(self.onClientConnected)
        self.client.gameStarted.connect(self.startGame)
        self.client.moveMade.connect(self.onClientMoveMade)
        self.waitDialog = dialogs.WaitDialog(self)

        self.chatWidget = chatwidget.ChatWidget()

        self.toolbar = QtWidgets.QToolBar()
        self.backAction = QtWidgets.QAction(QIcon(":/images/back.png"), "Back")
        self.fullscreenAction = QtWidgets.QAction(QIcon(":/images/fullscreen.png"), "Fullscreen")
        self.themeAction = QtWidgets.QAction(QIcon(":/images/lighttheme.png"), "Theme")
        self.zenModeAction = QtWidgets.QAction(QIcon(":/images/zenmode.png"), "Zenmode")
        self.copyFenAction = QtWidgets.QAction(QIcon(":/images/copy.png"), "Copy Fen")

        self.backAction.triggered.connect(self.toMainMenu)
        self.fullscreenAction.triggered.connect(self.updateFullscreen)
        self.zenModeAction.triggered.connect(self.updateZenMode)
        self.copyFenAction.triggered.connect(partial(pyperclip.copy, self.boardWidget.board.fen()))

        self.toolbar.addAction(self.backAction)
        self.toolbar.addAction(self.fullscreenAction)
        self.toolbar.addAction(self.themeAction)
        self.toolbar.addAction(self.zenModeAction)
        self.toolbar.addAction(self.copyFenAction)

        self.zenmode = False

        self.backAction.setShortcut(QKeySequence(Qt.Key_Escape))
        self.fullscreenAction.setShortcut(QKeySequence("Ctrl+F"))
        self.addToolBar(Qt.RightToolBarArea, self.toolbar)
        self.toolbar.hide()

        self.setCentralWidget(self.stackedWidget)
        self.setupMainMenuScene()
        self.setupGameScene()

    @Slot()
    def toMainMenu(self):
        self.toolbar.hide()

        self.boardWidget.reset()

        self.controlPanelWidget.reset()
        self.stackedWidget.setCurrentIndex(0)

        if self.stockfishEngine:
            self.toolbar.hide()
            self.boardWidget.moveMade.disconnect(self.pveOnMoveMade)
            self.stockfishEngine = None

        if self.client.webClient.state() == QAbstractSocket.ConnectedState:
            self.client.webClient.close()
        if self.chatWidget.isVisible():
            self.chatWidget.close()
            self.chatWidget = chatwidget.ChatWidget()

    @Slot()
    def updateFullscreen(self):
        if self.isFullScreen():
            self.setWindowState(self.windowState() & ~Qt.WindowFullScreen)
        else:
            self.setWindowState(self.windowState() | Qt.WindowFullScreen)

    @Slot()
    def updateZenMode(self):
        isFullscreen = self.windowState() & Qt.WindowFullScreen
        if not (not self.zenmode and isFullscreen):
            self.updateFullscreen()

        self.zenmode = not self.zenmode

        self.fullscreenAction.setDisabled(self.zenmode)
        self.controlPanelWidget.moveTable.setVisible(not self.zenmode)
        self.controlPanelWidget.firstName.setVisible(not self.zenmode)
        self.controlPanelWidget.secondName.setVisible(not self.zenmode)

    @Slot(str)
    def pveOnMoveMade(self, move):
        if not self.boardWidget.board.is_game_over():
            self.stockfishEngine.set_fen_position(self.boardWidget.board.fen())

            color = (self.boardWidget.accessibleSides == hichess.ONLY_WHITE_SIDE)

            if self.boardWidget.board.turn != color:
                self.boardWidget.push(chess.Move.from_uci(self.stockfishEngine.get_best_move()))
        else:
            if self.stockfishEngine:
                self.boardWidget.moveMade.disconnect(self.pveOnMoveMade)
                self.stockfishEngine = None

    def login(self):
        loginDialog = dialogs.LoginDialog(self)
        status = loginDialog.exec_()

        if status == dialogs.LoginDialog.Accepted:
            self.username = loginDialog.username
        else:
            raise dialogs.InvalidLogin()

    @Slot()
    def onClientConnected(self):
        self.client.gameStarted.connect(self.waitDialog.accept)
        self.waitDialog.exec_()

    @Slot()
    def onClientErrorReceived(self, error):
        if error == QAbstractSocket.SocketTimeoutError or error == QAbstractSocket.ConnectionRefusedError:
            QtWidgets.QMessageBox.warning(self, "Error",
                                          "Couldn't connect to the server")
        elif error == QAbstractSocket.RemoteHostClosedError:
            self.boardWidget.accessibleSides = hichess.BOTH_SIDES

    @Slot(str)
    def onServerError(self, error):
        QtWidgets.QMessageBox.warning(self, "Server", error)
        if self.waitDialog.isVisible():
            self.waitDialog.close()
        self.client.webClient.abort()
        self.username = ""
        self.login()

    @Slot()
    def onCheckmate(self, side):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Checkmate")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(f"{chess.COLOR_NAMES[side]} player won the game!")
        msg.exec_()

    @Slot()
    def onDraw(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Draw")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("This is a draw")
        msg.exec_()

    @Slot()
    def onGameOver(self):
        if self.client.webClient.state() == QAbstractSocket.ConnectedState:
            self.client.webClient.close(0)

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

        self.stackedWidget.addWidget(menuScene)

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
        self.boardWidget.goToMove(0)
        self.controlPanelWidget.moveTable.setCurrentCell(-1, -1)

        if not self.boardWidget.blockBoardOnPop:
            self.controlPanelWidget.moveTable.setRowCount(0)
            self.controlPanelWidget.nextColumn = 0

        if self.boardWidget.popStack:
            self.controlPanelWidget.toCurrentFenButton.setDisabled(False)
            self.controlPanelWidget.nextMoveButton.setDisabled(False)

    @Slot()
    def toCurrentFen(self):
        if not self.boardWidget.blockBoardOnPop:
            popStack = self.boardWidget.popStack.copy()
            while popStack:
                self.updateMoveTable(self.boardWidget.board.san(popStack.pop()))

        moveID = len(self.boardWidget.board.move_stack) + len(self.boardWidget.popStack)
        self.boardWidget.goToMove(moveID)
        self.controlPanelWidget.moveTable.setCurrentCell(
            self.controlPanelWidget.moveTable.rowCount()-1, not self.controlPanelWidget.nextColumn)

        if not self.boardWidget.popStack:
            self.controlPanelWidget.toCurrentFenButton.setDisabled(True)
            self.controlPanelWidget.nextMoveButton.setDisabled(True)

    @Slot()
    def previousMove(self):
        if self.boardWidget.board.move_stack:
            self.boardWidget.pop()
            if not self.boardWidget.blockBoardOnPop:
                self.controlPanelWidget.popMove()
            else:
                self.controlPanelWidget.toPreviousCell()

            if self.boardWidget.popStack:
                self.controlPanelWidget.toCurrentFenButton.setDisabled(False)
                self.controlPanelWidget.nextMoveButton.setDisabled(False)

    @Slot()
    def nextMove(self):
        if self.boardWidget.popStack:
            move = self.boardWidget.unpop()

            if not self.boardWidget.blockBoardOnPop:
                self.updateMoveTable(move)
            else:
                self.controlPanelWidget.toNextCell()

            if not self.boardWidget.popStack:
                self.controlPanelWidget.toCurrentFenButton.setDisabled(True)
                self.controlPanelWidget.nextMoveButton.setDisabled(True)

    @Slot()
    def onCellClicked(self, row, column):
        if self.controlPanelWidget.moveTable.item(row, column):
            moveNumber = row * 2 + column
            self.boardWidget.goToMove(moveNumber+1)

    def setupGameScene(self):
        gameSceneWidget = QtWidgets.QWidget()

        gameSceneLayout = QtWidgets.QHBoxLayout()
        gameSceneLayout.addWidget(self.boardWidget)
        gameSceneLayout.addWidget(self.controlPanelWidget)
        gameSceneLayout.setContentsMargins(0, 0, 0, 0)
        gameSceneLayout.setAlignment(Qt.AlignTop)
        gameSceneWidget.setLayout(gameSceneLayout)

        self.stackedWidget.addWidget(gameSceneWidget)

    @Slot()
    def playPve(self):
        pveDialog = dialogs.PveDialog(self)
        pveDialog.setMinimumSize(500, 630)
        res = pveDialog.exec_()

        if res == QtWidgets.QDialog.Accepted:
            self.toolbar.show()

            self.boardWidget.blockBoardOnPop = True
            self.controlPanelWidget.moveTable.setDisabled(False)

            SKILL_LEVELS = [0, 4, 8, 12, 14, 16, 18, 20]
            fen, level, color = pveDialog.data.values()
            self.controlPanelWidget.firstName.setText(f"Stockfish {SKILL_LEVELS[level]}")

            self.stockfishEngine = Stockfish()

            # fen
            self.stockfishEngine.set_fen_position(fen)

            # level
            self.stockfishEngine.set_skill_level(SKILL_LEVELS[level])

            self.boardWidget.moveMade.connect(self.pveOnMoveMade)

            # color
            if color == chess.WHITE:
                self.boardWidget.accessibleSides = hichess.ONLY_WHITE_SIDE
                self.boardWidget.flipped = False
            elif color == chess.BLACK:
                self.boardWidget.accessibleSides = hichess.ONLY_BLACK_SIDE
                self.boardWidget.flipped = True

            self.stockfishEngine.set_fen_position(self.boardWidget.board.fen())
            if self.boardWidget.board.turn != color:
                self.boardWidget.push(chess.Move.from_uci(self.stockfishEngine.get_best_move()))

            self.stackedWidget.setCurrentIndex(1)

    @Slot()
    def playOfflinePvp(self):
        self.toolbar.show()
        self.boardWidget.blockBoardOnPop = False
        self.boardWidget.accessibleSides = hichess.BOTH_SIDES
        self.controlPanelWidget.moveTable.setDisabled(True)
        self.stackedWidget.setCurrentIndex(1)

    @Slot()
    def playOnlinePvp(self):
        if not dialogs.LoginDialog.validator.validate(self.username, 0):
            self.login()
        self.toolbar.show()
        self.client.username = self.username
        self.client.startConnectionWithServer()

    @Slot()
    def startGame(self, packet: client.Packet):
        self.boardWidget.moveMade.connect(partial(self.client.sendPacket, client.MOVE))

        self.boardWidget.blockBoardOnPop = True
        self.controlPanelWidget.moveTable.setDisabled(False)

        self.stackedWidget.setCurrentIndex(1)

        opponentUsername = packet.payload

        self.controlPanelWidget.firstName.setText(opponentUsername)
        self.controlPanelWidget.secondName.setText(self.username)

        if packet.contentType == client.WHITE_PLAYER_DATA:
            self.boardWidget.accessibleSides = hichess.ONLY_WHITE_SIDE
            self.boardWidget.synchronize()
        elif packet.contentType == client.BLACK_PLAYER_DATA:
            self.boardWidget.accessibleSides = hichess.ONLY_BLACK_SIDE
            self.boardWidget.flip()

        self.addDockWidget(Qt.LeftDockWidgetArea, self.chatWidget)
        self.chatWidget.messageToBeSent.connect(partial(self.client.sendPacket, client.MESSAGE))
        self.client.messageReceived.connect(partial(self.chatWidget.showMessage, chatwidget.OPPONENT))
        self.client.serverMessageReceived.connect(partial(self.chatWidget.showMessage, chatwidget.SERVER))

    @Slot(str)
    def onClientMoveMade(self, move):
        if not self.boardWidget.popStack:
            self.boardWidget.makeMove(self.boardWidget.board.parse_san(move))
            self.updateMoveTable(move)
        else:
            self.boardWidget.popStack.appendleft(chess.Move.from_uci(move))
            self.controlPanelWidget.addMove(move)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            if self.boardWidget.board.move_stack:
                self.previousMove()
        elif event.key() == Qt.Key_Right:
            if self.boardWidget.popStack:
                self.nextMove()
