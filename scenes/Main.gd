extends Node

# Scene references
var main_menu_scene = preload("res://scenes/ui/MainMenu.tscn")
var game_scene = preload("res://scenes/Game.tscn")
var current_scene = null

func _ready():
	# Start with the main menu
	change_scene_to(main_menu_scene)
	
	# Connect to GameState signals
	GameState.game_over.connect(_on_game_over)

func _process(delta):
	# Handle global input
	if Input.is_action_just_pressed("pause") and current_scene == game_scene:
		# Toggle pause
		get_tree().paused = !get_tree().paused
		
		if get_tree().paused:
			AudioManager.play_narration("Game paused")
		else:
			AudioManager.play_narration("Game resumed")

func change_scene_to(scene):
	# Remove current scene if it exists
	if current_scene:
		current_scene.queue_free()
	
	# Instantiate new scene
	current_scene = scene.instantiate()
	add_child(current_scene)
	
	# Connect signals from the new scene
	if current_scene.has_signal("change_scene_requested"):
		current_scene.change_scene_requested.connect(_on_change_scene_requested)

func _on_change_scene_requested(scene_name):
	match scene_name:
		"main_menu":
			change_scene_to(main_menu_scene)
		"game":
			change_scene_to(game_scene)

func _on_game_over(victory):
	# Return to main menu after a delay
	await get_tree().create_timer(3.0).timeout
	change_scene_to(main_menu_scene)
