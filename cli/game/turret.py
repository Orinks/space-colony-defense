from dataclasses import dataclass
from typing import List, Optional
from cli.game.audio_service import AudioService, SoundEffect


@dataclass
class Enemy:
    position: int


@dataclass
class Projectile:
    position: int
    target: Optional[Enemy] = None


class Turret:
    def __init__(
        self,
        initial_position: int,
        screen_width: int = 10,
        audio_service: Optional[AudioService] = None,
    ) -> None:
        self.position = initial_position
        self.screen_width = screen_width
        self.audio_service = audio_service or AudioService()

    def move_left(self) -> None:
        if self.position > 0:
            self.position -= 1
            self.audio_service.play_sound(SoundEffect.TURRET_MOVE)

    def move_right(self) -> None:
        if self.position < self.screen_width:
            self.position += 1
            self.audio_service.play_sound(SoundEffect.TURRET_MOVE)

    def shoot(self, enemies: Optional[List[Enemy]] = None) -> Projectile:
        self.audio_service.play_sound(SoundEffect.TURRET_SHOOT)
        if not enemies:
            return Projectile(position=self.position)

        # Find nearest enemy
        nearest = min(enemies, key=lambda e: abs(e.position - self.position))
        return Projectile(position=self.position, target=nearest)
