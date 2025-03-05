"""
Save system for Space Colony Defense game.

This module handles saving and loading game state to/from disk.
"""
import os
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from cli.game.game_state import GameState, Resources, Colony
from cli.game.buildings import Building, BuildingType, BuildingLevel
from cli.game.audio_service import AudioService


def get_save_directory(base_dir: Optional[str] = None) -> str:
    """
    Get the directory for save files, creating it if it doesn't exist.
    
    Args:
        base_dir: Optional base directory to use instead of default
        
    Returns:
        Path to the save directory
    """
    if base_dir is None:
        # Use ~/.space_colony_defense/saves as the default save location
        save_dir = os.path.expanduser("~/.space_colony_defense/saves")
    else:
        save_dir = base_dir
        
    # Create the directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    return save_dir


def save_game(game_state: GameState, save_path: Optional[str] = None) -> bool:
    """
    Save the current game state to a file.
    
    Args:
        game_state: Current game state to save
        save_path: Optional path to save file
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Generate save path if not provided
        if save_path is None:
            save_dir = get_save_directory()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(save_dir, f"save_{timestamp}.json")
        
        # Convert game state to serializable dictionary
        save_data = {
            "colony": {
                "hp": game_state.colony.hp,
                "max_hp": game_state.colony.max_hp
            },
            "resources": {
                "energy": game_state.resources.energy,
                "metal": game_state.resources.metal,
                "food": game_state.resources.food
            },
            "wave": game_state.wave,
            "tech_points": game_state.tech_points,
            "buildings": [],
            "shield_strength": game_state.shield_strength,
            "missiles": game_state.missiles,
            "wave_skip_available": game_state.wave_skip_available,
            "save_time": time.time(),
            "save_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Serialize buildings
        for building in game_state.buildings:
            building_data = {
                "type": building.type.name,
                "level": building.level.name
            }
            save_data["buildings"].append(building_data)
        
        # Write to file
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
            
        print(f"Game saved to {save_path}")
        return True
        
    except Exception as e:
        print(f"Error saving game: {e}")
        return False


def load_game(save_path: str) -> Optional[GameState]:
    """
    Load a game state from a file.
    
    Args:
        save_path: Path to the save file
        
    Returns:
        Loaded GameState object, or None if loading failed
    """
    try:
        # Check if file exists
        if not os.path.exists(save_path):
            print(f"Save file not found: {save_path}")
            return None
        
        # Read save data
        with open(save_path, "r") as f:
            save_data = json.load(f)
        
        # Create audio service (muted for loading)
        audio = AudioService(enable_sounds=False, enable_narration=False)
        
        # Create colony
        colony_data = save_data["colony"]
        colony = Colony(
            hp=colony_data["hp"],
            max_hp=colony_data["max_hp"]
        )
        
        # Create resources
        resources_data = save_data["resources"]
        resources = Resources(
            energy=resources_data["energy"],
            metal=resources_data["metal"],
            food=resources_data["food"]
        )
        
        # Create game state
        game_state = GameState(
            colony=colony,
            resources=resources,
            wave=save_data["wave"],
            tech_points=save_data["tech_points"],
            audio=audio
        )
        
        # Set special attributes
        game_state.shield_strength = save_data.get("shield_strength", 0)
        game_state.missiles = save_data.get("missiles", 0)
        game_state.wave_skip_available = save_data.get("wave_skip_available", 0)
        
        # Load buildings
        for building_data in save_data["buildings"]:
            # Get building type
            try:
                building_type = BuildingType[building_data["type"]]
                building = Building(type=building_type, audio=audio)
                
                # Set building level
                building.level = BuildingLevel[building_data["level"]]
                
                # Add to game state
                game_state.buildings.append(building)
            except (KeyError, ValueError) as e:
                print(f"Error loading building: {e}")
                # Continue loading other buildings
        
        print(f"Game loaded from {save_path}")
        return game_state
        
    except Exception as e:
        print(f"Error loading game: {e}")
        return None


def auto_save(game_state: GameState) -> bool:
    """
    Automatically save the game to the auto-save slot.
    
    Args:
        game_state: Current game state to save
        
    Returns:
        True if auto-save was successful, False otherwise
    """
    save_dir = get_save_directory()
    auto_save_path = os.path.join(save_dir, "auto_save.json")
    return save_game(game_state, auto_save_path)


def list_save_files(save_dir: Optional[str] = None) -> List[str]:
    """
    List all available save files.
    
    Args:
        save_dir: Optional directory to look for save files
        
    Returns:
        List of paths to save files
    """
    if save_dir is None:
        save_dir = get_save_directory()
    
    # List all JSON files in the save directory
    save_files = []
    for filename in os.listdir(save_dir):
        if filename.endswith(".json"):
            save_files.append(os.path.join(save_dir, filename))
    
    return sorted(save_files, key=os.path.getmtime, reverse=True)


def get_save_info(save_path: str) -> Optional[Dict[str, Any]]:
    """
    Get summary information about a save file.
    
    Args:
        save_path: Path to the save file
        
    Returns:
        Dictionary with save info, or None if file couldn't be read
    """
    try:
        with open(save_path, "r") as f:
            save_data = json.load(f)
        
        # Extract relevant info
        return {
            "wave": save_data["wave"],
            "colony_hp": save_data["colony"]["hp"],
            "colony_max_hp": save_data["colony"]["max_hp"],
            "tech_points": save_data["tech_points"],
            "building_count": len(save_data["buildings"]),
            "save_date": save_data.get("save_date", "Unknown"),
            "filename": os.path.basename(save_path)
        }
    except Exception as e:
        print(f"Error reading save file {save_path}: {e}")
        return None

# Tech Tree Save/Load Functions
def save_tech_tree(tech_tree, save_path: Optional[str] = None) -> bool:
    """Save tech tree to file"""
    try:
        # Generate save path if not provided
        if save_path is None:
            save_dir = get_save_directory()
            save_path = os.path.join(save_dir, "tech_tree.json")
        
        # Convert tech tree to serializable dictionary
        save_data = {
            "owned_techs": tech_tree.owned_techs,
            "available_points": tech_tree.available_points
        }
        
        # Write to file
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
            
        print(f"Tech tree saved to {save_path}")
        return True
        
    except Exception as e:
        print(f"Error saving tech tree: {e}")
        return False

def load_tech_tree(save_path: Optional[str] = None):
    """Load tech tree from file"""
    try:
        # Import here to avoid circular imports
        from cli.game.tech_tree import PlayerTechTree
        
        # Generate save path if not provided
        if save_path is None:
            save_dir = get_save_directory()
            save_path = os.path.join(save_dir, "tech_tree.json")
        
        # Check if file exists
        if not os.path.exists(save_path):
            print(f"Tech tree file not found: {save_path}")
            return PlayerTechTree()  # Return a new tech tree
        
        # Read save data
        with open(save_path, "r") as f:
            save_data = json.load(f)
        
        # Create tech tree
        tech_tree = PlayerTechTree()
        tech_tree.owned_techs = save_data.get("owned_techs", {})
        tech_tree.available_points = save_data.get("available_points", 0)
        
        # Update tech levels based on owned_techs
        for tech_id, level in tech_tree.owned_techs.items():
            if tech_id in tech_tree.techs:
                tech_tree.techs[tech_id].level = level
        
        print(f"Tech tree loaded from {save_path}")
        return tech_tree
        
    except Exception as e:
        print(f"Error loading tech tree: {e}")
        from cli.game.tech_tree import PlayerTechTree
        return PlayerTechTree()  # Return a new tech tree on error
