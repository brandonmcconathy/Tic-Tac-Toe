import random
import json

class Room:

    def __init__(self):
        self.players = []

    def get_num_players(self):
        return len(self.players)
    
    def add_player(self, player):
        self.players.append(player)

class SinglePlayerRoom():

    def __init__(self, player, difficulty):
        self.player = player
        self.difficulty = difficulty

    def add_player(self, player):
        self.player = player

    def get_difficulty(self):
        return self.difficulty

class MultiPlayerRoom():

    def __init__(self):
        self.players = []
        self.player1 = None
        self.player2 = None
        self.active_player = None
        self.non_active_player = None

    def get_num_players(self):
        return len(self.players)
    
    def get_player1(self):
        return self.player1
    
    def get_player2(self):
        return self.player2
    
    def get_active_player(self):
        return self.active_player
    
    def get_non_active_player(self):
        return self.non_active_player
    
    def set_player1(self, player):
        self.player1 = player
    
    def set_player2(self, player):
        self.player2 = player

    def set_active_player(self, player):
        self.active_player = player
    
    def set_non_active_player(self, player):
        self.non_active_player = player
    
    def add_player(self, player):
        self.players.append(player)

    def assign_players(self):
        # Randomly assign players a player number
        first_player = random.randint(0, 1)
        self.player1 = self.players[first_player]
        self.player2 = self.players[0 if first_player else 1]

        # Assign symbols to players
        self.player1.symbol = 'X'
        self.player2.symbol = 'O'

        # Set player 1 as active
        self.active_player = self.player1
        self.non_active_player = self.player2

        # Send player 1 their player number
        player1_data = json.dumps({"player_num": 1, "is_active": True}).encode()
        self.player1.socket.send(player1_data)

        # Send player 2 their player number
        player2_data = json.dumps({"player_num": 2, "is_active": False}).encode()
        self.player2.socket.send(player2_data)

    def update_active_player(self):
        temp = self.active_player
        self.active_player = self.non_active_player
        self.non_active_player = temp

