"""
Model class to represent the board, pieces, and game rules.

IMPORTANT FOR TEAM:
- Put board state here.
- Put move legality helpers here.
- Put Stockfish integration here.
- Put Chess960 setup here.
- Keep ChessPiece.py for raw piece movement patterns only.
- Keep ChessView.py for drawing only.
- Keep ChessController.py for event handling only.
"""

import os
import random
import subprocess
from ChessPiece import Pawn, Knight, Bishop, Queen, King, Rook


class StockfishAPI:
    """
    Minimal Stockfish bridge.

    Stockfish is a free and open-source chess engine widely considered as one
    of the strongest engines for many years. To learn more about Stockfish,
    visit https://en.wikipedia.org/wiki/Stockfish_(chess).

    Put stockfish.exe at:
        stockfish/stockfish.exe

    Attributes:
        engine_path: a string representing the path to access Stockfish.
        process: Popen instance used to communicate with Stockfish.
    """

    def __init__(self, engine_path="stockfish/stockfish.exe"):
        """
        Initializes Stockfish bridge class
        """
        self.engine_path = engine_path
        self.process = None

        if os.path.exists(engine_path):
            self.process = subprocess.Popen(
                engine_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
            )
            self.send_command("uci")
            self.send_command("isready")

    def send_command(self, command):
        """
        Method to send commands to Stockfish

        Args:
            command: a string representing the command to send to Stockfish API.
        """
        if self.process is None:
            return
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def get_best_move(self, fen, depth=10):
        """
        Obtains best move from Stockfise for given position evaluated at a
        certain depth.

        Args:
            fen: a string representation of the entire board used to communicate
                with Stockfish
            depth: an int representing the depth of moves for which Stockfish
                will evaluate in order to fine the best move.

        Returns:
            A string representing the best move evaluated by Stockfist, or None
            if process is None.
        """
        if self.process is None:
            return None

        self.send_command(f"position fen {fen}")
        self.send_command(f"go depth {depth}")

        while True:
            line = self.process.stdout.readline().strip()
            if line.startswith("bestmove"):
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1]
                return None


class ChessModel:
    """
    Model representation of the chess game/board.
    """

    def __init__(self):
        """
        Initializes ChessModel instance

        Attributes:
            _board: a list of lists representing the spaces on a chess board.
            _turn: a string representing the color of whose turn it is.
            _move_number: an int tracking the move number of the game.
            _captured_pieces: a dictionary mapping each player's respective
                color to their pieces which they have lost in the game.
            _move_history: a list representing the move history on the board.
            _selected: a Piece instance when a piece is selected on the UI, or
                None if otherwise.
            _legal_moves: a list representing the legal moves of a selected
                piece on the board.
            _mode: a string representing the mode for the given game.
            _stockfish: an instance of StockfishAPI(?).
            _dragging: a boolean indicating whether or not a piece is being
                dragged.
            _drag_piece: a Piece instance representing the piece which is being
                dragged; None if a piece isn't being dragged.
            _drag_from: a tuple representing the position from which the piece
                is being dragged from; None if a piece isn't being dragged.
            _drag_mouse_pos: a tuple representing the position of the mouse as
                it is dragging a piece; None if a piece isn't being dragged.
        """
        self._board = [[None] * 8 for _ in range(8)]
        self._turn = "w"
        self._move_number = 1
        self._captured_pieces = {"w": [], "b": []}
        self._move_history = []
        self._selected = None
        self._legal_moves = []
        self._mode = None
        self._stockfish = None

        self._dragging = False
        self._drag_piece = None
        self._drag_from = None
        self._drag_mouse_pos = None

    def setup_standard(self):
        """
        Sets ChessModel instance to set up for conventional chess.
        """
        self._board = [[None] * 8 for _ in range(8)]
        self._turn = "w"
        self._move_number = 1
        self._captured_pieces = {"w": [], "b": []}
        self._move_history = []
        self.reset_selection()
        self.clear_drag()

        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_cls in enumerate(back_rank):
            self._board[0][col] = piece_cls("w")
            self._board[7][col] = piece_cls("b")

        for col in range(8):
            self._board[1][col] = Pawn("w")
            self._board[6][col] = Pawn("b")

    def setup_chess960(self):
        """
        Sets ChessModel instance to set up for the chess variant Chess960, also
        known as Fischer Random or Freestyle Chess. To learn more about Chess960,
        visit https://en.wikipedia.org/wiki/Chess960.
        """
        self._board = [[None] * 8 for _ in range(8)]
        self._turn = "w"
        self._move_number = 1
        self._captured_pieces = {"w": [], "b": []}
        self._move_history = []
        self.reset_selection()
        self.clear_drag()

        layout = self._generate_960_back_rank()

        for col, piece_cls in enumerate(layout):
            self._board[0][col] = piece_cls("w")
            self._board[7][col] = piece_cls("b")

        for col in range(8):
            self._board[1][col] = Pawn("w")
            self._board[6][col] = Pawn("b")

    def _generate_960_back_rank(self):
        """
        Generates the back row of pieces for Chess960. Chess 960 randomizes the
        back row of pieces according to the following rules:
        - The bishops must be on opposite colors.
        - The king must be in between the two rooks to allow for castling.

        Returns:
            A list containing the randomized order of pieces for the back row.
        """
        layout = [None] * 8

        dark_squares = [0, 2, 4, 6]
        light_squares = [1, 3, 5, 7]

        b1 = random.choice(dark_squares)
        b2 = random.choice(light_squares)
        layout[b1] = Bishop
        layout[b2] = Bishop

        remaining = [i for i in range(8) if layout[i] is None]
        q = random.choice(remaining)
        layout[q] = Queen

        remaining = [i for i in range(8) if layout[i] is None]
        n1, n2 = random.sample(remaining, 2)
        layout[n1] = Knight
        layout[n2] = Knight

        remaining = sorted([i for i in range(8) if layout[i] is None])
        layout[remaining[0]] = Rook
        layout[remaining[1]] = King
        layout[remaining[2]] = Rook

        return layout

    def start_game(self, mode):
        """
        Starts the game on the board by setting the _mode attribute and putting
        pieces onto the board.

        Args:
            mode: a string representing the game mode to be played.
        """
        self._mode = mode
        if mode == "chess960":
            self.setup_chess960()
        else:
            self.setup_standard()

    def maybe_make_stockfish(self):
        """
        Function to maybe use Stockfish to have a one player game.
        """
        api = StockfishAPI()
        return api if api.process is not None else None

    def set_stockfish(self, stockfish_api):
        """
        Setter to _stockfish to add Stockfish API to model

        Args:
            stockfish_api: a StockFishAPI instance used to communicate to
                Stockfish
        """
        self._stockfish = stockfish_api

    def apply_stockfish_move(self):
        """
        Uses Stockfish to play a move without user input.
        """
        if self._mode != "one_player":
            return

        if self._stockfish is None:
            return

        fen = self.board_to_fen()
        bestmove = self._stockfish.get_best_move(fen)

        if bestmove is None or len(bestmove) < 4:
            return

        start = bestmove[:2]
        end = bestmove[2:4]

        start_col, start_row = self.alg_to_coord(start)
        end_col, end_row = self.alg_to_coord(end)

        piece = self.get_piece(start_col, start_row)
        if piece is None:
            return

        legal = piece.valid_moves(start_col, start_row, self)
        if (end_col, end_row) in legal:
            self.move_piece(start_col, start_row, end_col, end_row)
            self.reset_selection()

    @property
    def mode(self):
        """
        Getter for game mode.

        Returns:
            a string representing the current game mode (chess960 or otherwise).
        """
        return self._mode

    @property
    def board(self):
        """
        Getter for physical board state

        Returns:
            a list of lists representing the current state of the chess board.
        """
        return self._board

    @property
    def turn(self):
        """
        Getter for whose turn it is

        Returns:
            a string represnting whose turn it is.
        """
        return self._turn

    @property
    def selected(self):
        """
        Getter for currently selected piece.

        Returns:
            a Piece instance of the currently selected piece.
        """
        return self._selected

    @selected.setter
    def selected(self, value):
        """
        Sets _selected to given piece.

        Args:
            value: a Piece instance.
        """
        self._selected = value

    @property
    def legal_moves(self):
        """
        Getter for legal moves at current state

        Returns:
            a list representing all legal moves.
        """
        return self._legal_moves

    @legal_moves.setter
    def legal_moves(self, value):
        """
        Sets _legal_moves to given moves.

        Args:
            value: a list representing the legal moves at the current state.
        """
        self._legal_moves = value

    @property
    def dragging(self):
        """
        Getter for dragging status.

        Returns:
            a boolean representing whether or not a piece is currently being
            dragged.
        """
        return self._dragging

    @property
    def drag_piece(self):
        """
        Getter for piece being dragged

        Returns:
            a Piece instance representing the one currently being dragged.
        """
        return self._drag_piece

    @property
    def drag_from(self):
        """
        Getter for original position of a dragged piece.

        Returns:
            A tuple representing the position from which a piece was dragged.
        """
        return self._drag_from

    @property
    def drag_mouse_pos(self):
        """
        Getter for the current mouse position.

        Returns:
            A tuple representing the current mouse position.
        """
        return self._drag_mouse_pos

    @property
    def move_history(self):
        """
        Getter for the move history.

        Returns:
            A list representing the move history of the board.
        """
        return self._move_history

    def begin_drag(self, col, row, mouse_pos):
        """
        Initiates instance to be in a dragging state.

        Args:
            col: an int representing the column of the position of the piece to
                be dragged.
            row: an int representing the row of the position of the piece to be
                dragged.
            mouse_pos: a tuple representing the position of the mouse.

        Returns:
            A boolean representing whether or not the dragging motion is
            happening or not.
        """
        piece = self.get_piece(col, row)
        if piece is None:
            return False
        self._dragging = True
        self._drag_piece = piece
        self._drag_from = (col, row)
        self._drag_mouse_pos = mouse_pos
        return True

    def update_drag(self, mouse_pos):
        """
        Updates mouse position while dragging.

        Args:
            mouse_pos: a tuple representing the position of the mouse.
        """
        self._drag_mouse_pos = mouse_pos

    def clear_drag(self):
        """
        Sets board state attributes back to not dragging.
        """
        self._dragging = False
        self._drag_piece = None
        self._drag_from = None
        self._drag_mouse_pos = None

    def get_piece(self, col, row):
        """
        Gets the piece at a certain position.

        Args:
            col: an int representing a column of the chess board
            row: an int representing a row of the chess board

        Returns:
            A Piece instance at that position, or None if there is no piece
            there.
        """
        if 0 <= col <= 7 and 0 <= row <= 7:
            return self._board[row][col]
        return None

    def set_piece(self, col, row, piece):
        """
        Sets the piece at a given position on the board.

        Args:
            col: an int representing a column of the chess board
            row: an int representing a row of the chess board
            piece: a Piece instance representing the piece to be set.
        """
        if 0 <= col <= 7 and 0 <= row <= 7:
            self._board[row][col] = piece

    def reset_selection(self):
        """
        Unselects a piece on the board.
        """
        self._selected = None
        self._legal_moves = []

    def is_legal_move(self, start_col, start_row, end_col, end_row):
        """
        Checks to see if a move is valid or not.
        INCOMPLETE
        """
        piece = self.get_piece(start_col, start_row)
        if piece is None:
            return False

        if piece.color != self._turn:
            return False

        moves = piece.valid_moves(start_col, start_row, self)
        return (end_col, end_row) in moves

    def coord_to_alg(self, col, row):
        """
        Converts internal chess board array to algebraic chess notation.

        Args:
            col: an int representing a column of the chess board.
            row: an int representing a row of the chess board.

        Returns:
            A string representing a board position in chess notation(ie a1, f8)
        """
        return chr(ord("a") + col) + str(row + 1)

    def alg_to_coord(self, square):
        """
        Converts algebraic chess notation to internal chess array.

        Args:
            square: A string representing a board position in chess notation.

        Returns:
            col: an int representing a column of the chess board.
            row: an int representing a row of the chess board.
        """
        col = ord(square[0]) - ord("a")
        row = int(square[1]) - 1
        return col, row

    def _piece_letter(self, piece):
        """
        Returns piece abbreviation assigned to pieces in algebraic notation.

        Args:
            piece: a Piece instance

        Returns:
            A string representing the piece's abbreviation.
        """
        mapping = {
            Pawn: "",
            Knight: "N",
            Bishop: "B",
            Rook: "R",
            Queen: "Q",
            King: "K",
        }
        return mapping.get(type(piece), "")

    def _format_move_text(
        self, piece, start_col, start_row, end_col, end_row, captured
    ):
        """
        Formats move into algebraic chess notation.
        NOTE: this doesn't currently include castling.

        Args:
            piece: a Piece instance representing the piece being moved.
            start_col: an int representing a column of the starting position of
                the piece.
            start_row: an int representing a row of the starting position of
                the piece.
            end_col: an int representing a column of the ending position of the
                piece.
            end_row: an int representing a row of the ending position of the
                piece.
            captured: a boolean representing whether or not a piece was
                captured during the move.

        Returns:
            A string with the algebraic notation of the described move.
        """
        start_sq = self.coord_to_alg(start_col, start_row)
        end_sq = self.coord_to_alg(end_col, end_row)
        prefix = self._piece_letter(piece)

        if isinstance(piece, Pawn):
            if captured:
                return f"{start_sq[0]}x{end_sq}"
            return end_sq

        if captured:
            return f"{prefix}x{end_sq}"
        return f"{prefix}{end_sq}"

    def move_piece(self, start_col, start_row, end_col, end_row):
        """
        Moves a piece on the board.

        Args:
            start_col: an int representing a column of the starting position of
                the piece.
            start_row: an int representing a row of the starting position of
                the piece.
            end_col: an int representing a column of the ending position of the
                piece.
            end_row: an int representing a row of the ending position of the
                piece.

        Returns:
            A boolean representing whether or not a piece was successfully
            moved.
        """
        piece = self.get_piece(start_col, start_row)
        if piece is None:
            return False

        target = self.get_piece(end_col, end_row)
        captured = target is not None

        if target is not None:
            self._captured_pieces[target.color].append(target)

        move_text = self._format_move_text(
            piece, start_col, start_row, end_col, end_row, captured
        )

        self.set_piece(end_col, end_row, piece)
        self.set_piece(start_col, start_row, None)
        piece.has_moved = True

        self._move_history.append(move_text)
        self._turn = "b" if self._turn == "w" else "w"
        self._move_number += 1
        return True

    def board_to_fen(self):
        """
        Converts the board state into a FEN string for input into Stockfish. To
        learn more about FEN strings, visit
        https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation.

        Returns:
            A string in the format of a FEN string.
        """
        fen_rows = []

        for row in range(7, -1, -1):
            empty = 0
            fen_row = ""

            for col in range(8):
                piece = self._board[row][col]
                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen_row += str(empty)
                        empty = 0
                    fen_row += piece.fen_symbol()

            if empty > 0:
                fen_row += str(empty)

            fen_rows.append(fen_row)

        side = "w" if self._turn == "w" else "b"
        return "/".join(fen_rows) + f" {side} - - 0 1"
