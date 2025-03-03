import pytest
from cli.game.menu_system import MenuSystem, MenuOption, MainMenuOption, OptionsMenuOption
from cli.game.game_state import GameState, Resources, Colony
from cli.game.audio_service import AudioService, SoundEffect
from typing import List

class MockAudioService:
    def __init__(self):
        self.played_sounds: List[SoundEffect] = []
        self.narrations: List[str] = []
        self.enable_sounds = True
        self.enable_narration = True
    
    def play_sound(self, effect: SoundEffect) -> None:
        self.played_sounds.append(effect)
    
    def play_narration(self, text: str) -> None:
        self.narrations.append(text)
        
    def toggle_sounds(self, enable: bool = None) -> None:
        if enable is not None:
            self.enable_sounds = enable
        else:
            self.enable_sounds = not self.enable_sounds
            
    def toggle_narration(self, enable: bool = None) -> None:
        if enable is not None:
            self.enable_narration = enable
        else:
            self.enable_narration = not self.enable_narration

def test_menu_navigation():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    
    # Act
    menu.navigate_down()
    
    # Assert
    assert SoundEffect.MENU_NAV in audio.played_sounds
    assert len(audio.narrations) > 0
    assert any(option_name.lower() in narration.lower() for option_name in [option.name.lower() for option in MenuOption] for narration in audio.narrations)

def test_status_query():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=80, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    
    # Act
    menu.query_status()
    
    # Assert
    assert any("Colony health: 80" in narration for narration in audio.narrations)
    assert any("50 energy" in narration for narration in audio.narrations)

def test_repair_colony_from_menu():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=50, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    
    # Act - Navigate to repair option and select it
    while menu.options[menu.current_index] != MenuOption.REPAIR:
        menu.navigate_down()
    menu.select_current_option()
    
    # Assert
    assert game_state.colony.hp == 100
    assert game_state.resources.metal == 10  # Cost 20 metal
    assert SoundEffect.ACTION_SUCCESS in audio.played_sounds

def test_show_main_menu():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    
    # Act
    menu.show_main_menu()
    
    # Assert
    assert menu.current_menu == "main"
    assert menu.current_index == 0
    assert any("Main Menu" in narration for narration in audio.narrations)

def test_main_menu_navigation():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    menu.show_main_menu()
    
    # Act
    menu.navigate_down()  # Should move to LOAD_GAME
    
    # Assert
    assert SoundEffect.MENU_NAV in audio.played_sounds
    assert menu.main_menu_options[menu.current_index] == MainMenuOption.LOAD_GAME
    assert any("load game" in narration.lower() for narration in audio.narrations)

def test_main_menu_select_new_game():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    menu.show_main_menu()
    
    # Make sure we're on NEW_GAME option
    while menu.main_menu_options[menu.current_index] != MainMenuOption.NEW_GAME:
        menu.navigate_down()
    
    # Act
    result = menu.select_current_option()
    
    # Assert
    assert result == "new_game"
    assert menu.current_menu == "game"
    assert SoundEffect.ACTION_SUCCESS in audio.played_sounds
    assert any("Starting new game" in narration for narration in audio.narrations)

def test_main_menu_select_options():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    menu.show_main_menu()
    
    # Navigate to OPTIONS
    while menu.main_menu_options[menu.current_index] != MainMenuOption.OPTIONS:
        menu.navigate_down()
    
    # Act
    result = menu.select_current_option()
    
    # Assert
    assert result is None  # No special result needed
    assert menu.current_menu == "options"
    assert menu.current_index == 0
    assert SoundEffect.MENU_NAV in audio.played_sounds
    assert any("Options menu" in narration for narration in audio.narrations)

def test_options_menu_sound_toggle():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    menu.show_main_menu()
    
    # Navigate to OPTIONS and select
    while menu.main_menu_options[menu.current_index] != MainMenuOption.OPTIONS:
        menu.navigate_down()
    menu.select_current_option()
    
    # Make sure we're on SOUND_TOGGLE
    while menu.options_menu_options[menu.current_index] != OptionsMenuOption.SOUND_TOGGLE:
        menu.navigate_down()
    
    # Act
    initial_sound_state = audio.enable_sounds
    menu.select_current_option()
    
    # Assert
    assert audio.enable_sounds != initial_sound_state
    assert any(("enabled" in narration or "disabled" in narration) 
               for narration in audio.narrations)

def test_options_menu_back_to_main():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    menu.show_main_menu()
    
    # Navigate to OPTIONS and select
    while menu.main_menu_options[menu.current_index] != MainMenuOption.OPTIONS:
        menu.navigate_down()
    menu.select_current_option()
    
    # Navigate to BACK
    while menu.options_menu_options[menu.current_index] != OptionsMenuOption.BACK:
        menu.navigate_down()
    
    # Act
    menu.select_current_option()
    
    # Assert
    assert menu.current_menu == "main"
    assert menu.current_index == 0
    assert SoundEffect.MENU_NAV in audio.played_sounds
    assert any("Returning to main menu" in narration for narration in audio.narrations)

def test_difficulty_settings():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    menu.show_main_menu()
    
    # Navigate to OPTIONS and select
    while menu.main_menu_options[menu.current_index] != MainMenuOption.OPTIONS:
        menu.navigate_down()
    menu.select_current_option()
    
    # Navigate to DIFFICULTY
    while menu.options_menu_options[menu.current_index] != OptionsMenuOption.DIFFICULTY:
        menu.navigate_down()
    
    # Act - cycle through difficulties
    initial_difficulty = menu.get_difficulty()
    menu.select_current_option()  # First change
    first_change = menu.get_difficulty()
    menu.select_current_option()  # Second change
    second_change = menu.get_difficulty()
    
    # Assert
    assert initial_difficulty != first_change
    assert first_change != second_change
    assert any("Difficulty set to" in narration for narration in audio.narrations)
    assert all(diff in [1, 2, 3] for diff in [initial_difficulty, first_change, second_change])
