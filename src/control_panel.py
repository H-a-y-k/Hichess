from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PySide2.QtCore import Qt, Slot


class GameControlPanel(QWidget):
    def __init__(self, first: str, second: str, parent=None):
        super(GameControlPanel, self).__init__(parent)

        self.flipButton = QPushButton("*")
        self.toStartFenButton = QPushButton("<<")
        self.previousMoveButton = QPushButton("<")
        self.nextMoveButton = QPushButton(">")
        self.toCurrentFenButton = QPushButton(">>")

        self.toStartFenButton.setDisabled(True)
        self.previousMoveButton.setDisabled(True)
        self.nextMoveButton.setDisabled(True)
        self.toCurrentFenButton.setDisabled(True)

        self.toolButtonsLayout = QHBoxLayout()
        self.toolButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.toolButtonsLayout.setSpacing(0)
        self.toolButtonsLayout.addWidget(self.flipButton)
        self.toolButtonsLayout.addWidget(self.toStartFenButton)
        self.toolButtonsLayout.addWidget(self.previousMoveButton)
        self.toolButtonsLayout.addWidget(self.nextMoveButton)
        self.toolButtonsLayout.addWidget(self.toCurrentFenButton)

        self.nextColumn = 0

        self.firstName = QLabel(first)
        self.secondName = QLabel(second)

        self.moveTable = QTableWidget()
        self.moveTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.moveTable.setFocusPolicy(Qt.NoFocus)
        self.moveTable.setSelectionMode(QTableWidget.SingleSelection)
        self.moveTable.currentCellChanged.connect(self.onCurrentChanged)

        self.moveTable.setColumnCount(2)
        self.moveTable.horizontalHeader().hide()
        self.moveTable.setMaximumHeight(300)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addStretch()
        layout.addLayout(self.toolButtonsLayout)
        layout.addWidget(self.firstName)
        layout.addWidget(self.moveTable)
        layout.addWidget(self.secondName)
        layout.addStretch()
        layout.setSpacing(0)

        self.setLayout(layout)

    def isLive(self) -> bool:
        if not self.moveTable.rowCount():
            return True
        return (self.moveTable.currentRow() == self.moveTable.rowCount() - 1 and
                self.moveTable.currentColumn() != self.nextColumn)

    def reset(self):
        self.moveTable.setRowCount(0)
        self.nextColumn = 0
        self.toStartFenButton.setDisabled(True)
        self.previousMoveButton.setDisabled(True)
        self.nextMoveButton.setDisabled(True)
        self.toCurrentFenButton.setDisabled(True)

    @Slot(int, int)
    def onCurrentChanged(self, row, column):
        self.toStartFenButton.setDisabled(self.moveTable.currentItem() is None)
        self.previousMoveButton.setDisabled(self.moveTable.currentItem() is None)

    def toPreviousCell(self):
        current = self.moveTable.currentItem()

        if current is not None:
            row = current.row()
            column = current.column()

            if row == column == 0:
                self.moveTable.setCurrentCell(-1, -1)
            else:
                prevCoord = row * 2 + column - 1
                if prevCoord % 2:
                    row -= 1

                self.moveTable.setCurrentCell(row, not column)

    def toNextCell(self):
        current = self.moveTable.currentItem()

        if self.moveTable.rowCount():
            if current is None:
                self.moveTable.setCurrentCell(0, 0)
            else:
                row = current.row()
                column = current.column()

                nextCoord = row * 2 + column + 1
                if nextCoord % 2 == 0:
                    row += 1

                self.moveTable.setCurrentCell(row, not column)

    def addMove(self, move: str) -> QTableWidgetItem:
        if self.isLive():
            if not self.nextColumn:
                self.moveTable.setRowCount(self.moveTable.rowCount() + 1)

        item = QTableWidgetItem(move)
        self.moveTable.setItem(self.moveTable.rowCount()-1, self.nextColumn, item)

        self.nextColumn = not self.nextColumn

        return item

    def popMove(self):
        if self.moveTable.rowCount():
            if self.isLive():
                self.toPreviousCell()

            self.nextColumn = not self.nextColumn

            self.moveTable.takeItem(self.moveTable.rowCount() - 1, self.nextColumn)

            if not self.nextColumn:
                self.moveTable.setRowCount(self.moveTable.rowCount()-1)

    def swapNames(self):
        temp = self.firstName.text()

        self.firstName.setText(self.secondName.text())
        self.secondName.setText(temp)
