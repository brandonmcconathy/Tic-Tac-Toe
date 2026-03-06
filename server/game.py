import json
import random

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
        self.active_player.socket.send(active_player_data)
        self.non_active_player.socket.send(non_active_player_data)

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
        self.player1.socket.close()
        self.player2.socket.close()

    def start_game(self):
        self.assign_players()
        while True:
            if not self.take_turn():
                self.close_connections()
                break
            if self.check_win():
                break
            self.update_active_player()

