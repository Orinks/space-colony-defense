from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Enemy:
    position: int


@dataclass
class Projectile:
    position: int
    target: Optional[Enemy] = None


class Turret:
    def __init__(self, initial_position: int, screen_width: int = 10) -> None:
        self.position = initial_position
        self.screen_width = screen_width

    def move_left(self) -> None:
        if self.position > 0:
            self.position -= 1

    def move_right(self) -> None:
        if self.position < self.screen_width:
            self.position += 1

    def shoot(self, enemies: Optional[List[Enemy]] = None) -> Projectile:
        if not enemies:
            return Projectile(position=self.position)

        # Find nearest enemy
        nearest = min(enemies, key=lambda e: abs(e.position - self.position))
        return Projectile(position=self.position, target=nearest)
