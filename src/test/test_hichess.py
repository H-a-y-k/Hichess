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
        w3 = hichess.PieceWidget(chess.A2, chess.Piece(chess.ROOK, chess.WHITE))
        w4 = hichess.PieceWidget(chess.A2, chess.Piece(chess.PAWN, chess.BLACK))
        w5 = hichess.PieceWidget(chess.A4, chess.Piece(chess.PAWN, chess.WHITE))
        w6 = hichess.PieceWidget(chess.H7, chess.Piece(chess.BISHOP, chess.BLACK))

        self.assertEqual(w1, w2)
        self.assertEqual(w2, w1)

        self.assertNotEqual(w1, w3)
        self.assertNotEqual(w3, w2)
        self.assertNotEqual(w1, w4)
        self.assertNotEqual(w1, w5)
        self.assertNotEqual(w1, w6)
        self.assertFalse(w1 != w6)

    def testTransformation(self):
        w = hichess.PieceWidget(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
        w.transformInto(chess.PAWN)
        self.assertEqual(w.piece, chess.Piece(chess.PAWN, chess.WHITE))


class BoardWidgetTestCase(unittest.TestCase):
    def testAddPiece(self):
        piece = chess.Piece(chess.PAWN, chess.WHITE)
        square = chess.A5

        boardWidget = hichess.BoardWidget()
        boardWidget.addPiece(square, piece)

        self.assertEqual(hichess.PieceWidget(square, piece),
                         boardWidget.pieceWidgetAt(square))
        self.assertIn(hichess.PieceWidget(square, piece), boardWidget.layout().widgets)

    def testPieceWidgetAt(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE))

        boardWidget = hichess.BoardWidget()
        boardWidget.addPiece(pieceWidget.square, pieceWidget.piece)

        self.assertEqual(pieceWidget, boardWidget.pieceWidgetAt(chess.A5))
        self.assertIsNone(boardWidget.pieceWidgetAt(chess.A6))

    def testMoveWidget(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE))

        boardWidget = hichess.BoardWidget()
        boardWidget.addPiece(pieceWidget.square, pieceWidget.piece)
        boardWidget.moveWidget(chess.A6, pieceWidget)

        self.assertEqual(pieceWidget, boardWidget.pieceWidgetAt(chess.A6))
        self.assertIsNone(boardWidget.pieceWidgetAt(chess.A5))

    def testIsLegalPromotion(self):
        pass

    def testPushPieceWidget(self):
        pass

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

    def testGameplay5(self):
        boardWidget = hichess.BoardWidget()
        moves = ["a1d6", "b2b6", "c2d5", "a7a6", "e1g1"]

        for uci in moves:
            with self.assertRaises(hichess.IllegalMoveError):
                boardWidget.pushPieceWidget(chess.Move.from_uci(uci).to_square, boardWidget.pieceWidgetAt(chess.Move.from_uci(uci).from_square))
                self.assertEqual(boardWidget.board.fen(), chess.Board.starting_fen)
                self._testBoardState(boardWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())
