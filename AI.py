
import copy
from math import sqrt, log, inf
import random

from Node import Node

    
class AI:
    def __init__(self, budget):
        self.budget = budget
        self.root_board = None
        self.search_board = None

    def MCTS(self, board):
        """Perform Monte Carlo Tree Search starting from a board configuration

        Args:
            board (Board): the board configuration to start from

        Returns:
            The action to take and its predicted win rate
        """
        root = Node(board)
        self.root_board = board

        iters = 0

        while iters < self.budget:
            self.search_board = copy.deepcopy(board)

            selected_node = self._select(root)
            expanded_node = self._expand(selected_node)
            winner = self._simulate(expanded_node)
            self._backpropagate(expanded_node, winner)
    
            iters += 1
            print(iters)
            if ((iters + 1) % 100 == 0):
                print(f"Iterations/budget: {iters + 1}/{self.budget}")
    
        best_child, action, action_win_rate = self._best_child(root, c=0)
        return action, action_win_rate


    def _select(self, root):
        """Select a node for expansion in the MCTS tree rooted at root

        Args:
            root (Node): the root of the MCTS tree

        Returns:
            The selected node to be expanded
        """
        n = root
        while len(n.untried_actions) == 0:
            new_node = self._best_child(n, c=1)[0]

            self.search_board.take_action(new_node.action)
            n = new_node
        return n

        
    def _expand(self, node):
        """Expand a node, i.e. generate a new node out of his potential children

        Args:
            node (Node): the node that needs to be expanded

        Returns:
            the child node created
        """
        if node.is_terminal:
            return node
        

        i = random.randint(0, len(node.untried_actions)-1)
        j = random.randint(0, len(node.untried_actions[i][1])-1)
        action = [node.untried_actions[i][0], node.untried_actions[i][1].pop(j)]

        if len(node.untried_actions[i][1]) == 0:
            del node.untried_actions[i]

        self.search_board.take_action(action)
        
        new_node = Node(self.search_board, parent=node, action=action)
        node.children.append(new_node)
        return new_node

    def _simulate(self, node):
        """Simulate the game from a node

        Args:
            node (Node): starting node, whose board state is stored in self.search_board

        Returns:
            The winner from the simulation
        """
        if node.is_terminal:
            return node.winner
        return self.search_board.simulate_game()

    def _backpropagate(self, node, winner):
        """Backpropagate the result of the simulation up from the expanded node to the root

        Args:
            node (Node): the expanded node
            winner (int): integer representing the player that won in the simulation
        """
        while True:
            node.n += 1

            if node.parent is None:
                break
            
            node.w += 1 if node.parent.turn == winner else 0
            node = node.parent


    def _best_child(self, parent, c=1):
        """Apply the UCT formula in order to determine the best child to visit (=== the best action to take)

        Args:
            parent (Node): the parent node from which to choose the action
            c (float): the exploration parameter in the UCT formula
        """
        best_child_node = None
        best_action = None

        best_uct_value = -1
        log_parent_visits = log(parent.n)

        for child in parent.children:
            uct_value = child.w / child.n + c * sqrt(log_parent_visits / child.n)

            if uct_value > best_uct_value:
                best_uct_value = uct_value

                best_child_node = child
                best_action = child.action

        return best_child_node, best_action, best_uct_value
