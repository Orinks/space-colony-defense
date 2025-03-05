import pytest
import os
import json
import tempfile
import shutil
from typing import Dict, Optional
from cli.game.game_state import GameState, Resources, Colony
from cli.game.buildings import Building, BuildingType
from cli.game.audio_service import AudioService

# Test constants
TEST_SAVE_DIR = tempfile.mkdtemp()


def setup_module():
    """Create a temporary directory for test saves"""
    os.makedirs(TEST_SAVE_DIR, exist_ok=True)


def teardown_module():
    """Remove the temporary directory after tests"""
    shutil.rmtree(TEST_SAVE_DIR)


@pytest.fixture
def sample_game_state():
    """Create a sample game state for testing"""
    audio = AudioService(enable_sounds=False, enable_narration=False)
    colony = Colony(hp=75, max_hp=100)
    resources = Resources(energy=50, metal=30, food=20)
    game_state = GameState(
        colony=colony, resources=resources, wave=3, tech_points=5, audio=audio
    )
    
    # Add some buildings
    solar_panel = Building(type=BuildingType.SOLAR_PANEL, audio=audio)
    hydroponic_farm = Building(type=BuildingType.HYDROPONIC_FARM, audio=audio)
    
    # Add buildings to game state
    game_state.buildings.append(solar_panel)
    game_state.buildings.append(hydroponic_farm)
    
    # Ensure resources are exactly as expected for the test
    game_state.resources = Resources(energy=50, metal=30, food=20)
    
    return game_state


def test_save_game_state(sample_game_state):
    """Test saving game state to a file"""
    from cli.game.save_system import save_game
    
    # Save the game
    save_path = os.path.join(TEST_SAVE_DIR, "test_save.json")
    success = save_game(sample_game_state, save_path)
    
    # Verify save was successful
    assert success is True
    assert os.path.exists(save_path)
    
    # Verify file contains valid JSON
    with open(save_path, "r") as f:
        save_data = json.load(f)
    
    # Check saved data matches game state
    assert save_data["colony"]["hp"] == 75
    assert save_data["colony"]["max_hp"] == 100
    assert save_data["resources"]["energy"] == 50
    assert save_data["resources"]["metal"] == 30
    assert save_data["resources"]["food"] == 20
    assert save_data["wave"] == 3
    assert save_data["tech_points"] == 5
    assert len(save_data["buildings"]) == 2
    assert save_data["buildings"][0]["type"] == "SOLAR_PANEL"
    assert save_data["buildings"][1]["type"] == "HYDROPONIC_FARM"


def test_load_game_state():
    """Test loading game state from a file"""
    from cli.game.save_system import load_game
    
    # Create a mock save file
    save_path = os.path.join(TEST_SAVE_DIR, "test_load.json")
    save_data = {
        "colony": {"hp": 65, "max_hp": 100},
        "resources": {"energy": 75, "metal": 45, "food": 15},
        "wave": 4,
        "tech_points": 8,
        "buildings": [
            {"type": "SOLAR_PANEL", "level": "BASIC"},
            {"type": "SHIELD_GENERATOR", "level": "IMPROVED"}
        ],
        "shield_strength": 45,
        "missiles": 2,
        "wave_skip_available": 1
    }
    
    with open(save_path, "w") as f:
        json.dump(save_data, f)
    
    # Load the game
    game_state = load_game(save_path)
    
    # Verify loaded state matches the save file
    assert game_state.colony.hp == 65
    assert game_state.colony.max_hp == 100
    assert game_state.resources.energy == 75
    assert game_state.resources.metal == 45
    assert game_state.resources.food == 15
    assert game_state.wave == 4
    assert game_state.tech_points == 8
    assert len(game_state.buildings) == 2
    assert game_state.buildings[0].type == BuildingType.SOLAR_PANEL
    assert game_state.buildings[0].level.name == "BASIC"
    assert game_state.buildings[1].type == BuildingType.SHIELD_GENERATOR
    assert game_state.buildings[1].level.name == "IMPROVED"
    assert game_state.shield_strength == 45
    assert game_state.missiles == 2
    assert game_state.wave_skip_available == 1


def test_load_nonexistent_file():
    """Test loading from a file that doesn't exist"""
    from cli.game.save_system import load_game
    
    # Try to load a non-existent file
    save_path = os.path.join(TEST_SAVE_DIR, "nonexistent_save.json")
    game_state = load_game(save_path)
    
    # Should return None
    assert game_state is None


def test_save_with_corrupted_data(sample_game_state, monkeypatch):
    """Test saving with corrupted game state"""
    from cli.game.save_system import save_game
    
    # Mock json.dump to raise an exception
    def mock_dump(*args, **kwargs):
        raise json.JSONDecodeError("Mock error", "", 0)
    
    monkeypatch.setattr(json, "dump", mock_dump)
    
    # Try to save the game
    save_path = os.path.join(TEST_SAVE_DIR, "corrupted_save.json")
    success = save_game(sample_game_state, save_path)
    
    # Verify save failed
    assert success is False


def test_load_corrupted_file():
    """Test loading from a corrupted file"""
    from cli.game.save_system import load_game
    
    # Create a corrupted save file
    save_path = os.path.join(TEST_SAVE_DIR, "corrupted_load.json")
    with open(save_path, "w") as f:
        f.write("{This is not valid JSON")
    
    # Try to load the game
    game_state = load_game(save_path)
    
    # Should return None
    assert game_state is None


def test_list_save_files():
    """Test listing available save files"""
    from cli.game.save_system import list_save_files
    
    # Create some test save files
    save_dir = os.path.join(TEST_SAVE_DIR, "list_test")
    os.makedirs(save_dir, exist_ok=True)
    
    save_files = [
        os.path.join(save_dir, "save1.json"),
        os.path.join(save_dir, "save2.json"),
        os.path.join(save_dir, "save3.json")
    ]
    
    for save_file in save_files:
        with open(save_file, "w") as f:
            f.write("{}")
    
    # List save files
    files = list_save_files(save_dir)
    
    # Verify correct files are returned
    assert len(files) == 3
    for save_file in save_files:
        assert os.path.basename(save_file) in [os.path.basename(f) for f in files]


def test_auto_save_directory_creation():
    """Test that the auto-save directory is created if it doesn't exist"""
    from cli.game.save_system import get_save_directory
    
    # Create a temporary path that doesn't exist
    temp_dir = os.path.join(TEST_SAVE_DIR, "nonexistent_dir")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    # Get the save directory, which should create it
    save_dir = get_save_directory(base_dir=temp_dir)
    
    # Verify directory was created
    assert os.path.exists(save_dir)
