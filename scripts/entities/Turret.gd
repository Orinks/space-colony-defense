extends Node2D

# Signals
signal shot_fired(projectile)
signal damaged(amount)
signal shield_changed(value)

# Export variables for configuration in the editor
@export var move_speed: float = 200.0
@export var fire_rate: float = 0.5
@export var max_shield: int = 100

# Internal variables
var shield: int = 100
var is_damaged: bool = false
var can_shoot: bool = true
var screen_width: float
var screen_size: Vector2
var projectile_scene: PackedScene

func _ready():
	# Initialize
	shield = max_shield
	screen_size = get_viewport_rect().size
	screen_width = screen_size.x
	
	# Load projectile scene
	projectile_scene = load("res://scenes/Projectile.tscn")
	
	# Set up shooting cooldown timer
	var timer = Timer.new()
	timer.wait_time = fire_rate
	timer.one_shot = true
	timer.name = "ShootCooldown"
	add_child(timer)
	timer.timeout.connect(_on_shoot_cooldown_timeout)

func _process(delta):
	# Handle movement
	handle_movement(delta)
	
	# Handle shooting
	if Input.is_action_just_pressed("shoot") and can_shoot:
		shoot()

func handle_movement(delta):
	var direction = 0
	
	if Input.is_action_pressed("move_left"):
		direction = -1
	elif Input.is_action_pressed("move_right"):
		direction = 1
	
	if direction != 0:
		# Move the turret
		position.x += direction * move_speed * delta
		
		# Clamp to screen bounds
		position.x = clamp(position.x, 0, screen_width)
		
		# Play movement sound
		AudioManager.play_sound(AudioManager.SoundEffect.TURRET_MOVE)
		
		# Narrate position for accessibility
		var position_percent = int(position.x / screen_width * 100)
		if position_percent % 10 == 0:  # Only narrate at 10% intervals
			AudioManager.play_narration("Position " + str(position_percent) + " percent")

func shoot():
	if not can_shoot:
		return
	
	# Create projectile
	var projectile = projectile_scene.instantiate()
	projectile.position = position + Vector2(0, -20)  # Offset from turret position
	
	# Play sound
	AudioManager.play_sound(AudioManager.SoundEffect.TURRET_SHOOT)
	
	# Emit signal
	emit_signal("shot_fired", projectile)
	
	# Start cooldown
	can_shoot = false
	$ShootCooldown.start()

func _on_shoot_cooldown_timeout():
	can_shoot = true

func take_damage(damage: int):
	# Apply shield protection if available
	if shield > 0:
		var absorbed = min(damage, shield)
		damage -= absorbed
		shield -= absorbed
		
		# Emit shield changed signal
		emit_signal("shield_changed", shield)
		
		# Narrate shield status
		var shield_percent = int(float(shield) / max_shield * 100)
		AudioManager.play_narration("Shield at " + str(shield_percent) + " percent")
	
	# Apply remaining damage to turret
	if damage > 0:
		is_damaged = true
		
		# Emit damaged signal
		emit_signal("damaged", damage)
		
		# Play sound
		AudioManager.play_sound(AudioManager.SoundEffect.ENEMY_HIT)
		
		# Narrate damage
		AudioManager.play_narration("Turret damaged")

func repair_shield(amount: int):
	var old_shield = shield
	shield = min(max_shield, shield + amount)
	
	# Emit shield changed signal
	emit_signal("shield_changed", shield)
	
	# Narrate shield repair
	var repaired = shield - old_shield
	if repaired > 0:
		AudioManager.play_narration("Shield repaired by " + str(repaired) + " points")
		AudioManager.play_sound(AudioManager.SoundEffect.CONSTRUCTION_COMPLETE)
	
	# Reset damaged flag if fully repaired
	if shield == max_shield:
		is_damaged = false
