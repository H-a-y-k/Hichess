from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PySide2.QtCore import QModelIndex
from collections import deque

import chess


class GameControlPanel(QWidget):
    def __init__(self, first: str, second: str, parent=None):
        super(GameControlPanel, self).__init__(parent)

        self.flipButton = QPushButton("*")
        self.toStartFenButton = QPushButton("<<")
        self.previousMoveButton = QPushButton("<")
        self.nextMoveButton = QPushButton(">")
        self.toCurrentFenButton = QPushButton(">>")

        self.toolButtonsLayout = QHBoxLayout()
        self.toolButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.toolButtonsLayout.setSpacing(0)
        self.toolButtonsLayout.addWidget(self.flipButton)
        self.toolButtonsLayout.addWidget(self.toStartFenButton)
        self.toolButtonsLayout.addWidget(self.previousMoveButton)
        self.toolButtonsLayout.addWidget(self.nextMoveButton)
        self.toolButtonsLayout.addWidget(self.toCurrentFenButton)

        self.moves = []
        self._column = 0

        self.firstName = QLabel(first)
        self.secondName = QLabel(second)

        self.moveTable = QTableWidget()
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
                self.moveTable.currentColumn() != self._column)

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
            if not self._column:
                self.moveTable.setRowCount(self.moveTable.rowCount() + 1)

        item = QTableWidgetItem(move)
        self.moveTable.setItem(self.moveTable.rowCount()-1, self._column, item)

        self._column = not self._column

        return item

    def popMove(self):
        if self.moveTable.rowCount():
            if self.isLive():
                self.toPreviousCell()

            self._column = not self._column

            self.moveTable.takeItem(self.moveTable.rowCount() - 1, self._column)

            if not self._column:
                self.moveTable.setRowCount(self.moveTable.rowCount()-1)

    def swapNames(self):
        temp = self.firstName.text()

        self.firstName.setText(self.secondName.text())
        self.secondName.setText(temp)
