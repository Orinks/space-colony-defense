import pytest
from typing import List
from cli.game.game_loop import GameLoop
from cli.game.audio_service import AudioService, SoundEffect
from cli.game.enemy_wave import Enemy, EnemyType

class MockAudioService:
    def __init__(self):
        self.played_sounds: List[SoundEffect] = []
        self.narrations: List[str] = []
    
    def play_sound(self, effect: SoundEffect) -> None:
        self.played_sounds.append(effect)
    
    def play_narration(self, text: str) -> None:
        self.narrations.append(text)

def test_game_loop_initialization():
    # Arrange
    audio = MockAudioService()
    
    # Act
    game = GameLoop(audio_service=audio)
    
    # Assert
    assert game.game_state is not None
    assert game.turret is not None
    assert game.is_game_over is False
    assert len(audio.narrations) > 0
    assert any("Main Menu" in narration for narration in audio.narrations)

def test_game_loop_wave_start():
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.in_main_menu = False  # Exit main menu
    game.game_running = True   # Start the game
    
    # Act
    game.start_wave()
    
    # Assert
    assert len(game.enemies) > 0  # Wave 1 should have some enemies
    assert game.is_wave_complete is False
    assert game.is_management_phase is False
    assert any("Wave 1" in narration for narration in audio.narrations)

def test_game_loop_player_movement():
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.in_main_menu = False  # Exit main menu
    game.game_running = True   # Start the game
    initial_position = game.turret.position
    
    # Act
    game.handle_input("right")
    
    # Assert
    assert game.turret.position == initial_position + 1
    assert SoundEffect.TURRET_MOVE in audio.played_sounds

def test_game_loop_player_shooting():
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.in_main_menu = False  # Exit main menu
    game.game_running = True   # Start the game
    game.start_wave()  # Ensure there are enemies
    
    # Act
    game.handle_input("shoot")
    
    # Assert
    assert len(game.projectiles) == 1
    assert SoundEffect.TURRET_SHOOT in audio.played_sounds

def test_game_loop_wave_completion():
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.in_main_menu = False  # Exit main menu
    game.game_running = True   # Start the game
    game.start_wave()
    
    # Act - artificially clear all enemies to simulate wave completion
    game.enemies = []
    game.update()
    
    # Assert
    assert game.is_wave_complete is True
    assert game.is_management_phase is True
    assert SoundEffect.ACTION_SUCCESS in audio.played_sounds
    assert any("Wave 1 complete" in narration for narration in audio.narrations)
    assert any("Management phase" in narration for narration in audio.narrations)

def test_game_loop_management_phase_end():
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.in_main_menu = False  # Exit main menu
    game.game_running = True   # Start the game
    game.is_management_phase = True  # Directly set management phase
    
    # Act
    game.handle_input("end_management")
    
    # Assert
    assert game.is_management_phase is False
    assert game.game_state.wave == 2  # Wave should be incremented
    assert len(game.enemies) > 0  # New wave should have started
    assert any("Wave 2" in narration for narration in audio.narrations)

def test_game_loop_game_over():
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.in_main_menu = False  # Exit main menu
    game.game_running = True   # Start the game
    
    # Act - set colony health to 0 to trigger game over
    game.game_state.colony.hp = 0
    game.update()
    
    # Assert
    assert game.is_game_over is True
    assert SoundEffect.ACTION_FAIL in audio.played_sounds
    assert any("Game Over" in narration for narration in audio.narrations)

def test_game_loop_full_wave_sequence():
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.in_main_menu = False  # Exit main menu
    game.game_running = True   # Start the game
    
    # Act 1 - Simulate end of wave
    game.is_wave_complete = True
    game.update()  # This should trigger management phase
    
    # Assert 1
    assert game.is_management_phase is True
    
    # Act 2 - End management phase to start wave 2
    game.handle_input("end_management")
    
    # Assert 2
    assert game.game_state.wave == 2
    assert game.is_wave_complete is False
    assert game.is_management_phase is False
    assert len(game.enemies) > 0  # Wave 2 has enemies
