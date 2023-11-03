import pygame

from utils import *

class Piece:
    def __init__(self, pos, color):
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.color = color
        self.king = True if (self.x, self.y) == CASTLE else False

    def get_possible_moves(self, board):
        output = []
        moves_north = []
        for y in range(self.y)[::-1]:
            moves_north.append(board.get_square_from_pos(
                (self.x, y)
            ))
        output.append(moves_north)
        moves_east = []
        for x in range(self.x + 1, GRID_COUNT):
            moves_east.append(board.get_square_from_pos(
                (x, self.y)
            ))
        output.append(moves_east)
        moves_south = []
        for y in range(self.y + 1, GRID_COUNT):
            moves_south.append(board.get_square_from_pos(
                (self.x, y)
            ))
        output.append(moves_south)
        moves_west = []
        for x in range(self.x)[::-1]:
            moves_west.append(board.get_square_from_pos(
                (x, self.y)
            ))
        output.append(moves_west)
        return output
    

    def get_moves(self, board):
        prev_square = board.get_square_from_pos(self.pos)
        output = []
        for direction in self.get_possible_moves(board):
            for square in direction:
                if square.occupying_piece is not None or square.type == CASTLE_TYPE or (square.type == CAMP_TYPE and (self.color == WHITE or prev_square.type != CAMP_TYPE)):
                    break
                else:
                    output.append(square)
        return output
    
    
    def move(self, board, square):
        for i in board.squares:
            i.highlight = False

        if square in self.get_moves(board):   # perform movement
            prev_square = board.get_square_from_pos(self.pos)
            self.pos, self.x, self.y = square.pos, square.x, square.y
            prev_square.occupying_piece = None
            square.occupying_piece = self
            board.selected_piece = None

            for d in DIRS:
                # mid stands for "middle", os stands for "other side"
                mid_pos = [self.x + d[0], self.y + d[1]]
                os_pos = [self.x + 2*d[0], self.y + 2*d[1]]
                if board.is_inside(mid_pos) and board.is_inside(os_pos):
                    mid_square = board.get_square_from_pos(mid_pos)
                    mid_piece = mid_square.occupying_piece
                    os_square = board.get_square_from_pos(os_pos)
                    os_piece = os_square.occupying_piece
                    if mid_piece is not None and mid_piece.color != self.color:
                        if mid_piece.king:
                            if mid_square.pos == CASTLE:
                                pieces = [board.get_piece_from_pos(p) for p in ADJ_CASTLE]
                                if all(p is not None and p.color == BLACK for p in pieces):
                                    board.king_capture = True
                                    mid_square.occupying_piece = None
                            elif mid_square.pos in ADJ_CASTLE:
                                if all(((sq.occupying_piece is not None and sq.occupying_piece.color == BLACK) or sq.type == CASTLE_TYPE) for sq in mid_square.adj_squares(board)): 
                                    board.king_capture = True
                                    mid_square.occupying_piece = None
                            elif (os_piece is not None and os_piece.color == self.color) or os_square.type == CAMP_TYPE:
                                board.king_capture = True
                                mid_square.occupying_piece = None
                            
                        else:
                            if (os_piece is not None and os_piece.color == self.color) or os_square.type == CASTLE_TYPE or (os_square.type == CAMP_TYPE and mid_square.type != CAMP_TYPE):
                                mid_square.occupying_piece = None

            return True
        
        else:   # reset selection
            board.selected_piece = None
            return False