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

        self.move_functions = {
            "p": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves
        }

        self.white_to_move = True
        self.move_log = []

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
        self.move_log.append(move)

        # Switch terms / swap players
        self.white_to_move = not self.white_to_move

    '''
    Undo a list move
    '''

    def undo_move(self):
        # Make sure that there is a move to indo
        if len(self.move_log) != 0:
            move = self.move_log.pop()
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
        moves = []
        # moves = [self.moves, self.board]

        # Go through board by row and by column
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                # First character is either BLACK, WHITE or empty
                # turn aka color
                turn = self.board[row][column][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    # What is the actual piece on the board?
                    piece = self.board[row][column][1]
                    self.move_functions[piece](row, column, moves)

        return moves

    '''
    Get all pawn moves located at row, col and add moves to the list
    '''

    def get_pawn_moves(self, row, column, moves):

        enemyColor = "b" if self.white_to_move else "w"

        # Note: White pawns to move
        if self.white_to_move:
            # If square in front of pawn is empty (up the board)
            if self.board[row - 1][column] == "--":
                moves.append(
                    Move((row, column), (row - 1, column), self.board)
                )

                # If we can do two-square pawn advance (in the beginning)
                if row == 6 and self.board[row - 2][column] == "--":
                    moves.append(
                        Move((row, column), (row - 2, column), self.board)
                    )

            # Captures to the left
            if column - 1 >= 0:
                if self.board[row - 1][column - 1][0] == enemyColor:
                    moves.append(
                        Move((row, column), (row - 1, column - 1), self.board)
                    )

            # Captures to the right
            if column + 1 <= 7:
                if self.board[row - 1][column + 1][0] == enemyColor:
                    print("here")
                    moves.append(
                        Move((row, column), (row - 1, column + 1), self.board)
                    )

        # Note: Black pawns to move
        else:
            # If square in front of pawn is empty (up the board)
            if self.board[row + 1][column] == "--":
                moves.append(
                    Move((row, column), (row + 1, column), self.board)
                )

                # If we can do two-square pawn advance (in the beginning)
                if row == 1 and self.board[row + 2][column] == "--":
                    moves.append(
                        Move((row, column), (row + 2, column), self.board)
                    )

            # Captures to the left
            if column - 1 >= 0:
                if self.board[row + 1][column - 1][0] == enemyColor:
                    moves.append(
                        Move((row, column), (row + 1, column - 1), self.board)
                    )

            # Captures to the right
            if column + 1 <= 7:
                if self.board[row + 1][column + 1][0] == enemyColor:
                    moves.append(
                        Move((row, column), (row + 1, column + 1), self.board)
                    )

        # TODO: Add pawn promotions later

    '''
    Get all rook moves located at row, col and add moves to the list
    '''

    def get_rook_moves(self, row, column, moves):
        # Variable 1: How we are changing the row
        # Variable 2: How we are changing the column
        # Directions:  Up       Left     Down    Right
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.white_to_move else "w"

        for d in directions:
            for i in range(1, 8):
                # Generate potential ranks and file move options
                endRow = row + d[0] * i
                endCol = column + d[1] * i

                # Make sure that that end square of endRow,endCol is on the board
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]

                    if endPiece == "--":
                        moves.append(
                            Move((row, column), (endRow, endCol), self.board)
                        )
                    elif endPiece[0] == enemyColor:
                        # We can move to that, but we cannot jump the enemy piece
                        moves.append(
                            Move((row, column), (endRow, endCol), self.board)
                        )
                        # Note: Check other direction
                        break
                    else:
                        # Found a friendly piece, nothing to caputre
                        # Note: Check other direction
                        break
                # Note: Off board condition
                else:
                    # Note: Check other direction
                    break

    """
    Get all the knight moves for the knight located at row, col and add moves to the list
    """

    def get_knight_moves(self, r, c, moves):
        # up/left up/right right/up right/down down/left down/right left/up left/down
        directions = ((-2, -1), (-2, 1), (-1, 2), (1, 2),
                      (2, -1), (2, 1), (-1, -2), (1, -2))
        allyColor = "w" if self.white_to_move else "b"

        for move in directions:
            endRow = r + move[0]
            endCol = c + move[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                # Note: Knight can hop over pieces, so I only worry about landing square
                if endPiece[0] != allyColor:  # either enemy piece or empty square
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get all the bishop moves for the bishop located at row, col and add moves to the list
    """

    def get_bishop_moves(self, r, c, moves):
        # diagonals: up/left     up/right down/right down/left
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemyColor = "b" if self.white_to_move else "w"

        for direction in directions:
            for i in range(1, 8):
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i

                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # check if the move is on board
                    endPiece = self.board[endRow][endCol]

                    if endPiece == "--":  # empty space is valid
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # capture enemy piece
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    # Queen moves just like a combination of rook and bishop
    def get_queen_moves(self, row, column, moves):
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)

    """
    Get all the king moves for the king located at row, col and add moves to the list
    """

    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, 1),
                      (1, 1), (1, 0), (1, -1), (0, -1))
        allyColor = "w" if self.white_to_move else "b"

        for move in king_moves:
            endRow = r + move[0]
            endCol = c + move[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


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
        self.moveID = (self.start_row, self.start_column,
                       self.end_row, self.end_column)
        print("moveID: ", self.moveID)

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        return isinstance(other, Move) and self.moveID == other.moveID

    def get_chess_notation(self):
        # Can add real Chess notation here
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.cols_to_files[column] + self.rows_to_ranks[row]
