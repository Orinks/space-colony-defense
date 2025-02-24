from enum import Enum, auto


class SoundEffect(Enum):
    TURRET_MOVE = auto()
    TURRET_SHOOT = auto()
    ENEMY_HIT = auto()
    ACTION_SUCCESS = auto()
    ACTION_FAIL = auto()
    MENU_NAV = auto()
    CONSTRUCTION_START = auto()
    CONSTRUCTION_COMPLETE = auto()
    RESOURCE_CHANGE = auto()


class AudioService:
    def play_sound(self, effect: SoundEffect) -> None:
        """Play a sound effect. This is a stub that will be replaced with real audio."""
        pass

    def play_narration(self, text: str) -> None:
        """Play narrated text. This is a stub that will be replaced with real audio."""
        pass
