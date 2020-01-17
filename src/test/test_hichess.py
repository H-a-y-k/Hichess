import unittest

import hichess.hichess as hichess
import chess
import chess.pgn

from PySide2.QtWidgets import QApplication
import os
import sys


class SquareWidgetTestCase(unittest.TestCase):
    def testParameterValidity(self):
        invalidSquare = 100
        with self.assertRaises(ValueError):
            hichess.SquareWidget(chess.D5)
            hichess.SquareWidget(invalidSquare)

    def testEquality(self):
        w1 = hichess.SquareWidget(chess.A1)
        w2 = hichess.SquareWidget(chess.A1)
        w3 = hichess.SquareWidget(chess.A6)
        w4 = hichess.SquareWidget(chess.A7)

        self.assertEqual(w1, w2)
        self.assertEqual(w2, w1)

        self.assertNotEqual(w1, w3)
        self.assertNotEqual(w2, w4)
        self.assertNotEqual(w3, w4)

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

    def testTransformation(self):
        w = hichess.PieceWidget(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
        w.transformInto(chess.PAWN)
        self.assertEqual(w.piece, chess.Piece(chess.PAWN, chess.WHITE))


class BoardLayoutTestCase(unittest.TestCase):
    def testAddWidget(self):
        pass

    def testDeleteWidgets(self):
        pass


class BoardWidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.boardWidget = hichess.BoardWidget(fen=None)

    def testMoveWidget(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE), parent=self.boardWidget)

        self.boardWidget.moveWidget(chess.A6, pieceWidget)
        file = chess.square_file(chess.square_mirror(chess.A6))
        rank = chess.square_rank(chess.square_mirror(chess.A6))

        self.assertEqual(pieceWidget.square, chess.A6)
        self.assertEqual(pieceWidget.pos().toTuple(), (file * pieceWidget.width(), rank * pieceWidget.height()))

    def testAddPiece(self):
        piece = chess.Piece(chess.PAWN, chess.WHITE)
        square = chess.A5

        self.boardWidget.addPiece(square, piece)

        with self.assertRaises(ValueError):
            self.boardWidget.addPiece(square, piece)

        self.assertEqual(hichess.PieceWidget(square, piece),
                         self.boardWidget.pieceWidgetAt(square))
        self.assertIn(hichess.PieceWidget(square, piece), self.boardWidget.layout().widgets)

    def testMovePieceWidget(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE))

        self.boardWidget.moveWidget(chess.A6, pieceWidget)

        self.assertEqual(pieceWidget, self.boardWidget.pieceWidgetAt(chess.A6))
        self.assertIsNone(self.boardWidget.pieceWidgetAt(chess.A5))

    def testPieceWidgetAt(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE))

        self.boardWidget.addPiece(pieceWidget.square, pieceWidget.piece)

        self.assertEqual(pieceWidget, self.boardWidget.pieceWidgetAt(chess.A5))
        self.assertIsNone(self.boardWidget.pieceWidgetAt(chess.A6))

    def testIsPseudoLegalPromotion(self):
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

    def testPop(self):
        pass

    def testPushForKingsideCastling(self):
        self.boardWidget.setFen("r1bqkbnr/1pp1pppp/p2p4/4n3/4P3/5NP1/PPPP1PBP/RNBQK2R w KQkq - 0 5")

        self.boardWidget.push(chess.Move(chess.E1, chess.G1))
        self.boardWidget.pop()

    def testPushForLegalMoves(self):
        self.boardWidget.setFen(chess.Board.starting_fen)

        for game in os.listdir("test/games"):
            with open("test/games/{}".format(game)) as pgn:
                for move in chess.pgn.read_game(pgn).mainline_moves():
                    self.boardWidget.push(move)

                for w in filter(lambda w: isinstance(w, hichess.PieceWidget), self.boardWidget.layout().widgets):
                    self.assertEqual(w.piece, self.boardWidget.board.piece_at(w.square))
            self.boardWidget = hichess.BoardWidget()

    def testPushForRaises(self):
        boardWidget = hichess.BoardWidget()

        illegalMoves = ["a1d6", "b2b6", "c2d5", "a7a6", "e1g1"]
        for uci in illegalMoves:
            with self.assertRaises(hichess.IllegalMoveError):
                boardWidget.pushPieceWidget(chess.Move.from_uci(uci).to_square,
                                            boardWidget.pieceWidgetAt(chess.Move.from_uci(uci).from_square))

                self.assertEqual(boardWidget.board.fen(), chess.Board.starting_fen)

                for w in filter(lambda w: isinstance(w, hichess.PieceWidget), boardWidget.layout().widgets):
                    self.assertEqual(w.piece, boardWidget.board.piece_at(w.square))

    def testHighlightLegalMoves(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())
