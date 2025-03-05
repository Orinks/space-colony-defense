from enum import Enum, auto
from typing import Dict, Optional
import os
import sys


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
        # Try to load configuration
        try:
            from cli.game.config import get_audio_config
            audio_config = get_audio_config()
            enable_sounds = audio_config.get("enable_sounds", enable_sounds)
            enable_narration = audio_config.get("enable_narration", enable_narration)
            use_running_screen_reader = audio_config.get("use_running_screen_reader", True)
            print(f"Loaded audio settings from config: enable_sounds={enable_sounds}, enable_narration={enable_narration}, use_running_screen_reader={use_running_screen_reader}")
        except ImportError:
            # Config module not available, use defaults
            print("Config module not available, using default audio settings")
            use_running_screen_reader = True
            pass
            
        self.enable_sounds = enable_sounds
        self.enable_narration = enable_narration
        self.sound_volumes: Dict[SoundEffect, float] = {
            effect: 1.0 for effect in SoundEffect
        }
        self.narration_volume = 1.0
        self.sral = None
        
        # Try to initialize SRAL, but don't crash if it fails
        try:
            # Try to use the direct SRAL module first
            # Check if we should use running screen reader or SAPI
            import sral
            from cli.sral_wrapper import SRALEngines
            
            if use_running_screen_reader:
                # Initialize with engines_exclude=0 to use any available engine
                # This will make SRAL use the currently active screen reader if available
                engines_exclude = 0
                print("Initializing SRAL to use running screen reader")
            else:
                # Initialize SRAL to use SAPI specifically by excluding all other engines
                engines_exclude = (
                    SRALEngines.NVDA | 
                    SRALEngines.JAWS | 
                    SRALEngines.SPEECH_DISPATCHER | 
                    SRALEngines.UIA | 
                    SRALEngines.AV_SPEECH | 
                    SRALEngines.NARRATOR
                )
                print(f"Initializing SRAL to use SAPI only with engines_exclude={engines_exclude}")
            
            self.sral = sral.Sral(engines_exclude=engines_exclude)
            
            # Verify which engine is being used
            current_engine = self.sral.get_current_engine()
            print(f"SRAL initialized with engine: {current_engine}")
            
            if not use_running_screen_reader and current_engine != SRALEngines.SAPI:
                print(f"Warning: Expected SAPI engine but got engine {current_engine}")
        except Exception as e:
            print(f"Could not initialize SRAL using direct module: {e}")
            print("Falling back to console output for narration")

    def play_sound(self, effect: SoundEffect) -> None:
        """Play a sound effect. This is a stub that will be replaced with real audio."""
        if self.enable_sounds:
            volume = self.sound_volumes.get(effect, 1.0)
            # In a real implementation, this would play the actual sound file
            # For example: pygame.mixer.Sound(f"sounds/{effect.name.lower()}.wav").play()
            print(f"Playing sound: {effect.name} at volume {volume}")

    def play_narration(self, text: str) -> None:
        """Play narrated text using SRAL if available, otherwise fall back to console."""
        if self.enable_narration:
            if self.sral:
                try:
                    # Use SRAL for text-to-speech with interrupt=False to prevent cutting off previous speech
                    self.sral.speak(text, interrupt=False)
                except Exception as e:
                    print(f"Error using SRAL for speech: {e}")
                    print(f"Narrating: {text} at volume {self.narration_volume}")
            else:
                # Fall back to console output
                print(f"Narrating: {text} at volume {self.narration_volume}")

    def set_sound_volume(self, effect: SoundEffect, volume: float) -> None:
        """Set the volume for a specific sound effect (0.0 to 1.0)"""
        self.sound_volumes[effect] = max(0.0, min(1.0, volume))

    def set_narration_volume(self, volume: float) -> None:
        """Set the volume for narration (0.0 to 1.0)"""
        self.narration_volume = max(0.0, min(1.0, volume))
        # If SRAL supports volume control in the future, we could set it here

    def toggle_sounds(self, enable: Optional[bool] = None) -> None:
        """Toggle or set the enable_sounds flag"""
        if enable is not None:
            self.enable_sounds = enable
        else:
            self.enable_sounds = not self.enable_sounds
            
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["enable_sounds"] = self.enable_sounds
            save_audio_config(audio_config)
            print(f"Saved audio config: enable_sounds={self.enable_sounds}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def toggle_narration(self, enable: Optional[bool] = None) -> None:
        """Toggle or set the enable_narration flag"""
        if enable is not None:
            self.enable_narration = enable
        else:
            self.enable_narration = not self.enable_narration
            if self.sral and not self.enable_narration:
                try:
                    # Stop any ongoing speech when disabling narration
                    self.sral.stop_speech()
                except Exception as e:
                    print(f"Error stopping SRAL speech: {e}")
                    
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["enable_narration"] = self.enable_narration
            save_audio_config(audio_config)
            print(f"Saved audio config: enable_narration={self.enable_narration}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def pause_speech(self) -> None:
        """Pause the current speech if SRAL is available"""
        if self.sral:
            try:
                self.sral.pause_speech()
            except Exception as e:
                print(f"Error pausing SRAL speech: {e}")

    def resume_speech(self) -> None:
        """Resume paused speech if SRAL is available"""
        if self.sral:
            try:
                self.sral.resume_speech()
            except Exception as e:
                print(f"Error resuming SRAL speech: {e}")

    def stop_speech(self) -> None:
        """Stop the current speech if SRAL is available"""
        if self.sral:
            try:
                self.sral.stop_speech()
            except Exception as e:
                print(f"Error stopping SRAL speech: {e}")

    def set_speech_rate(self, rate: int) -> None:
        """Set the speech rate (0-100) if SRAL is available"""
        if self.sral:
            try:
                self.sral.set_rate(rate)
            except Exception as e:
                print(f"Error setting SRAL speech rate: {e}")

    def __del__(self) -> None:
        """Clean up resources when the service is destroyed"""
        # SRAL handles cleanup in its own __del__ method
        pass
