extends Control

# Signals
signal change_scene_requested(scene_name)

# UI references
@onready var new_game_button = $MenuOptions/NewGameButton
@onready var load_game_button = $MenuOptions/LoadGameButton
@onready var options_button = $MenuOptions/OptionsButton
@onready var quit_button = $MenuOptions/QuitButton

@onready var options_menu = $OptionsMenu
@onready var sound_effects_button = $OptionsMenu/OptionsContainer/SoundEffectsButton
@onready var narration_button = $OptionsMenu/OptionsContainer/NarrationButton
@onready var screen_reader_button = $OptionsMenu/OptionsContainer/ScreenReaderButton
@onready var sound_volume_button = $OptionsMenu/OptionsContainer/SoundVolumeButton
@onready var narration_volume_button = $OptionsMenu/OptionsContainer/NarrationVolumeButton
@onready var speech_rate_button = $OptionsMenu/OptionsContainer/SpeechRateButton
@onready var difficulty_button = $OptionsMenu/OptionsContainer/DifficultyButton
@onready var options_back_button = $OptionsMenu/OptionsContainer/BackButton

@onready var load_game_menu = $LoadGameMenu
@onready var saves_list = $LoadGameMenu/SavesList
@onready var no_saves_label = $LoadGameMenu/SavesList/NoSavesLabel
@onready var load_game_back_button = $LoadGameMenu/BackButton

# Current menu state
var current_menu = "main"

func _ready():
	# Connect button signals
	new_game_button.pressed.connect(_on_new_game_button_pressed)
	load_game_button.pressed.connect(_on_load_game_button_pressed)
	options_button.pressed.connect(_on_options_button_pressed)
	quit_button.pressed.connect(_on_quit_button_pressed)
	
	sound_effects_button.pressed.connect(_on_sound_effects_button_pressed)
	narration_button.pressed.connect(_on_narration_button_pressed)
	screen_reader_button.pressed.connect(_on_screen_reader_button_pressed)
	sound_volume_button.pressed.connect(_on_sound_volume_button_pressed)
	narration_volume_button.pressed.connect(_on_narration_volume_button_pressed)
	speech_rate_button.pressed.connect(_on_speech_rate_button_pressed)
	difficulty_button.pressed.connect(_on_difficulty_button_pressed)
	options_back_button.pressed.connect(_on_options_back_button_pressed)
	
	load_game_back_button.pressed.connect(_on_load_game_back_button_pressed)
	
	# Set initial focus
	new_game_button.grab_focus()
	
	# Update options buttons
	update_options_buttons()
	
	# Play menu music
	AudioManager.play_music(AudioManager.MusicTrack.MENU)
	
	# Welcome narration
	AudioManager.play_narration("Space Colony Defense. Main Menu.")

func _process(delta):
	# Handle back button
	if Input.is_action_just_pressed("ui_cancel"):
		match current_menu:
			"options":
				_on_options_back_button_pressed()
			"load_game":
				_on_load_game_back_button_pressed()

func show_menu(menu_name):
	# Hide all menus
	$MenuOptions.visible = false
	options_menu.visible = false
	load_game_menu.visible = false
	
	# Show selected menu
	match menu_name:
		"main":
			$MenuOptions.visible = true
			new_game_button.grab_focus()
		"options":
			options_menu.visible = true
			sound_effects_button.grab_focus()
		"load_game":
			load_game_menu.visible = true
			load_save_files()
			if saves_list.get_child_count() > 1:  # More than just the NoSavesLabel
				saves_list.get_child(1).grab_focus()  # Focus first save
			else:
				load_game_back_button.grab_focus()
	
	current_menu = menu_name

func update_options_buttons():
	# Update button text based on current settings
	sound_effects_button.text = "Sound Effects: " + ("On" if AudioManager.enable_sounds else "Off")
	narration_button.text = "Narration: " + ("On" if AudioManager.enable_narration else "Off")
	screen_reader_button.text = "Screen Reader: " + ("Running" if AudioManager.use_running_screen_reader else "Direct")
	sound_volume_button.text = "Sound Volume: " + str(int(AudioManager.sound_volume * 100)) + "%"
	narration_volume_button.text = "Narration Volume: " + str(int(AudioManager.narration_volume * 100)) + "%"
	speech_rate_button.text = "Speech Rate: " + str(AudioManager.speech_rate)
	difficulty_button.text = "Difficulty: " + str(GameState.difficulty)

func load_save_files():
	# Clear existing save buttons
	for child in saves_list.get_children():
		if child != no_saves_label:
			child.queue_free()
	
	# Get save files
	var save_files = SaveManager.list_save_files()
	
	if save_files.size() > 0:
		no_saves_label.visible = false
		
		for i in range(save_files.size()):
			var file_name = save_files[i]
			var save_info = SaveManager.get_save_info(file_name)
			
			var button = Button.new()
			button.text = "Save " + str(i + 1) + " - Wave " + str(save_info.get("wave", 1))
			button.pressed.connect(_on_save_button_pressed.bind(i + 1))
			
			if i == 0:
				button.focus_neighbor_top = load_game_back_button.get_path()
			if i == save_files.size() - 1:
				button.focus_neighbor_bottom = load_game_back_button.get_path()
			
			saves_list.add_child(button)
	else:
		no_saves_label.visible = true

func _on_new_game_button_pressed():
	AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
	AudioManager.play_narration("Starting new game")
	emit_signal("change_scene_requested", "game")

func _on_load_game_button_pressed():
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)
	AudioManager.play_narration("Load game")
	show_menu("load_game")

func _on_options_button_pressed():
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)
	AudioManager.play_narration("Options")
	show_menu("options")

func _on_quit_button_pressed():
	AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
	AudioManager.play_narration("Quitting game")
	get_tree().quit()

func _on_sound_effects_button_pressed():
	AudioManager.set_sound_enabled(not AudioManager.enable_sounds)
	update_options_buttons()
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)

func _on_narration_button_pressed():
	AudioManager.set_narration_enabled(not AudioManager.enable_narration)
	update_options_buttons()
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)

func _on_screen_reader_button_pressed():
	AudioManager.toggle_running_screen_reader(not AudioManager.use_running_screen_reader)
	update_options_buttons()
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)

func _on_sound_volume_button_pressed():
	# Cycle through volume levels: 25%, 50%, 75%, 100%
	var new_volume = AudioManager.sound_volume + 0.25
	if new_volume > 1.0:
		new_volume = 0.25
	AudioManager.set_sound_volume(new_volume)
	update_options_buttons()
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)

func _on_narration_volume_button_pressed():
	# Cycle through volume levels: 25%, 50%, 75%, 100%
	var new_volume = AudioManager.narration_volume + 0.25
	if new_volume > 1.0:
		new_volume = 0.25
	AudioManager.set_narration_volume(new_volume)
	update_options_buttons()
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)

func _on_speech_rate_button_pressed():
	# Cycle through speech rates: 100, 150, 200, 250
	var new_rate = AudioManager.speech_rate + 50
	if new_rate > 250:
		new_rate = 100
	AudioManager.set_speech_rate(new_rate)
	update_options_buttons()
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)

func _on_difficulty_button_pressed():
	# Cycle through difficulty levels: 1, 2, 3
	var new_difficulty = GameState.difficulty + 1
	if new_difficulty > 3:
		new_difficulty = 1
	GameState.set_difficulty(new_difficulty)
	update_options_buttons()
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)

func _on_options_back_button_pressed():
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)
	AudioManager.play_narration("Back to main menu")
	show_menu("main")

func _on_load_game_back_button_pressed():
	AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)
	AudioManager.play_narration("Back to main menu")
	show_menu("main")

func _on_save_button_pressed(slot):
	AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
	AudioManager.play_narration("Loading save " + str(slot))
	
	if SaveManager.load_game(slot):
		emit_signal("change_scene_requested", "game")
	else:
		AudioManager.play_narration("Failed to load save")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
