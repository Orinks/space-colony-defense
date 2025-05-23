extends Node

# Constants
const CONFIG_DIR = "user://space_colony_defense"
const CONFIG_FILE = "user://space_colony_defense/config.json"
const SAVE_DIR = "user://space_colony_defense/saves"
const TECH_TREE_FILE = "user://space_colony_defense/tech_tree.json"

# Configuration data
var config_data: Dictionary = {}

func _ready():
	# Ensure directories exist
	ensure_directories()
	
	# Load configuration
	load_config()

func ensure_directories() -> void:
	# Create config directory if it doesn't exist
	var dir = DirAccess.open("user://")
	if not dir.dir_exists("space_colony_defense"):
		dir.make_dir("space_colony_defense")
		print("Created configuration directory: user://space_colony_defense")
	
	# Create saves directory if it doesn't exist
	dir = DirAccess.open("user://space_colony_defense")
	if not dir.dir_exists("saves"):
		dir.make_dir("saves")
		print("Created saves directory: user://space_colony_defense/saves")

func load_config() -> void:
	# Load configuration from file
	if FileAccess.file_exists(CONFIG_FILE):
		var file = FileAccess.open(CONFIG_FILE, FileAccess.READ)
		var json_string = file.get_as_text()
		var json = JSON.new()
		var error = json.parse(json_string)
		
		if error == OK:
			config_data = json.get_data()
			print("Loaded configuration: ", config_data)
		else:
			print("Error parsing configuration file: ", json.get_error_message())
			config_data = {}
	else:
		print("Configuration file not found, using defaults")
		config_data = {
			"audio": {
				"enable_sounds": true,
				"enable_narration": true,
				"use_running_screen_reader": true,
				"speech_rate": 150,
				"sound_volume": 1.0,
				"narration_volume": 1.0
			},
			"game": {
				"difficulty": 1
			}
		}
		save_config()

func save_config() -> void:
	# Save configuration to file
	var file = FileAccess.open(CONFIG_FILE, FileAccess.WRITE)
	var json_string = JSON.stringify(config_data, "  ")
	file.store_string(json_string)
	print("Saved configuration")

func has_config(section: String) -> bool:
	# Check if a configuration section exists
	return config_data.has(section)

func get_config(section: String) -> Dictionary:
	# Get a configuration section
	if has_config(section):
		return config_data[section]
	return {}

func set_config(section: String, data: Dictionary) -> void:
	# Set a configuration section
	config_data[section] = data

func save_game(slot: int = 1) -> bool:
	# Save the current game state to a file
	var save_path = SAVE_DIR + "/save_" + str(slot) + ".json"
	
	# Create save data
	var save_data = {
		"colony": {
			"hp": GameState.colony_hp,
			"max_hp": GameState.colony_max_hp
		},
		"resources": {
			"energy": GameState.energy,
			"metal": GameState.metal,
			"food": GameState.food
		},
		"progression": {
			"wave": GameState.wave,
			"tech_points": GameState.tech_points,
			"buildings": GameState.buildings,
			"shield_strength": GameState.shield_strength,
			"missiles": GameState.missiles,
			"wave_skip_available": GameState.wave_skip_available
		},
		"timestamp": Time.get_unix_time_from_system(),
		"version": "1.0"
	}
	
	# Save to file
	var file = FileAccess.open(save_path, FileAccess.WRITE)
	var json_string = JSON.stringify(save_data, "  ")
	file.store_string(json_string)
	
	print("Game saved to slot " + str(slot))
	return true

func load_game(slot: int = 1) -> bool:
	# Load a saved game from a file
	var save_path = SAVE_DIR + "/save_" + str(slot) + ".json"
	
	if not FileAccess.file_exists(save_path):
		print("Save file not found: " + save_path)
		return false
	
	# Load from file
	var file = FileAccess.open(save_path, FileAccess.READ)
	var json_string = file.get_as_text()
	var json = JSON.new()
	var error = json.parse(json_string)
	
	if error != OK:
		print("Error parsing save file: " + json.get_error_message())
		return false
	
	var save_data = json.get_data()
	
	# Apply save data to game state
	GameState.colony_hp = save_data["colony"]["hp"]
	GameState.colony_max_hp = save_data["colony"]["max_hp"]
	
	GameState.energy = save_data["resources"]["energy"]
	GameState.metal = save_data["resources"]["metal"]
	GameState.food = save_data["resources"]["food"]
	
	GameState.wave = save_data["progression"]["wave"]
	GameState.tech_points = save_data["progression"]["tech_points"]
	GameState.buildings = save_data["progression"]["buildings"]
	GameState.shield_strength = save_data["progression"]["shield_strength"]
	GameState.missiles = save_data["progression"]["missiles"]
	GameState.wave_skip_available = save_data["progression"]["wave_skip_available"]
	
	print("Game loaded from slot " + str(slot))
	return true

func auto_save() -> bool:
	# Automatically save the game to a special auto-save slot
	return save_game(0)

func list_save_files() -> Array:
	# List all available save files
	var save_files = []
	var dir = DirAccess.open(SAVE_DIR)
	
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		while file_name != "":
			if not dir.current_is_dir() and file_name.ends_with(".json"):
				save_files.append(file_name)
			file_name = dir.get_next()
	
	return save_files

func get_save_info(file_name: String) -> Dictionary:
	# Get information about a save file
	var save_path = SAVE_DIR + "/" + file_name
	
	if not FileAccess.file_exists(save_path):
		return {}
	
	# Load from file
	var file = FileAccess.open(save_path, FileAccess.READ)
	var json_string = file.get_as_text()
	var json = JSON.new()
	var error = json.parse(json_string)
	
	if error != OK:
		return {}
	
	var save_data = json.get_data()
	
	# Extract relevant info
	var info = {
		"wave": save_data["progression"]["wave"],
		"colony_hp": save_data["colony"]["hp"],
		"colony_max_hp": save_data["colony"]["max_hp"],
		"timestamp": save_data["timestamp"],
		"version": save_data["version"]
	}
	
	return info

func save_tech_tree(tech_tree: Dictionary) -> bool:
	# Save the tech tree to a file
	var file = FileAccess.open(TECH_TREE_FILE, FileAccess.WRITE)
	var json_string = JSON.stringify(tech_tree, "  ")
	file.store_string(json_string)
	
	print("Tech tree saved")
	return true

func load_tech_tree() -> Dictionary:
	# Load the tech tree from a file
	if not FileAccess.file_exists(TECH_TREE_FILE):
		print("Tech tree file not found")
		return {"owned_techs": {}, "available_points": 0}
	
	# Load from file
	var file = FileAccess.open(TECH_TREE_FILE, FileAccess.READ)
	var json_string = file.get_as_text()
	var json = JSON.new()
	var error = json.parse(json_string)
	
	if error != OK:
		print("Error parsing tech tree file: " + json.get_error_message())
		return {"owned_techs": {}, "available_points": 0}
	
	var tech_tree = json.get_data()
	print("Tech tree loaded")
	
	return tech_tree
