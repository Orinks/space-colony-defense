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
