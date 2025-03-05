#!/usr/bin/env python3
import sys
from cli.game.pygame_interface import PygameInterface


def main() -> None:
    """
    Main entry point for the Space Colony Defense game.
    """
    try:
        # Start the Pygame interface
        pygame_interface = PygameInterface()
        pygame_interface.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
