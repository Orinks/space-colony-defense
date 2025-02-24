import pytest
from typing import List
from cli.game.buildings import Building, BuildingType
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
    assert resources.metal == 20  # Should cost 30 metal
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
    assert resources.energy == 30  # Should cost 20 energy
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
    assert resources.energy == 5  # Solar panel should produce 5 energy
    assert any("Generated 5 energy" in narration for narration in audio.narrations)
