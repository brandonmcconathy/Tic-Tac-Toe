from abc import ABC, abstractmethod

class Game(ABC):

    def __init__(self, room):
        self.room = room
        self.last_move = None
        self.game_over = False
        self.board = [[' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' ']]
        
    def update_board(self, column, symbol):
        # Updates lowest empty row in given column
        row_to_update = 0
        for i, row in enumerate(self.board):
            if row[column] == ' ':
                row_to_update = i
        self.board[row_to_update][column] = symbol
        self.last_move = (row_to_update, column)

    def check_win(self):
        row = self.last_move[0]
        col = self.last_move[1]
        last_symbol = self.board[row][col]

        # Check horizontal
        left_bound = max(0, col - 3)
        for i in range(left_bound, col + 1):
            win = True
            for j in range(4):
                if j + i < 7:
                    if self.board[row][j + i] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return

        # Check Vertical
        top_bound = max(0, row - 3)
        for i in range(top_bound, row + 1):
            win = True
            for j in range(4):
                if j + i < 6:
                    if self.board[j + i][col] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return

        # Check Positive Diagonal
        min_row = row
        min_col = col
        for i in range(3):
            if min_row != 5 and min_col != 0:
                min_row += 1
                min_col -= 1

        col_i = min_col
        for row_i in range(min_row, row, -1):
            win = True
            for i in range(4):
                if row_i - i >= 0 and col_i + i < 7:
                    if self.board[row_i - i][col_i + i] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return
            col_i += 1

        # Check Negative Diagonal
        min_row = row
        min_col = col
        for i in range(3):
            if min_row != 0 and min_col != 0:
                min_row -= 1
                min_col -= 1

        col_i = min_col
        for row_i in range(min_row, row):
            win = True
            for i in range(4):
                if row_i + i < 6 and col_i + i < 7:
                    if self.board[row_i + i][col_i + i] != last_symbol:
                        win = False
                else:
                    # Index out of range
                    win = False
            if win:
                self.game_over = True
                return
            col_i += 1

        # Did not detect win
        self.game_over = False

    @abstractmethod
    def take_turn(self):
        pass

    @abstractmethod
    def start_game(self):
        pass
