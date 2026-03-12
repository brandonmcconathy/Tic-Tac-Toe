import os

from game import Game

class Singleplayer(Game):

    def __init__(self, room):
        super().__init__(room)

    def take_turn(self):
        return super().take_turn()
    
    def start_game(self):
        return super().start_game()