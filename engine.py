# Engine File
# - Store information about current state
# - Determine the valid moves at the current state
# - Keep the move log

class GameState:
    def __init__(self):
        # 8x8 2D List
        # Each element has two characters: color, and type of the piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.white_to_move = True
        self.moveLog = []

    def make_move(self, move):
        # Clear the piece from the starting square
        self.board[move.start_row][move.start_column] = "--"

        # Place the piece at the destination
        self.board[move.end_row][move.end_column] = move.piece_moved

        # Will be used later
        self.moveLog.append(move)

        # Switch terms / swap players 
        self.white_to_move = not self.white_to_move


class Move():

    # There is common Chess notation where:  
    # - Our rows are called ranks
    # - Our columns are called files

    ranks_to_rows = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }

    files_to_cols = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
    }

    # Mapping and flipping
    rows_to_ranks = {
        value: key for key, value in ranks_to_rows.items()
    }

    # Mapping and flipping
    cols_to_files = {
        value: key for key, value in files_to_cols.items()
    }

    def __init__(self, start_square, end_square, board):

        # Decoupling the tuples so we could visualise a move a little bit better
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]

        # What piece was moved, and what was captured?
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]

    def get_chess_notation(self):
        # Can add real Chess notation here
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.cols_to_files[column] + self.rows_to_ranks[row]