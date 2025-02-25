# Python CLI Template Knowledge

## Project Overview
A minimal Python CLI application template with modern Python features and type hints.

## Key Features
- Uses Poetry virtual environments for isolation
- Type hints and mypy for static type checking
- Modern Python packaging with pyproject.toml
- Black for code formatting

## Environment Setup
To activate the Poetry environment:
1. Run `poetry env use python` to ensure the correct Python version is used
2. Run `poetry shell` to activate the environment directly
3. Alternatively, you can get the path with `poetry env info` and activate it manually:
```bash
poetry env info
"C:\Users\username\AppData\Local\pypoetry\Cache\virtualenvs\cli-xyz123-py3.12\Scripts\activate.bat"
```

Always activate the Poetry environment before making any changes to the project to ensure consistent dependencies and Python version.

## Verifying changes
After every change, run:
```bash
mypy cli && black --check cli
```
This will check for type errors and formatting issues.

## Accessibility Guidelines
- Implement accessibility features alongside core functionality, not as an afterthought
- Every user interaction needs immediate audio feedback
- All status changes must have both sound effects and verbal narration
- Resource and state changes require clear audio indicators
- Menu systems must work with keyboard navigation and screen readers
- Test both functionality and accessibility features together

## Audio-First Development
- Design game mechanics around audio feedback first
- Use consistent audio grid system (e.g., positions 1-10) for spatial awareness
- Implement keyboard queries for game state (Tab to cycle, Q for status)
- Provide audio landmarks and reference points
- Use different sound profiles for different object types
- Menu navigation should be fully keyboard accessible with audio confirmation

## Game Architecture
- Game state is managed through a central GameLoop class
- Menu system supports multiple menu types (main, options, game management)
- Audio service provides both sound effects and narration
- Game can run in both text mode and Pygame mode
- All game elements provide audio feedback for accessibility
- Tests should account for different game states and menu navigation

## Running the Game
- Text mode: `python -m cli`
- Pygame mode: `python -m cli --pygame`
