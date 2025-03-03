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
from cli.sral_wrapper import SRALEngines
from cli.game.config import get_audio_config, save_audio_config


class PygameAudioService(AudioService):
    """Pygame implementation of the AudioService"""

    def __init__(
        self, enable_sounds: bool = True, enable_narration: bool = True
    ) -> None:
        # Load audio configuration before calling parent constructor
        # This ensures the correct speech mode is used from the start
        try:
            from cli.game.config import get_audio_config
            audio_config = get_audio_config()
            enable_sounds = audio_config.get("enable_sounds", enable_sounds)
            enable_narration = audio_config.get("enable_narration", enable_narration)
            self.using_running_screen_reader = audio_config.get("use_running_screen_reader", True)
            
            # Set speech rate and volumes from config
            self.speech_rate = audio_config.get("speech_rate", 150)
            self.narration_volume = audio_config.get("narration_volume", 1.0)
            sound_volume = audio_config.get("sound_volume", 1.0)
            
            print(f"Initializing PygameAudioService with use_running_screen_reader={self.using_running_screen_reader}")
        except ImportError:
            # Config module not available, use defaults
            print("Config module not available, using default audio settings")
            self.using_running_screen_reader = True
            self.speech_rate = 150
            self.narration_volume = 1.0
            sound_volume = 1.0
        
        # Now call the parent constructor with the correct settings
        # This will initialize SRAL with the appropriate speech mode
        super().__init__(enable_sounds, enable_narration)
        
        self.sounds: Dict[SoundEffect, Optional[pygame.mixer.Sound]] = {
            effect: None for effect in SoundEffect
        }
        
        # Update volumes from config
        for effect in SoundEffect:
            self.sound_volumes[effect] = sound_volume
        
        # Initialize text-to-speech engine
        self.tts_engine = None
        self.voice_speaker = None
        
        # Initialize audio
        self.initialize_audio()
        
        # Try SRAL first (already initialized in parent class)
        if self.sral:
            print("Using SRAL for text-to-speech in Pygame mode")
        else:
            # Try pyttsx3 if SRAL is not available
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

    def increase_speech_rate(self, amount: int = 10) -> None:
        """Increase the speech rate"""
        self.speech_rate = min(250, self.speech_rate + amount)
        print(f"Increasing speech rate to {self.speech_rate}")
        
        # Update the speech rate in the appropriate engine
        if self.sral:
            try:
                self.sral.set_rate(self.speech_rate)
                self.play_narration(f"Speech rate {self.speech_rate}")
            except Exception as e:
                print(f"Error setting SRAL speech rate: {e}")
        elif self.tts_engine:
            try:
                self.tts_engine.setProperty('rate', self.speech_rate)
                self.play_narration(f"Speech rate {self.speech_rate}")
            except Exception as e:
                print(f"Error setting pyttsx3 speech rate: {e}")
        elif self.voice_speaker:
            try:
                # Convert our 50-250 scale to -10 to 10 scale
                rate_normalized = int((self.speech_rate - 150) / 10)
                self.voice_speaker.Rate = rate_normalized
                self.play_narration(f"Speech rate {self.speech_rate}")
            except Exception as e:
                print(f"Error setting Windows Speech API rate: {e}")
        
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["speech_rate"] = self.speech_rate
            save_audio_config(audio_config)
            print(f"Saved audio config: speech_rate={self.speech_rate}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def decrease_speech_rate(self, amount: int = 10) -> None:
        """Decrease the speech rate"""
        self.speech_rate = max(50, self.speech_rate - amount)
        print(f"Decreasing speech rate to {self.speech_rate}")
        
        # Update the speech rate in the appropriate engine
        if self.sral:
            try:
                self.sral.set_rate(self.speech_rate)
                self.play_narration(f"Speech rate {self.speech_rate}")
            except Exception as e:
                print(f"Error setting SRAL speech rate: {e}")
        elif self.tts_engine:
            try:
                self.tts_engine.setProperty('rate', self.speech_rate)
                self.play_narration(f"Speech rate {self.speech_rate}")
            except Exception as e:
                print(f"Error setting pyttsx3 speech rate: {e}")
        elif self.voice_speaker:
            try:
                # Convert our 50-250 scale to -10 to 10 scale
                rate_normalized = int((self.speech_rate - 150) / 10)
                self.voice_speaker.Rate = rate_normalized
                self.play_narration(f"Speech rate {self.speech_rate}")
            except Exception as e:
                print(f"Error setting Windows Speech API rate: {e}")
        
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["speech_rate"] = self.speech_rate
            save_audio_config(audio_config)
            print(f"Saved audio config: speech_rate={self.speech_rate}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def increase_sound_volume(self, amount: float = 0.1) -> None:
        """Increase the sound volume"""
        for effect in SoundEffect:
            self.sound_volumes[effect] = min(1.0, self.sound_volumes[effect] + amount)
        
        # Play a sound to demonstrate the new volume
        self.play_sound(SoundEffect.MENU_NAV)
        self.play_narration(f"Sound volume {int(self.sound_volumes[SoundEffect.MENU_NAV] * 100)}%")
        
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["sound_volume"] = self.sound_volumes[SoundEffect.MENU_NAV]
            save_audio_config(audio_config)
            print(f"Saved audio config: sound_volume={self.sound_volumes[SoundEffect.MENU_NAV]}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def decrease_sound_volume(self, amount: float = 0.1) -> None:
        """Decrease the sound volume"""
        for effect in SoundEffect:
            self.sound_volumes[effect] = max(0.0, self.sound_volumes[effect] - amount)
        
        # Play a sound to demonstrate the new volume
        self.play_sound(SoundEffect.MENU_NAV)
        self.play_narration(f"Sound volume {int(self.sound_volumes[SoundEffect.MENU_NAV] * 100)}%")
        
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["sound_volume"] = self.sound_volumes[SoundEffect.MENU_NAV]
            save_audio_config(audio_config)
            print(f"Saved audio config: sound_volume={self.sound_volumes[SoundEffect.MENU_NAV]}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def increase_narration_volume(self, amount: float = 0.1) -> None:
        """Increase the narration volume"""
        self.narration_volume = min(1.0, self.narration_volume + amount)
        print(f"Increasing narration volume to {self.narration_volume}")
        
        # Update the volume in the appropriate engine
        if self.tts_engine:
            try:
                self.tts_engine.setProperty('volume', self.narration_volume)
            except Exception as e:
                print(f"Error setting pyttsx3 volume: {e}")
        elif self.voice_speaker:
            try:
                self.voice_speaker.Volume = int(self.narration_volume * 100)
            except Exception as e:
                print(f"Error setting Windows Speech API volume: {e}")
        
        # Play a narration to demonstrate the new volume
        self.play_narration(f"Narration volume {int(self.narration_volume * 100)}%")
        
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["narration_volume"] = self.narration_volume
            save_audio_config(audio_config)
            print(f"Saved audio config: narration_volume={self.narration_volume}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def decrease_narration_volume(self, amount: float = 0.1) -> None:
        """Decrease the narration volume"""
        self.narration_volume = max(0.0, self.narration_volume - amount)
        print(f"Decreasing narration volume to {self.narration_volume}")
        
        # Update the volume in the appropriate engine
        if self.tts_engine:
            try:
                self.tts_engine.setProperty('volume', self.narration_volume)
            except Exception as e:
                print(f"Error setting pyttsx3 volume: {e}")
        elif self.voice_speaker:
            try:
                self.voice_speaker.Volume = int(self.narration_volume * 100)
            except Exception as e:
                print(f"Error setting Windows Speech API volume: {e}")
        
        # Play a narration to demonstrate the new volume
        self.play_narration(f"Narration volume {int(self.narration_volume * 100)}%")
        
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["narration_volume"] = self.narration_volume
            save_audio_config(audio_config)
            print(f"Saved audio config: narration_volume={self.narration_volume}")
        except ImportError:
            # Config module not available
            print("Could not save audio configuration: Config module not available")
            pass

    def toggle_running_screen_reader(self, use_running_sr: bool) -> None:
        """Toggle between using SRAL directly or using the running screen reader"""
        if self.using_running_screen_reader == use_running_sr:
            # No change needed
            return
            
        self.using_running_screen_reader = use_running_sr
        print(f"Setting use_running_screen_reader to {use_running_sr}")
        
        # Save the configuration
        try:
            from cli.game.config import get_audio_config, save_audio_config
            audio_config = get_audio_config()
            audio_config["use_running_screen_reader"] = use_running_sr
            print(f"Updating audio config with use_running_screen_reader={use_running_sr}")
            save_audio_config(audio_config)
        except Exception as e:
            print(f"Error saving configuration: {e}")
        
        # Clean up existing SRAL instance if any
        if self.sral:
            # SRAL will clean up in its own __del__ method
            self.sral = None
            
        # Initialize a new SRAL instance with the appropriate settings
        try:
            import sral
            from cli.sral_wrapper import SRALEngines
            
            if self.using_running_screen_reader:
                # Initialize SRAL with engines_exclude=0 to use the running screen reader
                # This will make SRAL use the currently active screen reader
                engines_exclude = 0
                print(f"Initializing SRAL with engines_exclude={engines_exclude} to use running screen reader")
                self.sral = sral.Sral(engines_exclude=engines_exclude)
                print("SRAL initialized to use running screen reader")
                self.play_narration("Using running screen reader")
            else:
                # Initialize SRAL to use SAPI specifically by excluding all other engines
                engines_to_exclude = (
                    SRALEngines.NVDA | 
                    SRALEngines.JAWS | 
                    SRALEngines.SPEECH_DISPATCHER | 
                    SRALEngines.UIA | 
                    SRALEngines.AV_SPEECH | 
                    SRALEngines.NARRATOR
                )
                print(f"Initializing SRAL with engines_exclude={engines_to_exclude} to use SAPI only")
                self.sral = sral.Sral(engines_exclude=engines_to_exclude)
                
                # Verify SAPI is being used
                current_engine = self.sral.get_current_engine()
                print(f"Current engine after initialization: {current_engine}")
                
                if current_engine == SRALEngines.SAPI:
                    print("Successfully initialized SAPI direct speech")
                    self.play_narration("Using SAPI direct speech")
                else:
                    print(f"Warning: Expected SAPI engine but got engine {current_engine}")
                    self.play_narration("Speech engine changed, but not to SAPI as expected")
        except Exception as e:
            print(f"Error reinitializing SRAL: {e}")
            self.play_narration("Failed to change screen reader mode")


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
        
        # Initialize game loop with the configured audio service
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

        try:
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

            # Save configuration before exiting
            self.game.save_configuration()
            print("Configuration saved on exit")
            
        except Exception as e:
            print(f"Error in game loop: {e}")
            print("Attempting to save configuration before exit...")
            try:
                self.game.save_configuration()
            except Exception as e2:
                print(f"Failed to save configuration: {e2}")
        finally:
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
        
        # File saving controls
        if key == pygame.K_F11:  # F11 to save a text file
            self.save_text_file()
            self.audio.play_narration("Text file saved to disk")
            return True
        elif key == pygame.K_F12:  # F12 to save a screenshot
            self.save_screenshot()
            self.audio.play_narration("Screenshot saved to disk")
            return
            
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
        
    def save_text_file(self) -> None:
        """Save a text file with game state information"""
        try:
            import datetime
            import os
            
            # Create a logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            # Generate a filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join("logs", f"game_state_{timestamp}.txt")
            
            # Prepare game state information
            game_info = [
                f"Space Colony Defense - Game State - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"----------------------------------------",
                f"Wave: {self.game.game_state.wave}",
                f"Colony Health: {self.game.game_state.colony.hp}/{self.game.game_state.colony.max_hp}",
                f"Resources:",
                f"  Energy: {self.game.game_state.resources.energy}",
                f"  Metal: {self.game.game_state.resources.metal}",
                f"  Food: {self.game.game_state.resources.food}",
                f"Tech Points: {self.game.game_state.tech_points}",
                f"Shield Strength: {self.game.game_state.shield_strength}",
                f"Buildings: {len(self.game.game_state.buildings)}",
                f"Enemies: {len(self.game.enemies)}",
                f"Game State:",
                f"  In Main Menu: {self.game.in_main_menu}",
                f"  Game Running: {self.game.game_running}",
                f"  Is Game Over: {self.game.is_game_over}",
                f"  Is Management Phase: {self.game.is_management_phase}",
            ]
            
            # Add building information
            if self.game.game_state.buildings:
                game_info.append(f"\nBuildings:")
                for i, building in enumerate(self.game.game_state.buildings):
                    game_info.append(f"  {i+1}. {building.type.display_name()} (Level: {building.level.name})")
            
            # Write the file
            with open(filename, "w") as f:
                f.write("\n".join(game_info))
                
            print(f"Game state saved to {filename}")
            return
            
        except Exception as e:
            print(f"Error saving text file: {e}")
            self.audio.play_narration("Error saving text file")
    
    def save_screenshot(self) -> None:
        """Save a screenshot of the current game state"""
        try:
            import datetime
            import os
            
            # Create a screenshots directory if it doesn't exist
            os.makedirs("screenshots", exist_ok=True)
            
            # Generate a filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join("screenshots", f"screenshot_{timestamp}.png")
            
            # Save the screenshot
            pygame.image.save(self.screen, filename)
            
            print(f"Screenshot saved to {filename}")
            return
            
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            self.audio.play_narration("Error saving screenshot")

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
