from dataclasses import dataclass
from typing import List, Optional, Union, Any
from cli.game.audio_service import AudioService, SoundEffect


@dataclass
class Enemy:
    position: int


@dataclass
class Projectile:
    position: int
    target: Optional[Any] = None  # Use Any to handle both Enemy types


class Turret:
    def __init__(
        self,
        initial_position: int,
        screen_width: int = 10,
        audio_service: Optional[AudioService] = None,
        max_shield: int = 100,
    ) -> None:
        self.position = initial_position
        self.screen_width = screen_width
        self.audio_service = audio_service or AudioService()
        self.shield = max_shield
        self.max_shield = max_shield
        self.is_damaged = False

    def move_left(self) -> None:
        if self.position > 0:
            self.position -= 1
            self.audio_service.play_sound(SoundEffect.TURRET_MOVE)

    def move_right(self) -> None:
        if self.position < self.screen_width:
            self.position += 1
            self.audio_service.play_sound(SoundEffect.TURRET_MOVE)

    def shoot(self, enemies: Optional[List[Any]] = None) -> Projectile:
        self.audio_service.play_sound(SoundEffect.TURRET_SHOOT)
        if not enemies or len(enemies) == 0:
            return Projectile(position=self.position)

        # Find nearest enemy - handle both Enemy types (from turret.py and enemy_wave.py)
        # Check if enemies have 'position' or 'x' attribute
        if hasattr(enemies[0], "position"):
            nearest = min(enemies, key=lambda e: abs(e.position - self.position))
        else:
            # Assume enemy has 'x' attribute (from enemy_wave.py)
            nearest = min(enemies, key=lambda e: abs(e.x - self.position))

        return Projectile(position=self.position, target=nearest)

    def take_damage(self, damage: int = 10) -> None:
        """Apply damage to the turret's shield"""
        self.shield = max(0, self.shield - damage)
        self.is_damaged = self.shield < self.max_shield

        # Play appropriate sound effect based on shield state
        if self.shield == 0:
            self.audio_service.play_sound(SoundEffect.ACTION_FAIL)
            self.audio_service.play_narration("Warning: Shield depleted!")
        else:
            self.audio_service.play_sound(SoundEffect.ENEMY_HIT)

    def repair_shield(self, amount: int = 20) -> None:
        """Repair the turret's shield by the specified amount"""
        old_shield = self.shield
        self.shield = min(self.max_shield, self.shield + amount)
        self.is_damaged = self.shield < self.max_shield

        if self.shield > old_shield:
            self.audio_service.play_sound(SoundEffect.ACTION_SUCCESS)
            self.audio_service.play_narration(f"Shield repaired to {self.shield}%")
