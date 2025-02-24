from cli.game.enemy_wave import Enemy, EnemyType, ResourceDrop, ResourceType
from cli.game.game_state import GameState, Resources, Colony
from cli.game.audio_service import AudioService, SoundEffect
from typing import List

class MockAudioService:
    def __init__(self):
        self.played_sounds: List[SoundEffect] = []
        self.narrations: List[str] = []
    
    def play_sound(self, effect: SoundEffect) -> None:
        self.played_sounds.append(effect)
    
    def play_narration(self, text: str) -> None:
        self.narrations.append(text)

def test_resource_drop_on_enemy_defeat():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=0, metal=0, food=0),
        audio=audio
    )
    enemy = Enemy(
        type=EnemyType.BASIC_INVADER, 
        x=0, 
        resource_drop=ResourceDrop(ResourceType.ENERGY, 10)
    )
    
    # Act
    game_state.collect_resource(enemy)
    
    # Assert
    assert game_state.resources.energy == 10
    assert SoundEffect.RESOURCE_CHANGE in audio.played_sounds
    assert any("Energy +10" in narration for narration in audio.narrations)

def test_repair_colony_action():
    # Arrange
    audio = MockAudioService()
    colony = Colony(hp=80, max_hp=100)
    resources = Resources(energy=0, metal=20, food=0)
    
    # Act
    repair_success = colony.repair(resources, audio)
    
    # Assert
    assert repair_success is True
    assert colony.hp == 100
    assert resources.metal == 0
    assert SoundEffect.ACTION_SUCCESS in audio.played_sounds
    assert any("Colony repaired" in narration for narration in audio.narrations)

def test_resource_update_with_audio():
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=10, metal=10, food=10),
        audio=audio
    )
    delta = Resources(energy=5, metal=-3, food=2)
    
    # Act
    game_state.update_resources(delta)
    
    # Assert
    assert game_state.resources.energy == 15
    assert game_state.resources.metal == 7
    assert game_state.resources.food == 12
    assert SoundEffect.RESOURCE_CHANGE in audio.played_sounds
    assert any("Energy +5" in narration for narration in audio.narrations)
    assert any("Metal -3" in narration for narration in audio.narrations)
    assert any("Food +2" in narration for narration in audio.narrations)
