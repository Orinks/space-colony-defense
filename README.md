# Space Colony Defense

A roguelike tower defense game where you protect your space colony from waves of alien invaders.

## Overview

Defend your space colony against increasingly difficult waves of enemies. Manage resources, upgrade defenses, and make strategic decisions about when to press forward or retreat to safety.

### Key Features
- Control a defensive turret to protect your colony
- Fight multiple enemy types: Basic Invaders, Armored Ships, and Swarmers
- Collect and manage resources (energy, metal, food)
- Roguelike progression with permanent upgrades between runs
- Progressive difficulty scaling with each wave

## Development

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checker
mypy cli

# Run the game
python -m cli
```

## Project Structure
- `cli/` - Source files
  - `game/` - Core game logic
    - `turret.py` - Turret movement and shooting mechanics
    - `enemy_wave.py` - Enemy wave generation and behavior
- `tests/` - Test files
- `pyproject.toml` - Project configuration
