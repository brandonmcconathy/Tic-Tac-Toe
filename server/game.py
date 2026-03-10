import json
import socket
import os
from abc import ABC, abstractmethod

from connectionerror import ConnectionError

class Game:

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
                print("Room Process: Horiontal win - %s" %last_symbol)
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
                print("Room Process: Vertical win - %s" %last_symbol)
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
                print("Room Process: Postive Diagonal win - %s" %last_symbol)
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
                print("Room Process: Negative Diagonal win - %s" %last_symbol)
                self.game_over = True
                return
            col_i += 1

        # Did not detect win
        self.game_over = False

    def take_turn(self):
        # Send message to players to tell them if it is their turn
        active_player_data = json.dumps({"is_active": True, "board": self.board}).encode()
        non_active_player_data = json.dumps({"is_active": False, "board": self.board}).encode()
        try:
            self.room.active_player.socket.send(active_player_data)
            self.room.non_active_player.socket.send(non_active_player_data)
        except BrokenPipeError:
            raise ConnectionError

        # Wait for acitve player to take turn
        turn_bytes = self.room.active_player.socket.recv(4096)
        if not turn_bytes:
            # Connection closed
            raise ConnectionError

        turn_data = json.loads(turn_bytes.decode())
        column = turn_data["column"]

        # Update board
        self.update_board(column, self.room.active_player.symbol)

        # Check for win
        self.check_win()

        # Send updated board to players
        active_board_data = json.dumps({"board": self.board, "game_over": self.game_over, "won": True}).encode()
        non_active_board_data = json.dumps({"board": self.board, "game_over": self.game_over, "won": False}).encode()
        self.room.non_active_player.socket.send(non_active_board_data)
        self.room.active_player.socket.send(active_board_data)

        self.room.update_active_player()
    
    def close_connections(self):
        print("Room Process: A client disconnected. Closing connection")
        try:
            self.room.player1.socket.shutdown(socket.SHUT_RDWR)
            self.room.player1.socket.close()
        except OSError:
            print("Room Process: Player 1 closed the connection already.")

        try:
            self.room.player2.socket.shutdown(socket.SHUT_RDWR)
            self.room.player2.socket.close()
        except OSError:
            print("Room Process: Player 2 closed the connection already.")
        
        print("Room Process: Room exiting")
        os._exit(0)

    def start_game(self):
        self.room.assign_players()
        while True:
            try:
                self.take_turn()
            except ConnectionError:
                self.close_connections()    # Process exits in here

            if self.game_over:
                self.close_connections()


class Multiplayer(Game):

    def __init__(self, room):
        super().__init__(room)

