# Space Colony Defense

Space Colony Defense is an audio game for blind and visually impaired players, built with Godot 4.5+ that includes TTS integration, screen reader support, wave-based combat, resource management, and keyboard navigation.

## 🚧 Current Development Status

**This project is currently in early development.** The Godot implementation currently features:
- ✅ Complete TTS and screen reader integration system
- ✅ Audio system with fallback support
- ✅ Options menu with screen reader mode toggle
- ✅ Save/load configuration system
- ✅ Automated testing suite (11 passing tests)
- ⚠️ **Basic UI implementation** - most game mechanics described below are planned features

> **Note**: This README contains the planned feature set. The project was recently migrated from a Python implementation to Godot 4.5+, and many game mechanics are still being implemented. The current focus has been on TTS and screen reader systems.

## Project Overview

Space Colony Defense will combine fast-paced, wave-based shooting with resource management inspired by strategy games. You'll be a lone commander defending a fledgling space colony on an alien planet from waves of descending alien ships. Between waves, you'll manage resources like energy, metal, and food to upgrade your defenses, repair your colony, and survive increasingly tough invasions.

## Accessibility Features

**Currently implemented:**

- ✅ **Screen Reader Integration**: Automatic TTS disabling when screen reader mode is enabled to prevent conflicts
- ✅ **Multi-Platform TTS Support**: Godot's built-in TTS with OS-specific fallbacks (Windows PowerShell, macOS say, Linux espeak)
- ✅ **Configurable Audio Settings**: Adjustable speech rate (50-300 WPM), separate volume controls for sounds/narration
- ✅ **Screen Reader Mode Toggle**: Easy switching between direct TTS and screen reader compatibility
- ✅ **Comprehensive Audio Narration**: Menu navigation, option changes, and game state announcements
- ✅ **Keyboard Navigation**: Full keyboard control for menu systems
- 🚧 **Audio Feedback**: Planned for all game actions and events
- 🚧 **High Contrast Visuals**: Planned visual accessibility features

## Project Structure

```
project/
  scenes/
    Main.tscn         # Root scene
    Game.tscn         # Main game scene
    MainMenu.tscn     # Menu system
    Turret.tscn       # Player-controlled turret
    Enemy.tscn        # Enemy entities
    Projectile.tscn   # Projectiles
    Building.tscn     # Resource buildings
  scripts/
    autoload/
      GameState.gd    # Singleton for game state
      AudioManager.gd # Accessibility audio system
      SaveManager.gd  # Save/load system
    entities/
      Turret.gd       # Turret movement and shooting
      Enemy.gd        # Enemy behavior
      Building.gd     # Building production
      Projectile.gd   # Projectile movement
    ui/
      MenuController.gd # Menu navigation
      TechTreeUI.gd     # Tech tree interface
  assets/
    audio/
      effects/        # Sound effects
      music/          # Music tracks
```

## Game Mechanics (Planned)

The following game mechanics are planned for implementation:

- 🚧 **Combat Phase**: Control a turret to defend against waves of descending alien ships
- 🚧 **Management Phase**: Between waves, build and upgrade structures to generate resources
- 🚧 **Tech Tree**: Spend tech points to unlock permanent upgrades
- 🚧 **Resource Management**: Balance energy, metal, and food production
- 🚧 **Progressive Difficulty**: Face increasingly challenging waves with different enemy types

## Controls

**Currently implemented:**
- ✅ **Arrow Keys**: Navigate menus
- ✅ **Enter**: Select menu option
- ✅ **Escape**: Back/Cancel in menus

**Planned for game:**
- 🚧 **Left/Right Arrow Keys**: Move turret
- 🚧 **Space**: Shoot
- 🚧 **Escape**: Pause game

## Testing

The project includes a comprehensive test suite using the Gut testing framework:

- **11 passing tests** covering TTS and screen reader integration
- **Automated testing** for TTS and screen reader features
- **Test coverage** for audio system, screen reader mode, and configuration management

To run tests:
1. Open the project in Godot 4.5+
2. Enable the Gut plugin in Project Settings > Plugins
3. Use the Gut dock to run tests, or run via command line: `godot --headless -s addons/gut/gut_cmdln.gd -gtest`

## Installation

1. Download and install [Godot 4.5+](https://godotengine.org/download)
2. Clone or download this repository
3. Open the project in Godot 4.5+
4. Click the "Play" button or press F5 to run the game

**Current functionality:** You can navigate the main menu and options menu with full TTS support and screen reader integration.

## Contributing

Contributions are welcome, especially:
- Accessibility testing and feedback
- Screen reader compatibility improvements
- Audio design and implementation
- Game mechanics implementation
- Documentation improvements

The codebase includes comprehensive comments.
