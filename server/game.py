import time

class Game:

    def __init__(self, room):
        self.room = room

    def start_game(self):
        done = False
        print(self.room)
        while self.room.get_num_players() < 2:
            print(self.room)
            print("waiting for second player")
            time.sleep(1)

