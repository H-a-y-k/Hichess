import unittest
import hichess.hichess as hichess
from PySide2.QtWidgets import QApplication, QWidget
import sys
import chess

class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)

    def tearDown(self):
        sys.exit(self.app.exec_())

class SquareWidgetTestCase(WidgetTestCase):
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


class PieceWidgetTestCase(WidgetTestCase):
    def testEquality(self):
        w1 = hichess.PieceWidget(chess.PAWN, chess.A2)
        w2 = hichess.PieceWidget(chess.PAWN, chess.A2)
        self.assertEqual(w1, w2)

    def testTransformation(self):
        w = hichess.PieceWidget(chess.KING, chess.A2)
        w.transformInto(chess.PAWN)
        self.assertEqual(w.piece, chess.PAWN)


class BoardLayoutTestCase(WidgetTestCase):
    def testClearTemporaryWidgets(self):
        layout = hichess.BoardLayout(parent=QWidget())
        layout.addTemporaryWidget(QWidget())
        layout.addTemporaryWidget(QWidget())
if __name__ == '__main__':
    unittest.main()
