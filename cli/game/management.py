from typing import Optional
from cli.game.game_state import GameState
from cli.game.audio_service import AudioService, SoundEffect


def management_menu(
    game_state: GameState, audio: AudioService, test_input: Optional[str] = None
) -> None:
    """
    Display and handle the management menu with integrated audio feedback.

    Args:
        game_state: Current game state
        audio: Audio service for accessibility
        test_input: Optional input for testing purposes
    """
    # Announce current state
    state_announcement = (
        f"Colony HP: {game_state.colony.hp}, "
        f"Energy: {game_state.resources.energy}, "
        f"Metal: {game_state.resources.metal}, "
        f"Food: {game_state.resources.food}"
    )
    audio.play_narration(state_announcement)

    # Present options
    audio.play_narration("Available actions:")
    audio.play_narration("1: Repair Colony - 20 metal")
    audio.play_narration("2: Build Structure")
    audio.play_narration("3: Craft Special Weapon")

    # Handle input (simulated for testing)
    if test_input == "1":
        if game_state.colony.repair(game_state.resources):
            audio.play_sound(SoundEffect.ACTION_SUCCESS)
            audio.play_narration("Colony repaired")
        else:
            audio.play_sound(SoundEffect.ACTION_FAIL)
            audio.play_narration("Not enough metal")
    elif test_input == "down":
        audio.play_sound(SoundEffect.MENU_NAV)
        audio.play_narration("Build Structure")
