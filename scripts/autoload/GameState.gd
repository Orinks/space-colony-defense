extends Node

# Signals
signal resources_changed(resources)
signal wave_started(wave_num)
signal wave_completed(wave_num)
signal colony_damaged(amount)
signal game_over(victory)

# Colony properties
var colony_hp: int = 100
var colony_max_hp: int = 100

# Resources
var energy: int = 50
var metal: int = 20
var food: int = 10

# Game progression
var wave: int = 1
var tech_points: int = 0
var buildings: Array = []
var shield_strength: int = 0
var missiles: int = 0
var wave_skip_available: int = 0

# Wave tracking
var total_enemies_in_wave: int = 0
var enemies_defeated_in_current_wave: int = 0
var is_wave_complete: bool = false

# Game state
var is_game_active: bool = false
var is_in_management_phase: bool = false
var difficulty: int = 1

func _ready():
	# Initialize with default values
	reset_game_state()

func reset_game_state() -> void:
	# Reset colony
	colony_hp = 100
	colony_max_hp = 100

	# Reset resources
	energy = 50
	metal = 20
	food = 10

	# Reset progression
	wave = 1
	tech_points = 0
	buildings = []
	shield_strength = 0
	missiles = 0
	wave_skip_available = 0

	# Reset wave tracking
	total_enemies_in_wave = 0
	enemies_defeated_in_current_wave = 0
	is_wave_complete = false

	# Reset game state
	is_game_active = false
	is_in_management_phase = false

	# Load difficulty from config
	if SaveManager.has_config("game"):
		var config = SaveManager.get_config("game")
		difficulty = config.get("difficulty", 1)

	print("Game state reset")

func start_game() -> void:
	reset_game_state()
	is_game_active = true
	is_in_management_phase = false

	# Apply tech effects from persistent upgrades
	apply_tech_effects()

	# Start first wave
	start_wave(1)

	print("Game started")
	AudioManager.play_narration("Game started. Wave 1 incoming.")

func start_wave(wave_number: int) -> void:
	wave = wave_number
	is_wave_complete = false
	enemies_defeated_in_current_wave = 0
	is_in_management_phase = false

	# Generate enemies for this wave
	total_enemies_in_wave = 5 + wave * 2  # Simple formula for enemy count

	# Emit signal
	emit_signal("wave_started", wave)

	print("Wave " + str(wave) + " started with " + str(total_enemies_in_wave) + " enemies")
	AudioManager.play_narration("Wave " + str(wave) + " started. " + str(total_enemies_in_wave) + " enemies incoming.")
	AudioManager.play_music(AudioManager.MusicTrack.COMBAT)

func complete_wave() -> void:
	is_wave_complete = true
	is_in_management_phase = true

	# Award tech points for completing the wave
	var points_earned = max(1, wave / 3)
	tech_points += points_earned

	# Emit signal
	emit_signal("wave_completed", wave)

	print("Wave " + str(wave) + " completed. Gained " + str(points_earned) + " tech points.")
	AudioManager.play_narration("Wave " + str(wave) + " complete. Gained " + str(points_earned) + " tech points.")
	AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
	AudioManager.play_music(AudioManager.MusicTrack.MANAGEMENT)

	# Check if it was a boss wave (every 5 waves)
	if wave % 5 == 0:
		defeat_boss()

func defeat_boss() -> void:
	# Award extra tech points for defeating boss waves
	var boss_points = wave / 2
	tech_points += boss_points

	print("Boss defeated! Gained " + str(boss_points) + " additional tech points.")
	AudioManager.play_narration("Boss defeated! Gained " + str(boss_points) + " additional tech points.")

func start_next_wave() -> void:
	wave += 1
	start_wave(wave)

func enemy_defeated() -> void:
	enemies_defeated_in_current_wave += 1

	# Check if wave is complete
	if enemies_defeated_in_current_wave >= total_enemies_in_wave:
		complete_wave()

func damage_colony(amount: int) -> void:
	colony_hp = max(0, colony_hp - amount)

	# Emit signal
	emit_signal("colony_damaged", amount)

	print("Colony damaged! -" + str(amount) + " HP. Remaining: " + str(colony_hp) + "/" + str(colony_max_hp))
	AudioManager.play_narration("Colony damaged! " + str(amount) + " damage. " + str(colony_hp) + " health remaining.")
	AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)

	# Check for game over
	if colony_hp <= 0:
		trigger_game_over(false)

func heal_colony(amount: int) -> bool:
	# Check if we have enough resources
	if metal < amount / 2:
		AudioManager.play_narration("Not enough metal to repair colony.")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
		return false

	# Spend resources
	update_resources(0, -amount / 2, 0)

	# Heal colony
	var old_hp = colony_hp
	colony_hp = min(colony_max_hp, colony_hp + amount)
	var actual_heal = colony_hp - old_hp

	print("Colony repaired! +" + str(actual_heal) + " HP. Now: " + str(colony_hp) + "/" + str(colony_max_hp))
	AudioManager.play_narration("Colony repaired. " + str(actual_heal) + " health restored.")
	AudioManager.play_sound(AudioManager.SoundEffect.CONSTRUCTION_COMPLETE)

	return true

func update_resources(delta_energy: int, delta_metal: int, delta_food: int) -> void:
	var changed = false

	if delta_energy != 0:
		energy += delta_energy
		changed = true
		AudioManager.play_narration("Energy " + ("+" if delta_energy > 0 else "") + str(delta_energy))

	if delta_metal != 0:
		metal += delta_metal
		changed = true
		AudioManager.play_narration("Metal " + ("+" if delta_metal > 0 else "") + str(delta_metal))

	if delta_food != 0:
		food += delta_food
		changed = true
		AudioManager.play_narration("Food " + ("+" if delta_food > 0 else "") + str(delta_food))

	if changed:
		AudioManager.play_sound(AudioManager.SoundEffect.RESOURCE_CHANGE)
		emit_signal("resources_changed", {"energy": energy, "metal": metal, "food": food})

func add_building(building_type: String) -> bool:
	# Check if we have enough resources
	var cost = get_building_cost(building_type)
	if energy < cost.energy or metal < cost.metal or food < cost.food:
		AudioManager.play_narration("Not enough resources to build " + building_type)
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
		return false

	# Spend resources
	update_resources(-cost.energy, -cost.metal, -cost.food)

	# Add building
	buildings.append(building_type)

	print("Building constructed: " + building_type)
	AudioManager.play_narration(building_type + " constructed.")
	AudioManager.play_sound(AudioManager.SoundEffect.CONSTRUCTION_COMPLETE)

	return true

func get_building_cost(building_type: String) -> Dictionary:
	# Return the cost of a building
	match building_type:
		"Solar Panel":
			return {"energy": 10, "metal": 30, "food": 0}
		"Metal Extractor":
			return {"energy": 30, "metal": 20, "food": 0}
		"Farm":
			return {"energy": 20, "metal": 20, "food": 5}
		"Shield Generator":
			return {"energy": 50, "metal": 40, "food": 0}
		"Missile Silo":
			return {"energy": 40, "metal": 50, "food": 0}
		_:
			return {"energy": 0, "metal": 0, "food": 0}

func produce_from_buildings() -> void:
	# Generate resources from buildings
	for building in buildings:
		match building:
			"Solar Panel":
				update_resources(15, 0, 0)
			"Metal Extractor":
				update_resources(-5, 10, 0)
			"Farm":
				update_resources(-5, 0, 8)
			"Shield Generator":
				if energy >= 10:
					update_resources(-10, 0, 0)
					shield_strength = min(100, shield_strength + 25)
					AudioManager.play_narration("Shield charged to " + str(shield_strength) + " percent.")
			"Missile Silo":
				if energy >= 15 and metal >= 10:
					update_resources(-15, -10, 0)
					missiles += 1
					AudioManager.play_narration("Missile constructed. Total missiles: " + str(missiles))

func retreat() -> void:
	# Award tech points when player chooses to retreat
	if enemies_defeated_in_current_wave >= total_enemies_in_wave / 2:
		var points_earned = wave / 2
		tech_points += points_earned
		AudioManager.play_narration("Strategic retreat successful. Gained " + str(points_earned) + " tech points.")
	else:
		AudioManager.play_narration("Retreat completed. No tech points earned - not enough enemies defeated.")

	# End the game
	is_game_active = false
	AudioManager.play_music(AudioManager.MusicTrack.MENU)

func trigger_game_over(victory: bool) -> void:
	is_game_active = false

	if victory:
		print("Victory! Colony established successfully.")
		AudioManager.play_narration("Victory! Colony established successfully.")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
	else:
		print("Game over! Colony destroyed.")
		AudioManager.play_narration("Game over! Colony destroyed.")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)

	# Emit signal
	emit_signal("game_over", victory)
	AudioManager.play_music(AudioManager.MusicTrack.MENU)

func apply_tech_effects() -> void:
	# Apply effects from persistent tech upgrades
	# This would be implemented based on the tech tree system
	pass

func set_difficulty(level: int) -> void:
	difficulty = clamp(level, 1, 3)

	# Save to config
	var config = SaveManager.get_config("game") if SaveManager.has_config("game") else {}
	config["difficulty"] = difficulty
	SaveManager.set_config("game", config)
	SaveManager.save_config()

	print("Difficulty set to " + str(difficulty))
	AudioManager.play_narration("Difficulty set to " + str(difficulty))
