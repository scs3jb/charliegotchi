extends Wildlife
class_name Squirrel
## Squirrel - Fast scurrying, pauses to forage, very alert

var tail_rect: ColorRect = null
var ear_left: ColorRect = null
var ear_right: ColorRect = null
var is_foraging: bool = false
var forage_timer: float = 0.0
var alert_timer: float = 0.0
var tail_wag_offset: float = 0.0

var target_tree: Node2D = null
var climbing_timer: float = 0.0

func _ready() -> void:
	# Squirrel settings - hardest to approach
	base_speed = 55.0
	flee_speed = 180.0
	charlie_detection_radius = 90.0
	entertainment_value = 0.06  # 6%

	body_color = _random_squirrel_color()
	body_size = Vector2(10, 8)

	super._ready()
	_setup_squirrel_parts()

func _random_squirrel_color() -> Color:
	var colors = [
		Color(0.5, 0.35, 0.2),  # Brown
		Color(0.6, 0.5, 0.4),   # Tan
		Color(0.3, 0.3, 0.3),   # Gray
		Color(0.7, 0.4, 0.2),   # Red/rust
	]
	return colors[randi() % colors.size()]

func _setup_squirrel_parts() -> void:
	# Fluffy tail
	tail_rect = ColorRect.new()
	tail_rect.size = Vector2(6, 12)
	tail_rect.position = Vector2(-8, -14)
	tail_rect.color = body_color.lightened(0.1)
	add_child(tail_rect)

	# Left ear
	ear_left = ColorRect.new()
	ear_left.size = Vector2(3, 4)
	ear_left.position = Vector2(-3, -10)
	ear_left.color = body_color
	add_child(ear_left)

	# Right ear
	ear_right = ColorRect.new()
	ear_right.size = Vector2(3, 4)
	ear_right.position = Vector2(4, -10)
	ear_right.color = body_color
	add_child(ear_right)

func _physics_process(delta: float) -> void:
	# Override physics process to handle climbing
	if current_state == State.CLIMBING:
		_process_climbing(delta)
		return
		
	super._physics_process(delta)

	# Tail wagging animation
	tail_wag_offset += delta * 6.0
	if tail_rect:
		tail_rect.position.x = -8 + sin(tail_wag_offset) * 2

	# Alert behavior - occasionally stand up and look around
	if current_state == State.IDLE:
		alert_timer -= delta
		if alert_timer <= 0:
			_do_alert_check()
			alert_timer = randf_range(1.0, 3.0)

	# Foraging animation
	if is_foraging and body_rect:
		body_rect.position.y = -body_size.y / 2 + sin(Time.get_ticks_msec() * 0.02) * 1

func _do_alert_check() -> void:
	# Stand up briefly to check surroundings
	if body_rect and ear_left and ear_right:
		# Ears perk up
		ear_left.position.y = -12
		ear_right.position.y = -12

		# Reset after brief moment
		await get_tree().create_timer(0.5).timeout
		if is_instance_valid(ear_left):
			ear_left.position.y = -10
		if is_instance_valid(ear_right):
			ear_right.position.y = -10

func _process_idle(delta: float) -> void:
	idle_timer -= delta
	velocity = Vector2.ZERO

	# Forage behavior
	forage_timer -= delta
	if forage_timer <= 0:
		is_foraging = !is_foraging
		forage_timer = randf_range(0.5, 1.5)

	if idle_timer <= 0:
		is_foraging = false
		_start_moving()

func _process_moving(delta: float) -> void:
	move_timer -= delta

	# Squirrels scurry in quick bursts
	if randf() < 0.1:
		# Quick direction change
		move_direction = move_direction.rotated(randf_range(-0.5, 0.5))
		move_direction = move_direction.normalized()

	velocity = move_direction * base_speed
	_clamp_to_bounds()

	if move_timer <= 0:
		_start_idle()

func _start_idle() -> void:
	super._start_idle()
	idle_timer = randf_range(1.5, 4.0)  # Pause to forage
	is_foraging = true
	forage_timer = 0.3
	alert_timer = randf_range(0.5, 1.5)

func _start_moving() -> void:
	# Occasionally move to a tree instead of random wandering
	if randf() < 0.4:
		var trees = get_tree().get_nodes_in_group("trees")
		if trees.size() > 0:
			var random_tree = trees[randi() % trees.size()]
			move_direction = (random_tree.global_position - global_position).normalized()
			move_timer = randf_range(1.0, 2.0)
			current_state = State.MOVING
			return

	super._start_moving()
	move_timer = randf_range(0.3, 1.0)  # Quick bursts of movement
	is_foraging = false

	# Update tail direction based on movement
	if tail_rect:
		if move_direction.x > 0:
			tail_rect.position.x = -8
		else:
			tail_rect.position.x = 6

func _process_climbing(delta: float) -> void:
	climbing_timer -= delta
	# Move squirrel up the tree visually
	var progress = 1.0 - (climbing_timer / 1.0) # 0 to 1
	
	# Halfway up, pop behind the tree canopy
	if progress > 0.4:
		z_index = 0 # Return to normal Y-sort (which is now behind the tree since Y is much lower)
	
	if body_rect:
		# Scurry up
		body_rect.position.y -= delta * 60.0
		# Shrink and fade
		var scale_val = max(0.1, 1.0 - progress)
		scale = Vector2(scale_val, scale_val)
		modulate.a = max(0.0, 1.0 - progress * 1.5)
	
	if climbing_timer <= 0:
		_finish_despawn()

func _start_climbing(tree: Node2D) -> void:
	current_state = State.CLIMBING
	target_tree = tree
	if tree.has_method("set_squirrel_occupant"):
		tree.set_squirrel_occupant(self)
	climbing_timer = 1.0
	velocity = Vector2.ZERO
	# Position slightly south of the base so it's clearly in front at start
	global_position = tree.global_position + Vector2(0, 2)
	# Set high Z-index to scurry up the FRONT of the trunk
	z_index = 5

func _process_fleeing(delta: float) -> void:
	if target_tree and is_instance_valid(target_tree):
		var dist = global_position.distance_to(target_tree.global_position)
		if dist < 10:
			_start_climbing(target_tree)
		else:
			move_direction = (target_tree.global_position - global_position).normalized()
			velocity = move_direction * flee_speed
	else:
		super._process_fleeing(delta)

func _start_flee() -> void:
	# Find nearest tree to run to
	var trees = get_tree().get_nodes_in_group("trees")
	var nearest_tree = null
	var min_dist = INF
	
	for tree in trees:
		var dist = global_position.distance_to(tree.global_position)
		if dist < min_dist:
			min_dist = dist
			nearest_tree = tree
	
	target_tree = nearest_tree
	super._start_flee()
	
	if target_tree:
		move_direction = (target_tree.global_position - global_position).normalized()
	is_foraging = false

func get_wildlife_name() -> String:
	return "a squirrel"