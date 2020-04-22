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

import chess

import logging
from enum import Enum
from functools import partial
from typing import Optional, Mapping, Generator


class IllegalMove(Exception):
    pass


class CellWidget(QtWidgets.QPushButton):
    """
    """

    designated = QtCore.Signal(bool)

    def __init__(self, parent=None, isAccessible=False):
        super().__init__(parent=parent)

        self.isAccessible = isAccessible

        self._isPiece = False
        self._isHighlighted = False
        self._isMarked = False
        self.setCheckable(False)
        self._updateStyle()

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)

    def isPlain(self) -> bool:
        return not self._isPiece

    def setIsPlain(self, isPlain: bool):
        if self._isPiece == isPlain:
            self._isPiece = not isPlain
            self._updateStyle()

    def toPlain(self) -> "CellWidget":
        self.isAccessible = False
        self.setCheckable(False)
        self.setObjectName("")
        self.setIsPiece(False)
        return self

    def isPiece(self) -> bool:
        return self._isPiece

    def setIsPiece(self, isPiece: bool):
        self._isPiece = isPiece
        self._updateStyle()

    def toPiece(self, piece: chess.Piece) -> "CellWidget":
        self.setCheckable(self.isAccessible)
        self.setObjectName(f"cell_{chess.COLOR_NAMES[piece.color]}_{chess.PIECE_NAMES[piece.piece_type]}")
        self.setIsPiece(True)
        return self

    def isHighlighted(self) -> bool:
        return self._isHighlighted

    def highlight(self) -> "CellWidget":
        if not self._isHighlighted or self.isCheckable():
            self._isHighlighted = True
            self.setCheckable(False)
            self._updateStyle()
        return self

    def unhighlight(self) -> "CellWidget":
        if self._isHighlighted or self.isCheckable() != self.isAccessible:
            self._isHighlighted = False
            self.setCheckable(self.isAccessible)
            self._updateStyle()
        return self

    def setHighlighted(self, highlighted: bool) -> "CellWidget":
        if highlighted:
            return self.highlight()
        return self.unhighlight()

    def isMarked(self) -> bool:
        return self._isMarked

    def mark(self) -> "CellWidget":
        if not self._isMarked:
            self._isMarked = True
            self._updateStyle()
        self.designated.emit(self._isMarked)
        return self

    def unmark(self) -> "CellWidget":
        if self._isMarked:
            self._isMarked = False
            self._updateStyle()
        self.designated.emit(self._isMarked)
        return self

    def setMarked(self, marked: bool) -> "CellWidget":
        if marked:
            return self.mark()
        return self.unmark()

    def _updateStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.button() == QtCore.Qt.RightButton:
            self.setMarked(not self.isMarked())

    plain = QtCore.Property(bool, isPlain, setIsPlain)
    piece = QtCore.Property(bool, isPiece, setIsPiece)
    highlighted = QtCore.Property(bool, isHighlighted, setHighlighted)
    marked = QtCore.Property(bool, isMarked, setMarked, notify=designated)


class AccessibleSides(Enum):
    NONE = 0
    ONLY_WHITE = 1
    ONLY_BLACK = 2
    BOTH = 3


NO_SIDE = AccessibleSides.NONE
ONLY_WHITE_SIDE = AccessibleSides.ONLY_WHITE
ONLY_BLACK_SIDE = AccessibleSides.ONLY_BLACK
BOTH_SIDES = AccessibleSides.BOTH


class BoardWidget(QtWidgets.QLabel):
    """
    A graphical chess board.
    """

    moveMade = QtCore.Signal(str)

    def __init__(self, parent=None,
                 fen: Optional[str] = chess.STARTING_FEN,
                 flipped: bool = False,
                 sides: AccessibleSides = AccessibleSides.NONE):
        super().__init__(parent=parent)

        self.board = chess.Board(fen)
        self.flipped = flipped
        self.accessibleSides = sides

        self.defaultPixmap = self.pixmap()
        self.flippedPixmap = self.pixmap()
        self.lastCheckedCellWidget = None

        self._boardLayout = QtWidgets.QGridLayout()
        self._boardLayout.setContentsMargins(0, 0, 0, 0)
        self._boardLayout.setSpacing(0)

        def newCellWidget() -> CellWidget:
            cellWidget = CellWidget()
            cellWidget.clicked.connect(partial(self.onCellWidgetClicked, cellWidget))
            cellWidget.toggled.connect(partial(self.onCellWidgetToggled, cellWidget))
            cellWidget.designated.connect(self.onCellWidgetMarked)
            return cellWidget

        for i in range(8):
            for j in range(8):
                w = newCellWidget()
                self._boardLayout.addWidget(w, i, j)
        self.setLayout(self._boardLayout)

        self.setPieceMap(self.board.piece_map())

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                           QtWidgets.QSizePolicy.Ignored)

    def cellWidgets(self) -> Generator[CellWidget, None, None]:
        for w in self.children():
            if isinstance(w, CellWidget):
                yield w

    def cellIndexOfSquare(self, square: chess.Square) -> Optional[chess.Square]:
        if not self.flipped:
            return chess.square_mirror(square)
        return chess.square(7-chess.square_file(square), chess.square_rank(square))

    def squareOf(self, w: CellWidget) -> chess.Square:
        i = self._boardLayout.indexOf(w)
        if not self.flipped:
            return chess.square_mirror(i)
        return chess.square(7 - chess.square_file(i), chess.square_rank(i))

    def cellWidgetAtSquare(self, square: chess.Square) -> Optional[CellWidget]:
        """
        Returns the cell widget at the given square.
        """

        item = self._boardLayout.itemAt(self.cellIndexOfSquare(square))
        if item is not None:
            return item.widget()
        return None

    def updatePixmap(self) -> None:
        if not self.flipped:
            self.setPixmap(self.defaultPixmap)
        else:
            self.setPixmap(self.flippedPixmap)

    def setBoardPixmap(self, defaultPixmap, flippedPixmap) -> None:
        self.defaultPixmap = defaultPixmap
        self.flippedPixmap = flippedPixmap
        self.updatePixmap()

    def setAccessibleSides(self, accessibleSides: AccessibleSides):
        self.accessibleSides = accessibleSides
        self.setFen(self.board.fen())

    @QtCore.Slot()
    def onCellWidgetClicked(self, w: CellWidget):
        if w.isHighlighted():
            self.pushPiece(self.squareOf(w), self.lastCheckedCellWidget)

    @QtCore.Slot()
    def onCellWidgetToggled(self, w: CellWidget, toggled: bool):
        self.unhighlightCells()
        if toggled:
            self.uncheckCells(exceptFor=w)
            self.unmarkCells()
            self.highlightLegalMoveCellsFor(w)
            self.lastCheckedCellWidget = w

    @QtCore.Slot()
    def onCellWidgetMarked(self, marked: bool):
        if marked:
            self.uncheckCells()
            self.unhighlightCells()

    def setPieceAt(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        self.board.set_piece_at(square, piece)
        w = self.cellWidgetAtSquare(square)

        if self.accessibleSides == BOTH_SIDES:
            w.isAccessible = True
        elif piece.color == chess.WHITE:
            if self.accessibleSides == ONLY_WHITE_SIDE:
                w.isAccessible = True
        elif self.accessibleSides == ONLY_BLACK_SIDE:
            w.isAccessible = True

        w.toPiece(piece)

        return w

    def removePieceAt(self, square: chess.Square) -> CellWidget:
        w = self.cellWidgetAtSquare(square)
        w.toPlain()
        self.board.remove_piece_at(square)

        return w

    def addPiece(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        """
        This function is the safer version of the function
        `setPieceAt` for its ability to raise an error if the given
        square is invalid.

        Raises
        ------
        ValueError
            If the given square is already occupied.

        Returns
        -------
        The created cell widget.
        """

        if self.board.piece_at(square) is not None:
            raise ValueError("Square {} is occupied")
        return self.setPieceAt(square, piece)

    def synchronizeBoard(self) -> None:
        list(map(lambda w: w.toPlain(), self.cellWidgets()))

        for square, piece in self.board.piece_map().items():
            self.setPieceAt(square, piece)

    def setPieceMap(self, pieces: Mapping[int, chess.Piece]) -> None:
        self.board.set_piece_map(pieces)
        self.synchronizeBoard()

    def setFen(self, fen: Optional[str]) -> None:
        if fen is not None:
            self.board.set_fen(fen)
        else:
            self.board = chess.Board(None)
        self.synchronizeBoard()

    def isPseudoLegalPromotion(self, move: chess.Move) -> bool:
        piece = self.board.piece_at(move.from_square)

        if piece is not None and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                return chess.A8 <= move.to_square <= chess.H8
            elif piece.color == chess.BLACK:
                return chess.A1 <= move.to_square <= chess.H1
        return False

    def movePieceAt(self, fromSquare: chess.Square, toSquare: chess.Square):
        self.board.push(chess.Move(fromSquare, toSquare))
        self.synchronizeBoard()

    def movePiece(self, toSquare: chess.Square, w: CellWidget):
        self.movePieceAt(toSquare, self.squareOf(w))

    def pushPiece(self, toSquare: chess.Square, w: CellWidget) -> None:
        move = chess.Move(self.squareOf(w), toSquare)

        if self.isPseudoLegalPromotion(move):
            move.promotion = chess.QUEEN
            w.toPiece(move.promotion)

        if not self.board.is_legal(move):
            raise IllegalMove(f"illegal move {move} with {chess.PIECE_NAMES[self.board.piece_at(move.from_square).piece_type]}")
        logging.debug(f"\n{self.board.lan(move)} ({move.from_square} -> {toSquare})")

        self.board.push(move)
        self.synchronizeBoard()
        self.moveMade.emit(str(move))
        logging.debug(f"\n{self.board}\n")

        self.unhighlightCells()
        self.unmarkCells()

    def push(self, move: chess.Move) -> "BoardWidget":
        self.pushPiece(move.to_square, self.cellWidgetAtSquare(move.from_square))
        return self

    def pop(self) -> "BoardWidget":
        self.board.pop()
        self.synchronizeBoard()
        return self

    def highlightLegalMoveCellsFor(self, w: CellWidget) -> None:
        for move in self.board.legal_moves:
            if move.from_square == self.squareOf(w):
                self.cellWidgetAtSquare(move.to_square).highlight()

    def uncheckCells(self, exceptFor: Optional[CellWidget] = None):
        for w in self.cellWidgets():
            if w != exceptFor:
                w.setChecked(False)

    def unhighlightCells(self) -> None:
        list(map(lambda w: w.unhighlight(), self.cellWidgets()))

    def unmarkCells(self) -> None:
        list(map(lambda w: w.unmark(), self.cellWidgets()))

    def flip(self) -> "BoardWidget":
        self.flipped = not self.flipped
        self.synchronizeBoard()
        self.updatePixmap()
        return self

    def resizeEvent(self, event) -> None:
        s = min(self.width(), self.height())
        self.resize(s, s)
