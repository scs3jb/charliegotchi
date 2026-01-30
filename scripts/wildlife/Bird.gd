extends Wildlife
class_name Bird
## Bird - Hops on ground, flies to tree perches when startled

var is_flying: bool = false
var hop_timer: float = 0.0
var peck_timer: float = 0.0
var is_pecking: bool = false
var head_rect: ColorRect = null
var beak_rect: ColorRect = null
var tail_rect: ColorRect = null

func _ready() -> void:
	# Bird settings
	base_speed = 35.0
	flee_speed = 150.0
	charlie_detection_radius = 70.0
	entertainment_value = 0.04  # 4%

	body_color = _random_bird_color()
	body_size = Vector2(10, 7)

	super._ready()
	_setup_bird_parts()

func _random_bird_color() -> Color:
	var colors = [
		Color(0.6, 0.4, 0.3),   # Sparrow brown
		Color(0.3, 0.3, 0.35),  # Pigeon gray
		Color(0.9, 0.2, 0.2),   # Cardinal red
		Color(0.2, 0.4, 0.7),   # Blue jay
		Color(0.1, 0.1, 0.1),   # Crow black
	]
	return colors[randi() % colors.size()]

func _setup_bird_parts() -> void:
	# Head
	head_rect = ColorRect.new()
	head_rect.size = Vector2(5, 5)
	head_rect.position = Vector2(3, -6)
	head_rect.color = body_color.lightened(0.1)
	add_child(head_rect)

	# Beak
	beak_rect = ColorRect.new()
	beak_rect.size = Vector2(4, 2)
	beak_rect.position = Vector2(8, -4)
	beak_rect.color = Color(0.9, 0.7, 0.3)  # Yellow/orange beak
	add_child(beak_rect)

	# Tail
	tail_rect = ColorRect.new()
	tail_rect.size = Vector2(5, 3)
	tail_rect.position = Vector2(-7, -2)
	tail_rect.color = body_color.darkened(0.1)
	add_child(tail_rect)

func _physics_process(delta: float) -> void:
	super._physics_process(delta)

	# Pecking animation when idle
	if current_state == State.IDLE and not is_flying:
		peck_timer -= delta
		if peck_timer <= 0:
			is_pecking = !is_pecking
			peck_timer = 0.3 if is_pecking else randf_range(0.5, 1.5)
			_update_peck()

	# Update facing direction based on movement
	if velocity.length() > 5 and beak_rect and tail_rect:
		if velocity.x > 0:
			beak_rect.position.x = 8
			tail_rect.position.x = -7
		else:
			beak_rect.position.x = -7
			tail_rect.position.x = 3

func _update_peck() -> void:
	if head_rect:
		if is_pecking:
			head_rect.position.y = -3  # Head down
		else:
			head_rect.position.y = -6  # Head up
	if beak_rect:
		if is_pecking:
			beak_rect.position.y = -1
		else:
			beak_rect.position.y = -4

func _process_moving(delta: float) -> void:
	# Hopping movement
	hop_timer -= delta

	if hop_timer <= 0 and not is_flying:
		# Small hop
		hop_timer = 0.4
		velocity = move_direction * base_speed * 2.0  # Quick hop burst
	else:
		velocity = velocity.lerp(Vector2.ZERO, 0.1)  # Slow down between hops

	move_timer -= delta
	_clamp_to_bounds()

	if move_timer <= 0:
		_start_idle()

func _start_flee() -> void:
	is_flying = true
	super._start_flee()
	# Birds flee upward and away
	if charlie_ref:
		move_direction = (global_position - charlie_ref.global_position).normalized()
		move_direction.y = -abs(move_direction.y) - 0.5  # Fly upward
		move_direction = move_direction.normalized()

func _start_idle() -> void:
	super._start_idle()
	idle_timer = randf_range(2.0, 5.0)  # Birds spend more time foraging
	is_pecking = false
	peck_timer = randf_range(0.3, 1.0)

func _start_moving() -> void:
	super._start_moving()
	move_timer = randf_range(0.5, 1.5)  # Short bursts of movement
	hop_timer = 0.0

func get_wildlife_name() -> String:
	return "a bird"
