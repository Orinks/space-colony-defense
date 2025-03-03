# Testing Knowledge

## Testing Approach
- Use pytest for all test cases
- Follow Test-Driven Development (TDD) principles
- Write tests before implementing features
- Test both functionality and accessibility features

## Test Organization
- `test_turret.py`: Tests for turret movement, shooting, and damage
- `test_enemy_wave.py`: Tests for enemy wave generation and scaling
- `test_game_state.py`: Tests for game state management and loss conditions
- `test_resources.py`: Tests for resource collection and management
- `test_buildings.py`: Tests for building construction and resource production
- `test_management.py`: Tests for the management phase
- `test_menu_system.py`: Tests for menu navigation and selection
- `test_audio_service.py`: Tests for audio feedback and narration
- `test_sral_integration.py`: Tests for SRAL initialization and usage with success/failure cases

## Running Tests
```bash
pytest
```

## Test Guidelines
- Mock audio services for testing
- Use predictable random seeds for tests involving randomization
- Test edge cases (e.g., insufficient resources, maximum wave numbers)
- Verify both success and failure conditions
- Test accessibility features alongside functionality
- For SRAL tests, mock the SRAL library to test both success and failure paths
