extends Wildlife
class_name Butterfly
## Butterfly - Flutters erratically, hovers near flowers/trees

var flutter_offset: float = 0.0
var wing_state: bool = false
var wing_timer: float = 0.0
var wing_rect_left: ColorRect = null
var wing_rect_right: ColorRect = null

func _ready() -> void:
	# Butterfly settings
	base_speed = 25.0
	flee_speed = 80.0
	charlie_detection_radius = 50.0
	entertainment_value = 0.02  # 2%

	body_color = _random_butterfly_color()
	body_size = Vector2(4, 4)

	super._ready()
	_setup_wings()

func _random_butterfly_color() -> Color:
	var colors = [
		Color(1.0, 0.6, 0.2),   # Orange monarch
		Color(0.2, 0.6, 1.0),   # Blue morpho
		Color(1.0, 1.0, 0.3),   # Yellow swallowtail
		Color(0.9, 0.4, 0.8),   # Pink painted lady
		Color(1.0, 1.0, 1.0),   # White cabbage
	]
	return colors[randi() % colors.size()]

func _setup_wings() -> void:
	# Left wing
	wing_rect_left = ColorRect.new()
	wing_rect_left.size = Vector2(5, 4)
	wing_rect_left.position = Vector2(-7, -2)
	wing_rect_left.color = body_color
	wing_rect_left.color.a = 0.8
	add_child(wing_rect_left)

	# Right wing
	wing_rect_right = ColorRect.new()
	wing_rect_right.size = Vector2(5, 4)
	wing_rect_right.position = Vector2(2, -2)
	wing_rect_right.color = body_color
	wing_rect_right.color.a = 0.8
	add_child(wing_rect_right)

func _physics_process(delta: float) -> void:
	super._physics_process(delta)

	# Wing flapping animation
	wing_timer -= delta
	if wing_timer <= 0:
		wing_state = !wing_state
		wing_timer = 0.08 if current_state == State.FLEEING else 0.15
		_update_wings()

	# Flutter effect - bob up and down
	flutter_offset += delta * 8.0
	if body_rect:
		body_rect.position.y = -body_size.y / 2 + sin(flutter_offset) * 2

func _update_wings() -> void:
	if wing_state:
		# Wings up
		if wing_rect_left:
			wing_rect_left.position.y = -4
			wing_rect_left.size.y = 3
		if wing_rect_right:
			wing_rect_right.position.y = -4
			wing_rect_right.size.y = 3
	else:
		# Wings down
		if wing_rect_left:
			wing_rect_left.position.y = -1
			wing_rect_left.size.y = 4
		if wing_rect_right:
			wing_rect_right.position.y = -1
			wing_rect_right.size.y = 4

func _process_moving(delta: float) -> void:
	# Erratic flutter movement
	move_timer -= delta

	# Change direction frequently for erratic movement
	if randf() < 0.05:
		move_direction = move_direction.rotated(randf_range(-1.0, 1.0))
		move_direction = move_direction.normalized()

	velocity = move_direction * base_speed
	_clamp_to_bounds()

	if move_timer <= 0:
		_start_idle()

func _start_idle() -> void:
	super._start_idle()
	idle_timer = randf_range(0.5, 2.0)  # Shorter idle for butterflies

func _start_moving() -> void:
	super._start_moving()
	move_timer = randf_range(2.0, 5.0)  # Longer movement periods

func get_wildlife_name() -> String:
	return "a butterfly"
