# from src import Tiles
from src.game import GameState


def main():
    print("Hello from monopoly-game-mcp!")
    game = GameState(2)
    game.initialize_game()


if __name__ == "__main__":
    main()
