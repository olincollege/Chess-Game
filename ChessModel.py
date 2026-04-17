"""
Model class to represent the board and pieces.
"""

from ChessPiece import Pawn, Knight, Bishop, Queen, King, Rook


class ChessModel:
    """
    Model representation of the chess game/board

    Attributes:
        cols: list representing the columns of the chess board
        rows: list representing the rows of the chess board
    """

    cols = range(1, 9)
    rows = range(1, 9)

    def __init__(self):
        self.board = self._init_board
        self.move_number = 0
        self.turn = "w"
        self.captured_pieces = {"w": [], "b": []}
        self.move_history = []

    def _init_board(self):
        board = [[None] * 8 for _ in range(8)]

        for color, back_row, pawn_row in [("w", 0, 1), ("b", 7, 6)]:
            col_pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
            for col_index, piece_class in enumerate(col_pieces):
                board[back_row][col_index] = piece_class(color, (col_index, back_row))
                board[pawn_row][col_index] = Pawn(color, (col_index, pawn_row))
        return board
