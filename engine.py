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

    '''
    Takes a move and executes it
    Note: Will not work for castling, pawn promotion, and en-passant 
    '''

    def make_move(self, move):
        # Clear the piece from the starting square
        self.board[move.start_row][move.start_column] = "--"

        # Place the piece at the destination
        self.board[move.end_row][move.end_column] = move.piece_moved

        # Will be used later
        self.moveLog.append(move)

        # Switch terms / swap players
        self.white_to_move = not self.white_to_move

    '''
    Undo a list move
    '''

    def undo_move(self):
        # Make sure that there is a move to indo
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved

            # Put a captured piece on the board as well
            self.board[move.end_row][move.end_column] = move.piece_captured

            # Switch terms / swap players
            self.white_to_move = not self.white_to_move

    '''
    All moves considering checks
    '''

    def get_valid_moves(self):

        # Note: For now we do no care about checks, will come back later and fix this
        return self.get_all_possible_moves()

    '''
    All moves without considering checks
    '''

    def get_all_possible_moves(self):
        # TEST:
        # moves = []
        moves = [Move((6, 4), (4, 4), self.board)]

        # Go through board by row and by column
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                # First character is either BLACK, WHITE or empty
                # turn aka color
                turn = self.board[row][column][0]
                if (turn == "w" and self.white_to_move) and (turn == "b" and not self.white_to_move):
                    # What is the actual piece on the board?
                    # piece aka type
                    piece = self.board[row][column][1]
                    if piece == "p":
                        self.get_pawn_moves(row, column, moves)
                    elif piece == "R":
                        self.get_rook_moves(row, column, moves)

        return moves

    '''
    Get all pawn moves located at row, col and add moves to the list
    '''

    def get_pawn_moves(row, column, moves):
        pass

    '''
    Get all rook moves located at row, col and add moves to the list
    '''

    def get_rook_moves(row, column, moves):
        pass


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

        # Note: Generate unique ID for each move, like a simple hash function
        self.moveID = self.start_row * 1000 + self.start_column * \
            100 + self.end_row + self.end_column
        print(self.moveID)

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        # Can add real Chess notation here
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.cols_to_files[column] + self.rows_to_ranks[row]
