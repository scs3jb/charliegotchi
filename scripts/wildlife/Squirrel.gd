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

		# Reset after brief moment (handled in idle timer)
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
	super._start_moving()
	move_timer = randf_range(0.3, 1.0)  # Quick bursts of movement
	is_foraging = false

	# Update tail direction based on movement
	if tail_rect:
		if move_direction.x > 0:
			tail_rect.position.x = -8
		else:
			tail_rect.position.x = 6

func _start_flee() -> void:
	super._start_flee()
	is_foraging = false
	# Squirrels flee very quickly in zigzag pattern
	if charlie_ref:
		move_direction = (global_position - charlie_ref.global_position).normalized()
		move_direction = move_direction.rotated(randf_range(-0.5, 0.5))

func get_wildlife_name() -> String:
	return "a squirrel"
