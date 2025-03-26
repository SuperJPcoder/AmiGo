import numpy as np
import copy
from mcts.mcts_node import MCTSNode
import math

class MCTS:
    def __init__(self, policy_value_fn, board_size=5, c_param=1.4, n_simulations=100):
        self.policy_value_fn = policy_value_fn
        self.board_size = board_size
        self.c_param = c_param
        self.n_simulations = n_simulations

    def simulate_game(self, root):
        for _ in range(self.n_simulations):
            node = self.select(root)
            if not node.is_fully_expanded():
                node = self.expand(node)
            value = self.simulate(node)
            self.backpropagate(node, value)

    def select(self, node):
        while node.is_fully_expanded() and node.children:
            node = node.best_child(self.c_param)
        return node

    def expand(self, node):
        legal_moves = node.get_legal_moves(node.board, node.player)
        for move in legal_moves:
            if move not in node.children:
                new_board = self.simulate_move(node.board, move, node.player)
                new_player = 3 - node.player
                new_node = MCTSNode(node, move, new_board, new_player)
                policy, _ = self.policy_value_fn(new_board)
                new_node.P = policy[move[0] * self.board_size + move[1]]
                node.children[move] = new_node
        return list(node.children.values())[0]

    def simulate(self, node):
        _, value = self.policy_value_fn(node.board)
        return value if node.player == 1 else -value

    def backpropagate(self, node, value):
        while node is not None:
            node.N += 1
            node.W += value
            node.Q = node.W / node.N
            node = node.parent
            value = -value

    def simulate_move(self, board, move, player):
        new_board = copy.deepcopy(board)
        row, col = move
        new_board[row][col] = player
        self.capture_opponent(new_board, row, col, player)
        return new_board

    def capture_opponent(self, board, row, col, player):
        opponent = 3 - player
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.is_on_board(nr, nc) and board[nr][nc] == opponent:
                group = self.get_group(board, nr, nc)
                if not self.group_has_liberties(group, board):
                    for r, c in group:
                        board[r][c] = 0

    def is_on_board(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def get_group(self, board, row, col):
        color = board[row][col]
        if color == 0:
            return set()
        group = set()
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if (r, c) not in group:
                group.add((r, c))
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if self.is_on_board(nr, nc) and board[nr][nc] == color:
                        stack.append((nr, nc))
        return group

    def group_has_liberties(self, group, board):
        for r, c in group:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if self.is_on_board(nr, nc) and board[nr][nc] == 0:
                    return True
        return False

    def get_action_prob(self, board, temp=1.0):
        root = MCTSNode(None, None, board, 1)
        self.simulate_game(root)
        action_probs = np.zeros(self.board_size * self.board_size)
        for action, child in root.children.items():
            action_probs[action[0] * self.board_size + action[1]] = child.N ** (1.0 / temp)
        action_probs /= np.sum(action_probs)
        return action_probs
