import tkinter as tk
import copy
import random
import math
from tkinter import messagebox
import time

class MCTSNode:
    def __init__(self, board, player, move=None, parent=None):
        self.board = board
        self.player = player
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self, game):
        return len(self.children) == len(game.get_all_valid_moves(self.board, self.player))

    def best_child(self, c_param=1.41):
        choices = []
        for child in self.children:
            if child.visits == 0:
                uct = float('inf')
            else:
                uct = child.wins / child.visits + c_param * math.sqrt(math.log(self.visits) / child.visits)
            choices.append((uct, child))
        return max(choices, key=lambda x: x[0])[1]

    def expand(self, game):
        tried_moves = [child.move for child in self.children]
        for move in game.get_all_valid_moves(self.board, self.player):
            if move not in tried_moves:
                new_board = game.simulate_move(self.board, move[0], move[1], self.player)
                if new_board is not None:
                    child_node = MCTSNode(new_board, 3 - self.player, move, self)
                    self.children.append(child_node)
                    return child_node
        return None

    def simulate_random_game(self, game):
        sim_board = copy.deepcopy(self.board)
        sim_player = self.player
        moves = game.get_all_valid_moves(sim_board, sim_player)
        while moves:
            move = random.choice(moves)
            sim_board = game.simulate_move(sim_board, move[0], move[1], sim_player)
            if sim_board is None:
                break
            sim_player = 3 - sim_player
            moves = game.get_all_valid_moves(sim_board, sim_player)
        black_stones = sum(cell == 1 for row in sim_board for cell in row)
        white_stones = sum(cell == 2 for row in sim_board for cell in row)
        black_territory, white_territory = game.count_territory_on_board(sim_board)
        black_score = black_stones + black_territory
        white_score = white_stones + white_territory
        if self.player == 2:
            return 1 if white_score > black_score else 0
        else:
            return 1 if black_score > white_score else 0

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1 - result)

def mcts(game, board, player, iter_limit=10):
    root = MCTSNode(board, player)
    for _ in range(iter_limit):
        node = root
        while node.is_fully_expanded(game) and node.children:
            node = node.best_child()
        if not node.is_fully_expanded(game):
            node = node.expand(game)
        result = node.simulate_random_game(game)
        node.backpropagate(result)
    best = max(root.children, key=lambda c: c.visits)
    return best.move

class GoGame:
    def __init__(self, root):
        self.root = root
        self.board_size = 5
        self.cell_size = 60
        self.canvas_size = self.board_size * self.cell_size
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="burlywood")
        self.canvas.pack()
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.history = []
        self.future = []
        self.game_over = False
        self.canvas.bind("<Button-1>", self.make_move)
        self.draw_board()
        self.create_buttons()

    def create_buttons(self):
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()
        restart_button = tk.Button(self.button_frame, text="Restart", command=self.restart_game)
        restart_button.grid(row=0, column=0, padx=5, pady=5)
        undo_button = tk.Button(self.button_frame, text="Undo", command=self.undo_move)
        undo_button.grid(row=0, column=1, padx=5, pady=5)
        redo_button = tk.Button(self.button_frame, text="Redo", command=self.redo_move)
        redo_button.grid(row=0, column=2, padx=5, pady=5)

    def draw_board(self):
        self.canvas.delete("grid")
        offset = self.cell_size // 2
        for i in range(self.board_size):
            start = offset + i * self.cell_size
            self.canvas.create_line(offset, start, self.canvas_size - offset, start, tags="grid")
            self.canvas.create_line(start, offset, start, self.canvas_size - offset, tags="grid")
        self.draw_stones()

    def draw_stones(self):
        self.canvas.delete("stone")
        offset = self.cell_size // 2
        radius = self.cell_size // 3
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0:
                    x = c * self.cell_size + offset
                    y = r * self.cell_size + offset
                    color = "black" if self.board[r][c] == 1 else "white"
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="black", tags="stone")

    def make_move(self, event):
        if self.game_over:
            return
        row, col = self.get_cell(event.x, event.y)
        new_board = self.simulate_move(self.board, row, col, self.current_player)
        if new_board is not None:
            self.history.append(copy.deepcopy(self.board))
            self.board = new_board
            self.future.clear()
            self.current_player = 3 - self.current_player
            self.draw_board()
            self.check_end_condition()
            self.root.after(300, self.ai_move)

    def ai_move(self):
        if self.game_over or self.current_player != 2:
            return
        move = mcts(self, self.board, self.current_player)
        if move:
            row, col = move
            new_board = self.simulate_move(self.board, row, col, self.current_player)
            if new_board is not None:
                self.history.append(copy.deepcopy(self.board))
                self.board = new_board
                self.future.clear()
                self.current_player = 3 - self.current_player
                self.draw_board()
                self.check_end_condition()

    def get_all_valid_moves(self, board, player):
        valid = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board[r][c] == 0 and self.simulate_move(board, r, c, player) is not None:
                    valid.append((r, c))
        return valid

    def get_cell(self, x, y):
        offset = self.cell_size // 2
        col = int(round((x - offset) / self.cell_size))
        row = int(round((y - offset) / self.cell_size))
        return row, col

    def simulate_move(self, board, row, col, player):
        if not self.is_on_board(row, col) or board[row][col] != 0:
            return None
        new_board = copy.deepcopy(board)
        new_board[row][col] = player
        opponent = 3 - player
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.is_on_board(nr, nc) and new_board[nr][nc] == opponent:
                group = self.get_group(new_board, nr, nc)
                if not self.group_has_liberties(new_board, group):
                    for r, c in group:
                        new_board[r][c] = 0
        group = self.get_group(new_board, row, col)
        if not self.group_has_liberties(new_board, group):
            return None
        return new_board

    def is_on_board(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def get_group(self, board, row, col):
        color = board[row][col]
        group = set()
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if (r, c) in group:
                continue
            group.add((r, c))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if self.is_on_board(nr, nc) and board[nr][nc] == color and (nr, nc) not in group:
                    stack.append((nr, nc))
        return group

    def group_has_liberties(self, board, group):
        for r, c in group:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if self.is_on_board(nr, nc) and board[nr][nc] == 0:
                    return True
        return False

    def count_valid_moves(self, player):
        count = 0
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] == 0:
                    if self.simulate_move(self.board, r, c, player) is not None:
                        count += 1
        return count

    def count_territory(self):
        return self.count_territory_on_board(self.board)

    def count_territory_on_board(self, board):
        visited = set()
        black_territory = 0
        white_territory = 0
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board[r][c] == 0 and (r, c) not in visited:
                    group = set()
                    stack = [(r, c)]
                    while stack:
                        cell = stack.pop()
                        if cell in group:
                            continue
                        group.add(cell)
                        cr, cc = cell
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = cr + dr, cc + dc
                            if self.is_on_board(nr, nc):
                                if board[nr][nc] == 0 and (nr, nc) not in group:
                                    stack.append((nr, nc))
                    visited |= group
                    adjacent_colors = set()
                    for cell in group:
                        cr, cc = cell
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = cr + dr, cc + dc
                            if self.is_on_board(nr, nc) and board[nr][nc] != 0:
                                adjacent_colors.add(board[nr][nc])
                    if adjacent_colors == {1}:
                        black_territory += len(group)
                    elif adjacent_colors == {2}:
                        white_territory += len(group)
        return black_territory, white_territory

    def check_end_condition(self):
        all_stones = [cell for row in self.board for cell in row if cell != 0]
        if len(all_stones) > 1:
            if all(stone == all_stones[0] for stone in all_stones):
                winner = "Black" if all_stones[0] == 1 else "White"
                messagebox.showinfo("Game Over", f"All pieces are of one color. {winner} wins!")
                self.game_over = True
                self.canvas.unbind("<Button-1>")
                return
        if self.count_valid_moves(self.current_player) == 0:
            black_stones = sum(cell == 1 for row in self.board for cell in row)
            white_stones = sum(cell == 2 for row in self.board for cell in row)
            black_territory, white_territory = self.count_territory()
            black_score = black_stones + black_territory
            white_score = white_stones + white_territory
            if black_score > white_score:
                result = "Black wins!"
            elif white_score > black_score:
                result = "White wins!"
            else:
                result = "Draw!"
            messagebox.showinfo("Game Over", f"No valid moves left for the current player.\nBlack score: {black_score}\nWhite score: {white_score}\n{result}")
            self.game_over = True
            self.canvas.unbind("<Button-1>")

    def restart_game(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.history.clear()
        self.future.clear()
        self.game_over = False
        self.canvas.bind("<Button-1>", self.make_move)
        self.draw_board()

    def undo_move(self):
        if self.history and not self.game_over:
            self.future.append(copy.deepcopy(self.board))
            self.board = self.history.pop()
            self.current_player = 3 - self.current_player
            self.draw_board()

    def redo_move(self):
        if self.future and not self.game_over:
            self.history.append(copy.deepcopy(self.board))
            self.board = self.future.pop()
            self.current_player = 3 - self.current_player
            self.draw_board()

root = tk.Tk()
root.title("Go Game 5x5 with MCTS AI")
game = GoGame(root)
root.mainloop()
