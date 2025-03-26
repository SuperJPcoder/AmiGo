import numpy as np
import math

class MCTSNode:
    def __init__(self, parent, action, board, player):
        self.parent = parent
        self.action = action
        self.board = board
        self.player = player
        self.children = {}
        self.N = 0  # Number of visits
        self.W = 0  # Total value of the node
        self.Q = 0  # Average value
        self.P = 0  # Prior probability from neural network

    def is_fully_expanded(self):
        return len(self.children) == len(self.get_legal_moves(self.board, self.player))

    def get_legal_moves(self, board, player):
        legal_moves = []
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == 0:
                    legal_moves.append((r, c))
        return legal_moves

    def best_child(self, c_param=1.4):
        best_score = -float("inf")
        best_child = None
        for child in self.children.values():
            ucb_score = child.Q + c_param * child.P * math.sqrt(self.N) / (1 + child.N)
            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child
        return best_child
