#!/usr/bin/env python3
import sys
from cli.game.game_loop import GameLoop
from cli.game.audio_service import AudioService


def main() -> None:
    """
    Main entry point for the Space Colony Defense game.
    """
    # Check if we should use Pygame or text mode
    use_pygame = "--pygame" in sys.argv
    
    # Check for specific voice settings
    voice_index = None
    for i, arg in enumerate(sys.argv):
        if arg == "--voice" and i+1 < len(sys.argv):
            try:
                voice_index = int(sys.argv[i+1])
            except ValueError:
                print(f"Invalid voice index: {sys.argv[i+1]}")
    
    if use_pygame:
        try:
            from cli.game.pygame_interface import PygameInterface, PygameAudioService
            
            # Start the Pygame interface
            pygame_interface = PygameInterface()
            
            # Set specific voice if requested
            if voice_index is not None and isinstance(pygame_interface.audio, PygameAudioService):
                if pygame_interface.audio.set_voice_by_index(voice_index):
                    print(f"Using voice index: {voice_index}")
            
            pygame_interface.run()
        except ImportError:
            print("Pygame not installed. Running in text mode instead.")
            run_text_mode()
    else:
        run_text_mode()


def run_text_mode() -> None:
    """Run the game in text-only mode"""
    # Initialize audio service
    audio = AudioService()
    
    # Initialize game loop
    game = GameLoop(audio_service=audio)
    
    # Simple text-based game loop
    print("\nWelcome to Space Colony Defense!")
    print("\nMAIN MENU")
    print("Commands: [up, down, select, quit]")
    print("Game commands: [left, right, shoot, status, menu, repair, end_management, quit]")
    
    running = True
    while running:
        command = input("\nEnter command: ").strip().lower()
        
        if command == "quit":
            print("Thanks for playing!")
            break
        
        # Process input
        running = game.handle_input(command)
        
        # Update game state
        game.update()
        
        # Check for game over
        if game.is_game_over:
            print("\nGame Over! Options: [restart, menu, quit]")


if __name__ == "__main__":
    main()
