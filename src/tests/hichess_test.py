import unittest

from .. import hichess


class TestPieceWidget(unittest.TestCase):
    def setUp(self):
        self.boardWidget = hichess.PieceWidget()

if __name__ == '__main__':
    unittest.main()
