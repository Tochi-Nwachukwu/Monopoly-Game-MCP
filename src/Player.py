class Player:
    def __init__(self, player_name, id) -> None:
        self.player_name = player_name
        self.player_id = id
        self.board_position = 0
        self.player_money = 0
        self.player_avatar = "/src/data/images/bulb.svg"

    def add_player_money(self, amount):
        self.player_money += amount

    def subtract_player_money(self, amount):
        self.player_money -= amount

    def update_player_board_position(self, pos):
        self.board_position = pos

    def get_player_position(self):
        return self.board_position

    def get_player_details(self):
        return {
            "player_name": self.player_name,
            "player_id": self.player_id,
            "board_position": self.board_position,
            "player_money": self.player_money,
            "player_avatar": self.player_avatar,
        }
