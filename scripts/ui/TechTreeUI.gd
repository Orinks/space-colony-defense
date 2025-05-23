extends Control

# Tech tree data
var tech_tree = {
	"colony": {
		"reinforced_colony": {
			"name": "Reinforced Colony",
			"description": "Increases colony max HP by 25 per level",
			"max_level": 3,
			"level": 0,
			"cost": 5,
			"prerequisites": []
		},
		"advanced_shields": {
			"name": "Advanced Shields",
			"description": "Increases shield effectiveness by 25% per level",
			"max_level": 2,
			"level": 0,
			"cost": 8,
			"prerequisites": ["reinforced_colony"]
		},
		"auto_repair": {
			"name": "Auto-Repair Systems",
			"description": "Colony repairs 5 HP per wave automatically",
			"max_level": 1,
			"level": 0,
			"cost": 12,
			"prerequisites": ["advanced_shields"]
		}
	},
	"resources": {
		"resource_storage": {
			"name": "Resource Storage",
			"description": "Increases starting resources by 20 per level",
			"max_level": 3,
			"level": 0,
			"cost": 5,
			"prerequisites": []
		},
		"efficient_buildings": {
			"name": "Efficient Buildings",
			"description": "Buildings consume 25% less energy per level",
			"max_level": 2,
			"level": 0,
			"cost": 8,
			"prerequisites": ["resource_storage"]
		},
		"advanced_harvesting": {
			"name": "Advanced Harvesting",
			"description": "Resource buildings produce 50% more resources",
			"max_level": 1,
			"level": 0,
			"cost": 12,
			"prerequisites": ["efficient_buildings"]
		}
	},
	"weapons": {
		"rapid_fire": {
			"name": "Rapid Fire",
			"description": "Increases turret fire rate by 25% per level",
			"max_level": 3,
			"level": 0,
			"cost": 5,
			"prerequisites": []
		},
		"double_damage": {
			"name": "Double Damage",
			"description": "Increases projectile damage by 50% per level",
			"max_level": 2,
			"level": 0,
			"cost": 8,
			"prerequisites": ["rapid_fire"]
		},
		"multi_shot": {
			"name": "Multi-Shot",
			"description": "Turret fires 3 projectiles at once",
			"max_level": 1,
			"level": 0,
			"cost": 12,
			"prerequisites": ["double_damage"]
		}
	}
}

# UI state
var current_category: String = "colony"
var selected_tech: String = ""
var owned_techs: Dictionary = {}
var available_points: int = 0

# Accessibility properties
var last_narrated_tech: String = ""

func _ready():
	# Load tech tree data
	load_tech_tree()
	
	# Set up initial UI
	update_ui()

func _process(delta):
	# Handle navigation
	if Input.is_action_just_pressed("ui_left"):
		navigate_category(-1)
	elif Input.is_action_just_pressed("ui_right"):
		navigate_category(1)
	elif Input.is_action_just_pressed("ui_up"):
		navigate_tech(-1)
	elif Input.is_action_just_pressed("ui_down"):
		navigate_tech(1)
	elif Input.is_action_just_pressed("ui_accept"):
		purchase_selected_tech()

func load_tech_tree():
	# Load tech tree data from SaveManager
	var data = SaveManager.load_tech_tree()
	owned_techs = data.get("owned_techs", {})
	available_points = data.get("available_points", 0)
	
	# Update tech levels based on owned_techs
	for tech_id in owned_techs:
		var level = owned_techs[tech_id]
		
		# Find the tech in the tree
		for category in tech_tree:
			if tech_tree[category].has(tech_id):
				tech_tree[category][tech_id].level = level
	
	# Add available points from GameState
	available_points += GameState.tech_points
	GameState.tech_points = 0

func save_tech_tree():
	# Save tech tree data to SaveManager
	var data = {
		"owned_techs": owned_techs,
		"available_points": available_points
	}
	SaveManager.save_tech_tree(data)

func update_ui():
	# Clear existing UI
	for child in get_children():
		child.queue_free()
	
	# Create category labels
	var categories = ["Colony", "Resources", "Weapons"]
	var category_x = 100
	var category_spacing = 200
	
	for i in range(categories.size()):
		var category = categories[i]
		var label = Label.new()
		label.text = category
		label.position = Vector2(category_x + i * category_spacing, 50)
		
		if category.to_lower() == current_category:
			label.add_theme_color_override("font_color", Color.YELLOW)
		else:
			label.add_theme_color_override("font_color", Color.WHITE)
		
		add_child(label)
	
	# Create tech nodes for current category
	var techs = tech_tree[current_category]
	var tech_y = 100
	var tech_spacing = 50
	
	var i = 0
	for tech_id in techs:
		var tech = techs[tech_id]
		var label = Label.new()
		
		# Format tech name with level
		var level_text = ""
		if tech.level > 0:
			level_text = " (Level " + str(tech.level) + "/" + str(tech.max_level) + ")"
		else:
			level_text = " (Locked)"
		
		label.text = tech.name + level_text
		label.position = Vector2(100, tech_y + i * tech_spacing)
		
		# Check if tech is selected
		if tech_id == selected_tech:
			label.add_theme_color_override("font_color", Color.YELLOW)
		else:
			# Check if tech is available
			if is_tech_available(tech_id):
				label.add_theme_color_override("font_color", Color.WHITE)
			else:
				label.add_theme_color_override("font_color", Color.DARK_GRAY)
		
		add_child(label)
		i += 1
	
	# Create tech points display
	var points_label = Label.new()
	points_label.text = "Tech Points: " + str(available_points)
	points_label.position = Vector2(100, 300)
	add_child(points_label)
	
	# Create selected tech description
	if selected_tech != "":
		var tech = tech_tree[current_category][selected_tech]
		var desc_label = Label.new()
		desc_label.text = tech.description
		desc_label.position = Vector2(100, 350)
		add_child(desc_label)
		
		var cost_label = Label.new()
		cost_label.text = "Cost: " + str(tech.cost) + " points"
		cost_label.position = Vector2(100, 380)
		add_child(cost_label)
		
		var prereq_label = Label.new()
		var prereq_text = "Prerequisites: "
		
		if tech.prerequisites.size() > 0:
			for prereq in tech.prerequisites:
				var prereq_tech = find_tech_by_id(prereq)
				if prereq_tech:
					prereq_text += prereq_tech.name + ", "
			prereq_text = prereq_text.substr(0, prereq_text.length() - 2)  # Remove trailing comma
		else:
			prereq_text += "None"
		
		prereq_label.text = prereq_text
		prereq_label.position = Vector2(100, 410)
		add_child(prereq_label)

func navigate_category(direction: int):
	var categories = ["colony", "resources", "weapons"]
	var current_index = categories.find(current_category)
	
	if current_index != -1:
		current_index = (current_index + direction) % categories.size()
		if current_index < 0:
			current_index = categories.size() - 1
		
		current_category = categories[current_index]
		selected_tech = ""  # Reset selected tech
		
		# Play sound
		AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)
		
		# Narrate category
		AudioManager.play_narration(current_category.capitalize() + " category")
		
		update_ui()

func navigate_tech(direction: int):
	var techs = tech_tree[current_category].keys()
	
	if techs.size() == 0:
		return
	
	var current_index = -1
	
	if selected_tech == "":
		current_index = 0
	else:
		current_index = techs.find(selected_tech)
	
	if current_index != -1:
		current_index = (current_index + direction) % techs.size()
		if current_index < 0:
			current_index = techs.size() - 1
		
		selected_tech = techs[current_index]
		
		# Play sound
		AudioManager.play_sound(AudioManager.SoundEffect.MENU_NAV)
		
		# Narrate tech
		narrate_selected_tech()
		
		update_ui()

func narrate_selected_tech():
	if selected_tech != "":
		var tech = tech_tree[current_category][selected_tech]
		var narration = tech.name
		
		if tech.level > 0:
			narration += ", Level " + str(tech.level) + " of " + str(tech.max_level)
		
		if narration != last_narrated_tech:
			AudioManager.play_narration(narration)
			last_narrated_tech = narration

func purchase_selected_tech():
	if selected_tech == "":
		return
	
	var tech = tech_tree[current_category][selected_tech]
	
	# Check if tech is already at max level
	if tech.level >= tech.max_level:
		AudioManager.play_narration(tech.name + " already at maximum level")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
		return
	
	# Check if tech is available
	if not is_tech_available(selected_tech):
		AudioManager.play_narration(tech.name + " prerequisites not met")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
		return
	
	# Check if we have enough points
	if available_points < tech.cost:
		AudioManager.play_narration("Not enough tech points")
		AudioManager.play_sound(AudioManager.SoundEffect.ACTION_FAIL)
		return
	
	# Purchase tech
	available_points -= tech.cost
	tech.level += 1
	
	# Update owned_techs
	owned_techs[selected_tech] = tech.level
	
	# Play sound
	AudioManager.play_sound(AudioManager.SoundEffect.ACTION_SUCCESS)
	
	# Narrate purchase
	AudioManager.play_narration(tech.name + " upgraded to level " + str(tech.level))
	
	# Save tech tree
	save_tech_tree()
	
	# Update UI
	update_ui()

func is_tech_available(tech_id: String) -> bool:
	var tech = tech_tree[current_category][tech_id]
	
	# Check prerequisites
	for prereq in tech.prerequisites:
		var prereq_tech = find_tech_by_id(prereq)
		if not prereq_tech or prereq_tech.level == 0:
			return false
	
	return true

func find_tech_by_id(tech_id: String):
	# Find a tech by its ID
	for category in tech_tree:
		if tech_tree[category].has(tech_id):
			return tech_tree[category][tech_id]
	
	return null

func apply_tech_effects():
	# Apply effects from owned techs to the game state
	for tech_id in owned_techs:
		var level = owned_techs[tech_id]
		
		match tech_id:
			"reinforced_colony":
				var bonus_hp = level * 25  # 25/50/75 bonus HP
				GameState.colony_max_hp += bonus_hp
				GameState.colony_hp += bonus_hp
			"resource_storage":
				var bonus_resources = level * 20  # 20/40/60 bonus resources
				GameState.energy += bonus_resources
				GameState.metal += bonus_resources
				GameState.food += bonus_resources / 2
			# Add more tech effects here
	
	AudioManager.play_narration("Tech effects applied")

func get_tech_level(tech_id: String) -> int:
	return owned_techs.get(tech_id, 0)
