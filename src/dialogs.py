import PySide2.QtWidgets as QtWidgets
from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt, Signal, Slot, QRegExp
from PySide2.QtGui import QRegExpValidator, QPixmap

import random
from functools import partial

from hichess.hichess import BoardWidget, BOTH_SIDES
import chess


class HLineWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(HLineWidget, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class InvalidLogin(Exception):
    pass


class LoginDialog(QDialog):
    loginAccepted = Signal(str)
    loginRejected = Signal()

    validator = QRegExpValidator(QRegExp("[A-Za-z0-9_]{6,15}"))

    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.username = ""

        titleLabel = QtWidgets.QLabel("LOGIN")
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setMinimumHeight(35)

        self.usernameLineEdit = QtWidgets.QLineEdit()
        self.usernameLineEdit.setPlaceholderText("Username (a-zA-Z0-9_)")
        self.usernameLineEdit.setMinimumHeight(35)
        self.usernameLineEdit.setValidator(self.validator)
        self.usernameLineEdit.textChanged.connect(self.onUsernameTextChanged)

        rememberMeCheckBox = QtWidgets.QCheckBox("Remember me")
        rememberMeCheckBox.setMinimumHeight(35)

        self.loginButton = QtWidgets.QPushButton("Login")
        self.loginButton.clicked.connect(self.loginButtonClicked)
        self.loginButton.setDefault(True)
        self.loginButton.setMinimumHeight(35)
        self.loginButton.setDisabled(True)

        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.loginRejected.emit)
        self.cancelButton.setMinimumHeight(35)

        layout = QtWidgets.QFormLayout()
        layout.addRow(titleLabel)
        layout.addRow(self.usernameLineEdit)
        layout.addRow(rememberMeCheckBox)
        layout.addRow(self.cancelButton, self.loginButton)
        layout.setAlignment(titleLabel, Qt.AlignCenter)
        self.setLayout(layout)

        self.loginRejected.connect(self.reject)

    @Slot()
    def onUsernameTextChanged(self, text):
        if len(text) < 6:
            if self.loginButton.isEnabled():
                self.loginButton.setDisabled(True)
        elif not self.loginButton.isEnabled():
            self.loginButton.setEnabled(True)

    @Slot()
    def loginButtonClicked(self):
        if self.usernameLineEdit.validator().validate(self.usernameLineEdit.text(), 0):
            self.username = self.usernameLineEdit.text()
            self.loginAccepted.emit(self.username)
            self.accept()


class ChooseVariantSection(QtWidgets.QWidget):
    variantSelected = Signal(str)

    def __init__(self, parent=None):
        super(ChooseVariantSection, self).__init__(parent)

        self.layout = QtWidgets.QFormLayout()

        self.variantComboBox = QtWidgets.QComboBox()
        self.variantComboBox.addItem("Standard")
        self.variantComboBox.addItem("From position")
        self.variantComboBox.currentIndexChanged[str].connect(self.onVariantSelected)

        self.fromPositionLineEdit = QtWidgets.QLineEdit(chess.STARTING_FEN)
        self.previewBoardWidget = BoardWidget()
        self.previewBoardWidget.setBoardPixmap(defaultPixmap=QPixmap(":/images/chessboard.png"),
                                               flippedPixmap=QPixmap(":/images/flipped_chessboard.png"))
        self.fromPositionLineEdit.hide()

        self.fromPositionLineEdit.textChanged.connect(self.updatePreviewBoardWidget)

        self.layout.addRow("Variant", self.variantComboBox)
        self.layout.addRow("", self.fromPositionLineEdit)
        self.layout.addRow("", self.previewBoardWidget)

        self.setLayout(self.layout)

    @Slot(str)
    def onVariantSelected(self, name: str):
        self.fromPositionLineEdit.setVisible(name == "From position")

    @Slot(str)
    def updatePreviewBoardWidget(self, fen: str):
        try:
            self.previewBoardWidget.setFen(fen)
        except Exception as e:
            pass


class PveDialog(QDialog):
    def __init__(self, parent=None):
        super(PveDialog, self).__init__(parent)

        self.data = {
            "fen": chess.STARTING_FEN,
            "level": 0,
            "color": "white"
        }

        self.layout = QtWidgets.QVBoxLayout()

        self.chooseVariantSection = ChooseVariantSection()

        self.levelComboBox = QtWidgets.QComboBox()
        self.levelComboBox.addItem("Very Easy")
        self.levelComboBox.addItem("Easy 1")
        self.levelComboBox.addItem("Easy 2")
        self.levelComboBox.addItem("Medium 1")
        self.levelComboBox.addItem("Medium 2")
        self.levelComboBox.addItem("Hard 1")
        self.levelComboBox.addItem("Hard 2")
        self.levelComboBox.addItem("Very Hard")

        self.blackButton = QtWidgets.QPushButton("Black")
        self.randomButton = QtWidgets.QPushButton("Random")
        self.whiteButton = QtWidgets.QPushButton("White")

        self.blackButton.setFocusPolicy(Qt.NoFocus)
        self.randomButton.setFocusPolicy(Qt.NoFocus)
        self.whiteButton.setFocusPolicy(Qt.NoFocus)

        self.blackButton.clicked.connect(partial(self.doAccept, self.blackButton))
        self.randomButton.clicked.connect(partial(self.doAccept, self.randomButton))
        self.whiteButton.clicked.connect(partial(self.doAccept, self.whiteButton))

        chooseColorLayout = QtWidgets.QHBoxLayout()
        chooseColorLayout.addWidget(self.blackButton)
        chooseColorLayout.addWidget(self.randomButton)
        chooseColorLayout.addWidget(self.whiteButton)

        self.layout.setSpacing(5)

        self.layout.addWidget(QtWidgets.QLabel("Play against the Computer"))
        self.layout.addWidget(self.chooseVariantSection)
        self.layout.addWidget(HLineWidget())
        self.layout.addWidget(HLineWidget())
        self.layout.addWidget(self.levelComboBox)
        self.layout.addLayout(chooseColorLayout)

        self.setLayout(self.layout)

    @Slot(QtWidgets.QPushButton)
    def doAccept(self, colorButton):
        self.data["fen"] = self.chooseVariantSection.fromPositionLineEdit.text()
        self.data["level"] = self.levelComboBox.currentIndex()

        colorName = colorButton.text().lower()
        if colorButton.text().lower() == "random":
            self.data["color"] = random.choice([chess.WHITE, chess.BLACK])
        else:
            self.data["color"] = colorName == "white"

        self.accept()
