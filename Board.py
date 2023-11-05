import pygame
import random
import time     #TODO: remove

from Square import Square
from Piece import Piece
from utils import *

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_width = width // GRID_COUNT
        self.tile_height = height // GRID_COUNT

        self.selected_piece = None
        self.turn = WHITE_PLAYER

        self.king_square = None
        self.king_capture = False

        self.squares = self.generate_squares()
        self.setup_board()

    def generate_squares(self):
        output = []
        row = []
        for y in range(9):
            for x in range(9):
                row.append(
                    Square(x,  y, self.tile_width, self.tile_height)
                )
            output.append(row)
            row = []

        return output

    def get_square_from_pos(self, pos):
        return self.squares[pos[1]][pos[0]]

    def get_piece_from_pos(self, pos):
        return self.get_square_from_pos(pos).occupying_piece
    
    def setup_board(self):
        for y, row in enumerate(INITIAL_CONFIG):
            for x, piece in enumerate(row):
                if piece != '':
                    square = self.get_square_from_pos((x, y))
                    square.occupying_piece = Piece(
                        (x, y), WHITE if piece == 'w' or piece == 'k' else BLACK
                    )
                    if piece == 'k':
                        self.king_square = square

    def handle_click(self, mx, my):
        x = mx // self.tile_width
        y = my // self.tile_height
        clicked_square = self.get_square_from_pos((x, y))
        if self.selected_piece is None:
            if clicked_square.occupying_piece is not None:
                if clicked_square.occupying_piece.color == self.turn:
                    self.selected_piece = clicked_square.occupying_piece
        elif self.selected_piece.move(self, clicked_square):
            self.turn = 1 - self.turn
        elif clicked_square.occupying_piece is not None:
            if clicked_square.occupying_piece.color == self.turn:
                self.selected_piece = clicked_square.occupying_piece


    def is_inside(self, pos):
        return pos[0] >= 0 and pos[0] < GRID_COUNT and pos[1] >= 0 and pos[1] < GRID_COUNT

    # def king_square(self):
    #     for row in self.squares:
    #         for s in row:
    #             if s.occupying_piece is not None and s.occupying_piece.king:
    #                 return s
    #     raise Exception()

    def king_escaped(self):
        return self.king_square.type == ESCAPE_TYPE

    def king_captured(self):
        return self.king_capture


    def draw(self, display):
        # mark highlighted squares based on current selected piece, if any
        if self.selected_piece is not None:
            self.get_square_from_pos(self.selected_piece.pos).highlight = True
            for square in self.selected_piece.get_moves(self):
                square.highlight = True
        
        # draw squares
        for row in self.squares:
            for square in row:
                square.draw(display)

        # draw horizontal lines
        for r in range(GRID_COUNT + 1):
            y = r * GRID_SIZE
            pygame.draw.line(display, [0,0,0], [0, y],
                             [GRID_SIZE * GRID_COUNT, y], 2)
            
        # draw vertical lines    
        for c in range(GRID_COUNT + 1):
            x = c * GRID_SIZE
            pygame.draw.line(display, [0,0,0], [x, 0],
                             [x, GRID_SIZE * GRID_COUNT], 2)
            

    def actions(self):
        output = []
        for row in self.squares:
            for s in row:
                p = s.occupying_piece
                if p is not None and p.color == self.turn:
                    moves = p.get_moves(self)
                    if len(moves) > 0:
                        output.append([s.pos, [z.pos for z in moves]])
        return output

    def take_action(self, action):
        pos_start, pos_end = action
        if self.get_piece_from_pos(pos_start).move(self, self.get_square_from_pos(pos_end)):
            self.turn = 1 - self.turn


    def check_end_game(self):
        if self.king_captured():
            return True, BLACK_PLAYER    
        elif self.king_escaped():
            return True, WHITE_PLAYER
		            
        if len(self.actions()) == 0:
            return True, 1 - self.turn
        return False, None
    


    def simulate_game(self):
        while True:
            end, winner = self.check_end_game()
            if end:
                # input("Enter any key")  # TODO: remove - Just to stop after every simulated game
                return winner
            
            # TODO: use the same code between here and AI for random choice generation (?)
            possible_actions = self.actions()
            i = random.randint(0, len(possible_actions)-1)
            j = random.randint(0, len(possible_actions[i][1])-1)
            action = [possible_actions[i][0], possible_actions[i][1][j]]
            self.take_action(action)
            
            # TODO: remove -- just to visualize the simulation
            # screen.fill('white')
            # self.draw(screen)
            # pygame.display.update()
            # time.sleep(1)
