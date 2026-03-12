import socket
import os
import signal
import json

from multiplayer import Multiplayer
from singleplayer import Singleplayer
from room import MultiPlayerRoom, SinglePlayerRoom
from connectionerror import ConnectionError

class Player:

    def __init__(self, socket):
        self.socket = socket
        self.symbol = ''


class Server:

    def __init__(self):
        self.port = 50000       # Random port
        self.socket = None
        self.curr_room = MultiPlayerRoom()

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(5)
        print("Server Started. Listening for connections on port %d." %self.port)

        # Sets up signal to remove zombie processes
        signal.signal(signal.SIGCHLD, self.reap_children)

    def accept_new_connection(self):
        connection, address = self.socket.accept()
        print("New connection: ", address)

        # Gets if the player wants to play against another player or ai
        opponent_bytes = connection.recv(4096)
        if not opponent_bytes:
            # Connection closed
            raise ConnectionError
        opponent_data = json.loads(opponent_bytes.decode())
        
        play_player = opponent_data["play_player"]
        difficulty = opponent_data["difficulty"]
        self.put_new_connection_in_room(connection, play_player, difficulty)

    def put_new_connection_in_room(self, new_socket, play_player, difficulty):
        # Make new player
        player = Player(new_socket)

        if not play_player:
            new_room = SinglePlayerRoom(player)

            # Start room process
            newpid = os.fork()
            if newpid == 0:
                # Move process to game loop
                new_game = Singleplayer(new_room)
                new_game.start_game()   # Room process will exit and never return here
            
            print("Starting new singleplayer room process with pid: ", newpid)
            return

        # Add player to empty room
        if self.curr_room.get_num_players() == 0:
            self.curr_room.add_player(player)
            return

        # Add player to room with player in it already
        if self.curr_room.get_num_players() == 1:
            self.curr_room.add_player(player)
            
            # Start room process
            newpid = os.fork()
            if newpid == 0:
                # Move process to game loop
                new_game = Multiplayer(self.curr_room)
                new_game.start_game()   # Room process will exit and never return here

            print("Starting new room process with pid: ", newpid)
            return
        
        # curr_room is full. Add player to new room
        new_room = MultiPlayerRoom()
        new_room.add_player(player)
        self.curr_room = new_room

    def reap_children(self, signum, frame):
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
            except OSError:
                break


if __name__ == "__main__":
    server = Server()
    server.start_server()
    while True:
        try:
            server.accept_new_connection()
        except ConnectionError:
            pass
