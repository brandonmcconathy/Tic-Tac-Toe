import socket
import json
import os
import time

class Player:

    def __init__(self, player_socket):
        self.player_socket = player_socket

class Room:

    def __init__(self):
        self.players = []

    def get_num_players(self):
        return len(self.players)
    
    def add_player(self, player):
        self.players.append(player)


def put_new_connection_in_room(rooms, new_socket):
    # Add player to a room with space
    for room in rooms:
        if room.get_num_players() < 2:
            room.add_player(new_socket)
            return
    
    # Make new room
    new_room = make_new_room()
    new_room.add_player(new_socket)
    rooms.append(new_room)
    return

        
def make_new_room():
    new_room = Room()
    newpid = os.fork()
    if newpid == 0:
        # Move room process to game loop
        os._exit(0)
    return new_room

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

    while True:
        print_rooms_status(rooms)
        connection, address = server_socket.accept()

        # Add new player to a room
        put_new_connection_in_room(rooms, connection)
