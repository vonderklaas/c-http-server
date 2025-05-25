# Driver File
# - Handle user input
# - Display the current game state object

import pygame as p
from engine import GameState, Move

WIDTH = 512
HEIGHT = 512
DIMENSIONS = 8
SQ_SIZE = HEIGHT // DIMENSIONS
MAX_FPS = 15
IMAGES = {}

'''
    Initialize a global dictionary of images, called only once
'''


def load_images():
    # pieces = [
    #     "bp", "bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR",
    #     "wp", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"
    # ]
    pieces = ["bp", "bR", "bN", "bB", "bQ",
              "bK", "wp", "wR", "wN", "wB", "wQ", "wK"]

    # We can access an image now by calling "IMAGES["wp"]"
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(f"assets/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )


'''
Main driver for handling the user input and updating the graphics
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = GameState()

    # Move validations
    valid_moves = gs.get_valid_moves()
    # Flag variable to check if mode is made and it is valid, we generate new set of moves
    # Until that we should not re-generate the moves, so we can save some compute
    move_made = False

    # Only load images once
    load_images()

    running = True

    # Keep track of clicked square in a tuple (row, col)
    square_selected = ()

    # Keep track of both player clicks in two tuples like [(6, 4), (4, 4)]
    player_clicks = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:

                # x, y location of the mouse
                location = p.mouse.get_pos()
                row = location[1] // SQ_SIZE
                col = location[0] // SQ_SIZE

                # If user clicked same square twice, treat it as undo
                if square_selected == (row, col):
                    # Undo selection
                    square_selected = ()
                    # Reset player clicks
                    player_clicks = []
                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)

                # Was that the user second click? Now we want to register the move
                if len(player_clicks) == 2:
                    move = Move(player_clicks[0], player_clicks[1], gs.board)
                    print(f"Move made {move.get_chess_notation()}")

                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                        # Resets in order to enable next moves
                        square_selected = ()
                        player_clicks = []
                    else:
                        print(f"Invalid move attempt")
                        player_clicks = [square_selected]

            # Key handlers
            elif e.type == p.KEYDOWN:
                # Undo a move if Z is pressed
                if e.key == p.K_z:
                    gs.undo_move()
                    # Re-generate the valid moves
                    valid_moves = gs.get_valid_moves()
                    move_made = True

        if move_made:
            # Flag variable to check if mode is made and it is valid, we generate new set of moves
            # Until that we should not re-generate the moves, so we can save some compute
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs, square_selected)
        clock.tick(MAX_FPS)
        p.display.flip()


def highlight_square(screen, square_selected):
    if square_selected != ():
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)  # 0 is transparent, 255 is opaque
        s.fill(p.Color("blue"))  # Or use "yellow", "green", etc.
        screen.blit(s, (square_selected[1] *
                    SQ_SIZE, square_selected[0] * SQ_SIZE))


'''
Function responsible for all graphics to draw board, pieces for current game state
'''


def draw_game_state(screen, gs, square_selected):

    # Note: Order matters!

    # Draw squares on the board
    draw_board(screen)

    # highlight
    highlight_square(screen, square_selected)  # <- Add thi

    # Draw pieces on top of the squares
    draw_pieces(screen, gs.board)


'''
Draw squares of the board
'''


def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSIONS):
        for column in range(DIMENSIONS):

            # Determine which color do we want
            even_or_odd = (row + column) % 2
            color = colors[even_or_odd]
            p.draw.rect(screen, color, p.Rect(
                column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw pieces on the board using the current board state
'''


def draw_pieces(screen, board):
    for row in range(DIMENSIONS):
        for column in range(DIMENSIONS):
            piece = board[row][column]

            # If piece is not empty square
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
