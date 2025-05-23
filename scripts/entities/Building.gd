extends Node2D

# Building types
enum BuildingType {
	SOLAR_PANEL,
	METAL_EXTRACTOR,
	FARM,
	SHIELD_GENERATOR,
	MISSILE_SILO
}

# Export variables for configuration in the editor
@export var type: BuildingType = BuildingType.SOLAR_PANEL
@export var level: int = 1

# Production properties
var production_rate: float = 1.0  # Production cycles per minute
var energy_production: int = 0
var metal_production: int = 0
var food_production: int = 0
var energy_consumption: int = 0

# Internal variables
var production_timer: Timer

func _ready():
	# Set up appearance based on building type
	setup_appearance()
	
	# Set up production values
	setup_production()
	
	# Set up production timer
	production_timer = Timer.new()
	production_timer.wait_time = 60.0 / production_rate  # Convert rate to seconds
	production_timer.autostart = true
	production_timer.name = "ProductionTimer"
	add_child(production_timer)
	production_timer.timeout.connect(_on_production_timer_timeout)

func setup_appearance():
	# Set up appearance based on building type
	# This would be replaced with proper sprites in a real implementation
	var color = Color.BLUE
	var size = Vector2(40, 40)
	
	match type:
		BuildingType.SOLAR_PANEL:
			color = Color.YELLOW
		BuildingType.METAL_EXTRACTOR:
			color = Color.GRAY
		BuildingType.FARM:
			color = Color.GREEN
		BuildingType.SHIELD_GENERATOR:
			color = Color.BLUE
		BuildingType.MISSILE_SILO:
			color = Color.RED
	
	# Create a simple shape for the building
	var shape = ColorRect.new()
	shape.color = color
	shape.size = size
	shape.position = -size / 2  # Center the shape
	add_child(shape)
	
	# Add label with building name
	var label = Label.new()
	label.text = get_type_name()
	label.position = Vector2(-label.size.x / 2, size.y / 2 + 5)
	add_child(label)

func setup_production():
	match type:
		BuildingType.SOLAR_PANEL:
			energy_production = 15 * level
			metal_production = 0
			food_production = 0
			energy_consumption = 0
		BuildingType.METAL_EXTRACTOR:
			energy_production = 0
			metal_production = 10 * level
			food_production = 0
			energy_consumption = 5 * level
		BuildingType.FARM:
			energy_production = 0
			metal_production = 0
			food_production = 8 * level
			energy_consumption = 5 * level
		BuildingType.SHIELD_GENERATOR:
			energy_production = 0
			metal_production = 0
			food_production = 0
			energy_consumption = 10 * level
		BuildingType.MISSILE_SILO:
			energy_production = 0
			metal_production = 0
			food_production = 0
			energy_consumption = 15 * level

func _on_production_timer_timeout():
	produce_resources()

func produce_resources():
	# Check if we have enough energy for consumption
	if energy_consumption > 0 and GameState.energy < energy_consumption:
		AudioManager.play_narration(get_type_name() + " not producing - insufficient energy")
		return
	
	# Consume energy
	if energy_consumption > 0:
		GameState.update_resources(-energy_consumption, 0, 0)
	
	# Produce resources
	var resources_produced = false
	
	if energy_production > 0:
		GameState.update_resources(energy_production, 0, 0)
		resources_produced = true
	
	if metal_production > 0:
		GameState.update_resources(0, metal_production, 0)
		resources_produced = true
	
	if food_production > 0:
		GameState.update_resources(0, 0, food_production)
		resources_produced = true
	
	# Handle special building effects
	match type:
		BuildingType.SHIELD_GENERATOR:
			if GameState.shield_strength < 100:
				GameState.shield_strength = min(100, GameState.shield_strength + 25 * level)
				AudioManager.play_narration("Shield charged to " + str(GameState.shield_strength) + " percent")
				resources_produced = true
		BuildingType.MISSILE_SILO:
			if GameState.metal >= 10 * level:
				GameState.update_resources(0, -10 * level, 0)
				GameState.missiles += 1
				AudioManager.play_narration("Missile constructed. Total missiles: " + str(GameState.missiles))
				resources_produced = true
	
	if resources_produced:
		AudioManager.play_sound(AudioManager.SoundEffect.RESOURCE_CHANGE)

func upgrade():
	if level < 3:  # Maximum level
		level += 1
		setup_production()
		AudioManager.play_narration(get_type_name() + " upgraded to level " + str(level))
		AudioManager.play_sound(AudioManager.SoundEffect.CONSTRUCTION_COMPLETE)
		return true
	else:
		AudioManager.play_narration(get_type_name() + " already at maximum level")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
		return false

func get_type_name() -> String:
	match type:
		BuildingType.SOLAR_PANEL:
			return "Solar Panel"
		BuildingType.METAL_EXTRACTOR:
			return "Metal Extractor"
		BuildingType.FARM:
			return "Farm"
		BuildingType.SHIELD_GENERATOR:
			return "Shield Generator"
		BuildingType.MISSILE_SILO:
			return "Missile Silo"
		_:
			return "Unknown"

func get_upgrade_cost() -> Dictionary:
	var base_cost = {
		BuildingType.SOLAR_PANEL: {"energy": 20, "metal": 30, "food": 0},
		BuildingType.METAL_EXTRACTOR: {"energy": 30, "metal": 20, "food": 0},
		BuildingType.FARM: {"energy": 20, "metal": 20, "food": 10},
		BuildingType.SHIELD_GENERATOR: {"energy": 50, "metal": 40, "food": 0},
		BuildingType.MISSILE_SILO: {"energy": 40, "metal": 50, "food": 0}
	}
	
	var cost = base_cost[type]
	
	# Scale cost with level
	for resource in cost:
		cost[resource] = cost[resource] * level
	
	return cost
