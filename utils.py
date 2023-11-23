INITIAL_CONFIG = [
            ['EMPTY', 'EMPTY', 'EMPTY', 'BLACK', 'BLACK', 'BLACK', 'EMPTY', 'EMPTY', 'EMPTY'],
            ['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'BLACK', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'],
            ['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'WHITE', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'],
            ['BLACK', 'EMPTY', 'EMPTY', 'EMPTY', 'WHITE', 'EMPTY', 'EMPTY', 'EMPTY', 'BLACK'],
            ['BLACK', 'BLACK', 'WHITE', 'WHITE', 'KING', 'WHITE', 'WHITE', 'BLACK', 'BLACK'],
            ['BLACK', 'EMPTY', 'EMPTY', 'EMPTY', 'WHITE', 'EMPTY', 'EMPTY', 'EMPTY', 'BLACK'],
            ['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'WHITE', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'],
            ['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'BLACK', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'],
            ['EMPTY', 'EMPTY', 'EMPTY', 'BLACK', 'BLACK', 'BLACK', 'EMPTY', 'EMPTY', 'EMPTY']
        ]

ESCAPES = [(x, y) for x in [0, 8] for y in [1, 2, 6, 7]] + [(x, y) for y in [0, 8] for x in [1, 2, 6, 7]]
CAMPS = [(x, y) for x in [0, 8] for y in [3, 4, 5]] + [(x, y) for y in [0, 8] for x in [3, 4, 5]] + [(1, 4), (4, 1), (7, 4), (4, 7)]
CASTLE = (4, 4)
DEFENSES = [(4, 2), (4, 3), (4, 5), (4, 6), (2, 4), (3, 4), (5, 4), (6, 4)]
ADJ_CASTLE = [(4, 5), (5, 4), (4, 3), (3, 4)]

ESCAPE_TYPE = 'e'
CAMP_TYPE = 'c'
CASTLE_TYPE = 'a'
DEFENSE_TYPE = 'd'
ADJ_CASTLE_TYPE = 'z'

WHITE = 0
BLACK = 1

WHITE_PLAYER = 0
BLACK_PLAYER = 1

WHITE_COLOR = [255] * 3
BLACK_COLOR = [0] * 3

WINDOW_SIZE = (600, 600)
GRID_COUNT = 9
GRID_SIZE = WINDOW_SIZE[0] // GRID_COUNT
RADIUS = GRID_SIZE // 3
WIDTH = 0

DIRS = [[-1, 0], [0, -1], [0, 1], [1, 0]]

AI_BUDGET = 500    # 1600 is how many simulation AlphaZero uses
NUM_ACTIONS = 9 * 9 * 32