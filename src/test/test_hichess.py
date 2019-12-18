import unittest
import hichess.hichess as hichess
from PySide2.QtWidgets import QApplication, QWidget
import sys
import chess


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
        w.transformInto(chess.Piece(chess.PAWN, chess.WHITE))
        self.assertEqual(w.piece, chess.Piece(chess.PAWN, chess.WHITE))


class BoardLayoutTestCase(unittest.TestCase):
    def testDeleteWidgets(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())