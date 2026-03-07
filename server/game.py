import json
import random
import socket
import os

class Game:

    def __init__(self, room):
        self.room = room
        self.player1 = None
        self.player2 = None
        self.active_player = None
        self.non_active_player = None
        self.last_move = None
        self.board = [[' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' '],
                      [' ',' ',' ',' ',' ',' ',' ']]
        
    def update_board(self, column):
        # Updates lowest empty row in given column
        row_to_update = 0
        for i, row in enumerate(self.board):
            if row[column] == ' ':
                row_to_update = i
        self.board[row_to_update][column] = self.active_player.symbol
        self.last_move = (row_to_update, column)

    def check_win(self):
        row = self.last_move[0]
        col = self.last_move[1]
        last_symbol = self.active_player.symbol

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
                return True

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
                return True

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
                return True
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
                return True
            col_i += 1

        # Did not detect win
        return False

    def update_active_player(self):
        temp = self.active_player
        self.active_player = self.non_active_player
        self.non_active_player = temp

    def assign_players(self):
        # Randomly assign players a player number
        first_player = random.randint(0, 1)
        self.player1 = self.room.players[first_player]
        self.player2 = self.room.players[0 if first_player else 1]

        # Assign symbols to players
        self.player1.symbol = 'X'
        self.player2.symbol = 'O'

        # Set player 1 as active
        self.active_player = self.player1
        self.non_active_player = self.player2

        # Send player 1 their player number
        player1_data = json.dumps({"player_num": 1}).encode()
        self.player1.socket.send(player1_data)

        # Send player 2 their player number
        player2_data = json.dumps({"player_num": 2}).encode()
        self.player2.socket.send(player2_data)

    def take_turn(self):
        # Send message to players to tell them if it is their turn
        active_player_data = json.dumps({"is_active": True, "board": self.board}).encode()
        non_active_player_data = json.dumps({"is_active": False, "board": self.board}).encode()
        try:
            self.active_player.socket.send(active_player_data)
            self.non_active_player.socket.send(non_active_player_data)
        except BrokenPipeError:
            self.close_connections()

        # Wait for acitve player to take turn
        turn_bytes = self.active_player.socket.recv(2048)
        if not turn_bytes:
            # Connection closed
            return False

        turn_data = json.loads(turn_bytes.decode())
        column = turn_data["column"]

        # Update board
        self.update_board(column)

        # Send updated board to players
        board_data = json.dumps({"board": self.board}).encode()
        self.non_active_player.socket.send(board_data)
        self.active_player.socket.send(board_data)

        # Successful turn
        return True
    
    def close_connections(self):
        print("Room Process: A client disconnected. Closing connection")
        try:
            self.player1.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            try:
                self.player2.socket.shutdown(socket.SHUT_RDWR)

            except OSError:
                print("Room Process: Room exiting after 2 errors")
                os._exit(0)
        self.player1.socket.close()

        try:
            self.player2.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            print("Room Process: Room exiting after 1 error")
            os._exit(0)
        
        self.player2.socket.close()
        print("Room Process: Room exiting")
        os._exit(0)

    def start_game(self):
        self.assign_players()
        while True:
            if not self.take_turn():
                self.close_connections()
                break
            if self.check_win():
                break
            self.update_active_player()

