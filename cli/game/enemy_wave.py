from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class EnemyType(Enum):
    BASIC_INVADER = auto()
    ARMORED_SHIP = auto()
    SWARMER = auto()


class ResourceType(Enum):
    ENERGY = auto()
    METAL = auto()
    FOOD = auto()


@dataclass
class ResourceDrop:
    type: ResourceType
    amount: int


@dataclass
class Enemy:
    type: EnemyType
    x: int
    y: int = 0
    resource_drop: Optional[ResourceDrop] = None

    def get_resource_drop(self) -> Optional[ResourceDrop]:
        if self.resource_drop:
            return self.resource_drop

        # Default drops based on enemy type
        return {
            EnemyType.BASIC_INVADER: ResourceDrop(ResourceType.ENERGY, 10),
            EnemyType.ARMORED_SHIP: ResourceDrop(ResourceType.METAL, 15),
            EnemyType.SWARMER: ResourceDrop(ResourceType.FOOD, 5),
        }.get(self.type)


def generate_wave(wave_number: int) -> List[Enemy]:
    enemies: List[Enemy] = []
    screen_width = 10  # Basic screen width for spacing enemies

    if wave_number == 1:
        # Wave 1: Exactly 5 basic invaders
        for i in range(5):
            enemies.append(Enemy(type=EnemyType.BASIC_INVADER, x=i * 2))
        return enemies

    elif wave_number == 3:
        # Wave 3: Exactly 10 Basic Invaders + 2 Armored Ships
        for i in range(10):
            enemies.append(Enemy(type=EnemyType.BASIC_INVADER, x=i))
        enemies.append(Enemy(type=EnemyType.ARMORED_SHIP, x=3))
        enemies.append(Enemy(type=EnemyType.ARMORED_SHIP, x=7))
        return enemies

    elif wave_number == 5:
        # Wave 5: 8 Basic Invaders + 3 Swarmers
        for i in range(8):
            enemies.append(Enemy(type=EnemyType.BASIC_INVADER, x=i))
        for i in range(3):
            enemies.append(Enemy(type=EnemyType.SWARMER, x=i * 3 + 2))
        return enemies

    # Base number of enemies scales with wave number
    num_basic = 5 + wave_number * 2  # Double scaling factor
    num_armored = max(0, wave_number - 3) * 2  # Double scaling for armored ships
    num_swarmers = max(0, wave_number - 5)  # Keep swarmer scaling linear

    # Add Basic Invaders (more aggressive scaling for later waves)
    max_basic = min(
        num_basic + (wave_number // 10) * 3, screen_width
    )  # Extra scaling every 10 waves
    for i in range(max_basic):
        enemies.append(Enemy(type=EnemyType.BASIC_INVADER, x=i))

    # Add Armored Ships (more spacing between them)
    max_armored = min(
        num_armored + (wave_number // 15) * 2, screen_width // 2
    )  # Extra scaling every 15 waves
    for i in range(max_armored):
        enemies.append(Enemy(type=EnemyType.ARMORED_SHIP, x=i * 2 + 1))

    # Add Swarmers (even more spacing)
    max_swarmers = min(
        num_swarmers + wave_number // 20, screen_width // 3
    )  # Extra scaling every 20 waves
    for i in range(max_swarmers):
        enemies.append(Enemy(type=EnemyType.SWARMER, x=i * 3 + 2))

    # For later waves, add extra enemies by stacking them vertically
    if wave_number > 15:
        vertical_rows = wave_number // 15  # Add an extra row every 15 waves
        for row in range(1, vertical_rows + 1):
            for i in range(min(5, screen_width)):
                enemies.append(Enemy(type=EnemyType.BASIC_INVADER, x=i, y=row))

    return enemies
