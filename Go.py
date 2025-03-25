import tkinter as tk
import copy

class GoGame:
    def __init__(self, root):
        self.root = root
        self.board_size = 7
        self.cell_size = 60
        self.canvas_size = self.board_size * self.cell_size
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="burlywood")
        self.canvas.pack()
        
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.history = []  # Stores previous board states for undo/redo
        self.future = []   # Stores redo states if undo is done
        
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
        row, col = self.get_cell(event.x, event.y)
        new_board = self.simulate_move(self.board, row, col, self.current_player)
        
        if new_board is not None:
            self.history.append(copy.deepcopy(self.board))
            self.board = new_board
            self.future.clear()  # Clear redo history after a new move
            self.current_player = 3 - self.current_player
            self.draw_board()

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

    def restart_game(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.history.clear()
        self.future.clear()
        self.draw_board()

    def undo_move(self):
        if self.history:
            self.future.append(copy.deepcopy(self.board))
            self.board = self.history.pop()
            self.current_player = 3 - self.current_player
            self.draw_board()

    def redo_move(self):
        if self.future:
            self.history.append(copy.deepcopy(self.board))
            self.board = self.future.pop()
            self.current_player = 3 - self.current_player
            self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Go Game 7x7")
    game = GoGame(root)
    root.mainloop()
