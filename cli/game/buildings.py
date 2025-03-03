from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Any
from cli.game.game_state import Resources
from cli.game.audio_service import AudioService, SoundEffect


class BuildingType(Enum):
    SOLAR_PANEL = auto()
    HYDROPONIC_FARM = auto()
    SCRAP_FORGE = auto()
    SHIELD_GENERATOR = auto()
    RESEARCH_LAB = auto()
    REPAIR_BAY = auto()
    MISSILE_SILO = auto()
    COMMAND_CENTER = auto()

    def display_name(self) -> str:
        return self.name.replace("_", " ").title()


class BuildingLevel(Enum):
    BASIC = auto()
    IMPROVED = auto()
    ADVANCED = auto()


@dataclass
class BuildingCost:
    metal: int = 0
    energy: int = 0
    food: int = 0


class Building:
    def __init__(self, type: BuildingType, audio: AudioService):
        self.type = type
        self.audio = audio
        self.level = BuildingLevel.BASIC
        
        # Adjusted building costs for better game balance
        self._costs = {
            BuildingType.SOLAR_PANEL: BuildingCost(metal=25, energy=5),
            BuildingType.HYDROPONIC_FARM: BuildingCost(metal=20, energy=15, food=5),
            BuildingType.SCRAP_FORGE: BuildingCost(metal=35, energy=10),
            BuildingType.SHIELD_GENERATOR: BuildingCost(metal=45, energy=30),
            BuildingType.RESEARCH_LAB: BuildingCost(metal=30, energy=25, food=5),
            BuildingType.REPAIR_BAY: BuildingCost(metal=40, energy=20),
            BuildingType.MISSILE_SILO: BuildingCost(metal=50, energy=40, food=10),
            BuildingType.COMMAND_CENTER: BuildingCost(metal=60, energy=50, food=20),
        }
        
        # Adjusted production rates for better game balance
        self._production_rates = {
            BuildingType.SOLAR_PANEL: BuildingCost(energy=8),
            BuildingType.HYDROPONIC_FARM: BuildingCost(food=5),
            BuildingType.SCRAP_FORGE: BuildingCost(metal=3),
            BuildingType.SHIELD_GENERATOR: BuildingCost(), # No resources, provides shield effect
            BuildingType.RESEARCH_LAB: BuildingCost(), # Generates tech points, not resources
            BuildingType.REPAIR_BAY: BuildingCost(), # Auto-repairs turret and colony
            BuildingType.MISSILE_SILO: BuildingCost(), # Provides special weapons
            BuildingType.COMMAND_CENTER: BuildingCost(), # Provides wave skip ability
        }
        
        # Adjusted upgrade costs for better progression
        self._upgrade_costs = {
            BuildingLevel.IMPROVED: BuildingCost(metal=15, energy=15),
            BuildingLevel.ADVANCED: BuildingCost(metal=30, energy=30, food=10),
        }
        
        # Adjusted production multipliers for more significant upgrades
        self._level_multipliers = {
            BuildingLevel.BASIC: 1.0,
            BuildingLevel.IMPROVED: 1.75,  # Increased from 1.5
            BuildingLevel.ADVANCED: 3.0,   # Increased from 2.5
        }
        
        # Adjusted special effects for better game balance
        self._special_effects = {
            BuildingType.SHIELD_GENERATOR: {
                BuildingLevel.BASIC: 25,      # Increased base shield strength
                BuildingLevel.IMPROVED: 45,   # Improved shield
                BuildingLevel.ADVANCED: 75,   # Advanced shield
            },
            BuildingType.RESEARCH_LAB: {
                BuildingLevel.BASIC: 1,       # Tech points per turn
                BuildingLevel.IMPROVED: 3,    # Increased from 2
                BuildingLevel.ADVANCED: 5,    # Increased from 4
            },
            BuildingType.REPAIR_BAY: {
                BuildingLevel.BASIC: 10,      # Auto-repair amount
                BuildingLevel.IMPROVED: 20,   # Improved repair
                BuildingLevel.ADVANCED: 35,   # Advanced repair
            },
            BuildingType.MISSILE_SILO: {
                BuildingLevel.BASIC: 1,       # Number of missiles
                BuildingLevel.IMPROVED: 2,    # More missiles
                BuildingLevel.ADVANCED: 3,    # Even more missiles
            },
            BuildingType.COMMAND_CENTER: {
                BuildingLevel.BASIC: 0,       # No wave skip
                BuildingLevel.IMPROVED: 1,    # Skip 1 wave
                BuildingLevel.ADVANCED: 2,    # Skip 2 waves
            }
        }

    def check_resources(self, resources: Resources) -> bool:
        cost = self._costs[self.type]
        return resources.metal >= cost.metal and resources.energy >= cost.energy and resources.food >= cost.food

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
        resources.food -= cost.food

        self.audio.play_sound(SoundEffect.CONSTRUCTION_COMPLETE)
        return True

    def upgrade(self, resources: Resources) -> bool:
        """Upgrade building to the next level if possible"""
        # Check if already at max level
        if self.level == BuildingLevel.ADVANCED:
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            self.audio.play_narration("Maximum level reached")
            return False

        # Determine the next level
        next_level = BuildingLevel.IMPROVED if self.level == BuildingLevel.BASIC else BuildingLevel.ADVANCED
        
        # Check if enough resources
        cost = self._upgrade_costs[next_level]
        if resources.metal < cost.metal or resources.energy < cost.energy or resources.food < cost.food:
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            self.audio.play_narration("Insufficient resources for upgrade")
            return False

        # Deduct resources
        resources.metal -= cost.metal
        resources.energy -= cost.energy
        resources.food -= cost.food

        # Upgrade the building
        old_level = self.level
        self.level = next_level
        self.audio.play_sound(SoundEffect.CONSTRUCTION_COMPLETE)
        self.audio.play_narration(f"Upgraded {self.type.display_name()} from {old_level.name.lower()} to {self.level.name.lower()}")
        return True

    def produce_resources(self, resources: Resources) -> None:
        """Generate resources based on building type and level"""
        base_production = self._production_rates[self.type]
        multiplier = self._level_multipliers[self.level]
        
        if base_production.energy:
            produced_energy = int(base_production.energy * multiplier)
            resources.energy += produced_energy
            self.audio.play_narration(f"Generated {produced_energy} energy")
        
        if base_production.metal:
            produced_metal = int(base_production.metal * multiplier)
            resources.metal += produced_metal
            self.audio.play_narration(f"Generated {produced_metal} metal")
        
        if base_production.food:
            produced_food = int(base_production.food * multiplier)
            resources.food += produced_food
            self.audio.play_narration(f"Generated {produced_food} food")

    def get_production_rate(self) -> float:
        """Get the current production rate factoring in the building level"""
        base_production = self._production_rates[self.type]
        multiplier = self._level_multipliers[self.level]
        
        # Return the sum of all resources multiplied by level
        return (base_production.energy + base_production.metal + base_production.food) * multiplier

    def has_special_effect(self) -> bool:
        """Check if this building type has a special effect"""
        return self.type in self._special_effects

    def get_special_effect(self) -> int:
        """Get the special effect value for this building based on its level"""
        if not self.has_special_effect():
            return 0
            
        return self._special_effects[self.type][self.level]

    def apply_special_effect(self, target: Optional[Any]) -> None:
        """Apply the building's special effect to a target object"""
        if not self.has_special_effect():
            return
            
        effect_strength = self.get_special_effect()
        
        if self.type == BuildingType.SHIELD_GENERATOR:
            self.audio.play_narration(f"Shield generator activated at strength {effect_strength}")
            # In a real implementation, this would apply to the colony or turret
            if target is not None:
                # Apply shield effect to target
                pass
        
        elif self.type == BuildingType.REPAIR_BAY:
            self.audio.play_narration(f"Repair bay performing maintenance, restoring {effect_strength} HP")
            # Auto-repair colony and turret
            if target is not None and hasattr(target, 'colony'):
                target.colony.hp = min(target.colony.hp + effect_strength, target.colony.max_hp)
        
        elif self.type == BuildingType.MISSILE_SILO:
            self.audio.play_narration(f"Missile silo ready with {effect_strength} missiles")
            # In a real implementation, this would add missiles to the player's inventory
            if target is not None:
                # Add missiles to inventory
                pass
        
        elif self.type == BuildingType.COMMAND_CENTER:
            if effect_strength > 0:
                self.audio.play_narration(f"Command center can skip {effect_strength} waves")
            # In a real implementation, this would allow skipping waves
            if target is not None:
                # Enable wave skipping
                pass

    def produce_tech_points(self, current_tech_points: int) -> int:
        """Generate tech points for research lab buildings"""
        if self.type != BuildingType.RESEARCH_LAB:
            return current_tech_points
            
        tech_points_generated = self._special_effects[self.type][self.level]
        self.audio.play_narration(f"Generated {tech_points_generated} tech points")
        return current_tech_points + tech_points_generated
