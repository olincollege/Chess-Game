"""
Model class to represent the board and pieces.
"""

from ChessPiece import Pawn, Knight, Bishop, Queen, King, Rook


class ChessModel:
    """
    Model representation of the chess game/board

    Attributes:
        _cols: a list representing the columns of the chess board.
        _rows: a list representing the rows of the chess board.
        _board: a list of lists representing the actual chess board.
        _turn: a string representing whose turn it is in the game.
        _move_number: an int representing the move number that the game is on
        _captured_pieces: a dictionary representing the pieces that have been
        captured from both colors.
        _move_history: a list which stores all of the moves which have happened
        in the game.
    """

    _cols = range(1, 9)
    _rows = range(1, 9)

    def __init__(self):
        self._board = self._init_board()
        self._move_number = 0
        self._turn = "w"
        self._captured_pieces = {"w": [], "b": []}
        self._move_history = []

    def _init_board(self):
        """
        Function to create the chess board

        Returns:
            board: a list of lists representing the chess board with all pieces
            on the board
        """
        board = [[None] * 8 for _ in range(8)]

        for color, back_row, pawn_row in [("w", 0, 1), ("b", 7, 6)]:
            col_pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
            for col_index, piece_class in enumerate(col_pieces):
                board[back_row][col_index] = piece_class(color)
                board[pawn_row][col_index] = Pawn(color)
        return board

    def get_piece(self, col, row):
        """
        Gets the piece at a certain square.

        Args:
            col: an int representing the column of the board.
            row: an int representing the row of the board.

        Returns:
            A piece type of the piece at the specified square, or None if
            there is no piece there.
        """
        if 0 <= col <= 7 and 0 <= row <= 7:
            return self._board[row][col]
        else:
            return None

    @property
    def board(self):
        """
        Gets the whole board state.
        """
        return self._board

    @property
    def turn(self):
        """
        Gets the current turn of the game.
        """
        return self._turn

    @turn.setter
    def turn(self, color):
        """
        Sets whose turn it is in the game.

        Args:
            color: a string representing the turn to be set to.
        """
        if color not in ("w", "b"):
            raise ValueError(f"Invalid turn color: {color}")
        self._turn = color

    @property
    def move_number(self):
        """
        Gets the current move number of the game.
        """
        return self._move_number

    def remove_piece(self, row, col):
        """
        Removes a piece at the chosen square.

        Args:
            col: an int representing the column of the board.
            row: an int representing the row of the board.
        """
        self._board[row][col] = None

    def add_captured(self, color, piece):
        """
        Records a captured piece.

        Args:
            color: a string representing the color of the player which the
            piece belongs to.
            piece: a piece instance representing the piece which was captured.
        """
        self._captured_pieces[color].append(piece)
