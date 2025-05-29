import random

PIECE_SCORE = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}

KNIGHT_SCORES = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.6, 0.6, 0.6, 0.5, 0.2],
                 [0.2, 0.5, 0.6, 0.7, 0.7, 0.6, 0.5, 0.2],
                 [0.2, 0.5, 0.6, 0.7, 0.7, 0.6, 0.5, 0.2],
                 [0.2, 0.5, 0.6, 0.6, 0.6, 0.6, 0.5, 0.2],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

BISHOP_SCORES = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

ROOK_SCORES = [[0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
               [0.5, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.5],
               [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
               [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
               [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
               [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
               [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
               [0.2, 0.2, 0.2, 0.5, 0.5, 0.2, 0.2, 0.2]]

QUEEN_SCORES = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

PAWN_SCORES = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.2, 0.2, 0.3, 0.4, 0.4, 0.3, 0.2, 0.2],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.2, 0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2],
               [0.2, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.2],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

PIECE_POSITION_SCORES = {
    "wp": PAWN_SCORES,
    "bp": PAWN_SCORES[::-1],
    "wN": KNIGHT_SCORES,
    "bN": KNIGHT_SCORES[::-1],
    "wB": BISHOP_SCORES,
    "bB": BISHOP_SCORES[::-1],
    "wR": ROOK_SCORES,
    "bR": ROOK_SCORES[::-1],
    "wQ": QUEEN_SCORES,
    "bQ": QUEEN_SCORES[::-1]
}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
nextMove = None


def findRandomMove(validMoves):
    """
    Picks and returns a random move
    """
    return random.choice(validMoves)


def findBestMove(gs, validMoves, returnQueue):
    """
    Find nega max move helper. First recursive caller
    """
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -
                             CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    """
    White searches the highest value, black the lowest
    """
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = - \
            findMoveNegaMaxAlphaBeta(
                gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()

        # pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

    return maxScore


def scoreBoard(gs):
    """
    A positive score is good for white, a negative score is good for black
    """
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != "--":
                # score it by position
                piecePositionScore = 0
                if piece[1] != "K":
                    piecePositionScore = PIECE_POSITION_SCORES[piece][row][col]

                # score it by material
                if piece[0] == 'w':
                    score += PIECE_SCORE[piece[1]] + piecePositionScore
                elif piece[0] == 'b':
                    score -= PIECE_SCORE[piece[1]] + piecePositionScore

    return score
