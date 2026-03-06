import socket
import json

from game import Game

class Client:

    def __init__(self):
        self.server_host = "localhost"
        self.server_port = 50003
        self.socket = None
        self.player_num = None
        self.game = Game()

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

    def get_player_num(self):
        data = self.socket.recv(1024)
        json_data = json.loads(data.decode())
        self.player_num = json_data["player_num"]
        print("You are player %d" %self.player_num)
        print("You will have the symbol %s" %('X' if self.player_num == 1 else 'O'))

    def validate_column(self, column):
        if not column.isdigit():
            return False
        column = int(column)
        if column < 1 or column > 7:
            return False
        return True

    def take_turn(self):
        turn_bytes = self.socket.recv(1024)
        turn_data = json.loads(turn_bytes.decode())
        self.game.board = turn_data["board"]
        if turn_data["is_active"]:
            # Make move
            print("It's your turn!")
            column = input("Enter a column number from 1-7: ")

            # Validate input
            while not self.validate_column(column):
                print("Invalid Input")
                column = input("Enter a column number from 1-7: ")
            column = int(column) - 1                    # -1 because board is 0-indexed
            column_data = json.dumps({"column": column}).encode()
            self.socket.send(column_data)

        else:
            print("Please wait for the other player to make their move.")

        # Wait for updated board
        board_bytes = self.socket.recv(2048)
        board_data = json.loads(board_bytes.decode())
        self.game.board = board_data["board"]
        self.print_board()


    def print_board(self):
        print("---------------")
        for row in self.game.board:
            print('|', end="")
            for col in row:
                print(col, end="|")
            
            print("\n---------------")

if __name__ == "__main__":
    client = Client()
    client.connect_to_server()
    client.get_player_num()
    client.print_board()
    while True:
        client.take_turn()