import json
import socket
import os

from game import Game
from connectionerror import ConnectionError

class Multiplayer(Game):

    def __init__(self, room):
        super().__init__(room)

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
    
    def start_game(self):
        self.room.assign_players()
        while True:
            try:
                self.take_turn()
            except ConnectionError:
                self.close_connections()    # Process exits in here

            if self.game_over:
                self.close_connections()    # Process exits in here

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

