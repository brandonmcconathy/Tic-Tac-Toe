import os
import json
import random
import socket

from game import Game
from ai import AI

class Singleplayer(Game):

    def __init__(self, room):
        super().__init__(room)
        self.player_active = None
        self.ai = AI(self.room.get_difficulty())

    def assign_player_num(self):
        player_num = random.randint(0, 1)
        self.player_active = True if player_num else False
        self.room.player.symbol = 'X' if player_num else 'O'
        self.ai.symbol = 'O' if player_num else 'X'
        player_data = json.dumps({"player_num": player_num + 1, "is_active": self.player_active}).encode()
        self.room.player.socket.send(player_data)

    def take_turn(self):
        active_symbol = None
        if self.player_active:
            # Wait for acitve player to take turn
            turn_bytes = self.room.player.socket.recv(4096)
            if not turn_bytes:
                # Connection closed
                raise ConnectionError
            turn_data = json.loads(turn_bytes.decode())
            column = turn_data["column"]
            active_symbol = self.room.player.symbol
            
        else:
            # Take AI turn
            column = self.ai.take_turn(self.board)
            active_symbol = self.ai.symbol

        # Update the board with the new move
        self.update_board(column, active_symbol)

        # Check for a win
        self.check_win()

        # Send updated board to player
        player_data = json.dumps({"board": self.board, "game_over": self.game_over, "won": self.player_active}).encode()
        self.room.player.socket.send(player_data)

        self.update_active_player()

    def update_active_player(self):
        self.player_active = not self.player_active

    def close_connection(self):
        print("Room Process: Closing connection")
        try:
            self.room.player.socket.shutdown(socket.SHUT_RDWR)
            self.room.player.socket.close()
        except OSError:
            print("Room Process: Player 1 closed the connection already.")

        os._exit(0)
    
    def start_game(self):
        self.assign_player_num()
        while True:
            try:
                self.take_turn()
            except ConnectionError:
                self.close_connection()

            if self.game_over:
                self.close_connection()