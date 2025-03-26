import numpy as np

class GoEnv:
    def __init__(self, board_size=5):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = 1
        self.history = []  # Store previous states for undo

    def reset_board(self):
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        self.history.clear()

    def make_move(self, row, col, player):
        if not self.is_on_board(row, col) or self.board[row][col] != 0:
            return False
        self.history.append(np.copy(self.board))
        self.board[row][col] = player
        self.capture_opponent(row, col, player)
        group = self.get_group(row, col)
        if not self.group_has_liberties(group):
            self.board[row][col] = 0
            self.history.pop()
            return False
        self.current_player = 3 - player
        return True

    def get_legal_moves(self, player):
        legal_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 0:
                    temp_board = np.copy(self.board)
                    temp_board[row][col] = player
                    if self.is_valid_move(temp_board, row, col, player):
                        legal_moves.append((row, col))
        return legal_moves

    def is_valid_move(self, board, row, col, player):
        if board[row][col] != 0:
            return False
        board[row][col] = player
        group = self.get_group(row, col, board)
        if not self.group_has_liberties(group, board):
            return False
        return True

    def capture_opponent(self, row, col, player):
        opponent = 3 - player
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.is_on_board(nr, nc) and self.board[nr][nc] == opponent:
                group = self.get_group(nr, nc)
                if not self.group_has_liberties(group):
                    for r, c in group:
                        self.board[r][c] = 0

    def is_on_board(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def get_group(self, row, col, board=None):
        if board is None:
            board = self.board
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

    def group_has_liberties(self, group, board=None):
        if board is None:
            board = self.board
        for r, c in group:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if self.is_on_board(nr, nc) and board[nr][nc] == 0:
                    return True
        return False

    def check_winner(self):
        black_count = np.sum(self.board == 1)
        white_count = np.sum(self.board == 2)
        if len(self.get_legal_moves(1)) == 0 and len(self.get_legal_moves(2)) == 0:
            if black_count > white_count:
                return 1
            elif white_count > black_count:
                return 2
            else:
                return 0
        return -1
