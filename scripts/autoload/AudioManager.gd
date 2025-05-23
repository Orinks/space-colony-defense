extends Node

# Enums for sound effects and music tracks
enum SoundEffect {
	TURRET_MOVE,
	TURRET_SHOOT,
	ENEMY_HIT,
	ACTION_SUCCESS,
	ACTION_FAIL,
	MENU_NAV,
	CONSTRUCTION_START,
	CONSTRUCTION_COMPLETE,
	RESOURCE_CHANGE
}

enum MusicTrack {
	MENU,
	COMBAT,
	MANAGEMENT
}

# Audio configuration
var enable_sounds: bool = true
var enable_narration: bool = true
var use_running_screen_reader: bool = true
var speech_rate: int = 150
var sound_volume: float = 1.0
var narration_volume: float = 1.0

# Sound effect players
var sound_players: Dictionary = {}
var music_player: AudioStreamPlayer

# TTS system
var tts_queue: Array = []
var is_speaking: bool = false
var tts_timer: Timer

# Paths to sound files
var sound_paths: Dictionary = {
	SoundEffect.TURRET_MOVE: "res://assets/audio/effects/turret_move.wav",
	SoundEffect.TURRET_SHOOT: "res://assets/audio/effects/turret_shoot.wav",
	SoundEffect.ENEMY_HIT: "res://assets/audio/effects/enemy_hit.wav",
	SoundEffect.ACTION_SUCCESS: "res://assets/audio/effects/action_success.wav",
	SoundEffect.ACTION_FAIL: "res://assets/audio/effects/action_fail.wav",
	SoundEffect.MENU_NAV: "res://assets/audio/effects/menu_nav.wav",
	SoundEffect.CONSTRUCTION_START: "res://assets/audio/effects/construction_start.wav",
	SoundEffect.CONSTRUCTION_COMPLETE: "res://assets/audio/effects/construction_complete.wav",
	SoundEffect.RESOURCE_CHANGE: "res://assets/audio/effects/resource_change.wav"
}

var music_paths: Dictionary = {
	MusicTrack.MENU: "res://assets/audio/music/menu_theme.mp3",
	MusicTrack.COMBAT: "res://assets/audio/music/combat_music.ogg",
	MusicTrack.MANAGEMENT: "res://assets/audio/music/management.ogg"
}

# Speech descriptions for sound effects (for screen reader fallback)
var sound_descriptions: Dictionary = {
	SoundEffect.TURRET_MOVE: "Turret movement sound",
	SoundEffect.TURRET_SHOOT: "Turret firing sound",
	SoundEffect.ENEMY_HIT: "Enemy hit sound",
	SoundEffect.ACTION_SUCCESS: "Success sound",
	SoundEffect.ACTION_FAIL: "Failure sound",
	SoundEffect.MENU_NAV: "Menu navigation sound",
	SoundEffect.CONSTRUCTION_START: "Construction started sound",
	SoundEffect.CONSTRUCTION_COMPLETE: "Construction completed sound",
	SoundEffect.RESOURCE_CHANGE: "Resource change sound"
}

func _ready():
	# Initialize audio players
	initialize_audio_players()

	# Load configuration
	load_audio_config()

	# Initialize TTS
	initialize_tts()

func initialize_audio_players():
	# Create sound effect players
	for effect in SoundEffect.values():
		var player = AudioStreamPlayer.new()
		player.bus = "SFX"
		add_child(player)
		sound_players[effect] = player

	# Create music player
	music_player = AudioStreamPlayer.new()
	music_player.bus = "Music"
	music_player.volume_db = linear_to_db(0.5)  # Default music volume
	add_child(music_player)

	# Create TTS timer for simulating speech duration
	tts_timer = Timer.new()
	tts_timer.one_shot = true
	tts_timer.name = "TTSTimer"
	add_child(tts_timer)
	tts_timer.timeout.connect(_on_speech_finished)

# Create a spatial audio player for positional sound effects
func create_spatial_audio_player(effect: int, position: Vector2) -> AudioStreamPlayer2D:
	var player = AudioStreamPlayer2D.new()
	player.bus = "SFX"
	player.global_position = position

	# Load the sound effect
	var path = sound_paths.get(effect)
	if path and ResourceLoader.exists(path):
		player.stream = load(path)

	# Set volume
	player.volume_db = linear_to_db(sound_volume)

	return player

# Play a sound effect at a specific world position
func play_sound_at_position(effect: int, position: Vector2) -> void:
	if not enable_sounds:
		return

	var player = create_spatial_audio_player(effect, position)
	if player.stream:
		# Add to scene temporarily
		get_tree().current_scene.add_child(player)
		player.play()

		# Remove after playing
		player.finished.connect(func(): player.queue_free())

		# Narrate sound description for accessibility if narration is enabled
		if enable_narration and effect in [SoundEffect.ACTION_SUCCESS, SoundEffect.ACTION_FAIL]:
			play_narration(sound_descriptions[effect])
	else:
		print("Spatial sound effect not found: ", effect)
		if enable_narration and sound_descriptions.has(effect):
			play_narration(sound_descriptions[effect])

func initialize_tts():
	# In Godot 4, we'll use DisplayServer for TTS when available
	if DisplayServer.has_feature(DisplayServer.FEATURE_TEXT_TO_SPEECH):
		print("System TTS is available")
	else:
		print("System TTS not available, falling back to console output")

func load_audio_config():
	# Load audio configuration from SaveManager
	if SaveManager.has_config("audio"):
		var config = SaveManager.get_config("audio")
		enable_sounds = config.get("enable_sounds", enable_sounds)
		enable_narration = config.get("enable_narration", enable_narration)
		use_running_screen_reader = config.get("use_running_screen_reader", use_running_screen_reader)
		speech_rate = config.get("speech_rate", speech_rate)
		sound_volume = config.get("sound_volume", sound_volume)
		narration_volume = config.get("narration_volume", narration_volume)

		print("Loaded audio config: enable_sounds=", enable_sounds,
			", enable_narration=", enable_narration,
			", use_running_screen_reader=", use_running_screen_reader)
	else:
		print("No audio config found, using defaults")
		save_audio_config()

func save_audio_config():
	# Save audio configuration to SaveManager
	var config = {
		"enable_sounds": enable_sounds,
		"enable_narration": enable_narration,
		"use_running_screen_reader": use_running_screen_reader,
		"speech_rate": speech_rate,
		"sound_volume": sound_volume,
		"narration_volume": narration_volume
	}
	SaveManager.set_config("audio", config)
	SaveManager.save_config()
	print("Saved audio config")

func play_sound(effect: int, position: Vector2 = Vector2.ZERO) -> void:
	if not enable_sounds:
		return

	var player = sound_players.get(effect)
	if player:
		# Try to load the sound if not already loaded
		if player.stream == null:
			var path = sound_paths.get(effect)
			if path and ResourceLoader.exists(path):
				player.stream = load(path)
			else:
				print("Sound effect not found: ", effect)
				# Narrate sound description for accessibility if narration is enabled
				if enable_narration and sound_descriptions.has(effect):
					play_narration(sound_descriptions[effect])
				return

		# Set volume and play
		player.volume_db = linear_to_db(sound_volume)

		# Apply spatial audio positioning if position is provided and player supports it
		if position != Vector2.ZERO and player is AudioStreamPlayer2D:
			player.global_position = position

		player.play()

		# Narrate sound description for accessibility if narration is enabled
		# Only for important sounds that need description
		if enable_narration and effect in [SoundEffect.ACTION_SUCCESS, SoundEffect.ACTION_FAIL]:
			play_narration(sound_descriptions[effect])
	else:
		print("Playing sound: ", effect, " (fallback)")
		# Narrate sound description for accessibility if narration is enabled
		if enable_narration and sound_descriptions.has(effect):
			play_narration(sound_descriptions[effect])

func play_music(track: int) -> void:
	if not enable_sounds:
		return

	var path = music_paths.get(track)
	if path and ResourceLoader.exists(path):
		music_player.stream = load(path)
		music_player.play()
	else:
		print("Music track not found: ", track)

func stop_music() -> void:
	music_player.stop()

func play_narration(text: String) -> void:
	if not enable_narration:
		return

	# If screen reader mode is enabled, disable game TTS to avoid conflicts
	if use_running_screen_reader:
		print("Screen reader mode active - skipping TTS: ", text)
		return

	print("Narrating: ", text)

	# Use system TTS if available
	if DisplayServer.has_feature(DisplayServer.FEATURE_TEXT_TO_SPEECH):
		# Stop any current speech to avoid overlap
		if DisplayServer.tts_is_speaking():
			DisplayServer.tts_stop()

		# Note: tts_set_rate is not available in Godot 4.5
		# Speech rate will be handled by the OS-specific TTS implementations

		# Speak the text
		DisplayServer.tts_speak(text, "")
	else:
		# Queue the text for narration with fallback system
		tts_queue.append(text)
		_process_tts_queue()

func _process_tts_queue():
	if is_speaking or tts_queue.size() == 0:
		return

	# If screen reader mode is enabled, clear the queue and don't process TTS
	if use_running_screen_reader:
		tts_queue.clear()
		is_speaking = false
		return

	# Get the next text to speak
	var text = tts_queue.pop_front()
	is_speaking = true

	# Try to use OS-specific TTS if available
	var used_os_tts = false

	# On Windows, try to use PowerShell for TTS
	if OS.get_name() == "Windows":
		var args = [
			"-Command",
			'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Rate = ' +
			str((speech_rate - 150) / 50) + '; $speak.Speak("' + text.replace('"', '\\"') + '")'
		]
		var output = []
		OS.execute("powershell.exe", args, output, true)
		used_os_tts = true

	# On macOS, try to use say command
	elif OS.get_name() == "macOS":
		var args = ["-r", str(speech_rate / 50), text]
		var output = []
		OS.execute("say", args, output, true)
		used_os_tts = true

	# On Linux, try to use espeak
	elif OS.get_name() == "Linux":
		var args = ["-s", str(speech_rate), text]
		var output = []
		OS.execute("espeak", args, output, true)
		used_os_tts = true

	# If we couldn't use OS TTS, just print to console and simulate with timer
	if not used_os_tts:
		print("TTS (fallback): ", text)

		# Simulate speech duration based on text length
		var duration = text.length() * 0.05  # 50ms per character
		tts_timer.wait_time = duration
		tts_timer.start()
	else:
		# OS TTS is synchronous, so we can immediately process the next item
		is_speaking = false
		_process_tts_queue()

func _on_speech_finished():
	is_speaking = false
	_process_tts_queue()

func set_sound_enabled(enabled: bool) -> void:
	enable_sounds = enabled
	save_audio_config()

func set_narration_enabled(enabled: bool) -> void:
	enable_narration = enabled
	save_audio_config()

	if enabled:
		play_narration("Narration enabled")

func set_sound_volume(volume: float) -> void:
	sound_volume = clamp(volume, 0.0, 1.0)
	save_audio_config()

	# Play a sample sound to demonstrate the new volume
	play_sound(SoundEffect.MENU_NAV)

func set_narration_volume(volume: float) -> void:
	narration_volume = clamp(volume, 0.0, 1.0)
	save_audio_config()

	if enable_narration:
		play_narration("Narration volume set to " + str(int(narration_volume * 100)) + " percent")

func set_speech_rate(rate: int) -> void:
	speech_rate = clamp(rate, 50, 300)
	save_audio_config()

	# Note: tts_set_rate is not available in Godot 4.5
	# Speech rate changes will take effect in OS-specific TTS calls

	if enable_narration:
		play_narration("Speech rate set to " + str(speech_rate))

func toggle_running_screen_reader(use_running: bool) -> void:
	use_running_screen_reader = use_running
	save_audio_config()

	# When screen reader mode is enabled, we disable game TTS to avoid conflicts
	# When disabled, we re-enable game TTS for direct narration

	if enable_narration:
		if use_running_screen_reader:
			# Stop any current TTS before switching to screen reader mode
			if DisplayServer.has_feature(DisplayServer.FEATURE_TEXT_TO_SPEECH):
				if DisplayServer.tts_is_speaking():
					DisplayServer.tts_stop()
			# Clear any queued TTS
			tts_queue.clear()
			is_speaking = false

			# Provide one final announcement before disabling TTS
			# This will be skipped due to the new logic, so we temporarily override
			var temp_screen_reader = use_running_screen_reader
			use_running_screen_reader = false
			play_narration("Screen reader mode enabled. Game speech disabled.")
			use_running_screen_reader = temp_screen_reader
		else:
			play_narration("Direct speech mode enabled")
