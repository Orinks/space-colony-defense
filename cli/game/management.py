from cli.game.game_state import GameState
from cli.game.audio_service import AudioService, SoundEffect
from cli.game.buildings import Building, BuildingType, BuildingLevel
from typing import Optional, Dict

def management_menu(game_state: GameState, audio: AudioService, test_input: Optional[str] = None) -> None:
    """
    Display the management menu and handle user input
    
    Parameters:
        game_state: Current game state
        audio: Audio service for sound effects and narration
        test_input: Optional input for testing
    """
    # Announce colony status
    audio.play_narration(f"Colony HP: {game_state.colony.hp}/{game_state.colony.max_hp}")
    
    # Announce special effects
    if game_state.shield_strength > 0:
        audio.play_narration(f"Shield strength: {game_state.shield_strength}")
    if game_state.missiles > 0:
        audio.play_narration(f"Missiles available: {game_state.missiles}")
    if game_state.wave_skip_available > 0:
        audio.play_narration(f"Wave skip available: {game_state.wave_skip_available}")
    
    audio.play_narration(f"Resources - Energy: {game_state.resources.energy}, Metal: {game_state.resources.metal}, Food: {game_state.resources.food}")
    audio.play_narration(f"Tech points: {game_state.tech_points}")
    
    # Show menu options
    audio.play_narration("Management options:")
    audio.play_narration("1: Repair Colony - Cost: 20 metal")
    audio.play_narration("2: Build Structure")
    audio.play_narration("3: Upgrade Structure")
    audio.play_narration("4: Next Wave")
    
    if game_state.wave_skip_available > 0:
        audio.play_narration(f"5: Skip {game_state.wave_skip_available} Waves")
    
    # Handle input
    if test_input == "1" or test_input == "repair":
        # Repair colony
        if game_state.colony.repair(game_state.resources, audio):
            pass  # Success message handled by repair method
        else:
            # Make sure we play the failure sound
            audio.play_sound(SoundEffect.ACTION_FAIL)
            audio.play_narration("Not enough metal to repair colony")
    
    elif test_input == "2" or test_input == "build":
        # Show building options with costs and benefits
        show_building_options(game_state, audio)
    
    elif test_input == "down":
        # Simulate navigation
        audio.play_sound(SoundEffect.MENU_NAV)
        audio.play_narration("Build Structure")
    
    elif test_input and test_input.startswith("build_"):
        # Extract building type from input
        building_type_name = test_input[6:].upper()
        
        try:
            # For test compatibility, handle both SOLAR and SOLAR_PANEL
            if building_type_name == "SOLAR":
                building_type_name = "SOLAR_PANEL"
                
            building_type = BuildingType[building_type_name]
            building = Building(type=building_type, audio=audio)
            
            # Announce building details before construction
            announce_building_details(building, game_state, audio)
            
            if game_state.add_building(building):
                audio.play_sound(SoundEffect.ACTION_SUCCESS)
                audio.play_narration(f"{building_type.display_name()} constructed successfully")
            else:
                audio.play_sound(SoundEffect.ACTION_FAIL)
                # Message already played by building itself
        except (KeyError, ValueError):
            audio.play_sound(SoundEffect.ACTION_FAIL)
            audio.play_narration(f"Unknown building type: {building_type_name}")
    
    elif test_input and test_input.startswith("upgrade_"):
        # Extract building index from input
        try:
            building_index = int(test_input.split("_")[1])
            
            if 0 <= building_index < len(game_state.buildings):
                # Announce upgrade details before upgrading
                announce_upgrade_details(game_state.buildings[building_index], game_state, audio)
                
                if game_state.upgrade_building(building_index):
                    # Success message handled by the building itself
                    pass
                else:
                    # Failure message handled by the building itself
                    pass
            else:
                audio.play_sound(SoundEffect.ACTION_FAIL)
                audio.play_narration(f"Invalid building index: {building_index}")
        except (IndexError, ValueError):
            audio.play_sound(SoundEffect.ACTION_FAIL)
            audio.play_narration("Invalid building index")
    
    elif test_input == "skip_wave" and game_state.wave_skip_available > 0:
        game_state.skip_waves()
    
    # In a real implementation, we would wait for user input here
    # and handle the management phase loop

def show_building_options(game_state: GameState, audio: AudioService) -> None:
    """Show available building options with costs and benefits"""
    audio.play_narration("Available buildings:")
    
    # Create a temporary building to access costs and production rates
    temp_building = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    
    for building_type in BuildingType:
        temp_building.type = building_type
        cost = temp_building._costs[building_type]
        
        # Format cost string
        cost_str = []
        if cost.metal > 0:
            cost_str.append(f"{cost.metal} metal")
        if cost.energy > 0:
            cost_str.append(f"{cost.energy} energy")
        if cost.food > 0:
            cost_str.append(f"{cost.food} food")
        
        cost_text = ", ".join(cost_str)
        
        # Format benefit string
        benefit = get_building_benefit_description(building_type, temp_building)
        
        # Announce building option
        audio.play_narration(f"{building_type.display_name()} - Cost: {cost_text} - Benefit: {benefit}")

def announce_building_details(building: Building, game_state: GameState, audio: AudioService) -> None:
    """Announce detailed information about a building before construction"""
    cost = building._costs[building.type]
    
    # Format cost string
    cost_str = []
    if cost.metal > 0:
        cost_str.append(f"{cost.metal} metal")
    if cost.energy > 0:
        cost_str.append(f"{cost.energy} energy")
    if cost.food > 0:
        cost_str.append(f"{cost.food} food")
    
    cost_text = ", ".join(cost_str)
    
    # Check if player has enough resources
    has_resources = building.check_resources(game_state.resources)
    resource_status = "You have enough resources" if has_resources else "You don't have enough resources"
    
    # Get benefit description
    benefit = get_building_benefit_description(building.type, building)
    
    # Announce building details
    audio.play_narration(f"Building {building.type.display_name()}")
    audio.play_narration(f"Cost: {cost_text}")
    audio.play_narration(f"Benefit: {benefit}")
    audio.play_narration(resource_status)

def announce_upgrade_details(building: Building, game_state: GameState, audio: AudioService) -> None:
    """Announce detailed information about a building upgrade"""
    # Determine the next level
    if building.level == BuildingLevel.ADVANCED:
        audio.play_narration(f"{building.type.display_name()} is already at maximum level")
        return
        
    next_level = BuildingLevel.IMPROVED if building.level == BuildingLevel.BASIC else BuildingLevel.ADVANCED
    
    # Get upgrade cost
    cost = building._upgrade_costs[next_level]
    
    # Format cost string
    cost_str = []
    if cost.metal > 0:
        cost_str.append(f"{cost.metal} metal")
    if cost.energy > 0:
        cost_str.append(f"{cost.energy} energy")
    if cost.food > 0:
        cost_str.append(f"{cost.food} food")
    
    cost_text = ", ".join(cost_str)
    
    # Check if player has enough resources
    has_resources = (
        game_state.resources.metal >= cost.metal and
        game_state.resources.energy >= cost.energy and
        game_state.resources.food >= cost.food
    )
    resource_status = "You have enough resources" if has_resources else "You don't have enough resources"
    
    # Calculate production increase
    current_multiplier = building._level_multipliers[building.level]
    next_multiplier = building._level_multipliers[next_level]
    increase_percent = int((next_multiplier / current_multiplier - 1) * 100)
    
    # Get benefit description
    current_benefit = get_building_benefit_description(building.type, building)
    
    # Temporarily set building to next level to get new benefit
    original_level = building.level
    building.level = next_level
    new_benefit = get_building_benefit_description(building.type, building)
    building.level = original_level  # Restore original level
    
    # Announce upgrade details
    audio.play_narration(f"Upgrade {building.type.display_name()} from {building.level.name.lower()} to {next_level.name.lower()}")
    audio.play_narration(f"Cost: {cost_text}")
    audio.play_narration(f"Current: {current_benefit}")
    audio.play_narration(f"After upgrade: {new_benefit}")
    audio.play_narration(resource_status)

def get_building_benefit_description(building_type: BuildingType, building: Building) -> str:
    """Get a description of the building's benefit"""
    if building_type == BuildingType.SOLAR_PANEL:
        energy_production = building._production_rates[building_type].energy
        multiplier = building._level_multipliers[building.level]
        return f"Produces {int(energy_production * multiplier)} energy per turn"
        
    elif building_type == BuildingType.HYDROPONIC_FARM:
        food_production = building._production_rates[building_type].food
        multiplier = building._level_multipliers[building.level]
        return f"Produces {int(food_production * multiplier)} food per turn"
        
    elif building_type == BuildingType.SCRAP_FORGE:
        metal_production = building._production_rates[building_type].metal
        multiplier = building._level_multipliers[building.level]
        return f"Produces {int(metal_production * multiplier)} metal per turn"
        
    elif building_type == BuildingType.SHIELD_GENERATOR:
        shield_strength = building._special_effects[building_type][building.level]
        return f"Provides {shield_strength} shield strength"
        
    elif building_type == BuildingType.RESEARCH_LAB:
        tech_points = building._special_effects[building_type][building.level]
        return f"Generates {tech_points} tech points per turn"
        
    elif building_type == BuildingType.REPAIR_BAY:
        repair_amount = building._special_effects[building_type][building.level]
        return f"Repairs {repair_amount} HP per turn"
        
    elif building_type == BuildingType.MISSILE_SILO:
        missiles = building._special_effects[building_type][building.level]
        return f"Provides {missiles} missiles per turn"
        
    elif building_type == BuildingType.COMMAND_CENTER:
        wave_skip = building._special_effects[building_type][building.level]
        if wave_skip == 0:
            return "Command center needs to be upgraded to skip waves"
        return f"Allows skipping {wave_skip} waves"
        
    return "Unknown benefit"
