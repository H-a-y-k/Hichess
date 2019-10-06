from PySide2.QtWidgets import QLabel 
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from enum import Enum
from random import choice
import resources

class ChessBoard(QLabel):
    class BoardSide(Enum):
        white = 0
        black = 1
        random = 2

    def __init__(self, parent = None, side = BoardSide.random):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.loadBoardImage(side)

    def loadBoardImage(self, side):
        if (side == self.BoardSide.white):
            boardPix = QPixmap(":/images/chessboard.png")
        elif (side == self.BoardSide.black):
            boardPix = QPixmap(":/images/flipped_chessboard.png")
        elif (side == self.BoardSide.random):
            randSide = choice([self.BoardSide.white, self.BoardSide.black])
            return self.loadBoardImage(randSide)

        self.setPixmap(boardPix.scaled(self.width(), self.height(),
                                       Qt.KeepAspectRatioByExpanding,
                                       Qt.SmoothTransformation))