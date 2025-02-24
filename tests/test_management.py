import pytest
from typing import List
from cli.game.management import management_menu
from cli.game.game_state import GameState, Resources, Colony
from cli.game.audio_service import AudioService, SoundEffect

class MockAudioService:
    def __init__(self):
        self.played_sounds: List[SoundEffect] = []
        self.narrations: List[str] = []
    
    def play_sound(self, effect: SoundEffect) -> None:
        self.played_sounds.append(effect)
    
    def play_narration(self, text: str) -> None:
        self.narrations.append(text)

def test_management_menu_announces_state():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=80, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20)
    )
    
    # Act
    management_menu(game_state, audio)
    
    # Assert
    assert any("Colony HP: 80" in narration for narration in audio.narrations)
    assert any("Metal: 30" in narration for narration in audio.narrations)

def test_repair_colony_success_with_audio():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=50, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20)
    )
    
    # Act - simulate user selecting repair option
    management_menu(game_state, audio, test_input="1")
    
    # Assert
    assert game_state.colony.hp == 100  # Colony was repaired
    assert game_state.resources.metal == 10  # Metal was spent
    assert SoundEffect.ACTION_SUCCESS in audio.played_sounds
    assert any("Colony repaired" in narration for narration in audio.narrations)

def test_repair_colony_failure_insufficient_resources():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=50, max_hp=100),
        resources=Resources(energy=50, metal=10, food=20)
    )
    
    # Act - simulate user selecting repair option
    management_menu(game_state, audio, test_input="1")
    
    # Assert
    assert game_state.colony.hp == 50  # Colony was not repaired
    assert game_state.resources.metal == 10  # No metal was spent
    assert SoundEffect.ACTION_FAIL in audio.played_sounds
    assert any("Not enough metal" in narration for narration in audio.narrations)

def test_management_menu_keyboard_navigation():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20)
    )
    
    # Act - simulate arrow key navigation
    management_menu(game_state, audio, test_input="down")
    
    # Assert
    assert SoundEffect.MENU_NAV in audio.played_sounds
    assert any("Build Structure" in narration for narration in audio.narrations)
