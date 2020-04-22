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

import unittest

import hichess.hichess as hichess
import chess
import chess.pgn

from PySide2.QtWidgets import QApplication, QSizePolicy

import itertools
import os
import sys


class CellWidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.cellWidget = hichess.CellWidget()

    def testInit(self):
        self.assertTrue(self.cellWidget.isPlain())
        self.assertFalse(self.cellWidget.isAccessible)
        self.assertFalse(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())
        self.assertEqual(self.cellWidget.sizePolicy(), QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def testIsPlain(self):
        self.assertTrue(self.cellWidget.isPlain())
        self.cellWidget.setProperty("plain", False)
        self.assertFalse(self.cellWidget.isPlain())
        self.cellWidget.setProperty("plain", True)
        self.assertTrue(self.cellWidget.isPlain())

    def testSetIsPlain(self):
        self.assertTrue(self.cellWidget.isPlain())
        self.cellWidget.setIsPlain(False)
        self.assertFalse(self.cellWidget.isPlain())
        self.cellWidget.setIsPlain(True)
        self.assertTrue(self.cellWidget.isPlain())

    def testToPlain(self):
        self.cellWidget.isAccessible = True

        self.cellWidget.toPlain()
        self.assertTrue(self.cellWidget.isPlain())
        self.assertFalse(self.cellWidget.isAccessible)
        self.assertFalse(self.cellWidget.isCheckable())
        self.assertFalse(self.cellWidget.objectName())

    def testIsPiece(self):
        self.assertFalse(self.cellWidget.isPiece())
        self.cellWidget.setIsPiece(True)
        self.assertTrue(self.cellWidget.isPiece())
        self.cellWidget.setIsPiece(False)
        self.assertFalse(self.cellWidget.isPiece())

    def setIsPiece(self):
        self.assertFalse(self.cellWidget.isPiece())
        self.cellWidget.setIsPiece(True)
        self.assertTrue(self.cellWidget.isPiece())
        self.cellWidget.setIsPiece(False)
        self.assertFalse(self.cellWidget.isPiece())

    def testToPiece(self):
        for pieceType, color in itertools.product(chess.PIECE_TYPES, chess.COLORS):
            self.cellWidget.toPiece(chess.Piece(pieceType, color))
            self.assertTrue(self.cellWidget.isPiece())
            self.assertFalse(self.cellWidget.isAccessible)
            self.assertFalse(self.cellWidget.isCheckable())
            self.assertEqual(self.cellWidget.objectName(), f"cell_{chess.COLOR_NAMES[color]}_{chess.PIECE_NAMES[pieceType]}")

        self.cellWidget = hichess.CellWidget(isAccessible=True)
        for pieceType, color in itertools.product(chess.PIECE_TYPES, chess.COLORS):
            self.cellWidget.toPiece(chess.Piece(pieceType, color))
            self.assertTrue(self.cellWidget.isPiece())
            self.assertTrue(self.cellWidget.isAccessible)
            self.assertTrue(self.cellWidget.isCheckable())
            self.assertEqual(self.cellWidget.objectName(), f"cell_{chess.COLOR_NAMES[color]}_{chess.PIECE_NAMES[pieceType]}")

    def testIsHighlighted(self):
        self.assertFalse(self.cellWidget.isHighlighted())
        self.cellWidget.setProperty("highlighted", True)
        self.assertTrue(self.cellWidget.isHighlighted())
        self.cellWidget.setProperty("highlighted", False)
        self.assertFalse(self.cellWidget.isHighlighted())

    def testHighlight(self):
        self.cellWidget = hichess.CellWidget()
        self.assertFalse(self.cellWidget.isHighlighted())
        self.cellWidget.highlight()
        self.assertTrue(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

    def testUnhighlight(self):
        self.assertFalse(self.cellWidget.isHighlighted())
        self.cellWidget.highlight()
        self.assertTrue(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

        self.cellWidget.unhighlight()
        self.assertFalse(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

        self.cellWidget.isAccessible = True
        self.cellWidget.unhighlight()
        self.assertTrue(self.cellWidget.isCheckable())

        self.cellWidget.highlight()
        self.assertTrue(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

    def testSetHighlighted(self):
        self.assertFalse(self.cellWidget.isHighlighted())
        self.cellWidget.setHighlighted(True)
        self.assertTrue(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

        self.cellWidget.setHighlighted(False)
        self.assertFalse(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

        self.cellWidget.isAccessible = True
        self.cellWidget.setHighlighted(False)
        self.assertTrue(self.cellWidget.isCheckable())

        self.cellWidget.setHighlighted(True)
        self.assertTrue(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

    def isMarked(self):
        self.assertFalse(self.cellWidget.isMarked())
        self.cellWidget.setProperty("marked", True)
        self.assertTrue(self.cellWidget.isMarked())
        self.cellWidget.setProperty("marked", False)
        self.assertFalse(self.cellWidget.isMarked())

    def testMark(self):
        self.assertFalse(self.cellWidget.isMarked())
        self.cellWidget.mark()
        self.assertTrue(self.cellWidget.isMarked())

    def testUnmark(self):
        self.assertFalse(self.cellWidget.isMarked())
        self.cellWidget.mark()
        self.assertTrue(self.cellWidget.isMarked())

        self.cellWidget.unmark()
        self.assertFalse(self.cellWidget.isMarked())

    def testSetMarked(self):
        self.cellWidget = hichess.CellWidget()

        self.assertFalse(self.cellWidget.isMarked())
        self.cellWidget.mark()
        self.assertTrue(self.cellWidget.isMarked())

        self.cellWidget.mark()
        self.assertTrue(self.cellWidget.isMarked())

        self.cellWidget.unmark()
        self.assertFalse(self.cellWidget.isMarked())


class BoardWidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.boardWidget = hichess.BoardWidget()

    def tearDown(self):
        pass
        #for w in self.boardWidget.layout().widgets:
        #self.assertEqual(w, self.boardWidget.widgetAt(w.square))

    def testInit(self):
        pass

    def testGetCellWidgets(self):
        lyt = self.boardWidget.layout()
        lytWidgets = list([lyt.itemAt(i).widget() for i in range(lyt.count())])
        self.assertListEqual(lytWidgets, list(self.boardWidget.cellWidgets()))

    def testCellIndexOfSquare(self):
        for w in self.boardWidget.cellWidgets():
            pass

    def testSquareOf(self):
        pass

    def testCellWidgetAtSquare(self):
        pass

    def testUpdatePixmap(self):
        pass

    def testSetBoardPixmap(self):
        pass

    def testSetAccessibleSides(self):
        pass

    def testCellWidgetClick(self):
        pass

    def testPieceCellWidgetToggle(self):
        pass

    def testSetPieceAt(self):
        pass

    def testRemovePieceAt(self):
        pass

    def testAddPiece(self):
        #piece = chess.Piece(chess.PAWN, chess.WHITE)
        #square = chess.A5

        #self.boardWidget.addPiece(square, piece)

        #with self.assertRaises(ValueError):
            #self.boardWidget.addPiece(square, piece)

        # INCOMPLETE
        pass

    def testSynchronizeBoard(self):
        pass

    def testSetPieceMap(self):
        pass

    def testFen(self):
        pass

    def testIsPseudoLegalPromotion(self):
        self.boardWidget.setFen(None)

        a = chess.Move(chess.A7, chess.A8)
        b = chess.Move(chess.A2, chess.A1)
        c = chess.Move(chess.A3, chess.A4)
        d = chess.Move(chess.B7, chess.B8)
        e = chess.Move(chess.C7, chess.C8)

        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(a))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(b))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(c))

        self.boardWidget.addPiece(chess.A2, chess.Piece(chess.PAWN, chess.BLACK))
        self.boardWidget.addPiece(chess.A7, chess.Piece(chess.PAWN, chess.WHITE))
        self.boardWidget.addPiece(chess.B7, chess.Piece(chess.PAWN, chess.BLACK))
        self.boardWidget.addPiece(chess.C7, chess.Piece(chess.ROOK, chess.WHITE))

        self.assertTrue(self.boardWidget.isPseudoLegalPromotion(a))
        self.assertTrue(self.boardWidget.isPseudoLegalPromotion(b))

        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(c))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(d))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(e))

    def testMovePieceAt(self):
        pass

    def testMovePiece(self):
        pass

    def testPushPiece(self):
        pass

    def testPushForLegalMoves(self):
        """
        self.boardWidget.setFen(chess.STARTING_FEN)

        for game in os.listdir("test/games"):
            with open("test/games/{}".format(game)) as pgn:
                for move in chess.pgn.read_game(pgn).mainline_moves():
                    self.boardWidget.push(move)

                for w in self.boardWidget.layout().widgets:
                    pass
                    #self.assertEqual(w, hichess.PieceWidget(w.square, self.boardWidget.board.piece_at(w.square)))

            self.boardWidget.setFen(chess.STARTING_FEN)
        """
        pass

    def testPushForRaises(self):
        """
        boardWidget = hichess.BoardWidget()

        illegalMoves = ["a1d6", "b2b6", "c2d5", "a7a6", "e1g1"]
        for uci in illegalMoves:
            with self.assertRaises(hichess.IllegalMove):
                boardWidget.push(chess.Move.from_uci(uci))

            self.assertEqual(boardWidget.board.fen(), chess.Board.starting_fen)

            for w in boardWidget.layout().widgets:
                #self.assertEqual(w, hichess.PieceWidget(w.square, boardWidget.board.piece_at(w.square)))
                pass
        """
        pass

    def testPop(self):
        """
        self.boardWidget.setFen(chess.STARTING_FEN)
        boardCopy = self.boardWidget.board

        self.boardWidget.push(chess.Move(chess.A2, chess.A4))
        self.boardWidget.pop()

        self.assertEqual(self.boardWidget.board, boardCopy)
        """
        pass

    def testHighlightLegalMoveCellsFor(self):
        self.boardWidget.setFen("rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
        pass

    def testUnhighlightCells(self):
        pass

    def testFlip(self):
        """
        self.boardWidget.setFen(chess.STARTING_FEN)
        boardWidget2 = hichess.BoardWidget()
        self.boardWidget.flip()

        self.assertTrue(self.boardWidget.flipped)
        self.assertEqual(self.boardWidget.board, boardWidget2.board)
        for w in self.boardWidget.layout().widgets:
            self.assertEqual(w.pos(), boardWidget2.pieceWidgetAt(chess.square_mirror(w.square)).pos())

        self.boardWidget.flip()
        for w in self.boardWidget.layout().widgets:
            self.assertEqual(w.pos(), boardWidget2.pieceWidgetAt(w.square).pos())
        """
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())