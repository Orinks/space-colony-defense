from dataclasses import dataclass
from cli.game.enemy_wave import Enemy, ResourceType
from cli.game.audio_service import AudioService, SoundEffect
from typing import Optional, List


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
        self.buildings: List = []
        self.shield_strength = 0
        self.missiles = 0
        self.wave_skip_available = 0
        
        # For retreat calculations
        self.total_enemies_in_wave = 0
        self.enemies_defeated_in_current_wave = 0

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

    def add_building(self, building) -> bool:
        """Add a new building to the colony"""
        if building.construct(self.resources):
            self.buildings.append(building)
            return True
        return False

    def produce_from_buildings(self) -> None:
        """Run production cycle for all buildings"""
        for building in self.buildings:
            building.produce_resources(self.resources)
            
            # Handle special effects
            if building.has_special_effect():
                if building.type.name == "SHIELD_GENERATOR":
                    self.shield_strength = building.get_special_effect()
                    building.apply_special_effect(self)
                elif building.type.name == "RESEARCH_LAB":
                    self.tech_points = building.produce_tech_points(self.tech_points)
                elif building.type.name == "REPAIR_BAY":
                    effect_strength = building.get_special_effect()
                    self.colony.hp = min(self.colony.hp + effect_strength, self.colony.max_hp)
                    building.apply_special_effect(self)
                elif building.type.name == "MISSILE_SILO":
                    self.missiles = building.get_special_effect()
                    building.apply_special_effect(self)
                elif building.type.name == "COMMAND_CENTER":
                    self.wave_skip_available = building.get_special_effect()
                    building.apply_special_effect(self)

    def upgrade_building(self, building_index: int) -> bool:
        """Upgrade a building if possible"""
        if 0 <= building_index < len(self.buildings):
            return self.buildings[building_index].upgrade(self.resources)
        return False

    def check_loss(self) -> bool:
        return self.colony.hp <= 0

    def retreat(self) -> None:
        """Award tech points when player chooses to retreat, but only if they've made progress"""
        # Only award points if player has defeated at least 50% of the wave's enemies
        if self.enemies_defeated_in_current_wave >= self.total_enemies_in_wave // 2:
            points_earned = self.wave // 2
            self.tech_points += points_earned
            self.audio.play_narration(f"Strategic retreat successful. Gained {points_earned} tech points.")
        else:
            self.audio.play_narration("Retreat completed. No tech points earned - not enough enemies defeated.")
    
    def complete_wave(self) -> None:
        """Award tech points for completing a wave"""
        # More points for higher waves
        points_earned = max(1, self.wave // 3)
        self.tech_points += points_earned
        self.audio.play_narration(f"Wave {self.wave} complete. Gained {points_earned} tech points.")
    
    def defeat_boss(self) -> None:
        """Award tech points for defeating boss waves (every 5 waves)"""
        if self.wave % 5 == 0:
            boss_points = self.wave // 2
            self.tech_points += boss_points
            self.audio.play_narration(f"Boss defeated! Gained {boss_points} tech points.")
    
    def skip_waves(self) -> bool:
        """Skip waves if command center allows it"""
        if self.wave_skip_available > 0:
            self.wave += self.wave_skip_available
            self.audio.play_narration(f"Command center activated. Skipping {self.wave_skip_available} waves.")
            self.wave_skip_available = 0
            return True
        return False
        
    def fire_missile(self) -> bool:
        """Fire a missile if available"""
        if self.missiles > 0:
            self.missiles -= 1
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
            self.audio.play_narration(f"Missile fired! {self.missiles} missiles remaining.")
            return True
        self.audio.play_sound(SoundEffect.ACTION_FAIL)
        self.audio.play_narration("No missiles available.")
        return False
