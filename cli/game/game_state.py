from dataclasses import dataclass
from cli.game.enemy_wave import Enemy, ResourceType
from cli.game.audio_service import AudioService, SoundEffect
from typing import Optional


@dataclass
class Resources:
    energy: int
    metal: int
    food: int


@dataclass
class Colony:
    hp: int
    max_hp: int

    def repair(
        self, resources: Resources, audio: Optional[AudioService] = None
    ) -> bool:
        repair_cost = 20
        if resources.metal >= repair_cost:
            resources.metal -= repair_cost
            self.hp = self.max_hp
            if audio:
                audio.play_sound(SoundEffect.ACTION_SUCCESS)
                audio.play_narration("Colony repaired")
            return True
        return False


class GameState:
    def __init__(
        self,
        colony: Colony,
        resources: Resources,
        wave: int = 1,
        tech_points: int = 0,
        audio: Optional[AudioService] = None,
    ) -> None:
        self.colony = colony
        self.resources = resources
        self.wave = wave
        self.tech_points = tech_points
        self.audio = audio or AudioService()

    def collect_resource(self, enemy: Enemy) -> None:
        drop = enemy.get_resource_drop()
        if drop:
            if drop.type == ResourceType.ENERGY:
                self.resources.energy += drop.amount
                self.audio.play_sound(SoundEffect.RESOURCE_CHANGE)
                self.audio.play_narration(f"Energy +{drop.amount}")
            elif drop.type == ResourceType.METAL:
                self.resources.metal += drop.amount
                self.audio.play_sound(SoundEffect.RESOURCE_CHANGE)
                self.audio.play_narration(f"Metal +{drop.amount}")
            elif drop.type == ResourceType.FOOD:
                self.resources.food += drop.amount
                self.audio.play_sound(SoundEffect.RESOURCE_CHANGE)
                self.audio.play_narration(f"Food +{drop.amount}")

    def update_resources(self, delta: Resources) -> None:
        if delta.energy != 0:
            self.resources.energy += delta.energy
            self.audio.play_sound(SoundEffect.RESOURCE_CHANGE)
            self.audio.play_narration(
                f"Energy {'+' if delta.energy > 0 else ''}{delta.energy}"
            )

        if delta.metal != 0:
            self.resources.metal += delta.metal
            self.audio.play_sound(SoundEffect.RESOURCE_CHANGE)
            self.audio.play_narration(
                f"Metal {'+' if delta.metal > 0 else ''}{delta.metal}"
            )

        if delta.food != 0:
            self.resources.food += delta.food
            self.audio.play_sound(SoundEffect.RESOURCE_CHANGE)
            self.audio.play_narration(
                f"Food {'+' if delta.food > 0 else ''}{delta.food}"
            )

    def check_loss(self) -> bool:
        return self.colony.hp <= 0

    def retreat(self) -> None:
        # Award tech points based on current wave; using integer division for simplicity.
        self.tech_points += self.wave // 2
