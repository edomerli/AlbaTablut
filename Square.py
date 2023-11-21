import pygame

from utils import *

class Square:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.abs_x = x * width
        self.abs_y = y * height
        self.abs_pos = (self.abs_x, self.abs_y)
        self.pos = (x, y)


        if self.pos in ESCAPES:
            self.type = ESCAPE_TYPE
            self.draw_color = (0, 255, 255)
            self.highlight_color = (0, 255, 0)
        elif self.pos in CAMPS:
            self.type = CAMP_TYPE
            self.draw_color = (64, 64, 64)
            self.highlight_color = (0, 255, 0)
        elif self.pos == CASTLE:
            self.type = CASTLE_TYPE
            self.draw_color = (255, 140, 26)
            self.highlight_color = (0, 255, 0)
        elif self.pos in DEFENSES:
            self.type = DEFENSE_TYPE
            self.draw_color = (255, 204, 255)
            self.highlight_color = (0, 255, 0)
        elif self.pos in ADJ_CASTLE:
            self.type = ADJ_CASTLE_TYPE
            self.draw_color = (255, 212, 128)
            self.highlight = (0, 255, 0)
        else:
            self.type = None
            self.draw_color = (255, 212, 128)
            self.highlight_color = (0, 255, 0)

        self.occupying_piece = None
        self.highlight = False
        self.rect = pygame.Rect(
            self.abs_x,
            self.abs_y,
            self.width,
            self.height
        )

    def __eq__(self, other):
        # Defined in order to make the check of a square belonging to a list of squares faster
        # A square is defined by its position in this case
        return self.x == other.x and self.y == other.y

    def draw(self, display):
        # configures if tile should be light or dark or highlighted tile
        if self.highlight:
            pygame.draw.rect(display, self.highlight_color, self.rect, border_radius=1)
        else:
            pygame.draw.rect(display, self.draw_color, self.rect)
        # adds the chess piece icons
        if self.occupying_piece != None:    
            pygame.draw.circle(display, BLACK_COLOR if self.occupying_piece.color == BLACK else WHITE_COLOR, self.rect.center, RADIUS, WIDTH)
            if self.occupying_piece.king == True:
                pygame.draw.line(display, BLACK_COLOR, [self.rect.center[0] - self.width//6, self.rect.center[1]], 
                                 [self.rect.center[0] + self.width//6, self.rect.center[1]], 5)
                pygame.draw.line(display, BLACK_COLOR, [self.rect.center[0], self.rect.center[1] - self.width//6], 
                                 [self.rect.center[0], self.rect.center[1] + self.width//6], 5)
                
    def adj_squares(self, board):
        return [board.get_square_from_pos([self.x + d[0], self.y + d[1]]) for d in DIRS]
    
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