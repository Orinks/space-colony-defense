from enum import Enum, auto
from dataclasses import dataclass
from cli.game.game_state import Resources
from cli.game.audio_service import AudioService, SoundEffect


class BuildingType(Enum):
    SOLAR_PANEL = auto()
    HYDROPONIC_FARM = auto()
    SCRAP_FORGE = auto()

    def display_name(self) -> str:
        return self.name.replace("_", " ").title()


@dataclass
class BuildingCost:
    metal: int = 0
    energy: int = 0
    food: int = 0


class Building:
    def __init__(self, type: BuildingType, audio: AudioService):
        self.type = type
        self.audio = audio
        self._costs = {
            BuildingType.SOLAR_PANEL: BuildingCost(metal=30),
            BuildingType.HYDROPONIC_FARM: BuildingCost(metal=20, energy=20),
            BuildingType.SCRAP_FORGE: BuildingCost(metal=40, energy=10),
        }
        self._production_rates = {
            BuildingType.SOLAR_PANEL: BuildingCost(energy=5),
            BuildingType.HYDROPONIC_FARM: BuildingCost(food=3),
            BuildingType.SCRAP_FORGE: BuildingCost(metal=2),
        }

    def check_resources(self, resources: Resources) -> bool:
        cost = self._costs[self.type]
        return resources.metal >= cost.metal and resources.energy >= cost.energy

    def construct(self, resources: Resources) -> bool:
        if not self.check_resources(resources):
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            self.audio.play_narration("Insufficient resources")
            return False

        self.audio.play_sound(SoundEffect.CONSTRUCTION_START)
        self.audio.play_narration(f"Building {self.type.display_name()}")

        # Deduct resources
        cost = self._costs[self.type]
        resources.metal -= cost.metal
        resources.energy -= cost.energy

        self.audio.play_sound(SoundEffect.CONSTRUCTION_COMPLETE)
        return True

    def produce_resources(self, resources: Resources) -> None:
        production = self._production_rates[self.type]
        if production.energy:
            resources.energy += production.energy
            self.audio.play_narration(f"Generated {production.energy} energy")
        if production.metal:
            resources.metal += production.metal
            self.audio.play_narration(f"Generated {production.metal} metal")
        if production.food:
            resources.food += production.food
            self.audio.play_narration(f"Generated {production.food} food")
