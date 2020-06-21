import PySide2.QtWidgets as QtWidgets
from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QTextOption, QFontMetrics, QKeySequence
from enum import Enum
import time

import textwrap


class Sender(Enum):
    YOU = 0
    OPPONENT = 1
    SERVER = 2


YOU = Sender.YOU
OPPONENT = Sender.OPPONENT
SERVER = Sender.SERVER


class MessageWidget(QtWidgets.QTextBrowser):
    def __init__(self, message: str, parent=None):
        super(MessageWidget, self).__init__(parent)

        self.document().documentLayout().documentSizeChanged.connect(self.sizeChanged)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setPlainText(message)

    @Slot()
    def sizeChanged(self, newSize):
        fm = QFontMetrics(self.font())
        self.setMaximumWidth(max(min([fm.horizontalAdvance(self.toPlainText())+10, newSize.toSize().width()+10]), 40))
        if self.width() < self.document().textWidth():
            self.document().setTextWidth(self.width())
        self.setFixedHeight(newSize.height()+2)

    def focusOutEvent(self, event):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)


class MessageInputWidget(QtWidgets.QTextEdit):
    returnPressed = Signal()

    def __init__(self, parent=None):
        super(MessageInputWidget, self).__init__(parent)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.document().documentLayout().documentSizeChanged.connect(self.sizeChanged)

    @Slot()
    def sizeChanged(self, newSize):
        if newSize.height() < 300:
            self.setMinimumHeight(newSize.height() + 20)
        else:
            self.setMinimumHeight(300)


class ChatWidget(QtWidgets.QDockWidget):
    messageToBeSent = Signal(str)

    def __init__(self, parent=None):
        super(ChatWidget, self).__init__(parent=parent, flags=Qt.Window)

        self.time = ""
        self.setMinimumWidth(300)

        self.container = QtWidgets.QWidget()

        self.mainLayout = QtWidgets.QVBoxLayout()

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.chat = QtWidgets.QWidget()
        self.scrollArea.setFocusPolicy(Qt.NoFocus)
        self.chatLayout = QtWidgets.QVBoxLayout()
        self.chatLayout.setAlignment(Qt.AlignTop)

        self.messageInputWidget = MessageInputWidget()
        self.messageInputWidget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored
        ))

        self.sendButton = QtWidgets.QPushButton("Send")
        self.sendButton.clicked.connect(self.sendMessage)

        self.messageInputLayout = QtWidgets.QHBoxLayout()
        self.messageInputLayout.addWidget(self.messageInputWidget)
        self.messageInputLayout.addWidget(self.sendButton)
        self.messageInputLayout.setAlignment(Qt.AlignCenter)
        self.messageInputLayout.setContentsMargins(0, 0, 0, 0)
        self.messageInputLayout.setSpacing(0)

        self.mainLayout.addWidget(self.scrollArea)
        self.mainLayout.addLayout(self.messageInputLayout)
        self.mainLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.lastMessageSender = None

        self.scrollArea.verticalScrollBar().rangeChanged.connect(self.onRangeChanged)

        self.chat.setLayout(self.chatLayout)
        self.scrollArea.setWidget(self.chat)
        self.container.setLayout(self.mainLayout)
        self.setWidget(self.container)

        self.setFocusProxy(self.messageInputWidget)

    @Slot()
    def onRangeChanged(self, min, max):
        if self.lastMessageSender == YOU:
            self.lastMessageSender = None
            self.scrollArea.verticalScrollBar().setValue(max)

    @Slot()
    def sendMessage(self):
        text = self.messageInputWidget.toPlainText()
        wrapped = textwrap.wrap(text, 1600)
        for chunk in wrapped:
            self.showMessage(YOU, chunk)
            self.messageToBeSent.emit(chunk)
        self.messageInputWidget.clear()
        self.messageInputWidget.setFocus()

    def showMessage(self, sender: Sender, message: str) -> None:
        if self.time != time.strftime("%I:%M %p"):
            self.time = time.strftime("%I:%M %p")
            timeLabel = QtWidgets.QLabel(self.time)
            timeLabel.setSizePolicy(QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
            ))
            timeLabel.setAlignment(Qt.AlignCenter)
            self.chatLayout.addWidget(timeLabel)

        self.lastMessageSender = sender

        messageWidget = MessageWidget(message)

        if sender == YOU:
            self.chatLayout.addWidget(messageWidget, alignment=Qt.AlignLeft)
        elif sender == OPPONENT:
            self.chatLayout.addWidget(messageWidget, alignment=Qt.AlignRight)
        else:
            self.chatLayout.addWidget(messageWidget, alignment=Qt.AlignHCenter)
