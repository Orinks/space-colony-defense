from enum import Enum, auto
from typing import Dict, Optional


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
    def __init__(
        self, enable_sounds: bool = True, enable_narration: bool = True
    ) -> None:
        """Initialize the audio service with configurable settings"""
        self.enable_sounds = enable_sounds
        self.enable_narration = enable_narration
        self.sound_volumes: Dict[SoundEffect, float] = {
            effect: 1.0 for effect in SoundEffect
        }
        self.narration_volume = 1.0

    def play_sound(self, effect: SoundEffect) -> None:
        """Play a sound effect. This is a stub that will be replaced with real audio."""
        if self.enable_sounds:
            volume = self.sound_volumes.get(effect, 1.0)
            # In a real implementation, this would play the actual sound file
            # For example: pygame.mixer.Sound(f"sounds/{effect.name.lower()}.wav").play()
            print(f"Playing sound: {effect.name} at volume {volume}")

    def play_narration(self, text: str) -> None:
        """Play narrated text. This is a stub that will be replaced with real audio."""
        if self.enable_narration:
            # In a real implementation, this would use a text-to-speech engine
            # For example: pyttsx3.speak(text)
            print(f"Narrating: {text} at volume {self.narration_volume}")

    def set_sound_volume(self, effect: SoundEffect, volume: float) -> None:
        """Set the volume for a specific sound effect (0.0 to 1.0)"""
        self.sound_volumes[effect] = max(0.0, min(1.0, volume))

    def set_narration_volume(self, volume: float) -> None:
        """Set the volume for narration (0.0 to 1.0)"""
        self.narration_volume = max(0.0, min(1.0, volume))

    def toggle_sounds(self, enable: Optional[bool] = None) -> None:
        """Toggle or set the enable_sounds flag"""
        if enable is not None:
            self.enable_sounds = enable
        else:
            self.enable_sounds = not self.enable_sounds

    def toggle_narration(self, enable: Optional[bool] = None) -> None:
        """Toggle or set the enable_narration flag"""
        if enable is not None:
            self.enable_narration = enable
        else:
            self.enable_narration = not self.enable_narration
