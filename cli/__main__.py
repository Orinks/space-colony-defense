#!/usr/bin/env python3
import sys
from typing import Optional
from cli.game.game_loop import GameLoop
from cli.game.audio_service import AudioService


def main() -> None:
    """
    Main entry point for the Space Colony Defense game.
    """
    # Check if we should use text mode (pygame is now default)
    use_text_mode = "--text" in sys.argv
    
    # Check for specific voice settings
    voice_index = None
    speech_rate = 50  # Default speech rate (0-100)
    
    for i, arg in enumerate(sys.argv):
        if arg == "--voice" and i+1 < len(sys.argv):
            try:
                voice_index = int(sys.argv[i+1])
            except ValueError:
                print(f"Invalid voice index: {sys.argv[i+1]}")
        elif arg == "--rate" and i+1 < len(sys.argv):
            try:
                speech_rate = int(sys.argv[i+1])
                speech_rate = max(0, min(100, speech_rate))  # Clamp to 0-100
            except ValueError:
                print(f"Invalid speech rate: {sys.argv[i+1]}")
    
    if not use_text_mode:
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
            run_text_mode(voice_index, speech_rate)
    else:
        run_text_mode(voice_index, speech_rate)


def run_text_mode(voice_index: Optional[int] = None, speech_rate: int = 50) -> None:
    """Run the game in text-only mode"""
    # Initialize audio service
    audio = AudioService()
    
    # Set speech rate if SRAL is available
    if audio.sral:
        try:
            audio.set_speech_rate(speech_rate)
            
            # Set specific voice if requested and available
            if voice_index is not None:
                try:
                    # Try to get available voices
                    if hasattr(audio.sral, 'get_voice_count') and hasattr(audio.sral, 'set_voice'):
                        voice_count = audio.sral.get_voice_count()
                        if 0 <= voice_index < voice_count:
                            audio.sral.set_voice(voice_index)
                            print(f"Using voice index: {voice_index}")
                        else:
                            print(f"Voice index {voice_index} not available")
                except Exception as e:
                    print(f"Error setting voice: {e}")
        except Exception as e:
            print(f"Error setting speech rate: {e}")
    
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
