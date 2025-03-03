import pytest
from typing import List
from cli.game.management import management_menu
from cli.game.game_state import GameState, Resources, Colony
from cli.game.audio_service import AudioService, SoundEffect
from cli.game.buildings import Building, BuildingType, BuildingLevel

class MockAudioService:
    def __init__(self):
        self.played_sounds: List[SoundEffect] = []
        self.narrations: List[str] = []
    
    def play_sound(self, effect: SoundEffect) -> None:
        self.played_sounds.append(effect)
    
    def play_narration(self, text: str) -> None:
        self.narrations.append(text)

def test_management_menu_announces_state():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=80, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20)
    )
    
    # Act
    management_menu(game_state, audio)
    
    # Assert
    assert any("Colony HP: 80" in narration for narration in audio.narrations)
    assert any("Metal: 30" in narration for narration in audio.narrations)

def test_repair_colony_success_with_audio():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=50, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20)
    )
    
    # Act - simulate user selecting repair option
    management_menu(game_state, audio, test_input="1")
    
    # Assert
    assert game_state.colony.hp == 100  # Colony was repaired
    assert game_state.resources.metal == 10  # Metal was spent
    assert SoundEffect.ACTION_SUCCESS in audio.played_sounds
    assert any("Colony repaired" in narration for narration in audio.narrations)

def test_repair_colony_failure_insufficient_resources():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=50, max_hp=100),
        resources=Resources(energy=50, metal=10, food=20)
    )
    
    # Act - simulate user selecting repair option
    management_menu(game_state, audio, test_input="1")
    
    # Assert
    assert game_state.colony.hp == 50  # Colony was not repaired
    assert game_state.resources.metal == 10  # No metal was spent
    assert SoundEffect.ACTION_FAIL in audio.played_sounds
    assert any("Not enough metal" in narration for narration in audio.narrations)

def test_management_menu_keyboard_navigation():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20)
    )
    
    # Act - simulate arrow key navigation
    management_menu(game_state, audio, test_input="down")
    
    # Assert
    assert SoundEffect.MENU_NAV in audio.played_sounds
    assert any("Build Structure" in narration for narration in audio.narrations)

def test_building_construction_in_management():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=100, metal=100, food=20)
    )
    
    # Act - simulate building a solar panel
    management_menu(game_state, audio, test_input="build_solar")
    
    # Assert
    assert len(game_state.buildings) == 1
    assert game_state.buildings[0].type == BuildingType.SOLAR_PANEL
    assert game_state.resources.metal < 100  # Should have spent metal
    assert any("Solar Panel constructed" in narration for narration in audio.narrations)

def test_building_upgrade_in_management():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=100, metal=100, food=20),
        audio=audio  # Pass audio to game_state so it can be used by buildings
    )
    
    # Add a building to upgrade
    building = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    game_state.add_building(building)
    
    # Reset audio service to clear previous messages
    audio = MockAudioService()
    
    # Act - simulate upgrading the solar panel
    management_menu(game_state, audio, test_input="upgrade_0")
    
    # Assert
    assert game_state.buildings[0].level.name == "IMPROVED"
    assert game_state.resources.metal < 100  # Should have spent metal
    assert game_state.resources.energy < 100  # Should have spent energy
    assert any("Upgrade" in narration for narration in audio.narrations)

def test_resource_production_from_buildings():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=50, food=20)
    )
    
    # Add some buildings
    solar_panel = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    farm = Building(type=BuildingType.HYDROPONIC_FARM, audio=audio)
    
    game_state.add_building(solar_panel)
    game_state.add_building(farm)
    
    # Reset resources to a known state
    game_state.resources = Resources(energy=0, metal=0, food=0)
    
    # Act - run production cycle
    game_state.produce_from_buildings()
    
    # Assert
    assert game_state.resources.energy > 0  # Solar panel should have produced energy
    assert game_state.resources.food > 0  # Farm should have produced food
    assert any("Generated" in narration for narration in audio.narrations)

def test_shield_generator_effect():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=100, metal=100, food=20)
    )
    
    # Add a shield generator
    shield_gen = Building(type=BuildingType.SHIELD_GENERATOR, audio=audio)
    game_state.add_building(shield_gen)
    
    # Act - run production cycle (which activates special effects)
    game_state.produce_from_buildings()
    
    # Assert
    assert game_state.shield_strength > 0
    assert any("Shield generator activated" in narration for narration in audio.narrations)

def test_research_lab_tech_point_generation():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=100, metal=100, food=20),
        tech_points=5
    )
    
    # Add a research lab
    lab = Building(type=BuildingType.RESEARCH_LAB, audio=audio)
    game_state.add_building(lab)
    
    # Act - run production cycle
    game_state.produce_from_buildings()
    
    # Assert
    assert game_state.tech_points > 5  # Should have generated tech points
    assert any("Generated" in narration and "tech points" in narration 
               for narration in audio.narrations)
