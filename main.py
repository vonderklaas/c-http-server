# Driver File
# - Handle user input
# - Display the current game state object

import pygame as p
from engine import GameState

WIDTH = 512
HEIGHT = 512
DIMENSIONS = 8
SQ_SIZE = HEIGHT // DIMENSIONS
MAX_FPS = 15
IMAGES = {}

'''
Initialize a global dictionary of images, called only once.
'''
def load_images():
    pieces = [
        "bp", "bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR",
        "wp", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"
    ]

    # We can access an image now by calling "IMAGES["wp"]"
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(f"assets/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )


'''
Main driver for handling the user input and updating the graphics.
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = GameState()

    # Only load images once
    load_images() 

    running = True

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip( )


'''
Function responsible for all graphics to draw board, pieces for current game state
'''
def draw_game_state(screen, gs):

    # Note: Order matters!

    # Draw squares on the board
    draw_board(screen)

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
            p.draw.rect(screen, color, p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw pieces on the board using the current board state
'''
def draw_pieces(screen, board):
    for row in range(DIMENSIONS):
        for column in range(DIMENSIONS):
            piece = board[row][column]

            # If piece is not empty square
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()