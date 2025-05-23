extends Node2D

# Export variables for configuration in the editor
@export var speed: float = 300.0
@export var damage: int = 10

# Internal variables
var direction: Vector2 = Vector2(0, -1)  # Default: move up
var target: Node2D = null

func _ready():
	# Set up appearance
	var shape = ColorRect.new()
	shape.color = Color.YELLOW
	shape.size = Vector2(6, 12)
	shape.position = -shape.size / 2  # Center the shape
	add_child(shape)
	
	# Set up collision
	var collision = Area2D.new()
	collision.name = "Collision"
	add_child(collision)
	
	var shape_2d = CollisionShape2D.new()
	var rect_shape = RectangleShape2D.new()
	rect_shape.size = Vector2(6, 12)
	shape_2d.shape = rect_shape
	collision.add_child(shape_2d)
	
	# Connect signals
	collision.area_entered.connect(_on_collision_area_entered)
	collision.body_entered.connect(_on_collision_body_entered)

func _process(delta):
	# Move the projectile
	position += direction * speed * delta
	
	# Check if out of screen bounds
	var screen_size = get_viewport_rect().size
	if position.y < -20 or position.y > screen_size.y + 20 or position.x < -20 or position.x > screen_size.x + 20:
		queue_free()

func _on_collision_area_entered(area):
	# Check if collided with an enemy
	if area.get_parent() is Enemy:
		var enemy = area.get_parent()
		enemy.take_damage(damage)
		queue_free()

func _on_collision_body_entered(body):
	# Check if collided with an enemy
	if body is Enemy:
		body.take_damage(damage)
		queue_free()

func set_target(new_target: Node2D):
	target = new_target
	
	if target:
		# Calculate direction to target
		var target_pos = target.global_position
		direction = (target_pos - global_position).normalized()

func set_damage(new_damage: int):
	damage = new_damage
