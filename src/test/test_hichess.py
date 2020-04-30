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
from PySide2.QtGui import QPixmap

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
        self.boardWidget = hichess.BoardWidget(fen=chess.STARTING_FEN, flipped=False, sides=hichess.NO_SIDE)

    def tearDown(self):
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            cw = self.boardWidget.cellWidgetAtSquare(self.boardWidget.cellIndexOfSquare(i))

            self.assertEqual(cw.isAccessible, w.isAccessible)
            self.assertEqual(cw.isPlain(), w.isPlain())
            self.assertEqual(cw.isPiece(), w.isPiece())
            self.assertEqual(cw.isCheckable(), w.isCheckable())

            if w.isPiece():
                colorName, pieceName = cw.objectName().split('_')[1:]
                pieceType = chess.PIECE_TYPES[chess.PIECE_NAMES.index(pieceName) - 1]
                self.assertEqual(self.boardWidget.board.piece_at(self.boardWidget.squareOf(cw))
                                 , chess.Piece(pieceType, colorName == 'white'))
            else:
                self.assertFalse(cw.objectName())

    def testInit(self):
        pass

    def testGetCellWidgets(self):
        lyt = self.boardWidget.layout()
        lytWidgets = list([lyt.itemAt(i).widget() for i in range(lyt.count())])
        self.assertListEqual(lytWidgets, list(self.boardWidget.cellWidgets()))

    def testCellIndexOfSquare(self):
        for i in range(64):
            self.assertEqual(self.boardWidget.cellIndexOfSquare(i), chess.square_mirror(i))

        self.boardWidget.flipped = True
        for i in range(64):
            self.assertEqual(self.boardWidget.cellIndexOfSquare(i),
                             chess.square(7 - chess.square_file(i), chess.square_rank(i)))

    def testSquareOf(self):
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertEqual(self.boardWidget.squareOf(w), chess.square_mirror(i))

        self.boardWidget.flip()
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertEqual(self.boardWidget.squareOf(w),
                             chess.square(7 - chess.square_file(i), chess.square_rank(i)))

    def testCellWidgetAtSquare(self):
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertIs(w, self.boardWidget.cellWidgetAtSquare(chess.square_mirror(i)))

        self.boardWidget.flip()
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertIs(w, self.boardWidget.cellWidgetAtSquare(
                          chess.square(7 - chess.square_file(i), chess.square_rank(i))))

    def testCellWidgetClick(self):
        pass

    def testPieceCellWidgetToggle(self):
        pass

    def testCellWidgetMark(self):
        pass

    def testSetPieceAt(self):
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.WHITE))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)
        self.assertFalse(w.isAccessible)
        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertFalse(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        self.boardWidget = hichess.BoardWidget(sides=hichess.ONLY_WHITE_SIDE)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.WHITE))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)
        self.assertTrue(w.isAccessible)
        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertTrue(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        self.boardWidget = hichess.BoardWidget(fen=chess.STARTING_FEN,
                                               sides=hichess.ONLY_BLACK_SIDE)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.WHITE))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)
        self.assertFalse(w.isAccessible)
        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertFalse(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        self.boardWidget = hichess.BoardWidget(sides=hichess.ONLY_BLACK_SIDE)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.BLACK))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)
        self.assertTrue(w.isAccessible)
        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertTrue(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_black_pawn")

        self.boardWidget = hichess.BoardWidget(sides=hichess.BOTH_SIDES)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.BLACK))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)
        self.assertTrue(w.isAccessible)
        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertTrue(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_black_pawn")

    def testRemovePieceAt(self):
        self.boardWidget.removePieceAt(chess.A2)
        w = self.boardWidget.cellWidgetAtSquare(chess.A2)
        self.assertTrue(w.isPlain())
        self.assertFalse(w.isPiece())
        self.assertFalse(w.isCheckable())
        self.assertIsNone(self.boardWidget.board.piece_at(chess.A2))

        with self.assertRaises(ValueError):
            self.boardWidget.removePieceAt(chess.A2)

        for square in range(chess.A3, chess.H5):
            with self.assertRaises(ValueError):
                self.boardWidget.removePieceAt(square)

    def testAddPieceAt(self):
        square = chess.A5
        piece = chess.Piece(chess.PAWN, chess.WHITE)

        w = self.boardWidget.addPieceAt(square, piece)
        self.assertFalse(w.isAccessible)
        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertFalse(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        with self.assertRaises(ValueError):
            self.boardWidget.addPieceAt(square, piece)

    def testSynchronize(self):
        self.boardWidget = hichess.BoardWidget(fen=None)
        self.assertFalse(list(filter(lambda w: w.isPiece(), self.boardWidget.cellWidgets())))

        self.boardWidget.board.set_fen(chess.STARTING_FEN)
        self.boardWidget.synchronize()

        self.assertEqual(self.boardWidget.board.fen(), chess.Board.starting_fen)
        self.assertDictEqual(self.boardWidget.board.piece_map(), chess.Board().piece_map())

    def testSetPieceMap(self):
        self.boardWidget = hichess.BoardWidget(fen=None)
        self.assertFalse(self.boardWidget.board.piece_map())

        newPieceMap = chess.Board().piece_map()
        self.boardWidget.setPieceMap(newPieceMap)
        self.assertDictEqual(self.boardWidget.board.piece_map(), newPieceMap)

    def testFen(self):
        self.assertDictEqual(self.boardWidget.board.piece_map(), chess.Board().piece_map())

        self.boardWidget.setFen(None)
        self.assertFalse(self.boardWidget.board.piece_map())
        self.assertFalse(list(filter(lambda w: w.isPiece(), self.boardWidget.cellWidgets())))

        self.boardWidget.setFen(chess.STARTING_FEN)

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

        self.boardWidget.addPieceAt(chess.A2, chess.Piece(chess.PAWN, chess.BLACK))
        self.boardWidget.addPieceAt(chess.A7, chess.Piece(chess.PAWN, chess.WHITE))
        self.boardWidget.addPieceAt(chess.B7, chess.Piece(chess.PAWN, chess.BLACK))
        self.boardWidget.addPieceAt(chess.C7, chess.Piece(chess.ROOK, chess.WHITE))

        self.assertTrue(self.boardWidget.isPseudoLegalPromotion(a))
        self.assertTrue(self.boardWidget.isPseudoLegalPromotion(b))

        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(c))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(d))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(e))

    def testMovePieceAt(self):
        for gameName in os.listdir("test/games"):
            with open(f"test/games/{gameName}") as pgn:
                game = chess.pgn.read_game(pgn)
                self.boardWidget = hichess.BoardWidget(fen=game.board().fen(),
                                                       flipped=False, sides=hichess.NO_SIDE)
                for move in game.mainline_moves():
                    self.boardWidget.movePieceAt(move.from_square, move.to_square)
                    w = self.boardWidget.cellWidgetAtSquare(move.to_square)

                    self.assertTrue(w.isPiece())
                    colorName, pieceName = w.objectName().split('_')[1:]
                    pieceType = chess.PIECE_TYPES[chess.PIECE_NAMES.index(pieceName) - 1]
                    self.assertEqual(self.boardWidget.board.piece_at(self.boardWidget.squareOf(w)),
                                     chess.Piece(pieceType, colorName == 'white'))

    def testMovePiece(self):
        for gameName in os.listdir("test/games"):
            with open(f"test/games/{gameName}") as pgn:
                game = chess.pgn.read_game(pgn)
                self.boardWidget = hichess.BoardWidget(fen=game.board().fen(),
                                                       flipped=False, sides=hichess.NO_SIDE)
                for move in game.mainline_moves():
                    self.boardWidget.movePiece(move.to_square,
                                               self.boardWidget.cellWidgetAtSquare(move.from_square))
                    w = self.boardWidget.cellWidgetAtSquare(move.to_square)

                    self.assertTrue(w.isPiece())
                    colorName, pieceName = w.objectName().split('_')[1:]
                    pieceType = chess.PIECE_TYPES[chess.PIECE_NAMES.index(pieceName) - 1]
                    self.assertEqual(self.boardWidget.board.piece_at(self.boardWidget.squareOf(w)),
                                     chess.Piece(pieceType, colorName == 'white'))

    def testPush(self):
        for gameName in os.listdir("test/games"):
            with open(f"test/games/{gameName}") as pgn:
                game = chess.pgn.read_game(pgn)
                self.boardWidget = hichess.BoardWidget(fen=game.board().fen(),
                                                       flipped=False, sides=hichess.NO_SIDE)
                for move in game.mainline_moves():
                    self.boardWidget.push(move)
                    w = self.boardWidget.cellWidgetAtSquare(move.to_square)

                    self.assertTrue(w.isPiece())
                    colorName, pieceName = w.objectName().split('_')[1:]
                    pieceType = chess.PIECE_TYPES[chess.PIECE_NAMES.index(pieceName) - 1]
                    self.assertEqual(self.boardWidget.board.piece_at(self.boardWidget.squareOf(w)),
                                     chess.Piece(pieceType, colorName == 'white'))

    def testPushForRaises(self):
        boardWidget = hichess.BoardWidget()

        illegalMoves = ["a1d6", "b2b6", "c2d5", "a7a6", "e1g1"]
        for uci in illegalMoves:
            with self.assertRaises(hichess.IllegalMove):
                boardWidget.push(chess.Move.from_uci(uci))

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

    def testSetAccessibleSides(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())