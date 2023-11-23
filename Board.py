import pygame
import random
import numpy as np
import torch

from Square import Square
from Piece import Piece
from utils import *

class Board:
    def __init__(self, width, height, configuration=None, turn=None):
        self.width = width
        self.height = height
        self.tile_width = width // GRID_COUNT
        self.tile_height = height // GRID_COUNT

        self.selected_piece = None
        
        if turn is None:
            self.turn = WHITE_PLAYER
        else:
            self.turn = WHITE_PLAYER if turn == 'WHITE' else BLACK_PLAYER

        self.king_square = None
        self.king_capture = False

        self.squares = self.generate_squares()
        if configuration is None:
            self.setup_board(INITIAL_CONFIG)
        else:
            self.setup_board(configuration)

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
    
    def setup_board(self, configuration):
        for y, row in enumerate(configuration):
            for x, piece in enumerate(row):
                if piece != 'EMPTY':
                    square = self.get_square_from_pos((x, y))
                    square.occupying_piece = Piece(
                        (x, y), WHITE if piece == 'WHITE' or piece == 'KING' else BLACK
                    )
                    if piece == 'KING':
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
        successful = self.get_piece_from_pos(pos_start).move(self, self.get_square_from_pos(pos_end))
        assert successful
        if successful:
            self.turn = 1 - self.turn


    def check_end_game(self):
        if self.king_captured():
            return True, BLACK_PLAYER    
        elif self.king_escaped():
            return True, WHITE_PLAYER
		            
        if len(self.actions()) == 0:
            return True, 1 - self.turn
        return False, None

    
    def to_onehot_tensor(self):
        tensor = np.zeros((3, 9, 9))     # index 0 for black, 1 for white and 2 for king
        for x in range(9):
            for y in range(9):
                piece = self.get_piece_from_pos((x, y))
                if piece is None:
                    continue
                
                i = None
                if piece.king: 
                    i = 2
                elif piece.color == WHITE:
                    i = 1
                elif piece.color == BLACK:
                    i = 0
                
                if i is not None:
                    tensor[i, y, x] = 1
        return torch.from_numpy(tensor).float().unsqueeze(0)
    
    def legal_actions_array(self):
        tensor = np.zeros((9, 9, 32))   # 4 (num dirs) * 8 (max ray) = 32
        

        actions = self.actions()
        for pos_start, pos_ends in actions:
            for pos_end in pos_ends:
                
                if pos_start[0] == pos_end[0]:
                    i = pos_end[1] - pos_start[1]
                    i -= 1 if i > 0 else 0
                    i += 8

                elif pos_start[1] == pos_end[1]:
                    i = pos_end[0] - pos_start[0]
                    i -= 1 if i > 0 else 0
                    i += 8 + 16
                
                else:
                    raise ValueError
                
                tensor[pos_start[0], pos_start[1], i] = 1

        tensor = tensor.ravel()     # flatten tensor
        return tensor
    
    
    def index_to_action(self, index):
        z = index % 32
        index //= 32
        y = index % 9
        index //= 9
        x = index

        if z >= 16:
            z -= 16 + 8
            z += 1 if z >= 0 else 0
            pos_start = (x, y)
            pos_end = (x + z, y)
        else:
            z -= 8
            z += 1 if z >= 0 else 0
            pos_start = (x, y)
            pos_end = (x, y + z)
        return pos_start, pos_end


    def simulate_game(self):
        while True:
            end, winner = self.check_end_game()
            if end:
                # input("Enter any key")  # TODO: remove - Just to stop after every simulated game
                return winner
            
            possible_actions = self.actions()
            i = random.randint(0, len(possible_actions)-1)
            j = random.randint(0, len(possible_actions[i][1])-1)
            action = [possible_actions[i][0], possible_actions[i][1][j]]
            self.take_action(action)
            
            # screen.fill('white')
            # self.draw(screen)
            # pygame.display.update()
            # time.sleep(1)
