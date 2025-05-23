extends Node2D

# Signals
signal change_scene_requested(scene_name)

# Scene references
var enemy_scene = preload("res://scenes/Enemy.tscn")
var turret_scene = preload("res://scenes/Turret.tscn")
var projectile_scene = preload("res://scenes/Projectile.tscn")
var building_scene = preload("res://scenes/Building.tscn")

# Game state
var is_wave_active = false
var is_in_management_phase = false
var enemies_spawned = 0
var enemies_remaining = 0
var screen_size = Vector2.ZERO

# UI references
@onready var energy_label = $UI/ResourcesPanel/EnergyLabel
@onready var metal_label = $UI/ResourcesPanel/MetalLabel
@onready var food_label = $UI/ResourcesPanel/FoodLabel
@onready var colony_label = $UI/ColonyPanel/ColonyLabel
@onready var wave_label = $UI/WavePanel/WaveLabel
@onready var shield_label = $UI/ShieldPanel/ShieldLabel
@onready var pause_menu = $UI/PauseMenu
@onready var management_menu = $UI/ManagementMenu

# Node references
@onready var turret_node = $Turret
@onready var enemies_node = $Enemies
@onready var projectiles_node = $Projectiles
@onready var buildings_node = $Buildings
@onready var wave_timer = $WaveTimer
@onready var enemy_spawn_timer = $EnemySpawnTimer

func _ready():
	# Get screen size
	screen_size = get_viewport_rect().size
	
	# Connect signals
	GameState.resources_changed.connect(_on_resources_changed)
	GameState.wave_started.connect(_on_wave_started)
	GameState.wave_completed.connect(_on_wave_completed)
	GameState.colony_damaged.connect(_on_colony_damaged)
	GameState.game_over.connect(_on_game_over)
	
	wave_timer.timeout.connect(_on_wave_timer_timeout)
	enemy_spawn_timer.timeout.connect(_on_enemy_spawn_timer_timeout)
	
	# Initialize UI
	update_ui()
	
	# Create turret
	var turret = turret_scene.instantiate()
	turret.position = Vector2(screen_size.x / 2, screen_size.y - 50)
	turret_node.add_child(turret)
	
	# Connect turret signals
	turret.shot_fired.connect(_on_turret_shot_fired)
	turret.damaged.connect(_on_turret_damaged)
	turret.shield_changed.connect(_on_turret_shield_changed)
	
	# Start game
	GameState.start_game()

func _process(delta):
	# Handle pause
	if Input.is_action_just_pressed("pause"):
		toggle_pause()

func update_ui():
	# Update resource labels
	energy_label.text = "Energy: " + str(GameState.energy)
	metal_label.text = "Metal: " + str(GameState.metal)
	food_label.text = "Food: " + str(GameState.food)
	
	# Update colony label
	colony_label.text = "Colony: " + str(GameState.colony_hp) + "/" + str(GameState.colony_max_hp)
	
	# Update wave label
	wave_label.text = "Wave: " + str(GameState.wave)
	
	# Update shield label
	shield_label.text = "Shield: " + str(GameState.shield_strength) + "%"

func toggle_pause():
	get_tree().paused = !get_tree().paused
	pause_menu.visible = get_tree().paused
	
	if get_tree().paused:
		AudioManager.play_narration("Game paused")
	else:
		AudioManager.play_narration("Game resumed")

func start_wave(wave_number):
	# Reset wave state
	is_wave_active = true
	is_in_management_phase = false
	enemies_spawned = 0
	enemies_remaining = GameState.total_enemies_in_wave
	
	# Hide management menu
	management_menu.visible = false
	
	# Start enemy spawning
	enemy_spawn_timer.start()
	
	# Update UI
	update_ui()
	
	# Play wave start sound
	AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
	AudioManager.play_narration("Wave " + str(wave_number) + " starting")

func spawn_enemy():
	if enemies_spawned >= GameState.total_enemies_in_wave:
		enemy_spawn_timer.stop()
		return
	
	# Create enemy
	var enemy = enemy_scene.instantiate()
	
	# Set enemy type based on wave number
	if GameState.wave >= 5 and randf() < 0.2:
		enemy.type = enemy.EnemyType.SWARMER
	elif GameState.wave >= 3 and randf() < 0.3:
		enemy.type = enemy.EnemyType.ARMORED_SHIP
	else:
		enemy.type = enemy.EnemyType.BASIC_INVADER
	
	# Set enemy position
	enemy.position = Vector2(randf_range(50, screen_size.x - 50), -50)
	
	# Connect signals
	enemy.defeated.connect(_on_enemy_defeated)
	enemy.reached_bottom.connect(_on_enemy_reached_bottom)
	
	# Add to scene
	enemies_node.add_child(enemy)
	
	# Increment counter
	enemies_spawned += 1
	
	# Narrate enemy spawn for accessibility
	if enemies_spawned == 1 or enemies_spawned % 5 == 0:
		AudioManager.play_narration(enemy.get_type_name() + " spawned. " + str(enemies_remaining) + " enemies remaining")

func _on_resources_changed(resources):
	update_ui()

func _on_wave_started(wave_num):
	start_wave(wave_num)

func _on_wave_completed(wave_num):
	is_wave_active = false
	is_in_management_phase = true
	
	# Show management menu
	management_menu.visible = true
	
	# Update UI
	update_ui()

func _on_colony_damaged(amount):
	update_ui()

func _on_game_over(victory):
	# Stop all timers
	wave_timer.stop()
	enemy_spawn_timer.stop()
	
	# Clear enemies
	for enemy in enemies_node.get_children():
		enemy.queue_free()
	
	# Show game over message
	if victory:
		AudioManager.play_narration("Victory! Colony established successfully.")
	else:
		AudioManager.play_narration("Game over! Colony destroyed.")
	
	# Return to main menu after delay
	await get_tree().create_timer(3.0).timeout
	emit_signal("change_scene_requested", "main_menu")

func _on_turret_shot_fired(projectile):
	projectiles_node.add_child(projectile)

func _on_turret_damaged(amount):
	# Update UI
	update_ui()

func _on_turret_shield_changed(value):
	# Update shield label
	shield_label.text = "Shield: " + str(value) + "%"

func _on_enemy_defeated(enemy):
	enemies_remaining -= 1
	GameState.enemy_defeated()
	
	# Check if wave is complete
	if enemies_remaining <= 0 and enemies_spawned >= GameState.total_enemies_in_wave:
		wave_timer.start()

func _on_enemy_reached_bottom(enemy):
	enemies_remaining -= 1
	
	# Damage colony
	GameState.damage_colony(enemy.damage)
	
	# Check if wave is complete
	if enemies_remaining <= 0 and enemies_spawned >= GameState.total_enemies_in_wave:
		wave_timer.start()

func _on_wave_timer_timeout():
	if not GameState.is_wave_complete:
		GameState.complete_wave()

func _on_enemy_spawn_timer_timeout():
	spawn_enemy()
