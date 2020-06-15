import PySide2.QtWidgets as QtWidgets
from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QTextOption, QFontMetrics
from enum import Enum
import time


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

        self.setText(message)

    @Slot()
    def sizeChanged(self, newSize):
        fm = QFontMetrics(self.font())
        self.setFixedWidth(min([fm.horizontalAdvance(self.toPlainText())+10, newSize.toSize().width()]))
        self.setFixedHeight(newSize.height()+5)

    def focusOutEvent(self, event):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)


class MessageInputWidget(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super(MessageInputWidget, self).__init__(parent)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.document().documentLayout().documentSizeChanged.connect(self.sizeChanged)

    @Slot()
    def sizeChanged(self, newSize):
        if newSize.height() < 300:
            self.setMinimumHeight(newSize.height() + 5)


class ChatWidget(QtWidgets.QDockWidget):
    messageToBeSent = Signal(str)

    def __init__(self, parent=None):
        super(ChatWidget, self).__init__(parent)

        self.time = ""
        self.setMinimumWidth(300)

        self.container = QtWidgets.QWidget()

        self.mainLayout = QtWidgets.QVBoxLayout()

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.chat = QtWidgets.QWidget()
        self.chatLayout = QtWidgets.QVBoxLayout()
        self.chatLayout.setAlignment(Qt.AlignTop)

        self.messageInputWidget = MessageInputWidget()
        self.messageInputWidget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored
        ))
        self.sendButton = QtWidgets.QPushButton("Send")
        self.sendButton.clicked.connect(self.sendMessage)
        self.sendButton.setFocusPolicy(Qt.StrongFocus)

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

        self.chat.setLayout(self.chatLayout)
        self.scrollArea.setWidget(self.chat)
        self.container.setLayout(self.mainLayout)
        self.setWidget(self.container)

    @Slot()
    def sendMessage(self):
        self.showMessage(YOU, self.messageInputWidget.toPlainText())
        self.messageToBeSent.emit(self.messageInputWidget.toPlainText())

    def showMessage(self, sender: Sender, message: str) -> None:
        if self.time != time.strftime("%I:%M %p"):
            self.time = time.strftime("%I:%M %p")
            timeLabel = QtWidgets.QLabel(self.time)
            timeLabel.setSizePolicy(QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
            ))
            timeLabel.setAlignment(Qt.AlignCenter)
            self.chatLayout.addWidget(timeLabel)

        messageWidget = MessageWidget(message)

        if sender == YOU:
            self.chatLayout.addWidget(messageWidget, alignment=Qt.AlignLeft)
        elif sender == OPPONENT:
            self.chatLayout.addWidget(messageWidget, alignment=Qt.AlignRight)
        else:
            self.chatLayout.addWidget(messageWidget, alignment=Qt.AlignHCenter)
