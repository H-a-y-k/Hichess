import unittest

import hichess.hichess as hichess
import chess
import chess.pgn

from PySide2.QtWidgets import QApplication
import sys


class SquareWidgetTestCase(unittest.TestCase):
    def testParameterValidity(self):
        invalidSquare = 100
        with self.assertRaises(ValueError):
            hichess.SquareWidget(chess.D5)
            hichess.SquareWidget(invalidSquare)

    def testPropertyAssignment(self):
        invalidSquare = 100
        w = hichess.SquareWidget(chess.A1)
        with self.assertRaises(ValueError):
            w.square = chess.A2
            w.square = invalidSquare


class PieceWidgetTestCase(unittest.TestCase):
    def testEquality(self):
        w1 = hichess.PieceWidget(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
        w2 = hichess.PieceWidget(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
        self.assertEqual(w1, w2)

    def testTransformation(self):
        w = hichess.PieceWidget(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
        w.transformInto(chess.PAWN)
        self.assertEqual(w.piece, chess.Piece(chess.PAWN, chess.WHITE))


class BoardWidgetTestCase(unittest.TestCase):
    def testPieceWidgetAt(self):
        square = chess.A5
        pieceWidget = hichess.PieceWidget(square, chess.Piece(chess.PAWN, chess.WHITE))
        boardWidget = hichess.BoardWidget()
        boardWidget.loadPieceWidget(pieceWidget)
        self.assertTrue(pieceWidget, boardWidget.pieceWidgetAt(square))

    def _playGame(self, game: chess.pgn.Game, boardWidget):
        for move in game.mainline_moves():
            boardWidget.pushPieceWidget(move.to_square, boardWidget.pieceWidgetAt(move.from_square))

    def _testBoardState(self, boardWidget):
        for w in filter(lambda w: isinstance(w, hichess.PieceWidget), boardWidget.layout().widgets):
            self.assertTrue(w.piece, boardWidget.board.piece_at(w.square))

    def testGameplay1(self):
        boardWidget = hichess.BoardWidget()
        with open(r"test\games\long_game1.pgn", "r", encoding="utf-8-sig") as pgn:
            self._playGame(chess.pgn.read_game(pgn), boardWidget)
            self._testBoardState(boardWidget)

    def testGameplay2(self):
        boardWidget = hichess.BoardWidget()
        with open(r"test\games\long_game2.pgn", "r", encoding="utf-8-sig") as pgn:
            self._playGame(chess.pgn.read_game(pgn), boardWidget)
            self._testBoardState(boardWidget)

    def testGameplay3(self):
        boardWidget = hichess.BoardWidget()
        with open(r"test\games\long_game3.pgn", "r", encoding="utf-8-sig") as pgn:
            self._playGame(chess.pgn.read_game(pgn), boardWidget)
            self._testBoardState(boardWidget)

    def testGameplay4(self):
        boardWidget = hichess.BoardWidget()
        with open(r"test\games\long_game4.pgn", "r", encoding="utf-8-sig") as pgn:
            self._playGame(chess.pgn.read_game(pgn), boardWidget)
            self._testBoardState(boardWidget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())
