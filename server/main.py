import socket
import json
import os
import signal
import time

from game import Game

class Player:

    def __init__(self, player_socket):
        self.player_socket = player_socket


class Room:

    def __init__(self):
        self.players = []
        self.pid = 0

    def get_num_players(self):
        return len(self.players)
    
    def add_player(self, player):
        self.players.append(player)

    def set_pid(self, pid):
        self.pid = pid

    def kill_room(self):
        os.kill(self.pid, signal.SIGKILL)


def put_new_connection_in_room(rooms, new_socket):
    # Make new player
    player = Player(new_socket)

    # Add player to existing room
    for room in rooms:
        if room.get_num_players() < 2:
            room.add_player(player)
            
            # Start room process
            newpid = os.fork()
            if newpid == 0:
                # Move process to game loop
                new_game = Game(room)
                new_game.start_game
                os._exit(0)
            room.set_pid(newpid)
            return
    
    # Make new room
    new_room = make_new_room()
    new_room.add_player(player)
    rooms.append(new_room)

        
def make_new_room():
    new_room = Room()
    return new_room


def reap_children(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
        except OSError:
            break

def clean_up_rooms(rooms):
    for i, room in enumerate(rooms):
        if room.get_num_players() == 0:
            room.kill_room()            # Kills room process
            rooms.pop(i)

def print_rooms_status(rooms):
    print("%d Rooms" %len(rooms))
    for i, room in enumerate(rooms):
        print("Room %d: %d players" %(i, room.get_num_players()), end=' ')
    print()

if __name__ == "__main__":
    port = 50000       # Random port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)

    rooms = []

    # Removes zombie processes
    signal.signal(signal.SIGCHLD, reap_children)

    while True:
        print_rooms_status(rooms)
        connection, address = server_socket.accept()

        # Removes empty rooms
        if len(rooms) > 5:
            clean_up_rooms(rooms)

        # Add new player to a room
        put_new_connection_in_room(rooms, connection)
