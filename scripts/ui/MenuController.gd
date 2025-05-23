extends Control

# Signals
signal menu_option_selected(option)

# Menu types
enum MenuType {
	MAIN,
	OPTIONS,
	PAUSE,
	MANAGEMENT,
	TECH_TREE
}

# Current menu state
var current_menu: int = MenuType.MAIN
var selected_index: int = 0
var options: Array = []
var option_nodes: Array = []

# Accessibility properties
var last_narrated_option: String = ""

func _ready():
	# Set up initial menu
	set_menu(MenuType.MAIN)

func _process(delta):
	# Handle menu navigation
	if Input.is_action_just_pressed("ui_up"):
		navigate_menu(-1)
	elif Input.is_action_just_pressed("ui_down"):
		navigate_menu(1)
	elif Input.is_action_just_pressed("ui_accept"):
		select_current_option()

func set_menu(menu_type: int):
	current_menu = menu_type
	selected_index = 0
	options = []
	
	# Clear existing option nodes
	for node in option_nodes:
		if is_instance_valid(node):
			node.queue_free()
	option_nodes = []
	
	# Set up options based on menu type
	match menu_type:
		MenuType.MAIN:
			options = ["New Game", "Load Game", "Options", "Quit"]
			AudioManager.play_narration("Main Menu")
		MenuType.OPTIONS:
			options = ["Sound Effects: " + ("On" if AudioManager.enable_sounds else "Off"),
					  "Narration: " + ("On" if AudioManager.enable_narration else "Off"),
					  "Screen Reader Mode: " + ("Running" if AudioManager.use_running_screen_reader else "Direct"),
					  "Sound Volume: " + str(int(AudioManager.sound_volume * 100)) + "%",
					  "Narration Volume: " + str(int(AudioManager.narration_volume * 100)) + "%",
					  "Speech Rate: " + str(AudioManager.speech_rate),
					  "Difficulty: " + str(GameState.difficulty),
					  "Back"]
			AudioManager.play_narration("Options Menu")
		MenuType.PAUSE:
			options = ["Resume", "Save Game", "Options", "Quit to Main Menu"]
			AudioManager.play_narration("Game Paused")
		MenuType.MANAGEMENT:
			options = ["Build Solar Panel", "Build Metal Extractor", "Build Farm", 
					  "Build Shield Generator", "Build Missile Silo", 
					  "Repair Colony", "Start Next Wave", "Save and Quit"]
			AudioManager.play_narration("Management Phase")
		MenuType.TECH_TREE:
			options = ["Colony Upgrades", "Resource Upgrades", "Weapon Upgrades", "Back"]
			AudioManager.play_narration("Tech Tree")
	
	# Create option nodes
	create_option_nodes()
	
	# Narrate first option
	if options.size() > 0:
		narrate_option(options[0])

func create_option_nodes():
	var y_offset = 100
	var spacing = 50
	
	for i in range(options.size()):
		var option = options[i]
		var label = Label.new()
		label.text = option
		label.position = Vector2(50, y_offset + i * spacing)
		label.add_theme_color_override("font_color", Color.WHITE)
		add_child(label)
		option_nodes.append(label)

func navigate_menu(direction: int):
	# Update selected index
	selected_index = (selected_index + direction) % options.size()
	if selected_index < 0:
		selected_index = options.size() - 1
	
	# Update visual selection
	update_selection()
	
	# Play sound
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)
	
	# Narrate option
	narrate_option(options[selected_index])

func update_selection():
	for i in range(option_nodes.size()):
		var node = option_nodes[i]
		if i == selected_index:
			node.add_theme_color_override("font_color", Color.YELLOW)
		else:
			node.add_theme_color_override("font_color", Color.WHITE)

func narrate_option(option: String):
	if option != last_narrated_option:
		AudioManager.play_narration(option)
		last_narrated_option = option

func select_current_option():
	if selected_index >= 0 and selected_index < options.size():
		var option = options[selected_index]
		
		# Play sound
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
		
		# Handle option based on current menu
		match current_menu:
			MenuType.MAIN:
				handle_main_menu_option(option)
			MenuType.OPTIONS:
				handle_options_menu_option(option)
			MenuType.PAUSE:
				handle_pause_menu_option(option)
			MenuType.MANAGEMENT:
				handle_management_menu_option(option)
			MenuType.TECH_TREE:
				handle_tech_tree_menu_option(option)
		
		# Emit signal
		emit_signal("menu_option_selected", option)

func handle_main_menu_option(option: String):
	match option:
		"New Game":
			AudioManager.play_narration("Starting new game")
			GameState.start_game()
			# Switch to game scene
		"Load Game":
			AudioManager.play_narration("Loading game")
			# Show load game menu
		"Options":
			set_menu(MenuType.OPTIONS)
		"Quit":
			AudioManager.play_narration("Quitting game")
			get_tree().quit()

func handle_options_menu_option(option: String):
	if option.begins_with("Sound Effects:"):
		AudioManager.set_sound_enabled(not AudioManager.enable_sounds)
		set_menu(MenuType.OPTIONS)  # Refresh menu
	elif option.begins_with("Narration:"):
		AudioManager.set_narration_enabled(not AudioManager.enable_narration)
		set_menu(MenuType.OPTIONS)  # Refresh menu
	elif option.begins_with("Screen Reader Mode:"):
		AudioManager.toggle_running_screen_reader(not AudioManager.use_running_screen_reader)
		set_menu(MenuType.OPTIONS)  # Refresh menu
	elif option.begins_with("Sound Volume:"):
		# Cycle through volume levels: 25%, 50%, 75%, 100%
		var new_volume = AudioManager.sound_volume + 0.25
		if new_volume > 1.0:
			new_volume = 0.25
		AudioManager.set_sound_volume(new_volume)
		set_menu(MenuType.OPTIONS)  # Refresh menu
	elif option.begins_with("Narration Volume:"):
		# Cycle through volume levels: 25%, 50%, 75%, 100%
		var new_volume = AudioManager.narration_volume + 0.25
		if new_volume > 1.0:
			new_volume = 0.25
		AudioManager.set_narration_volume(new_volume)
		set_menu(MenuType.OPTIONS)  # Refresh menu
	elif option.begins_with("Speech Rate:"):
		# Cycle through speech rates: 100, 150, 200, 250
		var new_rate = AudioManager.speech_rate + 50
		if new_rate > 250:
			new_rate = 100
		AudioManager.set_speech_rate(new_rate)
		set_menu(MenuType.OPTIONS)  # Refresh menu
	elif option.begins_with("Difficulty:"):
		# Cycle through difficulty levels: 1, 2, 3
		var new_difficulty = GameState.difficulty + 1
		if new_difficulty > 3:
			new_difficulty = 1
		GameState.set_difficulty(new_difficulty)
		set_menu(MenuType.OPTIONS)  # Refresh menu
	elif option == "Back":
		set_menu(MenuType.MAIN)

func handle_pause_menu_option(option: String):
	match option:
		"Resume":
			AudioManager.play_narration("Resuming game")
			# Resume game
		"Save Game":
			AudioManager.play_narration("Saving game")
			SaveManager.save_game()
		"Options":
			set_menu(MenuType.OPTIONS)
		"Quit to Main Menu":
			AudioManager.play_narration("Quitting to main menu")
			set_menu(MenuType.MAIN)

func handle_management_menu_option(option: String):
	if option.begins_with("Build "):
		var building_type = option.substr(6)  # Remove "Build " prefix
		
		# Check if we have enough resources
		var cost = GameState.get_building_cost(building_type)
		if GameState.energy >= cost.energy and GameState.metal >= cost.metal and GameState.food >= cost.food:
			if GameState.add_building(building_type):
				AudioManager.play_narration(building_type + " constructed")
				set_menu(MenuType.MANAGEMENT)  # Refresh menu
		else:
			AudioManager.play_narration("Not enough resources to build " + building_type)
			AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
	elif option == "Repair Colony":
		if GameState.colony_hp < GameState.colony_max_hp:
			var repair_amount = 20
			if GameState.heal_colony(repair_amount):
				set_menu(MenuType.MANAGEMENT)  # Refresh menu
		else:
			AudioManager.play_narration("Colony already at full health")
			AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
	elif option == "Start Next Wave":
		AudioManager.play_narration("Starting next wave")
		GameState.start_next_wave()
	elif option == "Save and Quit":
		SaveManager.save_game()
		AudioManager.play_narration("Game saved")
		set_menu(MenuType.MAIN)

func handle_tech_tree_menu_option(option: String):
	match option:
		"Colony Upgrades":
			AudioManager.play_narration("Colony Upgrades")
			# Show colony upgrades
		"Resource Upgrades":
			AudioManager.play_narration("Resource Upgrades")
			# Show resource upgrades
		"Weapon Upgrades":
			AudioManager.play_narration("Weapon Upgrades")
			# Show weapon upgrades
		"Back":
			set_menu(MenuType.MANAGEMENT)
