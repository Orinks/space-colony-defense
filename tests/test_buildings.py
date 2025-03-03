import pytest
from typing import List
from cli.game.buildings import Building, BuildingType, BuildingLevel
from cli.game.game_state import Resources
from cli.game.audio_service import AudioService, SoundEffect

class MockAudioService:
    def __init__(self):
        self.played_sounds: List[SoundEffect] = []
        self.narrations: List[str] = []
    
    def play_sound(self, effect: SoundEffect) -> None:
        self.played_sounds.append(effect)
    
    def play_narration(self, text: str) -> None:
        self.narrations.append(text)

def test_solar_panel_construction():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=20, metal=50, food=10)
    building = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    
    # Act
    success = building.construct(resources)
    
    # Assert
    assert success is True
    assert resources.metal == 25  # Should cost 25 metal
    assert SoundEffect.CONSTRUCTION_START in audio.played_sounds
    assert SoundEffect.CONSTRUCTION_COMPLETE in audio.played_sounds
    assert any("Building Solar Panel" in narration for narration in audio.narrations)

def test_farm_construction():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=50, metal=40, food=10)
    building = Building(type=BuildingType.HYDROPONIC_FARM, audio=audio)
    
    # Act
    success = building.construct(resources)
    
    # Assert
    assert success is True
    assert resources.metal == 20  # Should cost 20 metal
    assert resources.energy == 35  # Should cost 15 energy
    assert any("Building Hydroponic Farm" in narration for narration in audio.narrations)

def test_insufficient_resources_prevents_construction():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=10, metal=10, food=10)
    building = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    
    # Act
    success = building.construct(resources)
    
    # Assert
    assert success is False
    assert resources.metal == 10  # Resources shouldn't be spent
    assert SoundEffect.ACTION_FAIL in audio.played_sounds
    assert any("Insufficient resources" in narration for narration in audio.narrations)

def test_building_produces_resources():
    # Arrange
    audio = MockAudioService()
    building = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    resources = Resources(energy=0, metal=50, food=0)
    
    # Act
    building.construct(resources)
    building.produce_resources(resources)
    
    # Assert
    assert resources.energy == 8  # Solar panel should produce 8 energy
    assert any("Generated 8 energy" in narration for narration in audio.narrations)

def test_new_building_type_shield_generator():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=100, metal=100, food=10)
    building = Building(type=BuildingType.SHIELD_GENERATOR, audio=audio)
    
    # Act
    success = building.construct(resources)
    
    # Assert
    assert success is True
    assert resources.metal == 55  # Should cost 45 metal
    assert resources.energy == 70  # Should cost 30 energy
    assert any("Building Shield Generator" in narration for narration in audio.narrations)

def test_building_upgrade():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=100, metal=100, food=10)
    building = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    
    # Act
    building.construct(resources)
    initial_production = building.get_production_rate()
    success = building.upgrade(resources)
    
    # Assert
    assert success is True
    assert building.level == BuildingLevel.IMPROVED
    assert resources.metal == 60  # 25 for construction + 15 for upgrade
    assert resources.energy == 80  # 5 for construction + 15 for upgrade
    assert building.get_production_rate() > initial_production
    assert SoundEffect.CONSTRUCTION_COMPLETE in audio.played_sounds
    assert any("Upgraded Solar Panel" in narration for narration in audio.narrations)

def test_building_maximum_level():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=200, metal=200, food=50)
    building = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    
    # Act - Upgrade to level 3 (maximum)
    building.construct(resources)
    building.upgrade(resources)  # Level 2
    building.upgrade(resources)  # Level 3
    max_level_production = building.get_production_rate()
    success = building.upgrade(resources)  # Try to upgrade beyond max
    
    # Assert
    assert success is False
    assert building.level == BuildingLevel.ADVANCED
    assert building.get_production_rate() == max_level_production
    assert SoundEffect.ACTION_FAIL in audio.played_sounds
    assert any("Maximum level reached" in narration for narration in audio.narrations)

def test_multiple_buildings_production():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=100, metal=100, food=10)
    solar_panel = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    hydroponic_farm = Building(type=BuildingType.HYDROPONIC_FARM, audio=audio)
    
    # Act
    solar_panel.construct(resources)
    hydroponic_farm.construct(resources)
    
    initial_energy = resources.energy
    initial_food = resources.food
    
    solar_panel.produce_resources(resources)
    hydroponic_farm.produce_resources(resources)
    
    # Assert
    assert resources.energy > initial_energy
    assert resources.food > initial_food
    assert any("Generated 8 energy" in narration for narration in audio.narrations)
    assert any("Generated 5 food" in narration for narration in audio.narrations)

def test_shield_generator_special_effect():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=100, metal=100, food=10)
    shield_generator = Building(type=BuildingType.SHIELD_GENERATOR, audio=audio)
    
    # Act
    shield_generator.construct(resources)
    shield_strength = shield_generator.get_special_effect()
    
    # Assert
    assert shield_strength > 0
    assert shield_generator.has_special_effect() is True
    shield_generator.apply_special_effect(None)  # Should not raise exception
    assert any("Shield generator activated" in narration for narration in audio.narrations)

def test_research_lab_tech_points_generation():
    # Arrange
    audio = MockAudioService()
    resources = Resources(energy=100, metal=100, food=10)
    research_lab = Building(type=BuildingType.RESEARCH_LAB, audio=audio)
    
    # Act
    research_lab.construct(resources)
    tech_points_before = 0
    tech_points_after = research_lab.produce_tech_points(tech_points_before)
    
    # Assert
    assert tech_points_after > tech_points_before
    assert any("Generated 1 tech points" in narration for narration in audio.narrations)
