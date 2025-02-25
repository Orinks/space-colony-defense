import pygame
import sys
import os
from typing import Dict, Optional, Tuple, List, Any, cast
from cli.game.game_loop import GameLoop
from cli.game.audio_service import AudioService, SoundEffect
from cli.game.menu_system import (
    MenuSystem,
    MainMenuOption,
    OptionsMenuOption,
    MenuOption,
)
from cli.game.enemy_wave import EnemyType


class PygameAudioService(AudioService):
    """Pygame implementation of the AudioService"""

    def __init__(
        self, enable_sounds: bool = True, enable_narration: bool = True
    ) -> None:
        super().__init__(enable_sounds, enable_narration)
        self.sounds: Dict[SoundEffect, Optional[pygame.mixer.Sound]] = {
            effect: None for effect in SoundEffect
        }
        # Default speech rate (words per minute): lower = slower, higher = faster
        self.speech_rate = 150  # Changed from 180 to 150 for slower speech
        self.initialize_audio()
        
        # Initialize text-to-speech engine
        self.tts_engine = None
        self.voice_speaker = None
        
        # Try pyttsx3 first
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # List available voices
            voices = self.tts_engine.getProperty('voices')
            print(f"Found {len(voices)} voices using pyttsx3:")
            
            # Find female voice - on Windows, female voices typically have "female" in their ID or name
            female_voice = None
            default_voice = None
            
            for i, voice in enumerate(voices):
                voice_name = voice.name
                voice_id = voice.id
                gender = getattr(voice, 'gender', 'unknown')
                
                # Save the first voice as default
                if i == 0:
                    default_voice = voice
                
                # Print voice info
                print(f"  Voice {i+1}: ID={voice_id}, Name={voice_name}, Gender={gender}")
                
                # Look for female voice indicators
                if (gender == 'female' or 
                    'female' in voice_id.lower() or 
                    'woman' in voice_name.lower() or
                    'zira' in voice_name.lower()):  # Microsoft Zira is a common female voice
                    female_voice = voice
                    print(f"  *** Detected as female voice: {voice_name} ***")
            
            # Set female voice if found, otherwise use default
            if female_voice:
                self.tts_engine.setProperty('voice', female_voice.id)
                print(f"Set voice to female voice: {female_voice.name}")
            else:
                print("No female voice found, using default voice")
            
            # Set speech rate (default is 200)
            self.tts_engine.setProperty('rate', self.speech_rate)
            
            # Set initial volume
            self.tts_engine.setProperty('volume', self.narration_volume)
            
            print(f"Text-to-speech engine initialized successfully (Rate: {self.speech_rate}, Volume: {self.narration_volume})")
            
        except Exception as e:
            print(f"pyttsx3 initialization failed: {e}")
            print("Trying alternative Windows Speech API...")
            
            # Fall back to direct Windows Speech API if pyttsx3 fails
            try:
                import win32com.client
                self.voice_speaker = win32com.client.Dispatch("SAPI.SpVoice")
                
                # List available voices
                voices = self.voice_speaker.GetVoices()
                print(f"Found {voices.Count} voices using Windows Speech API:")
                
                # Find female voice
                for i in range(voices.Count):
                    voice = voices.Item(i)
                    voice_id = voice.Id
                    voice_name = voice.GetDescription()
                    print(f"  Voice {i+1}: ID={voice_id}, Name={voice_name}")
                    
                    # Look for female voice indicators
                    if ('female' in voice_name.lower() or 
                        'woman' in voice_name.lower() or 
                        'zira' in voice_name.lower()):
                        self.voice_speaker.Voice = voice
                        print(f"  *** Set to female voice: {voice_name} ***")
                        break
                
                # Set rate (-10 to 10, with 0 being normal)
                # Convert our 50-250 scale to -10 to 10 scale
                # 150 (our default) maps to 0 (normal speed)
                rate_normalized = int((self.speech_rate - 150) / 10)
                self.voice_speaker.Rate = rate_normalized
                
                # Set volume (0-100)
                self.voice_speaker.Volume = int(self.narration_volume * 100)
                
                print(f"Windows Speech API initialized successfully (Rate: {rate_normalized}, Volume: {int(self.narration_volume * 100)})")
                
            except Exception as e:
                print(f"Windows Speech API initialization failed: {e}")
                print("Falling back to text-only narration")
        
        print("Speech rate can be adjusted with + and - keys")
        print("Sound volume can be adjusted with [ and ] keys")
        print("Narration volume can be adjusted with { and } keys")
    
    def set_speech_rate(self, rate: int) -> None:
        """Set the speech rate (words per minute)"""
        # Keep rate within reasonable bounds (50-250)
        self.speech_rate = max(50, min(250, rate))
        
        if self.tts_engine is not None:
            self.tts_engine.setProperty('rate', self.speech_rate)
            print(f"Speech rate set to {self.speech_rate}")
            
            # Announce the new rate
            self.play_narration(f"Speech rate {self.speech_rate}")
        elif self.voice_speaker is not None:
            # Convert our 50-250 scale to -10 to 10 scale
            rate_normalized = int((self.speech_rate - 150) / 10)
            self.voice_speaker.Rate = rate_normalized
            print(f"Speech rate set to {self.speech_rate} (Windows API rate: {rate_normalized})")
            
            # Announce the new rate
            self.play_narration(f"Speech rate {self.speech_rate}")
    
    def increase_speech_rate(self, amount: int = 10) -> None:
        """Increase the speech rate"""
        self.set_speech_rate(self.speech_rate + amount)
    
    def decrease_speech_rate(self, amount: int = 10) -> None:
        """Decrease the speech rate"""
        self.set_speech_rate(self.speech_rate - amount)
    
    def set_voice_by_id(self, voice_id: str) -> bool:
        """Set the voice by ID"""
        if self.tts_engine is None:
            return False
            
        try:
            self.tts_engine.setProperty('voice', voice_id)
            return True
        except:
            print(f"Failed to set voice with ID: {voice_id}")
            return False
    
    def set_voice_by_index(self, index: int) -> bool:
        """Set the voice by index in the voices list"""
        if self.tts_engine is not None:
            try:
                voices = self.tts_engine.getProperty('voices')
                if 0 <= index < len(voices):
                    self.tts_engine.setProperty('voice', voices[index].id)
                    print(f"Set voice to: {voices[index].name}")
                    return True
                else:
                    print(f"Voice index out of range: {index}, max: {len(voices)-1}")
                    return False
            except:
                print(f"Failed to set voice with index: {index}")
                return False
        elif self.voice_speaker is not None:
            try:
                voices = self.voice_speaker.GetVoices()
                if 0 <= index < voices.Count:
                    self.voice_speaker.Voice = voices.Item(index)
                    print(f"Set voice to: {voices.Item(index).GetDescription()}")
                    return True
                else:
                    print(f"Voice index out of range: {index}, max: {voices.Count-1}")
                    return False
            except:
                print(f"Failed to set voice with index: {index}")
                return False
        return False
    
    def set_female_voice(self) -> bool:
        """Attempt to set a female voice"""
        if self.tts_engine is not None:
            try:
                voices = self.tts_engine.getProperty('voices')
                
                # First look for voices explicitly marked as female
                for voice in voices:
                    gender = getattr(voice, 'gender', 'unknown')
                    if gender.lower() == 'female':
                        self.tts_engine.setProperty('voice', voice.id)
                        print(f"Set voice to female voice: {voice.name}")
                        return True
                
                # Then try to find voices with 'female', 'woman', or 'zira' in their name/id
                for voice in voices:
                    voice_id = voice.id.lower()
                    voice_name = voice.name.lower()
                    
                    if ('female' in voice_id or 'woman' in voice_name or 
                        'zira' in voice_name or 'microsoft zira' in voice_name):
                        self.tts_engine.setProperty('voice', voice.id)
                        print(f"Set voice to likely female voice: {voice.name}")
                        return True
                
                # For Microsoft SAPI5 on Windows, try voice #1 which is often female (Zira)
                if len(voices) > 1:
                    self.tts_engine.setProperty('voice', voices[1].id)
                    print(f"Set voice to second voice (likely female): {voices[1].name}")
                    return True
                    
                print("No female voice found")
                return False
            except Exception as e:
                print(f"Error setting female voice with pyttsx3: {e}")
                return False
        elif self.voice_speaker is not None:
            try:
                voices = self.voice_speaker.GetVoices()
                
                # Try to find voices with 'female', 'woman', or 'zira' in their name
                for i in range(voices.Count):
                    voice = voices.Item(i)
                    voice_name = voice.GetDescription().lower()
                    
                    if ('female' in voice_name or 'woman' in voice_name or 
                        'zira' in voice_name or 'microsoft zira' in voice_name):
                        self.voice_speaker.Voice = voice
                        print(f"Set voice to likely female voice: {voice.GetDescription()}")
                        return True
                
                # For Microsoft SAPI5 on Windows, try voice #1 which is often female (Zira)
                if voices.Count > 1:
                    self.voice_speaker.Voice = voices.Item(1)
                    print(f"Set voice to second voice (likely female): {voices.Item(1).GetDescription()}")
                    return True
                    
                print("No female voice found")
                return False
            except Exception as e:
                print(f"Error setting female voice with Windows Speech API: {e}")
                return False
        return False

    def initialize_audio(self) -> None:
        """Initialize the Pygame mixer and load sound files"""
        try:
            pygame.mixer.init()
            
            # Check if sounds directory exists
            sound_dir = "sounds"
            if os.path.exists(sound_dir):
                # Load sound files if they exist
                for effect in SoundEffect:
                    filename = os.path.join(sound_dir, f"{effect.name.lower()}.wav")
                    if os.path.exists(filename):
                        try:
                            self.sounds[effect] = pygame.mixer.Sound(filename)
                            print(f"Loaded sound: {filename}")
                        except pygame.error as e:
                            print(f"Error loading sound {filename}: {e}")
            
            print("Pygame audio initialized successfully")
        except pygame.error as e:
            print(f"Warning: Pygame mixer initialization failed: {e}")
            print("Falling back to text-based audio feedback")

    def play_sound(self, effect: SoundEffect) -> None:
        """Play a sound effect using Pygame mixer"""
        if not self.enable_sounds:
            return

        volume = self.sound_volumes.get(effect, 1.0)

        # If we have a loaded sound, play it
        if self.sounds[effect] is not None:
            sound = self.sounds[effect]
            if sound is not None:  # Extra check for mypy
                sound.set_volume(volume)
                sound.play()
        else:
            # Fall back to text output for now
            print(f"Playing sound: {effect.name} at volume {volume}")

    def play_narration(self, text: str) -> None:
        """Play narrated text using a text-to-speech engine"""
        if not self.enable_narration:
            return

        # Always print to console for accessibility
        print(f"Narrating: {text} at volume {self.narration_volume}")
        
        # Use text-to-speech engine if available
        if self.tts_engine is not None:
            try:
                # Set the volume
                self.tts_engine.setProperty("volume", self.narration_volume)
                
                # Queue the text to be spoken
                self.tts_engine.say(text)
                
                # Play the queued text
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Error with pyttsx3 narration: {e}")
                # Fall back to Windows Speech API if pyttsx3 fails
                if self.voice_speaker is None:
                    try:
                        import win32com.client
                        self.voice_speaker = win32com.client.Dispatch("SAPI.SpVoice")
                        self.voice_speaker.Volume = int(self.narration_volume * 100)
                        rate_normalized = int((self.speech_rate - 150) / 10)
                        self.voice_speaker.Rate = rate_normalized
                        print("Falling back to Windows Speech API")
                    except Exception as e2:
                        print(f"Could not initialize Windows Speech API: {e2}")
                
                if self.voice_speaker is not None:
                    try:
                        self.voice_speaker.Speak(text)
                    except Exception as e3:
                        print(f"Error with Windows Speech API: {e3}")
        
        # Use Windows Speech API if pyttsx3 is not available
        elif self.voice_speaker is not None:
            try:
                # Set the volume (0-100)
                self.voice_speaker.Volume = int(self.narration_volume * 100)
                
                # Speak the text
                self.voice_speaker.Speak(text)
            except Exception as e:
                print(f"Error with Windows Speech API narration: {e}")
    
    def set_narration_volume(self, volume: float) -> None:
        """Set the volume for narration (0.0 to 1.0)"""
        # Call the parent method to update the narration_volume property
        super().set_narration_volume(volume)
        
        # Also update the TTS engine if available
        if self.tts_engine is not None:
            try:
                self.tts_engine.setProperty("volume", self.narration_volume)
            except Exception as e:
                print(f"Error setting pyttsx3 volume: {e}")
        
        if self.voice_speaker is not None:
            try:
                self.voice_speaker.Volume = int(self.narration_volume * 100)
            except Exception as e:
                print(f"Error setting Windows Speech API volume: {e}")
                
        print(f"Narration volume set to {self.narration_volume}")
        
        # Announce the new volume
        self.play_narration(f"Narration volume {int(self.narration_volume * 100)}%")
    
    def increase_narration_volume(self, amount: float = 0.1) -> None:
        """Increase narration volume"""
        self.set_narration_volume(self.narration_volume + amount)
    
    def decrease_narration_volume(self, amount: float = 0.1) -> None:
        """Decrease narration volume"""
        self.set_narration_volume(self.narration_volume - amount)
    
    def set_sound_effect_volume(self, volume: float) -> None:
        """Set volume for all sound effects"""
        for effect in SoundEffect:
            self.set_sound_volume(effect, volume)
        print(f"All sound effects set to volume {volume}")
        
        # Announce the change
        self.play_narration(f"Sound effect volume {int(volume * 100)}%")
        
        # Play a sound to demonstrate new volume
        self.play_sound(SoundEffect.MENU_NAV)
    
    def increase_sound_volume(self, amount: float = 0.1) -> None:
        """Increase sound effect volume"""
        # Get current volume (use first effect as reference)
        current = self.sound_volumes.get(SoundEffect.MENU_NAV, 1.0)
        new_volume = min(1.0, current + amount)
        self.set_sound_effect_volume(new_volume)
    
    def decrease_sound_volume(self, amount: float = 0.1) -> None:
        """Decrease sound effect volume"""
        # Get current volume (use first effect as reference)
        current = self.sound_volumes.get(SoundEffect.MENU_NAV, 1.0)
        new_volume = max(0.0, current - amount)
        self.set_sound_effect_volume(new_volume)


class PygameInterface:
    """Pygame interface for the Space Colony Defense game"""

    def __init__(self, width: int = 800, height: int = 600) -> None:
        """Initialize the Pygame interface"""
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Space Colony Defense")

        # Initialize clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Initialize audio service
        self.audio = PygameAudioService()
        
        # Try to set female voice
        if isinstance(self.audio, PygameAudioService):
            self.audio.set_female_voice()

        # Initialize game loop
        self.game = GameLoop(audio_service=self.audio)

        # Font for text rendering
        self.font = pygame.font.SysFont("Arial", 24)  # Use a default font name

        # Colors
        self.colors = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "gray": (128, 128, 128),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
        }

    def run(self) -> None:
        """Run the main game loop"""
        running = True

        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self.handle_keydown(event.key)

            # Update game state
            self.game.update()

            # Render the game
            self.render()

            # Cap the frame rate
            self.clock.tick(self.fps)

        # Clean up
        pygame.quit()
        sys.exit()

    def handle_keydown(self, key: int) -> bool:
        """Handle keyboard input"""
        # Volume and rate controls (available in all game states)
        if isinstance(self.audio, PygameAudioService):
            # Speech rate controls
            if key == pygame.K_EQUALS or key == pygame.K_PLUS:  # + key
                self.audio.increase_speech_rate(10)
                return True
            elif key == pygame.K_MINUS:  # - key
                self.audio.decrease_speech_rate(10)
                return True
                
            # Sound volume controls
            elif key == pygame.K_RIGHTBRACKET:  # ] key
                self.audio.increase_sound_volume(0.1)
                return True
            elif key == pygame.K_LEFTBRACKET:  # [ key
                self.audio.decrease_sound_volume(0.1)
                return True
                
            # Narration volume controls - use shift+[ and shift+] instead of { and }
            # since pygame doesn't have direct constants for these
            elif key == pygame.K_RIGHTBRACKET and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Shift+]
                self.audio.increase_narration_volume(0.1)
                return True
            elif key == pygame.K_LEFTBRACKET and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Shift+[
                self.audio.decrease_narration_volume(0.1)
                return True
        
        # Main menu navigation
        if self.game.in_main_menu or self.game.is_management_phase:
            if key == pygame.K_UP:
                self.game.handle_input("up")
            elif key == pygame.K_DOWN:
                self.game.handle_input("down")
            elif key == pygame.K_RETURN:
                return self.game.handle_input("select")
            elif key == pygame.K_ESCAPE:
                if not self.game.in_main_menu:
                    self.game.handle_input("menu")

        # Game controls
        elif self.game.game_running:
            if key == pygame.K_LEFT:
                self.game.handle_input("left")
            elif key == pygame.K_RIGHT:
                self.game.handle_input("right")
            elif key == pygame.K_SPACE:
                self.game.handle_input("shoot")
            elif key == pygame.K_s:
                self.game.handle_input("status")
            elif key == pygame.K_ESCAPE:
                self.game.handle_input("menu")

        # Game over controls
        elif self.game.is_game_over:
            if key == pygame.K_r:
                self.game.handle_input("restart")
            elif key == pygame.K_m:
                self.game.handle_input("menu")
            elif key == pygame.K_ESCAPE:
                return False  # Exit the game

        return True  # Continue running

    def render(self) -> None:
        """Render the game state to the screen"""
        # Clear the screen
        self.screen.fill(self.colors["black"])

        # Render different screens based on game state
        if self.game.in_main_menu:
            self.render_main_menu()
        elif self.game.is_management_phase:
            self.render_management_phase()
        elif self.game.is_game_over:
            self.render_game_over()
        elif self.game.game_running:
            self.render_game()

        # Update the display
        pygame.display.flip()

    def render_main_menu(self) -> None:
        """Render the main menu"""
        title = self.font.render("SPACE COLONY DEFENSE", True, self.colors["white"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        # Render menu options
        y_pos = 200
        for i, option in enumerate(self.game.menu.main_menu_options):
            color = (
                self.colors["green"]
                if i == self.game.menu.current_index
                else self.colors["white"]
            )
            text = self.font.render(option.name.replace("_", " "), True, color)
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y_pos))
            y_pos += 50

        # Render controls help
        controls = self.font.render(
            "Use UP/DOWN arrows to navigate, ENTER to select", True, self.colors["gray"]
        )
        self.screen.blit(
            controls, (self.width // 2 - controls.get_width() // 2, self.height - 50)
        )

    def render_management_phase(self) -> None:
        """Render the management phase"""
        title = self.font.render("MANAGEMENT PHASE", True, self.colors["white"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Render colony status
        colony_hp = self.font.render(
            f"Colony HP: {self.game.game_state.colony.hp}/{self.game.game_state.colony.max_hp}",
            True,
            self.colors["white"],
        )
        self.screen.blit(colony_hp, (50, 100))

        # Render resources
        resources = self.font.render(
            f"Energy: {self.game.game_state.resources.energy}  "
            f"Metal: {self.game.game_state.resources.metal}  "
            f"Food: {self.game.game_state.resources.food}",
            True,
            self.colors["white"],
        )
        self.screen.blit(resources, (50, 130))

        # Render menu options
        y_pos = 200
        for i, option in enumerate(self.game.menu.options):
            color = (
                self.colors["green"]
                if i == self.game.menu.current_index
                else self.colors["white"]
            )
            text = self.font.render(option.name, True, color)
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y_pos))
            y_pos += 50

        # Render controls help
        controls = self.font.render(
            "Use UP/DOWN arrows to navigate, ENTER to select, ESC for main menu",
            True,
            self.colors["gray"],
        )
        self.screen.blit(
            controls, (self.width // 2 - controls.get_width() // 2, self.height - 50)
        )

    def render_game_over(self) -> None:
        """Render the game over screen"""
        title = self.font.render("GAME OVER", True, self.colors["red"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        wave = self.font.render(
            f"You survived until wave {self.game.game_state.wave}",
            True,
            self.colors["white"],
        )
        self.screen.blit(wave, (self.width // 2 - wave.get_width() // 2, 150))

        tech = self.font.render(
            f"Tech points earned: {self.game.game_state.tech_points}",
            True,
            self.colors["white"],
        )
        self.screen.blit(tech, (self.width // 2 - tech.get_width() // 2, 200))

        restart = self.font.render(
            "Press R to restart, M for main menu, ESC to quit",
            True,
            self.colors["gray"],
        )
        self.screen.blit(
            restart, (self.width // 2 - restart.get_width() // 2, self.height - 50)
        )

    def render_game(self) -> None:
        """Render the main game screen"""
        # Render wave information
        wave = self.font.render(
            f"Wave {self.game.game_state.wave}", True, self.colors["white"]
        )
        self.screen.blit(wave, (10, 10))

        # Render colony status
        colony_hp = self.font.render(
            f"Colony: {self.game.game_state.colony.hp}/{self.game.game_state.colony.max_hp}",
            True,
            self.colors["white"],
        )
        self.screen.blit(colony_hp, (10, 40))

        # Render turret shield
        shield = self.font.render(
            f"Shield: {self.game.turret.shield}/{self.game.turret.max_shield}",
            True,
            (
                self.colors["blue"]
                if not self.game.turret.is_damaged
                else self.colors["red"]
            ),
        )
        self.screen.blit(shield, (10, 70))

        # Render resources
        resources = self.font.render(
            f"Energy: {self.game.game_state.resources.energy}  "
            f"Metal: {self.game.game_state.resources.metal}  "
            f"Food: {self.game.game_state.resources.food}",
            True,
            self.colors["white"],
        )
        self.screen.blit(resources, (self.width - resources.get_width() - 10, 10))

        # Render turret
        turret_x = self.game.turret.position * (self.width // 10)
        pygame.draw.rect(
            self.screen,
            (
                self.colors["blue"]
                if not self.game.turret.is_damaged
                else self.colors["red"]
            ),
            (turret_x - 15, self.height - 50, 30, 30),
        )

        # Render enemies
        for enemy in self.game.enemies:
            enemy_x = enemy.x * (self.width // 10)
            enemy_y = enemy.y * 50 + 100

            # Different colors for different enemy types
            if enemy.type == EnemyType.BASIC_INVADER:
                color = self.colors["red"]
                size = 15
            elif enemy.type == EnemyType.ARMORED_SHIP:
                color = self.colors["gray"]
                size = 20
            else:  # SWARMER
                color = self.colors["green"]
                size = 10

            pygame.draw.circle(self.screen, color, (enemy_x, enemy_y), size)

        # Render projectiles
        for projectile in self.game.projectiles:
            proj_x = projectile.position * (self.width // 10)
            pygame.draw.rect(
                self.screen, self.colors["white"], (proj_x - 2, self.height - 60, 4, 10)
            )

        # Render controls help
        controls = self.font.render(
            "LEFT/RIGHT to move, SPACE to shoot, S for status, ESC for menu",
            True,
            self.colors["gray"],
        )
        self.screen.blit(
            controls, (self.width // 2 - controls.get_width() // 2, self.height - 20)
        )
