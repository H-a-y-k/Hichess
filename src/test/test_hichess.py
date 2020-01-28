import unittest

import hichess.hichess as hichess
import chess
import chess.pgn

from PySide2.QtWidgets import QApplication
import logging
import os
import sys

class SquareWidgetTestCase(unittest.TestCase):
    def testProperty(self):
        invalidSquare = 100
        w = hichess.SquareWidget(chess.A1)
        w.square = chess.A2

        with self.assertRaises(ValueError):
            w.square = invalidSquare

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
        boardWidget = hichess.BoardWidget()
        w = boardWidget.layout().widgets[0]
        layout = hichess.BoardLayout(None)

        with self.assertLogs(level=logging.WARN):
            layout.addWidget(w)
            self.assertNotIn(w, layout.widgets)

        boardWidget.layout().removeWidget(w)

        boardWidget.layout().addWidget(w)

        self.assertIn(w, boardWidget.layout().widgets)
        self.assertIs(w.parent(), boardWidget)

    def testRemoveWidget(self):
        boardWidget = hichess.BoardWidget()
        w = boardWidget.layout().widgets[0]
        boardWidget.layout().removeWidget(w)

        self.assertNotIn(w, boardWidget.layout().widgets)
        self.assertIsNone(w.parent())

    def testDeleteWidgets(self):
        boardWidget = hichess.BoardWidget()
        self.assertEqual(len(boardWidget.layout().widgets), 32)
        boardWidget.layout().deleteWidgets()
        self.assertFalse(boardWidget.layout().widgets)

        boardWidget = hichess.BoardWidget()
        boardWidget.layout().deleteWidgets(lambda w: isinstance(w, hichess.PieceWidget) and w.piece.piece_type == chess.PAWN)
        self.assertEqual(len(boardWidget.layout().widgets), 16)

class BoardWidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.boardWidget = hichess.BoardWidget(fen=None)

    def tearDown(self):
        for w in self.boardWidget.layout().widgets:
            self.assertEqual(w, self.boardWidget.pieceWidgetAt(w.square))

    def testPieceWidgetAt(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE))

        self.boardWidget.addPiece(pieceWidget.square, pieceWidget.piece)

        self.assertEqual(pieceWidget, self.boardWidget.pieceWidgetAt(chess.A5))
        self.assertIsNone(self.boardWidget.pieceWidgetAt(chess.A6))
        self.assertEqual(self.boardWidget.pieceWidgetAt(chess.A5).square, chess.A5)

    def testMoveWidget(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE), parent=self.boardWidget)

        self.boardWidget.moveWidget(chess.A6, pieceWidget)
        file = chess.square_file(chess.square_mirror(chess.A6))
        rank = chess.square_rank(chess.square_mirror(chess.A6))

        self.assertEqual(pieceWidget.square, chess.A6)
        self.assertEqual(pieceWidget.pos().toTuple(), (file * pieceWidget.width(), rank * pieceWidget.height()))

    def testMovePieceWidget(self):
        pieceWidget = hichess.PieceWidget(chess.A5, chess.Piece(chess.PAWN, chess.WHITE))

        self.boardWidget.layout().addWidget(pieceWidget)
        self.boardWidget.movePieceWidget(chess.A6, pieceWidget)

        self.assertEqual(pieceWidget, self.boardWidget.pieceWidgetAt(chess.A6))
        self.assertIsNone(self.boardWidget.pieceWidgetAt(chess.A5))

    def testAddPiece(self):
        piece = chess.Piece(chess.PAWN, chess.WHITE)
        square = chess.A5

        self.boardWidget.addPiece(square, piece)

        with self.assertRaises(ValueError):
            self.boardWidget.addPiece(square, piece)

        self.assertEqual(hichess.PieceWidget(square, piece), self.boardWidget.pieceWidgetAt(square))
        self.assertIn(hichess.PieceWidget(square, piece), self.boardWidget.layout().widgets)

    def testSetPieceMap(self):
        otherBoardWidget = hichess.BoardWidget()
        self.boardWidget.setPieceMap(otherBoardWidget.board.piece_map())

        self.assertEqual(otherBoardWidget.board.piece_map(), self.boardWidget.board.piece_map())
        self.assertEqual(otherBoardWidget.board.board_fen(), self.boardWidget.board.board_fen())

    def testSetFen(self):
        fen = "r1bqkb1r/ppppppp1/2n2n1p/8/8/5NP1/PPPPPPBP/RNBQK2R w KQkq - 0 4"
        otherBoardWidget = hichess.BoardWidget(fen=fen)
        self.boardWidget.setFen(fen)

        self.assertDictEqual(otherBoardWidget.board.piece_map(), self.boardWidget.board.piece_map())
        self.assertEqual(otherBoardWidget.board.fen(), self.boardWidget.board.fen())

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

    def testKingsideCastling(self):
        otherBoard = chess.Board(fen="r1bqkb1r/ppppppp1/2n2n1p/8/8/5NP1/PPPPPPBP/RNBQK2R w KQkq - 0 4")
        self.boardWidget.setFen(otherBoard.fen())
        color = chess.WHITE
        move = chess.Move(chess.E1, chess.G1)

        self.assertTrue(otherBoard.has_kingside_castling_rights(color))
        self.assertTrue(self.boardWidget.board.has_kingside_castling_rights(color))

        otherBoard.push(move)
        self.boardWidget.push(move)

        self.assertFalse(otherBoard.has_kingside_castling_rights(color))
        self.assertFalse(self.boardWidget.board.has_kingside_castling_rights(color))
        self.assertEqual(otherBoard, self.boardWidget.board)

        for w in self.boardWidget.layout().widgets:
            self.assertEqual(w, hichess.PieceWidget(w.square, self.boardWidget.board.piece_at(w.square)))

        otherBoard.pop()
        self.boardWidget.pop()

        color = chess.BLACK
        move = chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square))
        otherBoard = otherBoard.mirror()
        self.boardWidget.setFen(otherBoard.fen())

        self.assertTrue(otherBoard.has_kingside_castling_rights(color))
        self.assertTrue(self.boardWidget.board.has_kingside_castling_rights(color))

        otherBoard.push(move)
        self.boardWidget.push(move)

        self.assertFalse(otherBoard.has_kingside_castling_rights(color))
        self.assertFalse(self.boardWidget.board.has_kingside_castling_rights(color))
        self.assertEqual(otherBoard, self.boardWidget.board)

    def testQueensideCastling(self):
        otherBoard = chess.Board(fen="rn1qkbnr/pp2pppp/2p5/3p1b2/3P4/2N1B3/PPPQPPPP/R3KBNR w KQkq - 2 5")
        self.boardWidget.setFen(otherBoard.fen())
        color = chess.WHITE
        move = chess.Move(chess.E1, chess.C1)

        self.assertTrue(otherBoard.has_queenside_castling_rights(color))
        self.assertTrue(self.boardWidget.board.has_queenside_castling_rights(color))

        otherBoard.push(move)
        self.boardWidget.push(move)

        self.assertFalse(otherBoard.has_queenside_castling_rights(color))
        self.assertFalse(self.boardWidget.board.has_queenside_castling_rights(color))
        self.assertEqual(otherBoard, self.boardWidget.board)

        for w in self.boardWidget.layout().widgets:
            self.assertEqual(w, hichess.PieceWidget(w.square, self.boardWidget.board.piece_at(w.square)))

        otherBoard.pop()
        self.boardWidget.pop()

        color = chess.BLACK
        move = chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square))
        otherBoard = otherBoard.mirror()
        self.boardWidget.setFen(otherBoard.fen())

        self.assertTrue(otherBoard.has_queenside_castling_rights(color))
        self.assertTrue(self.boardWidget.board.has_queenside_castling_rights(color))

        otherBoard.push(move)
        self.boardWidget.push(move)

        self.assertFalse(otherBoard.has_queenside_castling_rights(color))
        self.assertFalse(self.boardWidget.board.has_queenside_castling_rights(color))
        self.assertEqual(otherBoard, self.boardWidget.board)

    def testEnPassant(self):
        otherBoard = chess.Board(fen="rnbqkbnr/ppp1ppp1/8/3pP2p/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3")
        self.boardWidget.setFen(otherBoard.fen())
        move = chess.Move(chess.E5, chess.D6)

        self.assertTrue(otherBoard.is_en_passant(move))
        self.assertTrue(self.boardWidget.board.is_en_passant(move))

        otherBoard.push(move)
        self.boardWidget.push(move)

        self.assertFalse(otherBoard.is_en_passant(move))
        self.assertFalse(self.boardWidget.board.is_en_passant(move))
        self.assertEqual(otherBoard, self.boardWidget.board)

        for w in self.boardWidget.layout().widgets:
            self.assertEqual(w, hichess.PieceWidget(w.square, self.boardWidget.board.piece_at(w.square)))

        otherBoard.pop()
        self.boardWidget.pop()

        otherBoard = otherBoard.mirror()
        self.boardWidget.setFen(otherBoard.fen())
        move = chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square))

        self.assertTrue(otherBoard.is_en_passant(move))
        self.assertTrue(self.boardWidget.board.is_en_passant(move))

        otherBoard.push(move)
        self.boardWidget.push(move)

        self.assertFalse(otherBoard.is_en_passant(move))
        self.assertFalse(self.boardWidget.board.is_en_passant(move))
        self.assertEqual(otherBoard, self.boardWidget.board)

    def testPushForLegalMoves(self):
        self.boardWidget.setFen(chess.Board.starting_fen)

        for game in os.listdir("test/games"):
            with open("test/games/{}".format(game)) as pgn:
                for move in chess.pgn.read_game(pgn).mainline_moves():
                    self.boardWidget.push(move)

                for w in self.boardWidget.layout().widgets:
                    self.assertEqual(w, hichess.PieceWidget(w.square, self.boardWidget.board.piece_at(w.square)))

            self.boardWidget = hichess.BoardWidget(fen=None)

    def testPushForRaises(self):
        boardWidget = hichess.BoardWidget()

        illegalMoves = ["a1d6", "b2b6", "c2d5", "a7a6", "e1g1"]
        for uci in illegalMoves:
            with self.assertRaises(hichess.IllegalMoveError):
                boardWidget.pushPieceWidget(chess.Move.from_uci(uci).to_square,
                                            boardWidget.pieceWidgetAt(chess.Move.from_uci(uci).from_square))

            self.assertEqual(boardWidget.board.fen(), chess.Board.starting_fen)

            for w in boardWidget.layout().widgets:
                self.assertEqual(w, hichess.PieceWidget(w.square, boardWidget.board.piece_at(w.square)))

    def testPop(self):
        self.boardWidget.setFen(chess.STARTING_FEN)
        boardCopy = self.boardWidget.board

        self.boardWidget.push(chess.Move(chess.A2, chess.A4))
        self.boardWidget.pop()

        self.assertEqual(self.boardWidget.board, boardCopy)

    def testHighlightLegalMoves(self):
        self.boardWidget.highlightLegalMovesFor(self.boardWidget.pieceWidgetAt(chess.A1))

    def testFlip(self):
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

    def testSetLayout(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())
