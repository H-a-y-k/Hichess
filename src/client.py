import PySide2.QtCore as QtCore
import PySide2.QtWebSockets as QtWebSockets
from PySide2.QtNetwork import QAbstractSocket

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
        self.webClient.open(QtCore.QUrl.fromUserInput("ws://192.168.1.4:54545"))

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
