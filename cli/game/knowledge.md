# Game Module Knowledge

## Component Overview
- `game_loop.py`: Central game loop that coordinates all game components
- `game_state.py`: Manages the overall state of the game (colony, resources, wave number)
- `turret.py`: Handles turret movement, shooting, and damage
- `enemy_wave.py`: Generates waves of enemies with increasing difficulty
- `menu_system.py`: Manages menu navigation and selection
- `management.py`: Handles the management phase between combat waves
- `buildings.py`: Building system for resource generation
- `audio_service.py`: Provides sound effects and narration for accessibility

## Design Principles
- Audio-first design: All game mechanics have audio feedback
- Keyboard accessibility: Full game playable without visual cues
- Progressive difficulty: Waves get harder as the game progresses
- Resource management: Strategic decisions between combat waves

## Implementation Notes
- Enemy waves scale in difficulty based on wave number
- Resources (energy, metal, food) are used for repairs and construction
- Buildings generate resources over time
- The game follows a roguelike structure with permadeath and meta-progression

## Testing Strategy
- Test both functionality and accessibility features
- Verify audio feedback for all user interactions
- Test resource management and building construction
- Ensure proper wave scaling and difficulty progression
