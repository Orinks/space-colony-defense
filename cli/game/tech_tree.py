from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any


class TechCategory(Enum):
    """Categories for tech upgrades"""
    DEFENSE = auto()     # Colony & turret defense
    WEAPONS = auto()     # Weapons and attack
    ECONOMY = auto()     # Resource generation
    SPECIAL = auto()     # Special abilities


class TechUpgrade:
    """Represents a technology that can be purchased with tech points"""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        category: TechCategory,
        cost: int,
        level: int = 0,
        max_level: int = 3,
        prerequisites: Optional[List[str]] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.base_cost = cost
        self.level = level  # Not purchased initially
        self.max_level = max_level
        self.prerequisites = prerequisites or []
        
    def get_cost(self, current_level: int) -> int:
        """Returns cost to upgrade to the next level"""
        return self.base_cost * (current_level + 1)
        
    def can_purchase(self, owned_techs: Dict[str, int], available_points: int) -> bool:
        """Check if this tech can be purchased with current points and owned techs"""
        # If already at max level, can't purchase
        if self.level >= self.max_level:
            return False
            
        # Check if we have enough points
        next_level_cost = self.get_cost(self.level)
        if available_points < next_level_cost:
            return False
            
        # Check prerequisites
        for prereq_id in self.prerequisites:
            if prereq_id not in owned_techs or owned_techs[prereq_id] < 1:
                return False
                
        return True
        
    def get_effect_description(self, level: Optional[int] = None) -> str:
        """Get a description of the effect at the given level"""
        if level is None:
            level = self.level
            
        # Each tech would override this with specific effects
        if level == 0:
            return "Not purchased"
        elif level == 1:
            return f"{self.name} Level 1 effect"
        elif level == 2:
            return f"{self.name} Level 2 effect"
        else:
            return f"{self.name} Level 3 effect"


# Example tech definitions
TECH_UPGRADES = {
    # DEFENSE category
    "reinforced_colony": TechUpgrade(
        id="reinforced_colony",
        name="Reinforced Colony",
        description="Increases colony max HP",
        category=TechCategory.DEFENSE,
        cost=10,
        max_level=3,
    ),
    "advanced_shields": TechUpgrade(
        id="advanced_shields",
        name="Advanced Shields",
        description="Shield generators produce stronger shields",
        category=TechCategory.DEFENSE,
        cost=15,
        max_level=2,
        prerequisites=["reinforced_colony"],
    ),
    
    # WEAPONS category
    "rapid_fire": TechUpgrade(
        id="rapid_fire",
        name="Rapid Fire",
        description="Decreases turret cooldown time",
        category=TechCategory.WEAPONS,
        cost=10,
        max_level=3,
    ),
    "multi_shot": TechUpgrade(
        id="multi_shot",
        name="Multi-Shot",
        description="Chance to fire multiple projectiles",
        category=TechCategory.WEAPONS,
        cost=20,
        max_level=2,
        prerequisites=["rapid_fire"],
    ),
    
    # ECONOMY category
    "resource_storage": TechUpgrade(
        id="resource_storage",
        name="Resource Storage",
        description="Start with more initial resources",
        category=TechCategory.ECONOMY,
        cost=5,
        max_level=3,
    ),
    "efficient_buildings": TechUpgrade(
        id="efficient_buildings",
        name="Efficient Buildings",
        description="Buildings produce more resources",
        category=TechCategory.ECONOMY,
        cost=15,
        max_level=2,
        prerequisites=["resource_storage"],
    ),
    
    # SPECIAL category
    "wave_skip": TechUpgrade(
        id="wave_skip",
        name="Wave Skip",
        description="Start at higher wave numbers",
        category=TechCategory.SPECIAL,
        cost=30,
        max_level=3,
    ),
}


class PlayerTechTree:
    """Manages the player's tech tree and purchased technologies"""
    
    def __init__(self):
        # Initialize all available techs
        self.techs = {tech_id: tech for tech_id, tech in TECH_UPGRADES.items()}
        # Dictionary mapping tech IDs to owned levels
        self.owned_techs: Dict[str, int] = {}
        # Available tech points to spend
        self.available_points: int = 0
        
    def purchase_tech(self, tech_id: str, available_points: int) -> bool:
        """Attempt to purchase a tech upgrade"""
        if tech_id not in self.techs:
            return False
            
        tech = self.techs[tech_id]
        current_level = self.owned_techs.get(tech_id, 0)
        
        # Check if we can purchase this tech
        if not tech.can_purchase(self.owned_techs, available_points):
            return False
            
        # Purchase successful
        cost = tech.get_cost(current_level)
        tech.level = current_level + 1
        self.owned_techs[tech_id] = current_level + 1
        
        return True
        
    def get_available_techs(self, available_points: int) -> Dict[str, TechUpgrade]:
        """Get all techs that can be purchased with available points"""
        return {
            tech_id: tech for tech_id, tech in self.techs.items()
            if tech.can_purchase(self.owned_techs, available_points)
        }
        
    def apply_tech_effects(self, game_state: Any) -> None:
        """Apply all owned tech effects to the game state"""
        # This is where we modify the game state based on owned techs
        for tech_id, level in self.owned_techs.items():
            if tech_id == "reinforced_colony":
                bonus_hp = level * 25  # 25/50/75 bonus HP
                game_state.colony.max_hp += bonus_hp
                game_state.colony.hp += bonus_hp
            elif tech_id == "resource_storage":
                bonus_resources = level * 20  # 20/40/60 bonus resources
                game_state.resources.energy += bonus_resources
                game_state.resources.metal += bonus_resources
                game_state.resources.food += bonus_resources // 2
            elif tech_id == "wave_skip" and level > 0:
                # Start at wave 1, 3, or 5 based on level
                game_state.wave = max(game_state.wave, level * 2 - 1)
            # And so on for other techs...
