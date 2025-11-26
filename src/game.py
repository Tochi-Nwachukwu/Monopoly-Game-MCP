import json
from src import Tiles
from src.Bank import Bank
from src.Logger import Logger
from src.Player import Player
from src.constants import land_tiles, railroad_tiles
from src.roll_dice import roll_dice


class GameState:
    def __init__(self, players) -> None:
        self.players = []
        self.player_turn = 0
        self.no_of_players = len(self.players)
        self.status = "INITILIZING"
        self.logger = Logger()
        self.game_tiles = []

    def update_player_turn():
        pass
        # This function knows the maximum number of players and switches to the next players

    def get_stats(self):
        game_stats = {
            "status": self.status,
            "players": self.players,
            "no_of_players": self.no_of_players,
            "player_turn": self.player_turn,
            "bank": self.bank.get_bank_balance(),
        }

        print(game_stats)
        return game_stats

    def register_players(self):
        pass
        # this function will check to see the available ids in the pull, and assign player ids based on the player.

        player1 = Player("ChatGPT", 1)
        player2 = Player("Claude", 2)
        player1.add_player_money(1500)
        player2.add_player_money(1500)
        self.players.append(player1)
        self.players.append(player2)

    def initialize_game(self):
        component = "INITIALIZE_GAME"
        self.populate_tiles()
        self.register_players()
        self.bank = Bank()
        self.logger.log(component, "INITIALIZED GAME -- READY TO PLAY")

    def move_player(self, player_obj):
        component = "MOVE_PLAYER"
        dice_value = roll_dice()
        steps = dice_value["dice1"] + dice_value["dice2"]
        current_player_pos = player_obj.get_player_position()
        new_pos = current_player_pos + steps

        if new_pos >= 40:
            new_pos -= 40
        player_obj.update_player_board_position(new_pos)

        self.logger.log(component, json.dumps(player_obj.get_player_details()))

    def populate_tiles(self):
        component = "INITIALIZE TILES"
        self.generate_tiles(land_tiles, "street")
        self.generate_tiles(railroad_tiles, "railroad")
        self.logger.log(
            component,
            f"Successfully Initilized Tiles -  {len(self.game_tiles)} tiles ",
        )

    def generate_tiles(self, tile_list, type):
        # Map tile types to their respective classes
        tile_classes = {"street": Tiles.Land, "railroad": Tiles.Railroad}

        if type not in tile_classes:
            raise ValueError(f"Unknown tile type: {type}")

        initial_count = len(self.game_tiles)
        tile_class = tile_classes[type]

        # Create all tiles
        for id in tile_list:
            self.game_tiles.append(tile_class(id))

        tiles_added = len(self.game_tiles) - initial_count

        # Log once after all tiles are created
        self.logger.log(
            type,
            f"Successfully Initialized {type} Tiles - Added {tiles_added} tiles (Total: {len(self.game_tiles)})",
        )

    def get_players(self):
        return self.players

    def run_tile_action(self):
        pass

    def manage_turns(self):
        # This function manages the turns of the players
        if self.player_turn == 0:
            Logger.log("Manage Turns", "Moving player 1")
            player1 = self.players[0]
            self.move_player(player1)
            details = player1.get_player_details()
            
            print(details)
            Logger.log("Manage Turns", "Successfully moved player")
