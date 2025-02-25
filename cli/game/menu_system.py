from enum import Enum, auto
from typing import List, Optional, Dict, Callable, Any
from cli.game.game_state import GameState
from cli.game.audio_service import AudioService, SoundEffect


class MenuOption(Enum):
    BUILD = auto()
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
    DIFFICULTY = auto()
    BACK = auto()


class MenuSystem:
    def __init__(self, game_state: GameState, audio: AudioService):
        self.game_state = game_state
        self.audio = audio
        self.options = list(MenuOption)
        self.current_index = 0

        # Main menu setup
        self.main_menu_options = list(MainMenuOption)
        self.options_menu_options = list(OptionsMenuOption)
        self.current_menu = "game"  # Can be "main", "game", or "options"

        # Difficulty settings
        self.difficulty_level = 1  # 1=Easy, 2=Medium, 3=Hard

    def navigate_up(self) -> None:
        if self.current_menu == "main":
            self.current_index = (self.current_index - 1) % len(self.main_menu_options)
        elif self.current_menu == "options":
            self.current_index = (self.current_index - 1) % len(
                self.options_menu_options
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
        else:  # game menu
            self.current_index = (self.current_index + 1) % len(self.options)
        self._announce_current_option()

    def select_current_option(self) -> Optional[str]:
        """Returns an action string if needed, otherwise None"""
        if self.current_menu == "main":
            return self._handle_main_menu_selection()
        elif self.current_menu == "options":
            return self._handle_options_menu_selection()
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
        elif option == OptionsMenuOption.DIFFICULTY:
            # Cycle through difficulty levels
            self.difficulty_level = (self.difficulty_level % 3) + 1
            difficulty_names = {1: "Easy", 2: "Medium", 3: "Hard"}
            self.audio.play_narration(
                f"Difficulty set to {difficulty_names[self.difficulty_level]}"
            )
            return None
        elif option == OptionsMenuOption.BACK:
            self.audio.play_sound(SoundEffect.MENU_NAV)
            self.audio.play_narration("Returning to main menu")
            self.current_menu = "main"
            self.current_index = 0
            return None
        return None

    def _handle_game_menu_selection(self) -> None:
        """Handle selection in the game menu"""
        option = self.options[self.current_index]
        if option == MenuOption.STATUS:
            self._announce_status()
        elif option == MenuOption.BUILD:
            self._announce_build_options()
        elif option == MenuOption.REPAIR:
            self._try_repair_colony()
        elif option == MenuOption.NEXT_WAVE:
            self._announce_next_wave()

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
                f"Selected {self.main_menu_options[self.current_index].name.lower().replace('_', ' ')}"
            )
        elif self.current_menu == "options":
            self.audio.play_narration(
                f"Selected {self.options_menu_options[self.current_index].name.lower().replace('_', ' ')}"
            )
        else:  # game menu
            self.audio.play_narration(
                f"Selected {self.options[self.current_index].name.lower()}"
            )

    def _announce_status(self) -> None:
        status = (
            f"Colony health: {self.game_state.colony.hp} of {self.game_state.colony.max_hp}. "
            f"Resources: {self.game_state.resources.energy} energy, "
            f"{self.game_state.resources.metal} metal, "
            f"{self.game_state.resources.food} food."
        )
        self.audio.play_narration(status)

    def _announce_build_options(self) -> None:
        self.audio.play_narration(
            "Build menu. Press numbers 1 through 9 to select position. "
            "Available buildings: Solar Panel, Hydroponic Farm, Scrap Forge."
        )

    def _try_repair_colony(self) -> None:
        if self.game_state.colony.repair(self.game_state.resources, self.audio):
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
        else:
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            self.audio.play_narration("Not enough metal to repair colony")

    def _announce_next_wave(self) -> None:
        self.audio.play_narration(f"Prepare for wave {self.game_state.wave}")

    def get_difficulty(self) -> int:
        """Return the current difficulty setting"""
        return self.difficulty_level
