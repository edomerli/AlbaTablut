

class Node:
    def __init__(self, board, parent=None, action=None):
        self.turn = board.turn
        self.is_terminal, self.winner = board.check_end_game()
        self.untried_actions = board.actions()

        self.parent = parent
        self.action = action

        self.w = 0
        self.n = 0
        self.children = []