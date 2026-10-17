"""Game entry point."""

from src.game.game import Game


def main() -> None:
    """Instantiate and run the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
