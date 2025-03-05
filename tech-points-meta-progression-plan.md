# Tech Points and Meta-Progression System Implementation Plan

## Overview

This document outlines a detailed plan for implementing a roguelike meta-progression system in Space Colony Defense. The system will allow players to earn Tech Points during runs, which can be spent on permanent upgrades that persist between game sessions.

## System Components

### 1. Tech Points Acquisition

Extend the `GameState` class to award Tech Points in more scenarios:

```python
def retreat(self) -> None:
    """Award tech points when player chooses to retreat"""
    # Existing code
    self.tech_points += self.wave // 2
    self.audio.play_narration(f"Retreat successful. Gained {self.wave // 2} tech points.")
    
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
```

### 2. Tech Tree Data Structure

Create a new module `cli/game/tech_tree.py`:

```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

class TechCategory(Enum):
    DEFENSE = auto()     # Colony & turret defense
    WEAPONS = auto()     # Weapons and attack
    ECONOMY = auto()     # Resource generation
    SPECIAL = auto()     # Special abilities

class TechUpgrade:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        category: TechCategory,
        cost: int,
        level: int = 1,
        max_level: int = 3,
        prerequisites: Optional[List[str]] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.base_cost = cost
        self.level = 0  # Not purchased initially
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
```

### 3. Concrete Tech Upgrades

Extend the `tech_tree.py` with specific upgrades:

```python
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
    def __init__(self):
        # Initialize all available techs
        self.techs = {tech_id: tech for tech_id, tech in TECH_UPGRADES.items()}
        # Dictionary mapping tech IDs to owned levels
        self.owned_techs: Dict[str, int] = {}
        
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
        
    def apply_tech_effects(self, game_state) -> None:
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
```

### 4. Save/Load Tech Tree

Extend the save system to persist tech tree progress:

```python
# Add to cli/game/save_system.py
def save_tech_tree(tech_tree: PlayerTechTree, filename: Optional[str] = None) -> bool:
    """Save tech tree to file"""
    try:
        tech_data = {
            "owned_techs": tech_tree.owned_techs,
            "available_points": tech_tree.available_points
        }
        
        if not filename:
            filename = os.path.join(SAVE_DIR, "tech_tree.json")
            
        with open(filename, 'w') as f:
            json.dump(tech_data, f)
        return True
    except Exception as e:
        print(f"Error saving tech tree: {e}")
        return False

def load_tech_tree(filename: Optional[str] = None) -> Optional[PlayerTechTree]:
    """Load tech tree from file"""
    try:
        if not filename:
            filename = os.path.join(SAVE_DIR, "tech_tree.json")
            
        if not os.path.exists(filename):
            return PlayerTechTree()  # New tech tree
            
        with open(filename, 'r') as f:
            tech_data = json.load(f)
            
        tech_tree = PlayerTechTree()
        tech_tree.owned_techs = tech_data.get("owned_techs", {})
        tech_tree.available_points = tech_data.get("available_points", 0)
        
        # Update tech levels based on owned_techs
        for tech_id, level in tech_tree.owned_techs.items():
            if tech_id in tech_tree.techs:
                tech_tree.techs[tech_id].level = level
                
        return tech_tree
    except Exception as e:
        print(f"Error loading tech tree: {e}")
        return None
```

### 5. Tech Tree Menu Interface

Create a new menu for the tech tree:

```python
# Add to cli/game/menu_system.py
class TechTreeOption(Enum):
    DEFENSE = auto()
    WEAPONS = auto()
    ECONOMY = auto() 
    SPECIAL = auto()
    BACK = auto()

# Add to MenuSystem class
def show_tech_tree_menu(self) -> None:
    """Show the tech tree menu"""
    self.current_menu = "tech_tree"
    self.current_index = 0
    self.tech_tree_options = list(TechTreeOption)
    
    # Load tech tree
    from cli.game.save_system import load_tech_tree
    self.tech_tree = load_tech_tree()
    
    self.audio.play_narration(f"Tech Tree. You have {self.tech_tree.available_points} tech points available.")
    self._announce_current_option()

def _handle_tech_tree_selection(self) -> Optional[str]:
    """Handle selection in the tech tree menu"""
    option = self.tech_tree_options[self.current_index]
    
    if option == TechTreeOption.BACK:
        self.audio.play_sound(SoundEffect.MENU_NAV)
        self.audio.play_narration("Returning to main menu")
        self.current_menu = "main"
        self.current_index = 0
        return None
        
    # Show category-specific tech upgrades
    category_map = {
        TechTreeOption.DEFENSE: TechCategory.DEFENSE,
        TechTreeOption.WEAPONS: TechCategory.WEAPONS,
        TechTreeOption.ECONOMY: TechCategory.ECONOMY,
        TechTreeOption.SPECIAL: TechCategory.SPECIAL,
    }
    
    if option in category_map:
        self._show_category_techs(category_map[option])
        
    return None

def _show_category_techs(self, category: TechCategory) -> None:
    """Show techs in a specific category"""
    self.current_menu = "tech_category"
    self.current_index = 0
    
    # Filter techs by category
    self.category_techs = [
        tech for tech_id, tech in self.tech_tree.techs.items()
        if tech.category == category
    ]
    
    # Add a "Back" option
    self.category_techs.append(None)  # None represents "Back"
    
    self.audio.play_narration(f"{category.name} technologies")
    self._announce_current_tech_option()

def _announce_current_tech_option(self) -> None:
    """Announce the current tech option"""
    if self.current_index >= len(self.category_techs):
        return
        
    tech = self.category_techs[self.current_index]
    
    if tech is None:
        self.audio.play_narration("Back to tech categories")
        return
        
    # Announce tech details
    level_text = f"Level {tech.level}/{tech.max_level}" if tech.level > 0 else "Not purchased"
    cost_text = f"Cost: {tech.get_cost(tech.level)} tech points" if tech.level < tech.max_level else "Maximum level"
    
    self.audio.play_narration(
        f"{tech.name}. {level_text}. {tech.description}. {cost_text}"
    )
    
def _handle_tech_category_selection(self) -> None:
    """Handle selection in a tech category menu"""
    if self.current_index >= len(self.category_techs):
        return
        
    tech = self.category_techs[self.current_index]
    
    if tech is None:
        # Back option
        self.audio.play_sound(SoundEffect.MENU_NAV)
        self.current_menu = "tech_tree"
        self.current_index = 0
        self._announce_current_option()
        return
        
    # Try to purchase the tech
    current_level = tech.level
    if self.tech_tree.purchase_tech(tech.id, self.tech_tree.available_points):
        self.tech_tree.available_points -= tech.get_cost(current_level)
        self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
        self.audio.play_narration(f"Purchased {tech.name} level {tech.level}")
        
        # Save tech tree
        from cli.game.save_system import save_tech_tree
        save_tech_tree(self.tech_tree)
    else:
        self.audio.play_sound(SoundEffect.ACTION_FAIL)
        
        # Explain why purchase failed
        if tech.level >= tech.max_level:
            self.audio.play_narration(f"{tech.name} is already at maximum level")
        elif self.tech_tree.available_points < tech.get_cost(tech.level):
            self.audio.play_narration(f"Not enough tech points. You need {tech.get_cost(tech.level)}")
        else:
            # Check prerequisites
            missing_prereqs = [
                prereq_id for prereq_id in tech.prerequisites
                if prereq_id not in self.tech_tree.owned_techs or self.tech_tree.owned_techs[prereq_id] < 1
            ]
            
            if missing_prereqs:
                prereq_names = [self.tech_tree.techs[prereq_id].name for prereq_id in missing_prereqs]
                self.audio.play_narration(f"Missing prerequisites: {', '.join(prereq_names)}")
            else:
                self.audio.play_narration("Cannot purchase this technology")
```

### 6. Integrating Tech Tree with Game Loop

Update the game loop to use the tech tree:

```python
# Add to cli/game/game_loop.py
def __init__(self, audio_service: Optional[AudioService] = None) -> None:
    """Initialize the game loop with all required components"""
    self.audio = audio_service or AudioService()
    self.game_running = False
    self.in_main_menu = True
    
    # Initialize menu system
    self.menu = MenuSystem(None, self.audio)
    
    # Load tech tree
    from cli.game.tech_tree import PlayerTechTree
    from cli.game.save_system import load_tech_tree
    self.tech_tree = load_tech_tree() or PlayerTechTree()
    
    # Reset the game with the loaded configuration
    self.reset_game()

def reset_game(self) -> None:
    # Existing reset_game code...
    
    # Apply tech tree effects when starting a new game
    if hasattr(self, 'tech_tree'):
        self.tech_tree.apply_tech_effects(self.game_state)

def game_over(self) -> None:
    """Handle game over state"""
    self.is_game_over = True
    self.audio.play_sound(SoundEffect.ACTION_FAIL)
    self.audio.play_narration(
        f"Game Over! Your colony was destroyed on wave {self.game_state.wave}. You earned {self.game_state.tech_points} tech points."
    )
    
    # Add tech points to persistent tech tree
    if hasattr(self, 'tech_tree'):
        self.tech_tree.available_points += self.game_state.tech_points
        from cli.game.save_system import save_tech_tree
        save_tech_tree(self.tech_tree)
```

### 7. Main Menu Integration

Update the main menu to include the tech tree:

```python
# Add to cli/game/menu_system.py
class MainMenuOption(Enum):
    NEW_GAME = auto()
    LOAD_GAME = auto()
    TECH_TREE = auto()  # Add this option
    OPTIONS = auto()
    EXIT = auto()

def _handle_main_menu_selection(self) -> Optional[str]:
    """Handle selection in the main menu"""
    option = self.main_menu_options[self.current_index]
    if option == MainMenuOption.NEW_GAME:
        # Existing code...
    elif option == MainMenuOption.LOAD_GAME:
        # Existing code...
    elif option == MainMenuOption.TECH_TREE:
        self.audio.play_sound(SoundEffect.MENU_NAV)
        self.audio.play_narration("Tech Tree")
        self.show_tech_tree_menu()
        return None
    elif option == MainMenuOption.OPTIONS:
        # Existing code...
    elif option == MainMenuOption.EXIT:
        # Existing code...
```

## Testing Plan

1. Unit tests for `TechUpgrade` and `PlayerTechTree` classes
2. Integration tests for tech point acquisition
3. Save/load tests for tech tree persistence
4. UI tests for tech tree menu navigation

## Application Effects

Implement specific effects for each tech upgrade:

1. Reinforced Colony: Increase `colony.max_hp` and initial `colony.hp`
2. Rapid Fire: Decrease turret cooldown time
3. Resource Storage: Increase starting resources
4. Wave Skip: Start at higher wave numbers
5. Advanced Shields: Increase shield strength from Shield Generators
6. Multi-Shot: Add chance for turret to fire multiple projectiles
7. Efficient Buildings: Increase resource production rates
8. And so on...

Each tech upgrade should provide meaningful and noticeable gameplay changes that persist between runs, encouraging players to invest in different strategies.
