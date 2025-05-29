"""
This class is responsible for storing all information about the current state of a chess game.
It validates valid moves and keeps a move log.
"""


class GameState:
    def __init__(self):
        """
        Board is a 8x8 2d list, each element in list has 2 characters.
        The first character represents the color of the piece: 'b' or 'w'.
        The second character represents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'p'.
        "--" represents an empty space with no piece.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.whiteToMove = True
        self.checkmate = False
        self.stalemate = False
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.moveLog = []

    def makeMove(self, move):
        """
        Takes a Move as a parameter and executes it (won't work for castling, en-passant and pawn promotion)
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # update king's position
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # if enpassant move, capture pawn
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        # if pawn moves twice, next move can capture enpassant
        # only on 2-square pawn advances
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # make castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side
                # move the rook
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol +
                                        1] = '--'  # erase old rook
            else:  # queen side
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # update castle rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        """
        Undo the last move
        """
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # update king's position
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # give back castle rights if move took them away
            self.castleRightsLog.pop()
            self.currentCastlingRight = CastleRights(self.castleRightsLog[-1].wks, self.castleRightsLog[-1].bks,
                                                     self.castleRightsLog[-1].wqs, self.castleRightsLog[-1].bqs)

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side
                    self.board[move.endRow][move.endCol +
                                            1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen side
                    self.board[move.endRow][move.endCol -
                                            2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            # undo possible game over
            self.checkmate = False
            self.stalemate = False

    def getValidMoves(self):
        """
        All moves, considering checks.
        1. Generates all possible moves
        2. For each move, makes the move
        3. Generates all opponent's moves
        4. For each opponent move, check if your king is attacked
        """

        tempEnpassantePossible = self.enpassantPossible
        tempCurrentCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])

            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassantPossible = tempEnpassantePossible
        self.currentCastlingRight = tempCurrentCastleRights
        return moves

    def inCheck(self):
        """
        Determines if the current player is in check
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        """
        Determines if the enemy can attack square at row and column
        """
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True

        return False

    def getAllPossibleMoves(self):
        """
        All moves without considering checks
        """
        moves = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # either w or b

                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]  # either p, R, N, B, K, Q
                    self.moveFunctions[piece](r, c, moves)

        return moves

    def getPawnMoves(self, r, c, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add moves to the list
        """
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # left capture
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:  # left enpassante
                    moves.append(Move((r, c), (r - 1, c - 1),
                                 self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # right capture
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:  # right enpassante
                    moves.append(Move((r, c), (r - 1, c + 1),
                                 self.board, isEnpassantMove=True))

        else:
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # right capture
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:  # right enpassante
                    moves.append(Move((r, c), (r + 1, c - 1),
                                 self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # left capture
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:  # left enpassante
                    moves.append(Move((r, c), (r + 1, c + 1),
                                 self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        """
        Get all the rook moves for the rook located at row, col and add moves to the list
        """
        # up, left, down, right
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"

        for direction in directions:
            for i in range(1, 8):
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i

                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # check for possible moves only in boundaries of the board
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

    def getKnightMoves(self, r, c, moves):
        """
        Get all the knight moves for the knight located at row, col and add moves to the list
        """
        directions = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2),
                      # up/left up/right right/up right/down down/left down/right left/up left/down
                      (1, -2))
        allyColor = "w" if self.whiteToMove else "b"

        for move in directions:
            endRow = r + move[0]
            endCol = c + move[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # either enemy piece or empty square
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        """
        Get all the bishop moves for the bishop located at row, col and add moves to the list
        """
        # diagonals: up/left up/right down/right down/left
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemyColor = "b" if self.whiteToMove else "w"

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

    def getQueenMoves(self, r, c, moves):
        """
        Get all the queen moves for the queen located at row, col and add moves to the list
        """
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        """
        Get all the king moves for the king located at row, col and add moves to the list
        """
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, 1),
                      (1, 1), (1, 0), (1, -1), (0, -1))
        allyColor = "w" if self.whiteToMove else "b"

        for move in king_moves:
            endRow = r + move[0]
            endCol = c + move[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def updateCastleRights(self, move):
        """
        Update the castle rights given the move
        """
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # right rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # left rook
                    self.currentCastlingRight.bks = False

        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                    self.currentCastlingRight.qks = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    def getCastleMoves(self, r, c, moves):
        """
        Generate all valid castle moves for the king at (r, c) and add them to the list
        """
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(
                    Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(
                    Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    """
    In chess, fields on the board are described by two symbols, one of them being number between 1-8 (which is corresponding to rows)
    and the second one being a letter between a-f (corresponding to columns), in order to use this notation we need to map our [row][col] coordinates
    to match the ones used in the original chess game
    """
    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
            self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        self.isCastleMove = isCastleMove

        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.isCapture = self.pieceCaptured != "--"

    def __eq__(self, other):
        """
        Overriding the equals method
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID

    def __str__(self):
        """
        Overriding the string function
        """
        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
