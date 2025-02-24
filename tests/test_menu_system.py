import pytest
from cli.game.menu_system import MenuSystem, MenuOption
from cli.game.game_state import GameState, Resources, Colony
from cli.game.audio_service import AudioService, SoundEffect
from typing import List

class MockAudioService:
    def __init__(self):
        self.played_sounds: List[SoundEffect] = []
        self.narrations: List[str] = []
    
    def play_sound(self, effect: SoundEffect) -> None:
        self.played_sounds.append(effect)
    
    def play_narration(self, text: str) -> None:
        self.narrations.append(text)

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
    assert any("Selected" in narration for narration in audio.narrations)

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
