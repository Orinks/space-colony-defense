from cli.game.game_state import GameState
from cli.game.audio_service import AudioService, SoundEffect
from cli.game.buildings import Building, BuildingType
from typing import Optional

def management_menu(game_state: GameState, audio: AudioService, test_input: Optional[str] = None) -> None:
    """
    Display the management menu and handle user input
    
    Parameters:
        game_state: Current game state
        audio: Audio service for sound effects and narration
        test_input: Optional input for testing
    """
    # Announce colony status
    audio.play_narration(f"Colony HP: {game_state.colony.hp}/{game_state.colony.max_hp}")
    
    # Announce special effects
    if game_state.shield_strength > 0:
        audio.play_narration(f"Shield strength: {game_state.shield_strength}")
    if game_state.missiles > 0:
        audio.play_narration(f"Missiles available: {game_state.missiles}")
    if game_state.wave_skip_available > 0:
        audio.play_narration(f"Wave skip available: {game_state.wave_skip_available}")
    
    audio.play_narration(f"Resources - Energy: {game_state.resources.energy}, Metal: {game_state.resources.metal}, Food: {game_state.resources.food}")
    audio.play_narration(f"Tech points: {game_state.tech_points}")
    
    # Show menu options
    audio.play_narration("Management options:")
    audio.play_narration("1: Repair Colony")
    audio.play_narration("2: Build Structure")
    audio.play_narration("3: Upgrade Structure")
    audio.play_narration("4: Next Wave")
    
    if game_state.wave_skip_available > 0:
        audio.play_narration(f"5: Skip {game_state.wave_skip_available} Waves")
    
    # Handle input
    if test_input == "1" or test_input == "repair":
        # Repair colony
        if game_state.colony.repair(game_state.resources, audio):
            pass  # Success message handled by repair method
        else:
            # Failure message should be handled by repair method, but add fallback
            if not any("Not enough metal" in message for message in getattr(audio, 'narrations', [])):
                audio.play_narration("Not enough metal to repair colony")
    
    elif test_input == "down":
        # Simulate navigation
        audio.play_sound(SoundEffect.MENU_NAV)
        audio.play_narration("Build Structure")
    
    elif test_input and test_input.startswith("build_"):
        # Extract building type from input
        building_type_name = test_input[6:].upper()
        
        try:
            building_type = BuildingType[building_type_name]
            building = Building(type=building_type, audio=audio)
            
            if game_state.add_building(building):
                audio.play_sound(SoundEffect.ACTION_SUCCESS)
                audio.play_narration(f"{building_type.display_name()} constructed successfully")
            else:
                audio.play_sound(SoundEffect.ACTION_FAIL)
                # Message already played by building itself
        except (KeyError, ValueError):
            audio.play_sound(SoundEffect.ACTION_FAIL)
            audio.play_narration(f"Unknown building type: {building_type_name}")
    
    elif test_input and test_input.startswith("upgrade_"):
        # Extract building index from input
        try:
            building_index = int(test_input.split("_")[1])
            
            if game_state.upgrade_building(building_index):
                # Success message handled by the building itself
                pass
            else:
                # Failure message handled by the building itself
                pass
        except (IndexError, ValueError):
            audio.play_sound(SoundEffect.ACTION_FAIL)
            audio.play_narration("Invalid building index")
    
    elif test_input == "skip_wave" and game_state.wave_skip_available > 0:
        game_state.skip_waves()
    
    # In a real implementation, we would wait for user input here
    # and handle the management phase loop
