from google import genai

class AI:

    def __init__(self, difficulty):
        self.symbol = None
        self.difficulty = difficulty
        self.ai_client = genai.Client()

    def take_turn(self, board):
        prompt = f"You are a {self.difficulty} computer opponent in a connect 4 game." \
            "Respond in 1 integer between the values of 1 and 7 including " \
            "both endpoints. The integer is the value of the column that " \
            "you want to play in. This is the current state of the board " \
            "where each array inside the main array is a row of the " \
            "connect 4 game and each entry in the arrays are the columns." \
            f"{board}"
        response = self.ai_client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        return int(response.text)