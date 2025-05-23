# Testing Setup for Space Colony Defense

## Gut Testing Framework

This project uses Gut (Godot Unit Testing) for automated testing.

### Installation

1. **Via Godot Asset Library (Recommended):**
   - Open the project in Godot 4.5+
   - Go to AssetLib tab
   - Search for "GUT"
   - Download and install "GUT - Godot Unit Testing (Godot 4)"
   - Enable the plugin in Project Settings > Plugins

2. **Manual Installation:**
   - Download from: https://github.com/bitwes/Gut/releases/latest
   - Extract to `addons/gut/` directory
   - Enable the plugin in Project Settings > Plugins

### Running Tests

1. **Through Godot Editor:**
   - After installing Gut, a "Gut" dock will appear
   - Click "Run All" to run all tests
   - Individual tests can be run by selecting them

2. **Command Line:**
   ```bash
   godot --headless -s addons/gut/gut_cmdln.gd -gtest
   ```

### Test Structure

- All test files should be in the `test/` directory
- Test files should extend `GutTest`
- Test methods should start with `test_`
- Use `before_each()` and `after_each()` for setup/teardown

### Example Test

See `test_example.gd` for basic test examples covering:
- GameState singleton testing
- AudioManager testing  
- Resource management testing
- SaveManager configuration testing

### Test Coverage

Tests should cover:
- [ ] Core singletons (GameState, AudioManager, SaveManager)
- [ ] Input system functionality
- [ ] Resource management operations
- [ ] Building system mechanics
- [ ] Enemy behavior and spawning
- [ ] Collision detection
- [ ] Save/load functionality
- [ ] Audio system integration
- [ ] UI navigation and accessibility

### Notes

- Gut requires Godot 4.3+ (we're using 4.5+)
- Tests run in isolation with proper setup/teardown
- Mock objects can be created for complex dependencies
- Integration tests should verify system interactions
