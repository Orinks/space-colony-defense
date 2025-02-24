from enum import Enum, auto
from typing import List, Optional
from cli.game.game_state import GameState
from cli.game.audio_service import AudioService, SoundEffect


class MenuOption(Enum):
    BUILD = auto()
    REPAIR = auto()
    STATUS = auto()
    NEXT_WAVE = auto()


class MenuSystem:
    def __init__(self, game_state: GameState, audio: AudioService):
        self.game_state = game_state
        self.audio = audio
        self.options = list(MenuOption)
        self.current_index = 0

    def navigate_up(self) -> None:
        self.current_index = (self.current_index - 1) % len(self.options)
        self._announce_current_option()

    def navigate_down(self) -> None:
        self.current_index = (self.current_index + 1) % len(self.options)
        self._announce_current_option()

    def select_current_option(self) -> None:
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

    def _announce_current_option(self) -> None:
        self.audio.play_sound(SoundEffect.MENU_NAV)
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
