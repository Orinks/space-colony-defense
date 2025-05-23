# Space Colony Defense

A wave-based space shooter with resource management and accessibility features, built in Godot 4.

## Project Overview

Space Colony Defense combines the fast-paced, wave-based shooting of Space Invaders with resource management inspired by strategy games. You're a lone commander defending a fledgling space colony on an alien planet from waves of descending alien ships. Between waves, you manage resources like energy, metal, and food to upgrade your defenses, repair your colony, and survive increasingly tough invasions.

## Accessibility Features

This game is designed with accessibility as a core feature:

- **Screen Reader Support**: Full text-to-speech narration using Godot's built-in TTS and OS-specific fallbacks
- **Audio Feedback**: Every game action has appropriate audio cues
- **Keyboard Navigation**: Complete keyboard control for all game functions
- **Configurable Settings**: Adjustable speech rate, sound volumes, and more
- **High Contrast Visuals**: Clear visual distinction between game elements

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

## Game Mechanics

- **Combat Phase**: Control a turret to defend against waves of descending alien ships
- **Management Phase**: Between waves, build and upgrade structures to generate resources
- **Tech Tree**: Spend tech points to unlock permanent upgrades
- **Resource Management**: Balance energy, metal, and food production
- **Progressive Difficulty**: Face increasingly challenging waves with different enemy types

## Controls

- **Left/Right Arrow Keys**: Move turret
- **Space**: Shoot
- **Escape**: Pause game
- **Enter**: Select menu option
- **Arrow Keys**: Navigate menus

## Installation

1. Download and install [Godot 4](https://godotengine.org/download)
2. Clone or download this repository
3. Open the project in Godot 4
4. Click the "Play" button or press F5 to run the game
