from enum import Enum, auto
from typing import List, Optional, Dict, Callable, Any
from cli.game.game_state import GameState
from cli.game.audio_service import AudioService, SoundEffect
from cli.game.buildings import BuildingType, Building


class MenuOption(Enum):
    BUILD = auto()
    UPGRADE = auto()
    REPAIR = auto()
    STATUS = auto()
    NEXT_WAVE = auto()


class MainMenuOption(Enum):
    NEW_GAME = auto()
    OPTIONS = auto()
    EXIT = auto()


class OptionsMenuOption(Enum):
    SOUND_TOGGLE = auto()
    NARRATION_TOGGLE = auto()
    TOGGLE_SPEECH_MODE = auto()
    DIFFICULTY = auto()
    BACK = auto()


class BuildMenuOption(Enum):
    SOLAR_PANEL = auto()
    HYDROPONIC_FARM = auto()
    SCRAP_FORGE = auto()
    SHIELD_GENERATOR = auto()
    RESEARCH_LAB = auto()
    REPAIR_BAY = auto()
    MISSILE_SILO = auto()
    COMMAND_CENTER = auto()
    BACK = auto()


class MenuSystem:
    def __init__(self, game_state: Optional[GameState], audio: AudioService):
        self.game_state = game_state
        self.audio = audio
        self.options = list(MenuOption)
        self.current_index = 0

        # Main menu setup
        self.main_menu_options = list(MainMenuOption)
        self.options_menu_options = list(OptionsMenuOption)
        self.build_menu_options = list(BuildMenuOption)
        self.current_menu = "game"  # Can be "main", "game", "options", or "build"

        # Load difficulty settings from config
        try:
            from cli.game.config import get_game_config
            game_config = get_game_config()
            self.difficulty_level = game_config.get("difficulty", 1)  # 1=Easy, 2=Medium, 3=Hard
        except ImportError:
            # Config module not available, use default
            self.difficulty_level = 1
        
        # Screen reader settings - default to using running screen reader
        from cli.game.pygame_interface import PygameAudioService
        self.use_running_screen_reader = isinstance(self.audio, PygameAudioService) and self.audio.using_running_screen_reader

    def navigate_up(self) -> None:
        if self.current_menu == "main":
            self.current_index = (self.current_index - 1) % len(self.main_menu_options)
        elif self.current_menu == "options":
            self.current_index = (self.current_index - 1) % len(
                self.options_menu_options
            )
        elif self.current_menu == "build":
            self.current_index = (self.current_index - 1) % len(
                self.build_menu_options
            )
        else:  # game menu
            self.current_index = (self.current_index - 1) % len(self.options)
        self._announce_current_option()

    def navigate_down(self) -> None:
        if self.current_menu == "main":
            self.current_index = (self.current_index + 1) % len(self.main_menu_options)
        elif self.current_menu == "options":
            self.current_index = (self.current_index + 1) % len(
                self.options_menu_options
            )
        elif self.current_menu == "build":
            self.current_index = (self.current_index + 1) % len(
                self.build_menu_options
            )
        else:  # game menu
            self.current_index = (self.current_index + 1) % len(self.options)
        self._announce_current_option()

    def select_current_option(self) -> Optional[str]:
        """Returns an action string if needed, otherwise None"""
        if self.current_menu == "main":
            return self._handle_main_menu_selection()
        elif self.current_menu == "options":
            return self._handle_options_menu_selection()
        elif self.current_menu == "build":
            return self._handle_build_menu_selection()
        else:  # game menu
            self._handle_game_menu_selection()
            return None

    def _handle_main_menu_selection(self) -> Optional[str]:
        """Handle selection in the main menu"""
        option = self.main_menu_options[self.current_index]
        if option == MainMenuOption.NEW_GAME:
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
            self.audio.play_narration("Starting new game")
            self.current_menu = "game"
            self.current_index = 0
            return "new_game"
        elif option == MainMenuOption.OPTIONS:
            self.audio.play_sound(SoundEffect.MENU_NAV)
            self.audio.play_narration("Options menu")
            self.current_menu = "options"
            self.current_index = 0
            return None
        elif option == MainMenuOption.EXIT:
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
            self.audio.play_narration("Exiting game")
            return "exit"
        return None

    def _handle_options_menu_selection(self) -> Optional[str]:
        """Handle selection in the options menu"""
        option = self.options_menu_options[self.current_index]
        if option == OptionsMenuOption.SOUND_TOGGLE:
            self.audio.toggle_sounds()
            status = "enabled" if self.audio.enable_sounds else "disabled"
            self.audio.play_narration(f"Sound effects {status}")
            return None
        elif option == OptionsMenuOption.NARRATION_TOGGLE:
            # We need to check status before toggling, as the narration might be silenced
            was_enabled = self.audio.enable_narration
            self.audio.toggle_narration()
            if not was_enabled:
                # If narration was off, we need to play this directly
                print(f"Narration enabled")
            else:
                self.audio.play_narration("Narration disabled")
            return None
        elif option == OptionsMenuOption.TOGGLE_SPEECH_MODE:
            # Toggle between SAPI direct speech and running screen reader (Pygame mode only)
            from cli.game.pygame_interface import PygameAudioService
            if isinstance(self.audio, PygameAudioService):
                # Get current state before toggling
                current_state = self.audio.using_running_screen_reader
                # Toggle to opposite state
                new_state = not current_state
                # Update menu state to match
                self.use_running_screen_reader = new_state
                # Apply the change to the audio service
                self.audio.toggle_running_screen_reader(new_state)
                # The narration will be played by the toggle_running_screen_reader method
            else:
                self.audio.play_narration("Speech mode toggling only works in Pygame mode")
            return None
        elif option == OptionsMenuOption.DIFFICULTY:
            # Cycle through difficulty levels
            self.difficulty_level = (self.difficulty_level % 3) + 1
            difficulty_names = {1: "Easy", 2: "Medium", 3: "Hard"}
            self.audio.play_narration(
                f"Difficulty set to {difficulty_names[self.difficulty_level]}"
            )
            
            # Save the configuration
            try:
                from cli.game.config import get_game_config, save_game_config
                game_config = get_game_config()
                game_config["difficulty"] = self.difficulty_level
                save_game_config(game_config)
            except ImportError:
                # Config module not available
                pass
                
            return None
        elif option == OptionsMenuOption.BACK:
            self.audio.play_sound(SoundEffect.MENU_NAV)
            self.audio.play_narration("Returning to main menu")
            self.current_menu = "main"
            self.current_index = 0
            return None
        return None

    def _handle_build_menu_selection(self) -> Optional[str]:
        """Handle selection in the build menu"""
        option = self.build_menu_options[self.current_index]
        
        if option == BuildMenuOption.BACK:
            self.audio.play_sound(SoundEffect.MENU_NAV)
            self.audio.play_narration("Returning to game menu")
            self.current_menu = "game"
            self.current_index = 0
            return None
            
        # Map menu option to building type
        building_type_map = {
            BuildMenuOption.SOLAR_PANEL: BuildingType.SOLAR_PANEL,
            BuildMenuOption.HYDROPONIC_FARM: BuildingType.HYDROPONIC_FARM,
            BuildMenuOption.SCRAP_FORGE: BuildingType.SCRAP_FORGE,
            BuildMenuOption.SHIELD_GENERATOR: BuildingType.SHIELD_GENERATOR,
            BuildMenuOption.RESEARCH_LAB: BuildingType.RESEARCH_LAB,
            BuildMenuOption.REPAIR_BAY: BuildingType.REPAIR_BAY,
            BuildMenuOption.MISSILE_SILO: BuildingType.MISSILE_SILO,
            BuildMenuOption.COMMAND_CENTER: BuildingType.COMMAND_CENTER,
        }
        
        if self.game_state and option in building_type_map:
            building_type = building_type_map[option]
            building = Building(type=building_type, audio=self.audio)
            
            if self.game_state.add_building(building):
                self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
                self.audio.play_narration(f"{building_type.display_name()} constructed successfully")
            else:
                self.audio.play_sound(SoundEffect.ACTION_FAIL)
                # Construction failed message already played by the building itself
                
            # Return to game menu after construction attempt
            self.current_menu = "game"
            self.current_index = 0
            
        return None

    def _handle_game_menu_selection(self) -> None:
        """Handle selection in the game menu"""
        if not self.game_state:
            return
            
        option = self.options[self.current_index]
        if option == MenuOption.STATUS:
            self._announce_status()
        elif option == MenuOption.BUILD:
            self._show_build_menu()
        elif option == MenuOption.UPGRADE:
            self._show_upgrade_options()
        elif option == MenuOption.REPAIR:
            self._try_repair_colony()
        elif option == MenuOption.NEXT_WAVE:
            self._announce_next_wave()

    def _show_build_menu(self) -> None:
        """Show the build menu"""
        self.current_menu = "build"
        self.current_index = 0
        self.audio.play_narration("Build menu. Select a building to construct.")
        self._announce_current_option()

    def _show_upgrade_options(self) -> None:
        """Show options for upgrading existing buildings"""
        if not self.game_state or not self.game_state.buildings:
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            self.audio.play_narration("No buildings to upgrade")
            return
            
        # For now, just upgrade the first building as an example
        # A more complete implementation would list all buildings and let the player choose
        if self.game_state.upgrade_building(0):
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
            # Upgrade success message already played by the building itself
        else:
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            # Upgrade failure message already played by the building itself

    def query_status(self) -> None:
        self._announce_status()

    def show_main_menu(self) -> None:
        """Switch to the main menu"""
        self.current_menu = "main"
        self.current_index = 0
        self._announce_main_menu()

    def _announce_main_menu(self) -> None:
        """Announce the main menu options"""
        self.audio.play_narration(
            "Main Menu. Use up and down arrows to navigate, Enter to select."
        )
        self._announce_current_option()

    def _announce_current_option(self) -> None:
        self.audio.play_sound(SoundEffect.MENU_NAV)
        if self.current_menu == "main":
            self.audio.play_narration(
                f"{self.main_menu_options[self.current_index].name.lower().replace('_', ' ')}"
            )
        elif self.current_menu == "options":
            option = self.options_menu_options[self.current_index]
            
            # Add current state information for toggle options
            if option == OptionsMenuOption.SOUND_TOGGLE:
                state = "enabled" if self.audio.enable_sounds else "disabled"
                self.audio.play_narration(
                    f"{option.name.lower().replace('_', ' ')}. Currently {state}"
                )
            elif option == OptionsMenuOption.NARRATION_TOGGLE:
                state = "enabled" if self.audio.enable_narration else "disabled"
                self.audio.play_narration(
                    f"{option.name.lower().replace('_', ' ')}. Currently {state}"
                )
            elif option == OptionsMenuOption.TOGGLE_SPEECH_MODE:
                # Check if we're in pygame mode
                from cli.game.pygame_interface import PygameAudioService
                if isinstance(self.audio, PygameAudioService):
                    state = "using running screen reader" if self.audio.using_running_screen_reader else "using SAPI direct speech"
                    self.audio.play_narration(
                        f"{option.name.lower().replace('_', ' ')}. Currently {state}"
                    )
                else:
                    self.audio.play_narration(
                        f"{option.name.lower().replace('_', ' ')}"
                    )
            elif option == OptionsMenuOption.DIFFICULTY:
                difficulty_names = {1: "Easy", 2: "Medium", 3: "Hard"}
                self.audio.play_narration(
                    f"{option.name.lower().replace('_', ' ')}. Currently set to {difficulty_names[self.difficulty_level]}"
                )
            else:
                self.audio.play_narration(
                    f"{option.name.lower().replace('_', ' ')}"
                )
        elif self.current_menu == "build":
            self.audio.play_narration(
                f"{self.build_menu_options[self.current_index].name.lower().replace('_', ' ')}"
            )
        else:  # game menu
            self.audio.play_narration(
                f"{self.options[self.current_index].name.lower()}"
            )

    def _announce_status(self) -> None:
        if not self.game_state:
            self.audio.play_narration("Game not started yet")
            return
            
        shield_info = ""
        if self.game_state.shield_strength > 0:
            shield_info = f"Shield strength: {self.game_state.shield_strength}. "
            
        status = (
            f"Colony health: {self.game_state.colony.hp} of {self.game_state.colony.max_hp}. "
            f"{shield_info}"
            f"Resources: {self.game_state.resources.energy} energy, "
            f"{self.game_state.resources.metal} metal, "
            f"{self.game_state.resources.food} food. "
            f"Tech points: {self.game_state.tech_points}. "
            f"Buildings: {len(self.game_state.buildings)}."
        )
        self.audio.play_narration(status)

    def _announce_build_options(self) -> None:
        self.audio.play_narration(
            "Build menu. Select a building to construct. "
            "Available buildings: Solar Panel, Hydroponic Farm, Scrap Forge, "
            "Shield Generator, Research Lab, Repair Bay, Missile Silo, Command Center."
        )

    def _try_repair_colony(self) -> None:
        if not self.game_state:
            return
            
        if self.game_state.colony.repair(self.game_state.resources, self.audio):
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
        else:
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            self.audio.play_narration("Not enough metal to repair colony")

    def _announce_next_wave(self) -> None:
        if not self.game_state:
            return
            
        self.audio.play_narration(f"Prepare for wave {self.game_state.wave}")

    def get_difficulty(self) -> int:
        """Return the current difficulty setting"""
        return self.difficulty_level
