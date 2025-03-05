from cli.game.game_state import GameState, Resources, Colony
from cli.game.audio_service import AudioService, SoundEffect
from unittest.mock import MagicMock

def test_game_loss_triggers_reset():
    # Arrange
    colony = Colony(hp=0, max_hp=100)
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=0, metal=0, food=0),
        wave=1,
        tech_points=0
    )
    # Act & Assert
    assert game_state.check_loss() is True

def test_tech_points_award_on_retreat():
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    audio = MagicMock()
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=0, metal=0, food=0),
        wave=15,
        tech_points=5,
        audio=audio
    )
    game_state.total_enemies_in_wave = 10
    game_state.enemies_defeated_in_current_wave = 6  # 60% defeated
    
    initial_tech_points = game_state.tech_points
    
    # Act
    game_state.retreat()
    
    # Assert
    assert game_state.tech_points > initial_tech_points
    audio.play_narration.assert_called_with(f"Strategic retreat successful. Gained {game_state.tech_points - initial_tech_points} tech points.")

def test_early_retreat_awards_no_tech_points():
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    audio = MagicMock()
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=0, metal=0, food=0),
        wave=15,
        tech_points=5,
        audio=audio
    )
    game_state.total_enemies_in_wave = 10
    game_state.enemies_defeated_in_current_wave = 3  # Only 30% defeated
    
    initial_tech_points = game_state.tech_points
    
    # Act
    game_state.retreat()
    
    # Assert
    assert game_state.tech_points == initial_tech_points
    audio.play_narration.assert_called_with("Retreat completed. No tech points earned - not enough enemies defeated.")

def test_tech_points_awarded_for_wave_completion():
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    audio = MagicMock()
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=50, metal=30, food=20),
        wave=5,
        tech_points=10,
        audio=audio
    )
    
    initial_tech_points = game_state.tech_points
    
    # Act
    game_state.complete_wave()
    
    # Assert
    assert game_state.tech_points > initial_tech_points
    audio.play_narration.assert_called_with(f"Wave {game_state.wave} complete. Gained {game_state.tech_points - initial_tech_points} tech points.")
    
def test_boss_wave_awards_extra_tech_points():
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    audio = MagicMock()
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=50, metal=30, food=20),
        wave=5,  # Boss wave
        tech_points=10,
        audio=audio
    )
    
    initial_tech_points = game_state.tech_points
    
    # Act
    game_state.defeat_boss()
    
    # Assert
    assert game_state.tech_points > initial_tech_points
    # Boss points should be wave // 2 = 2
    assert game_state.tech_points == initial_tech_points + 2
    audio.play_narration.assert_called_with(f"Boss defeated! Gained {game_state.tech_points - initial_tech_points} tech points.")
