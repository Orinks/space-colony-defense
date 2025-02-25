from typing import List
import pytest
from cli.game.turret import Turret, Projectile, Enemy
from cli.game.audio_service import AudioService, SoundEffect

def test_turret_moves_left():
    # Arrange
    turret = Turret(initial_position=5)
    # Act
    turret.move_left()
    # Assert
    assert turret.position == 4

def test_turret_moves_right():
    # Arrange
    turret = Turret(initial_position=5)
    # Act
    turret.move_right()
    # Assert
    assert turret.position == 6

def test_turret_cannot_move_past_left_boundary():
    # Arrange
    turret = Turret(initial_position=0)
    # Act
    turret.move_left()
    # Assert
    assert turret.position == 0

def test_turret_cannot_move_past_right_boundary():
    # Arrange
    turret = Turret(initial_position=10, screen_width=10)
    # Act
    turret.move_right()
    # Assert
    assert turret.position == 10

def test_turret_can_shoot():
    turret = Turret(initial_position=5)
    projectile = turret.shoot()
    assert projectile is not None
    assert projectile.position == turret.position

def test_turret_projectile_starts_at_turret_position():
    turret = Turret(initial_position=3)
    projectile = turret.shoot()
    assert projectile.position == 3

def test_turret_targets_nearest_enemy():
    # Arrange
    turret = Turret(initial_position=5)
    enemies = [
        Enemy(position=8),  # 3 units away
        Enemy(position=3),  # 2 units away
        Enemy(position=10)  # 5 units away
    ]
    # Act
    projectile = turret.shoot(enemies)
    # Assert
    assert projectile.target == enemies[1]  # Should target enemy at position 3

def test_turret_plays_move_sound(monkeypatch):
    # Arrange
    played_sounds = []
    
    class MockAudioService:
        def play_sound(self, effect: SoundEffect) -> None:
            played_sounds.append(effect)
    
    turret = Turret(initial_position=5, audio_service=MockAudioService())
    
    # Act
    turret.move_left()
    
    # Assert
    assert len(played_sounds) == 1
    assert played_sounds[0] == SoundEffect.TURRET_MOVE

def test_turret_plays_shoot_sound(monkeypatch):
    # Arrange
    played_sounds = []
    
    class MockAudioService:
        def play_sound(self, effect: SoundEffect) -> None:
            played_sounds.append(effect)
    
    turret = Turret(initial_position=5, audio_service=MockAudioService())
    
    # Act
    turret.shoot()
    
    # Assert
    assert len(played_sounds) == 1
    assert played_sounds[0] == SoundEffect.TURRET_SHOOT

def test_turret_initializes_with_full_shield():
    # Arrange & Act
    turret = Turret(initial_position=5, max_shield=100)
    
    # Assert
    assert turret.shield == 100
    assert turret.max_shield == 100
    assert turret.is_damaged is False

def test_turret_takes_damage():
    # Arrange
    turret = Turret(initial_position=5, max_shield=100)
    
    # Act
    turret.take_damage(30)
    
    # Assert
    assert turret.shield == 70
    assert turret.is_damaged is True

def test_turret_shield_cannot_go_below_zero():
    # Arrange
    turret = Turret(initial_position=5, max_shield=100)
    
    # Act
    turret.take_damage(150)  # Damage more than shield
    
    # Assert
    assert turret.shield == 0
    assert turret.is_damaged is True

def test_turret_shield_depletion_plays_sound():
    # Arrange
    played_sounds = []
    narrations = []
    
    class MockAudioService:
        def play_sound(self, effect: SoundEffect) -> None:
            played_sounds.append(effect)
        
        def play_narration(self, text: str) -> None:
            narrations.append(text)
    
    turret = Turret(initial_position=5, audio_service=MockAudioService(), max_shield=100)
    
    # Act
    turret.take_damage(100)  # Fully deplete shield
    
    # Assert
    assert SoundEffect.ACTION_FAIL in played_sounds
    assert any("Shield depleted" in narration for narration in narrations)

def test_turret_repairs_shield():
    # Arrange
    turret = Turret(initial_position=5, max_shield=100)
    turret.take_damage(50)  # Reduce shield to 50
    
    # Act
    turret.repair_shield(30)
    
    # Assert
    assert turret.shield == 80
    assert turret.is_damaged is True  # Still damaged, not at max

def test_turret_repair_cannot_exceed_max_shield():
    # Arrange
    turret = Turret(initial_position=5, max_shield=100)
    turret.take_damage(20)  # Reduce shield to 80
    
    # Act
    turret.repair_shield(30)  # Try to repair by 30 (would be 110)
    
    # Assert
    assert turret.shield == 100  # Should be capped at max
    assert turret.is_damaged is False  # At max, so not damaged

def test_turret_repair_plays_sound():
    # Arrange
    played_sounds = []
    narrations = []
    
    class MockAudioService:
        def play_sound(self, effect: SoundEffect) -> None:
            played_sounds.append(effect)
        
        def play_narration(self, text: str) -> None:
            narrations.append(text)
    
    turret = Turret(initial_position=5, audio_service=MockAudioService(), max_shield=100)
    turret.take_damage(40)  # Reduce shield to 60
    
    # Act
    turret.repair_shield(20)
    
    # Assert
    assert SoundEffect.ACTION_SUCCESS in played_sounds
    assert any("Shield repaired" in narration for narration in narrations)
