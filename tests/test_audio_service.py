import pytest
from cli.game.audio_service import AudioService, SoundEffect

def test_audio_service_initialization():
    # Arrange & Act
    audio = AudioService()
    
    # Assert
    assert audio.enable_sounds is True
    assert audio.enable_narration is True
    assert all(volume == 1.0 for volume in audio.sound_volumes.values())
    assert audio.narration_volume == 1.0

def test_audio_service_toggle_sounds():
    # Arrange
    audio = AudioService(enable_sounds=True)
    
    # Act
    audio.toggle_sounds()
    
    # Assert
    assert audio.enable_sounds is False
    
    # Act again
    audio.toggle_sounds()
    
    # Assert again
    assert audio.enable_sounds is True

def test_audio_service_toggle_narration():
    # Arrange
    audio = AudioService(enable_narration=True)
    
    # Act
    audio.toggle_narration()
    
    # Assert
    assert audio.enable_narration is False
    
    # Act with explicit parameter
    audio.toggle_narration(True)
    
    # Assert
    assert audio.enable_narration is True

def test_audio_service_set_sound_volume():
    # Arrange
    audio = AudioService()
    
    # Act
    audio.set_sound_volume(SoundEffect.TURRET_SHOOT, 0.5)
    
    # Assert
    assert audio.sound_volumes[SoundEffect.TURRET_SHOOT] == 0.5
    
    # Act with out-of-range volume
    audio.set_sound_volume(SoundEffect.TURRET_MOVE, 1.5)
    
    # Assert clamped to valid range
    assert audio.sound_volumes[SoundEffect.TURRET_MOVE] == 1.0
    
    # Act with negative volume
    audio.set_sound_volume(SoundEffect.ENEMY_HIT, -0.5)
    
    # Assert clamped to valid range
    assert audio.sound_volumes[SoundEffect.ENEMY_HIT] == 0.0

def test_audio_service_set_narration_volume():
    # Arrange
    audio = AudioService()
    
    # Act
    audio.set_narration_volume(0.7)
    
    # Assert
    assert audio.narration_volume == 0.7
    
    # Act with out-of-range volume
    audio.set_narration_volume(1.2)
    
    # Assert clamped to valid range
    assert audio.narration_volume == 1.0
