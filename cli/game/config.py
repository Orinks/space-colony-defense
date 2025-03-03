"""Configuration management for the game."""
import os
import json
from typing import Dict, Any, Optional

# Default configuration path
CONFIG_DIR = os.path.expanduser("~/.space_colony_defense")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Default configuration
DEFAULT_CONFIG = {
    "audio": {
        "enable_sounds": True,
        "enable_narration": True,
        "use_running_screen_reader": True,
        "speech_rate": 150,
        "sound_volume": 1.0,
        "narration_volume": 1.0
    },
    "game": {
        "difficulty": 1
    }
}


def ensure_config_dir() -> None:
    """Ensure the configuration directory exists."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        print(f"Created configuration directory: {CONFIG_DIR}")


def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default if it doesn't exist."""
    ensure_config_dir()
    
    print(f"Loading configuration from: {CONFIG_FILE}")
    
    if not os.path.exists(CONFIG_FILE):
        # Create default configuration file
        print("Configuration file does not exist, creating default")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        print(f"Loaded configuration: {config}")
        
        # Ensure all default keys exist (in case config file is from older version)
        merged_config = DEFAULT_CONFIG.copy()
        for section, values in config.items():
            if section in merged_config:
                merged_config[section].update(values)
        
        print(f"Merged configuration: {merged_config}")
        return merged_config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    
    print(f"Saving configuration to: {CONFIG_FILE}")
    print(f"Configuration to save: {config}")
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print("Configuration saved successfully")
    except Exception as e:
        print(f"Error saving configuration: {e}")


def get_audio_config() -> Dict[str, Any]:
    """Get audio configuration."""
    config = load_config()
    return config.get("audio", DEFAULT_CONFIG["audio"])


def save_audio_config(audio_config: Dict[str, Any]) -> None:
    """Save audio configuration."""
    config = load_config()
    config["audio"] = audio_config
    save_config(config)


def get_game_config() -> Dict[str, Any]:
    """Get game configuration."""
    config = load_config()
    return config.get("game", DEFAULT_CONFIG["game"])


def save_game_config(game_config: Dict[str, Any]) -> None:
    """Save game configuration."""
    config = load_config()
    config["game"] = game_config
    save_config(config)
