
import copy
from math import sqrt, log
import random
import numpy as np
import torch
import collections
from typing import Mapping

from AlphaZeroNet import AlphaZeroNet
from utils import *

    
class DummyNode:
    """A place holder to make computation possible for the root node."""

    def __init__(self):
        self.parent = None
        self.child_W = collections.defaultdict(float)
        self.child_N = collections.defaultdict(float)

class Node:
    def __init__(self, board, pi=None, parent=None, action=None):
        self.turn = board.turn
        self.is_terminal, self.winner = board.check_end_game()

        self.is_expanded = False
        self.parent = parent
        self.action = action    # the action that from the parent's board lead to this Node's board

        self.child_W = np.zeros(NUM_ACTIONS, dtype=np.float32)
        self.child_N = np.zeros(NUM_ACTIONS, dtype=np.float32)
        self.pi = np.zeros(NUM_ACTIONS, dtype=np.float32) if pi is None else pi

        self.children: Mapping[int, Node] = {}

    @property
    def N(self):
        """The number of visits for current node is stored at parent's level."""
        return self.parent.child_N[self.action]
    
    @N.setter
    def N(self, value):
        self.parent.child_N[self.action] = value

    @property
    def W(self):
        """The total value for current node is stored at parent's level."""
        return self.parent.child_W[self.action]

    @W.setter
    def W(self, value):
        self.parent.child_W[self.action] = value


        
    def set_pi(self, pi):
        self.pi = pi


    

class AI:
    def __init__(self, budget, player_color):
        self.budget = budget
        self.player_color = player_color
        self.root_board = None
        self.search_board = None

        self.alphazero = AlphaZeroNet((3, 9, 9), NUM_ACTIONS, num_res_block=9, num_filters=128, num_fc_units=128).float()


    def MCTS(self, board, root_noise = True):
        """Perform Monte Carlo Tree Search starting from a board configuration

        Args:
            board (Board): the board configuration from which to start the search
        Returns:
            The action to take and its predicted win rate
        """
        self.root_board = board
        pi, _ = self.alphazero(self.root_board.to_onehot_tensor())
        pi = pi.detach().numpy().ravel()
        
        # TODO: should I use sparse tensors TO REPRESENT BOARD (not pi! almost dense)? And when to convert? It will save me memory

        # TODO: mask pi with legal moves, or do so inside the network -> at this point I can
        # avoid it because I'm doing it inside _generate_search_policy, but let's see if it's better to do it in the model as well
        
        if root_noise:
            pi = self._add_dirichlet_noise(pi, self.root_board.legal_actions_array(), self.root_board.promising_actions_array(self.root_board.turn))

        root = Node(board, pi=pi, parent=DummyNode())

        iters = 0

        while iters < self.budget:
            self.search_board = copy.deepcopy(board)

            node_to_expand = self._select(root)
            if node_to_expand.is_terminal:
                v = 1 if node_to_expand.winner == node_to_expand.turn else -1
            else:
                v = self._expand(node_to_expand)
            self._backpropagate(node_to_expand, v)
    
            iters += 1
            # if ((iters + 1) % 100 == 0):
            #     print(f"Iterations/budget: {iters + 1}/{self.budget}")
    
        root_legal_actions = self.root_board.legal_actions_array()
        best_child, action, action_win_rate = self._best_child(root, root_legal_actions, c=0)   # Note: action_win_rate is in range [-1, 1]
        
        
        return self.root_board.index_to_action(action), action_win_rate, self._generate_search_policy(root, root_legal_actions)


    def _select(self, root):
        """Select a node for expansion in the MCTS tree rooted at root

        Args:
            root (Node): the root of the MCTS tree

        Returns:
            The selected node to be expanded
        """
        n = root   

        while n.is_expanded:
            new_node = self._best_child(n, self.search_board.legal_actions_array(), c=1)[0]  # this will create a new unexpanded node if needed
            
            self.search_board.take_action(self.search_board.index_to_action(new_node.action))
            n = new_node
        return n

        
    def _expand(self, node):
        """Expand a node, i.e. compute the probability distribution over its actions Pi and set it in its object 
        and return its value V for backpropagation

        Args:
            node (Node): the node that needs to be expanded

        Returns:
            the value of this node
        """
        if node.is_expanded:
            raise RuntimeError("Node is already expanded")
        
        new_board_tensor = self.search_board.to_onehot_tensor()
        pi, v = self.alphazero(new_board_tensor)
        node.set_pi(pi.detach().numpy().ravel())

        node.is_expanded = True
        
        return v


    def _backpropagate(self, node, value):
        """Backpropagate the result of the simulation up from the expanded node to the root

        Args:
            node (Node): the expanded node
            value (int): value of the expanded node's state
        """
        while node.parent is not None:
            node.N += 1
            node.W += value
            node = node.parent
            value = -value


    def _best_child(self, parent, legal_actions, c=1):
        """Apply the UCT formula in order to determine the best child to visit (=== the best action to take)

        Args:
            parent (Node): the parent node from which to choose the action
            c (float): the exploration parameter in the UCT formula
        """
        sqrt_parent_visits = sqrt(parent.N)

        # The minus in the first term (Q value) is because the children win rates are with respect to the other player
        puct_scores = - parent.child_W / (parent.child_N + 1e-5) + c * parent.pi * sqrt_parent_visits / (parent.child_N + 1)

        puct_scores = np.where(legal_actions == 1, puct_scores, -9999)
            
        best_action = np.argmax(puct_scores)

        assert legal_actions[best_action] == 1

        if best_action not in parent.children:
            parent.children[best_action] = Node(self.search_board, parent=parent, action=best_action)

        return parent.children[best_action], best_action, puct_scores[best_action]


    def _generate_search_policy(self, root, legal_actions):
        root.child_N = legal_actions * root.child_N       
        
        #TODO: add temperature
        return root.child_N / np.sum(root.child_N)  # normalize visits
    
    def _add_dirichlet_noise(self, pi, legal_actions, eps=0.25, alpha=30.0):
        alphas = np.ones_like(legal_actions) * alpha
        noise = legal_actions * np.random.dirichlet(alphas)
        noise = noise / noise.sum()  # normalize
        # print(sum(pi))
        # print(noise)
        # print(sum(noise))
        # print(sum((1 - eps) * pi + eps * noise))
        return (1 - eps) * pi + eps * noise


