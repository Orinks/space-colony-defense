extends Node2D

# Signals
signal defeated(enemy)
signal reached_bottom(enemy)

# Enemy types
enum EnemyType {
	BASIC_INVADER,
	ARMORED_SHIP,
	SWARMER,
	DESTROYER,
	BOSS
}

# Export variables for configuration in the editor
@export var type: EnemyType = EnemyType.BASIC_INVADER
@export var speed: float = 50.0
@export var health: int = 10
@export var damage: int = 10

# Resource drop properties
var resource_drop = {
	"type": "",  # "energy", "metal", "food"
	"amount": 0
}

# Movement properties
var target_position: Vector2
var screen_size: Vector2
var move_direction: Vector2 = Vector2(0, 1)  # Default: move down
var is_defeated: bool = false

func _ready():
	# Initialize
	screen_size = get_viewport_rect().size
	
	# Set up resource drop based on enemy type
	setup_resource_drop()
	
	# Set up appearance based on type
	setup_appearance()

func _process(delta):
	if is_defeated:
		return
	
	# Move the enemy
	position += move_direction * speed * delta
	
	# Check if reached bottom of screen
	if position.y > screen_size.y:
		emit_signal("reached_bottom", self)
		queue_free()

func setup_resource_drop():
	match type:
		EnemyType.BASIC_INVADER:
			resource_drop = {
				"type": "energy",
				"amount": 10
			}
		EnemyType.ARMORED_SHIP:
			resource_drop = {
				"type": "metal",
				"amount": 15
			}
		EnemyType.SWARMER:
			resource_drop = {
				"type": "food",
				"amount": 5
			}
		EnemyType.DESTROYER:
			resource_drop = {
				"type": "metal",
				"amount": 20
			}
		EnemyType.BOSS:
			# Bosses drop multiple resources
			resource_drop = {
				"type": "all",
				"amount": 30
			}

func setup_appearance():
	# Set up appearance based on enemy type
	# This would be replaced with proper sprites in a real implementation
	var color = Color.RED
	var size = Vector2(30, 30)
	
	match type:
		EnemyType.BASIC_INVADER:
			color = Color.RED
			size = Vector2(30, 30)
		EnemyType.ARMORED_SHIP:
			color = Color.DARK_GRAY
			size = Vector2(40, 40)
		EnemyType.SWARMER:
			color = Color.YELLOW
			size = Vector2(20, 20)
		EnemyType.DESTROYER:
			color = Color.PURPLE
			size = Vector2(50, 50)
		EnemyType.BOSS:
			color = Color.DARK_RED
			size = Vector2(80, 80)
	
	# Create a simple shape for the enemy
	var shape = ColorRect.new()
	shape.color = color
	shape.size = size
	shape.position = -size / 2  # Center the shape
	add_child(shape)

func take_damage(amount: int):
	health -= amount
	
	# Check if defeated
	if health <= 0 and not is_defeated:
		defeat()

func defeat():
	is_defeated = true
	
	# Play sound
	AudioManager.play_sound(AudioManager.SoundEffect.ENEMY_HIT)
	
	# Emit signal
	emit_signal("defeated", self)
	
	# Drop resources
	drop_resources()
	
	# Animate defeat
	animate_defeat()

func drop_resources():
	# Update game state with resource drop
	if resource_drop["type"] == "all":
		# Drop all resource types
		GameState.update_resources(resource_drop["amount"], resource_drop["amount"], resource_drop["amount"] / 2)
	else:
		# Drop specific resource type
		match resource_drop["type"]:
			"energy":
				GameState.update_resources(resource_drop["amount"], 0, 0)
			"metal":
				GameState.update_resources(0, resource_drop["amount"], 0)
			"food":
				GameState.update_resources(0, 0, resource_drop["amount"])

func animate_defeat():
	# Simple defeat animation
	var tween = create_tween()
	tween.tween_property(self, "modulate", Color(1, 1, 1, 0), 0.5)
	tween.tween_callback(queue_free)

func get_type_name() -> String:
	match type:
		EnemyType.BASIC_INVADER:
			return "Basic Invader"
		EnemyType.ARMORED_SHIP:
			return "Armored Ship"
		EnemyType.SWARMER:
			return "Swarmer"
		EnemyType.DESTROYER:
			return "Destroyer"
		EnemyType.BOSS:
			return "Boss"
		_:
			return "Unknown"
