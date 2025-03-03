# CLI Module Knowledge

## Project Structure
- The CLI module is the main entry point for the Space Colony Defense game
- It contains the game logic and interfaces for both text-based and Pygame modes
- All game components are designed with accessibility as a core feature

## Module Organization
- `__main__.py`: Entry point that handles command-line arguments and starts the game
- `sral_wrapper.py`: Wrapper for the SRAL accessibility library
- `game/`: Submodule containing all game logic components
- `game/config.py`: Configuration management for persisting user preferences

## Running the Game
- Default mode: Pygame mode (runs automatically when you execute `python -m cli`)
- Text mode: `python -m cli --text`
- Voice selection: `python -m cli --voice <index>`
- Speech rate: `python -m cli --rate <0-100>`

## Controls
- Up/Down arrows: Navigate menus
- Enter: Select menu option
- Left/Right arrows: Move turret (in gameplay)
- Space: Shoot (in gameplay)
- S key: Status check
- Escape: Return to menu
- + and -: Adjust speech rate
- [ and ]: Adjust sound volume
- { and }: Adjust narration volume
- F11: Save game state to text file (in "logs" folder)
- F12: Save screenshot (in "screenshots" folder)

## Development Guidelines
- All user interactions must have audio feedback
- Menu systems must be fully navigable with keyboard
- Status changes require both sound effects and verbal narration
- Test both functionality and accessibility features together

## SRAL Integration
- `sral_wrapper.py` provides a wrapper for the SRAL accessibility library
- Do not modify this file as it's a critical interface to the accessibility layer
- The wrapper handles text-to-speech functionality for the game
- SRAL.dll is required for the wrapper to function properly
- The direct `sral` module is preferred over the wrapper when available
- Always include error handling for SRAL operations as they may fail
- SRAL is used in both text mode and Pygame mode, with fallbacks to other TTS engines
- In Pygame mode, users can toggle using the running screen reader via the options menu
- By default, SRAL uses the running screen reader (engines_exclude=0)
- To switch to SAPI direct speech, use `engines_exclude` with all engines except SAPI
- The "Toggle Speech Mode" option switches between running screen reader and SAPI direct speech
- Menu options display their current state (e.g., "Currently using running screen reader")
- Speech mode settings persist across program sessions via the configuration system

## Configuration System
- User preferences are stored in `~/.space_colony_defense/config.json`
- Configuration includes audio settings (speech mode, volumes, rates) and game settings (difficulty)
- Settings are automatically saved when changed and loaded on game startup
- This ensures user preferences persist across game sessions
- When toggling speech modes, the configuration is updated immediately and persists across restarts
- SAPI initializes correctly at startup based on the saved speech mode setting
