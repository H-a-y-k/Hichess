import PySide2.QtWidgets as QtWidgets
from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt, Signal, Slot, QRegExp, QFile, QFileInfo, QDir
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


class _EngineEdit(QtWidgets.QWidget):
    def __init__(self, path, parent=None):
        super(_EngineEdit, self).__init__(parent)

        self.pathEdit = QtWidgets.QLineEdit(path)
        self.pathEdit.setPlaceholderText("Path")

        self.browseButton = QtWidgets.QPushButton("Browse")
        self.browseButton.clicked.connect(self.browse)

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.pathEdit)
        self.mainLayout.addWidget(self.browseButton)
        self.setLayout(self.mainLayout)

    @Slot()
    def browse(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Engine", QDir.currentPath())
        self.pathEdit.setText(filename[0])


class WaitDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(WaitDialog, self).__init__(parent)

        waitLabel = QtWidgets.QLabel("Waiting for a player...")
        waitLabel.setAlignment(Qt.AlignCenter)
        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)

        waitDialogLayout = QtWidgets.QVBoxLayout()
        waitDialogLayout.addWidget(waitLabel)
        waitDialogLayout.addWidget(cancelButton)
        self.setLayout(waitDialogLayout)


class _ChooseVariantSection(QtWidgets.QGroupBox):
    variantSelected = Signal(str)

    def __init__(self, parent=None):
        super(_ChooseVariantSection, self).__init__(parent)

        self.setTitle("Variant")
        self.mainLayout = QtWidgets.QVBoxLayout()

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

        self.mainLayout.addWidget(self.variantComboBox)
        self.mainLayout.addWidget(self.fromPositionLineEdit)
        self.mainLayout.addWidget(self.previewBoardWidget)

        self.setLayout(self.mainLayout)

    @Slot(str)
    def onVariantSelected(self, name: str):
        self.fromPositionLineEdit.setVisible(name == "From position")

        if name == "Standard":
            self.previewBoardWidget.reset()
        elif name == "From position":
            self.previewBoardWidget.setFen(self.fromPositionLineEdit.text())

    @Slot(str)
    def updatePreviewBoardWidget(self, fen: str):
        try:
            self.previewBoardWidget.setFen(fen)
        except Exception as e:
            pass


class _ChooseLevelSection(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(_ChooseLevelSection, self).__init__(parent)

        self.setTitle("Level")

        self.mainLayout = QtWidgets.QVBoxLayout()

        self.levelComboBox = QtWidgets.QComboBox()
        self.levelComboBox.addItem("Very Easy")
        self.levelComboBox.addItem("Easy 1")
        self.levelComboBox.addItem("Easy 2")
        self.levelComboBox.addItem("Medium 1")
        self.levelComboBox.addItem("Medium 2")
        self.levelComboBox.addItem("Hard 1")
        self.levelComboBox.addItem("Hard 2")
        self.levelComboBox.addItem("Very Hard")

        self.mainLayout.addWidget(self.levelComboBox)
        self.setLayout(self.mainLayout)


class _ChooseColorSection(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(_ChooseColorSection, self).__init__(parent)

        self.setTitle("Color")

        self.mainLayout = QtWidgets.QHBoxLayout()

        self.blackButton = QtWidgets.QPushButton("Black")
        self.randomButton = QtWidgets.QPushButton("Random")
        self.whiteButton = QtWidgets.QPushButton("White")

        self.blackButton.setFocusPolicy(Qt.NoFocus)
        self.randomButton.setFocusPolicy(Qt.NoFocus)
        self.whiteButton.setFocusPolicy(Qt.NoFocus)

        self.mainLayout.addWidget(self.blackButton)
        self.mainLayout.addWidget(self.randomButton)
        self.mainLayout.addWidget(self.whiteButton)
        self.setLayout(self.mainLayout)


class PveDialog(QDialog):
    def __init__(self, parent=None):
        super(PveDialog, self).__init__(parent)

        self.data = {
            "fen": chess.STARTING_FEN,
            "level": 0,
            "color": "white"
        }

        self.mainLayout = QtWidgets.QVBoxLayout()

        self.chooseVariantSection = _ChooseVariantSection()
        self.chooseLevelSection = _ChooseLevelSection()
        self.chooseColorSection = _ChooseColorSection()

        self.chooseColorSection.blackButton.clicked.connect(
            partial(self.doAccept, self.chooseColorSection.blackButton))
        self.chooseColorSection.randomButton.clicked.connect(
            partial(self.doAccept, self.chooseColorSection.randomButton))
        self.chooseColorSection.whiteButton.clicked.connect(
            partial(self.doAccept, self.chooseColorSection.whiteButton))

        self.mainLayout.setSpacing(10)

        self.mainLayout.addWidget(self.chooseVariantSection)
        self.mainLayout.addWidget(self.chooseLevelSection)
        self.mainLayout.addWidget(self.chooseColorSection)

        self.setLayout(self.mainLayout)

    @Slot(QtWidgets.QPushButton)
    def doAccept(self, colorButton):
        self.data["fen"] = self.chooseVariantSection.fromPositionLineEdit.text()
        self.data["level"] = self.chooseLevelSection.levelComboBox.currentIndex()

        colorName = colorButton.text().lower()
        if colorButton.text().lower() == "random":
            self.data["color"] = random.choice([chess.WHITE, chess.BLACK])
        else:
            self.data["color"] = (colorName == "white")

        self.accept()


class SettingsDialog(QtWidgets.QDialog):
    validator = QRegExpValidator(QRegExp("[A-Za-z0-9_]{6,16}"))

    def __init__(self, username, enginePath, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.newUsername = ""
        self.newEnginePath = ""

        self.mainLayout = QtWidgets.QFormLayout()

        self.usernameLineEdit = QtWidgets.QLineEdit(username)
        self.usernameLineEdit.setPlaceholderText("Username (a-zA-Z0-9_)")
        self.usernameLineEdit.setMinimumHeight(35)
        self.usernameLineEdit.setValidator(self.validator)
        self.usernameLineEdit.textChanged.connect(self.validateFields)

        self.engineEdit = _EngineEdit(enginePath)
        self.engineEdit.pathEdit.textChanged.connect(self.validateFields)

        buttonBox = QtWidgets.QDialogButtonBox()
        self.okButton = buttonBox.addButton("Ok", QtWidgets.QDialogButtonBox.AcceptRole)
        self.cancelButton = buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.okButton.clicked.connect(self._ok)
        self.cancelButton.clicked.connect(self.reject)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setAlignment(Qt.AlignBottom)
        self.mainLayout.addRow("Username", self.usernameLineEdit)
        self.mainLayout.addRow("Engine", self.engineEdit)
        self.mainLayout.addWidget(buttonBox)
        self.setLayout(self.mainLayout)

        self.validateFields()

    def _validateEnginePath(self, path):
        return QFile.exists(path) and QFileInfo(path).isFile()

    @Slot(str)
    def validateFields(self):
        usernameValid = self.validator.validate(self.usernameLineEdit.text(), 0) and \
                        6 <= len(self.usernameLineEdit.text()) <= 16
        pathValid = self._validateEnginePath(self.engineEdit.pathEdit.text())

        if not usernameValid or not pathValid:
            if self.okButton.isEnabled():
                self.okButton.setDisabled(True)
        else:
            if not self.okButton.isEnabled():
                self.okButton.setDisabled(False)

        if not usernameValid:
            self.usernameLineEdit.setStyleSheet("border: 1px solid red;")
        else:
            self.usernameLineEdit.setStyleSheet("border: 1px solid green;")

        if not pathValid:
            self.engineEdit.pathEdit.setStyleSheet("border: 1px solid red;")
        else:
            self.engineEdit.pathEdit.setStyleSheet("border: 1px solid green;")

    @Slot()
    def _ok(self):
        if self.validator.validate(self.usernameLineEdit.text(), 0):
            self.newUsername = self.usernameLineEdit.text()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid username")
            self.reject()

        if self._validateEnginePath(self.engineEdit.pathEdit.text()):
            self.newEnginePath = self.engineEdit.pathEdit.text()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "The specified engine's path does not exist.")
            self.reject()

        self.accept()
