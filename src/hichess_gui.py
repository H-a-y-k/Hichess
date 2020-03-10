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
import PySide2.QtCore as QtCore
from PySide2.QtGui import QRegExpValidator
import PySide2.QtWebSockets as QtWebSockets
import PySide2.QtNetwork as QtNetwork
import hichess.hichess as hichess

import logging


class Client(QtCore.QObject):
    UDP_SERVER_PORT = 45454
    UDP_CLIENT_PORT = 45455

    def __init__(self, username, parent=None):
        super().__init__(parent)

        self.udpClient = QtNetwork.QUdpSocket(self)
        self.webClient = QtWebSockets.QWebSocket(
            "", QtWebSockets.QWebSocketProtocol.VersionLatest, self)

        self.udpClient.readyRead.connect(self.processPendingDatagrams)
        self.webClient.connected.connect(self.onConnected)
        self.webClient.textMessageReceived.connect(self.onTextMessageReceived)

        interfaces = QtNetwork.QNetworkInterface.allInterfaces()
        for interface in interfaces:
            if (interface.isValid() and
                    not interface.flags() & QtNetwork.QNetworkInterface.IsLoopBack and
                    not interface.flags() & QtNetwork.QNetworkInterface.IsPointToPoint and
                    interface.flags() & QtNetwork.QNetworkInterface.IsUp and
                    interface.flags() & QtNetwork.QNetworkInterface.IsRunning):
                addresses = interface.addressEntries()
                for address in addresses:
                    if (not address.ip().isNull() and
                            not address.ip().isLoopback() and
                            address.ip().protocol() == QtNetwork.QAbstractSocket.IPv4Protocol and
                            not address.broadcast().isNull()):
                        logging.debug(f"Address: {str(address.broadcast())}")
                        self.udpClient.bind(address.ip(), self.UDP_CLIENT_PORT,
                                            QtNetwork.QUdpSocket.ShareAddress)
                        self.udpClient.writeDatagram(QtCore.QByteArray("User = {}".format(username).encode()),
                                                     address.broadcast(), self.UDP_SERVER_PORT)
                        return

    @QtCore.Slot()
    def processPendingDatagrams(self):
        socket = self.sender()
        logging.debug("Processing datagrams...")
        while socket and socket.hasPendingDatagrams():
            datagram = socket.receiveDatagram()
            logging.debug(datagram.data())
            logging.debug(datagram.data().startsWith(b"ws://"))
            if datagram.data().startsWith(b"ws://"):
                self.webClient.open(QtCore.QUrl.fromEncoded(datagram.data()))

    @QtCore.Slot()
    def onConnected(self):
        logging.debug("Web client connected to server")

    @QtCore.Slot()
    def onTextMessageReceived(self, mes):
        logging.debug(mes)

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

    @QtCore.Slot()
    def connectToServer(self, username):
        self.client = Client(username, self)

    def playOnline(self):
        loginDialog = QtWidgets.QDialog(self)
        loginDialogLayout = QtWidgets.QVBoxLayout()

        nameEdit = QtWidgets.QLineEdit()
        nameRx = QtCore.QRegExp("[A-Za-z0-9_]{6,15}")
        nameEdit.setValidator(QRegExpValidator(nameRx))

        nameEdit.returnPressed.connect(lambda: (self.connectToServer(nameEdit.text())))

        loginDialogLayout.addWidget(nameEdit)
        loginDialog.setLayout(loginDialogLayout)

        loginDialog.exec_()
