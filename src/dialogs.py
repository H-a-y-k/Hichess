import PySide2.QtWidgets as QtWidgets
from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt, Signal, Slot, QRegExp
from PySide2.QtGui import QRegExpValidator, QPixmap

from functools import partial

from hichess.hichess import BoardWidget, BOTH_SIDES
import chess


class LoginDialog(QDialog):
    loginAccepted = Signal(str)
    loginRejected = Signal()

    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)

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
        if self.usernameLineEdit.validator().validate(self.usernameLineEdit.text(), 0):
            self.loginAccepted.emit(self.usernameLineEdit.text())
            self.close()


class PveDialog(QDialog):
    def __init__(self, parent=None):
        super(PveDialog, self).__init__(parent)

        self.data = {
            "variant": "standard",
            "timeControl": "unlimited",
            "level": 0,
            "color": "white"
        }

        self.layout = QtWidgets.QFormLayout()

        self.variantComboBox = QtWidgets.QComboBox()
        self.variantComboBox.addItem("Standard")
        self.variantComboBox.addItem("From Position")
        self.variantComboBox.currentIndexChanged[str].connect(self.onNewVariantSelected)

        self.fromPositionLineEdit = QtWidgets.QLineEdit(chess.STARTING_FEN)
        self.previewBoardWidget = BoardWidget()
        self.previewBoardWidget.setBoardPixmap(defaultPixmap=QPixmap(":/images/chessboard.png"),
                                               flippedPixmap=QPixmap(":/images/flipped_chessboard.png"))
        self.fromPositionLineEdit.textChanged.connect(self.updatePreviewBoardWidget)

        self.fromPositionLineEdit.hide()
        self.previewBoardWidget.hide()

        self.timeControlComboBox = QtWidgets.QComboBox()
        self.timeControlComboBox.addItem("Unlimited")
        self.timeControlComboBox.addItem("Real Time")
        self.timeControlComboBox.addItem("Correspondence")

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

        self.layout.addRow(QtWidgets.QLabel("Play against the Computer"))
        self.layout.addRow("Variant", self.variantComboBox)
        self.layout.addRow(self.fromPositionLineEdit)
        self.layout.addRow("", self.previewBoardWidget)
        self.layout.addRow("Time control", self.timeControlComboBox)
        self.layout.addRow("Difficulty", self.levelComboBox)
        self.layout.addRow(chooseColorLayout)
        self.setLayout(self.layout)

        self.setMinimumWidth(500)

    @Slot(str)
    def onNewVariantSelected(self, name: str):
        if name == "Standard":
            self.fromPositionLineEdit.hide()
            self.previewBoardWidget.hide()
            self.resize(self.width(), self.minimumHeight())
        elif name == "From Position":
            self.fromPositionLineEdit.show()
            self.previewBoardWidget.show()
            self.resize(self.width(), 500)

    @Slot(str)
    def updatePreviewBoardWidget(self, fen: str):
        try:
            self.previewBoardWidget.setFen(fen)
        except:
            pass

    @Slot(QtWidgets.QPushButton)
    def doAccept(self, colorButton):
        self.data["variant"] = self.variantComboBox.currentText().lower()
        self.data["timeControl"] = self.timeControlComboBox.currentText().lower()
        self.data["level"] = self.levelComboBox.currentIndex()
        self.data["color"] = colorButton.text().lower()
        self.accept()
