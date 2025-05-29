"""
This is the main driver file. 
It is responsible for handling user input and displaying the current game state
"""


import pygame as p
from engine import GameState, Move
from ai import findBestMove, findRandomMove
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # Mainly for animations
IMAGES = {}
COLORS = [p.Color("white"), p.Color("gray")]


def loadImages():
    """
    Initialize global dictionary of images. 
    This will be called exactly once in the main function
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK',
              'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            "assets/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    """
    The main driver for the code. 
    It will handle user input and updating the graphics
    """
    p.init()
    p.display.set_caption('[Chess Engine] by vonderklaas')
    p.mixer.init()
    screen = p.display.set_mode(
        [BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT])
    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = GameState()
    validMoves = gs.getValidMoves()
    sqSelected = ()  # keep track of last user click, tuple: (row, col)
    # keep track of last two player clicks, two tuples: [(row, col), (row, col)]
    playerClicks = []
    playerOne = True  # If true, human is playing white, otherwise AI is playing white
    playerTwo = False  # same as above, except playing black
    moveFinderProcess = None
    returnQueue = None
    AIThinking = False
    gameOver = False
    moveMade = False
    moveUndone = False
    animate = False
    running = True

    loadImages()

    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (
            not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    # user clicked the same square twice or the move log
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2 and isHumanTurn:
                        move = Move(
                            playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        if not gameOver and not isHumanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # used to pass data between threads
                moveFinderProcess = Process(
                    target=findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = findRandomMove(validMoves)

                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            if gs.stalemate:
                text = "Stalemate."
            else:
                text = "Black wins by checkmate!" if gs.whiteToMove else "White wins by checkmate!"
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    """
    Responsible for all the graphics within a current game state
    """
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)


def drawBoard(screen):
    """
    Draws the squares on the board.
    In chess, the top left square is always light.
    """
    global COLORS
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(
                c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, sqSelected):
    """
    Highlight square selection
    """
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # highlight valid moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(
                        s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    """
    Draws the pieces on top of the board using the current GameState.board
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]

            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    """
    Draws the move log on the right side of the window
    """
    moveLogRect = p.Rect(
        BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("dark gray"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):  # append opponent move
            moveString += str(moveLog[i + 1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 2
    padding = 5
    lineSpacing = 2
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]

        textObject = font.render(text, True, p.Color('White'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


def animateMove(move, screen, board, clock):
    """
    Animating a move including playing the sound
    """
    if move.isCapture:
        p.mixer.music.load("audio/capture.mp3")
        p.mixer.music.play()
    else:
        p.mixer.music.load("audio/move.mp3")
        p.mixer.music.play()

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 7
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount,
                move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE,
                           move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + \
                    1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE,
                                   enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], p.Rect(
                c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    """
    Draw text on screen
    """
    # Draw text shadow
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

    # Draw main text
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
