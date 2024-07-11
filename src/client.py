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

import PySide2.QtCore as QtCore
import PySide2.QtWebSockets as QtWebSockets
from PySide2.QtNetwork import QAbstractSocket

import socket

import logging
from numpy import uint8, int64


ContentType = uint8
[NONE, PLAYER_DATA, WHITE_PLAYER_DATA, BLACK_PLAYER_DATA, MESSAGE, SERVER_MESSAGE, MOVE, ERROR] = range(8)


class Packet:
    def __init__(self, contentType: ContentType = NONE, payload: str = ""):
        self.contentType = contentType
        self.payload = payload

    def serialize(self) -> QtCore.QByteArray:
        _bytearray = QtCore.QByteArray()
        datastream = QtCore.QDataStream(_bytearray, QtCore.QIODevice.WriteOnly)

        datastream.writeUInt8(self.contentType)
        datastream.writeString(self.payload)

        return _bytearray

    @staticmethod
    def deserialize(_bytearray: QtCore.QByteArray) -> "Packet":
        packet = Packet()
        datastream = QtCore.QDataStream(_bytearray)

        packet.contentType = datastream.readUInt8()
        packet.payload = datastream.readString()

        return packet


class Client(QtCore.QObject):
    gameStarted = QtCore.Signal(Packet)
    moveMade = QtCore.Signal(str)
    messageReceived = QtCore.Signal(str)
    serverMessageReceived = QtCore.Signal(str)
    serverError = QtCore.Signal(str)

    def __init__(self, username, parent=None):
        super(Client, self).__init__(parent)

        self.webClient = QtWebSockets.QWebSocket(
            "", QtWebSockets.QWebSocketProtocol.VersionLatest, self)

        self.username = username
        self.functionMapper = {WHITE_PLAYER_DATA: self.processPlayerData,
                               BLACK_PLAYER_DATA: self.processPlayerData,
                               MOVE: self.processMove,
                               MESSAGE: self.processMessage,
                               SERVER_MESSAGE: self.processServerMessage,
                               ERROR: self.processError}

        self.webClient.connected.connect(self.authorize)
        self.webClient.binaryMessageReceived.connect(self.processBinaryMessage)

    def startConnectionWithServer(self):
        # retrieve local ip
        local_hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(local_hostname)[2]
        filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]
        ip = filtered_ips[:1][0]

        self.webClient.open(QtCore.QUrl.fromUserInput(f"ws://{ip}:21166"))

    @QtCore.Slot()
    def authorize(self):
        logging.debug("Web client connected to server")
        self.sendPacket(PLAYER_DATA, self.username)

    def sendPacket(self, contentType: ContentType, payload: str) -> int64:
        packet = Packet(contentType, payload)
        return self.webClient.sendBinaryMessage(packet.serialize())

    def processPlayerData(self, packet: Packet):
        self.gameStarted.emit(packet)

    def processMove(self, packet: Packet):
        self.moveMade.emit(packet.payload)

    def processMessage(self, message):
        self.messageReceived.emit(message.payload)

    def processServerMessage(self, message):
        self.serverMessageReceived.emit(message.payload)

    def processError(self, error):
        self.serverError.emit(error.payload)

    @QtCore.Slot()
    def processBinaryMessage(self, message: QtCore.QByteArray):
        packet = Packet.deserialize(message)
        if packet.contentType != NONE:
            self.functionMapper[packet.contentType](packet)
