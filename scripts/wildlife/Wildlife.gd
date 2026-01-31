extends CharacterBody2D
class_name Wildlife
## Wildlife - Base class for wildlife creatures that Charlie can spot

@export var base_speed: float = 30.0
@export var flee_speed: float = 100.0
@export var charlie_detection_radius: float = 60.0  # How close Charlie must get to scare it
@export var entertainment_value: float = 0.02  # Entertainment boost when Charlie interacts

# State machine
enum State { IDLE, MOVING, FLEEING, DESPAWNING, CLIMBING }
var current_state: State = State.IDLE

# Movement
var move_direction: Vector2 = Vector2.ZERO
var move_timer: float = 0.0
var idle_timer: float = 0.0

# Visual
var body_rect: ColorRect = null
var body_color: Color = Color.WHITE
var body_size: Vector2 = Vector2(8, 8)

# References
var charlie_ref: Node2D = null

# Lifetime
var lifetime: float = 30.0  # Despawn after 30 seconds if not scared away
var despawn_timer: float = 0.0
var fade_alpha: float = 1.0

# Bounds for movement
var bounds_min: Vector2 = Vector2(30, 50)
var bounds_max: Vector2 = Vector2(820, 450)

signal wildlife_fled(wildlife: Wildlife)
signal wildlife_despawned(wildlife: Wildlife)

func _ready() -> void:
	add_to_group("wildlife")
	_setup_visual()
	_start_idle()

func _setup_visual() -> void:
	# Create ColorRect for body
	body_rect = ColorRect.new()
	body_rect.size = body_size
	body_rect.position = -body_size / 2
	body_rect.color = body_color
	add_child(body_rect)

func _physics_process(delta: float) -> void:
	match current_state:
		State.IDLE:
			_process_idle(delta)
		State.MOVING:
			_process_moving(delta)
		State.FLEEING:
			_process_fleeing(delta)
		State.DESPAWNING:
			_process_despawning(delta)

	# Check lifetime
	lifetime -= delta
	if lifetime <= 0 and current_state != State.DESPAWNING:
		_start_despawn()

	# Check for Charlie
	if charlie_ref and current_state != State.FLEEING and current_state != State.DESPAWNING:
		var distance_to_charlie = global_position.distance_to(charlie_ref.global_position)
		if distance_to_charlie < charlie_detection_radius:
			_start_flee()

	move_and_slide()

func _process_idle(delta: float) -> void:
	idle_timer -= delta
	velocity = Vector2.ZERO

	if idle_timer <= 0:
		_start_moving()

func _process_moving(delta: float) -> void:
	move_timer -= delta
	velocity = move_direction * base_speed

	# Keep within bounds
	_clamp_to_bounds()

	if move_timer <= 0:
		_start_idle()

func _process_fleeing(delta: float) -> void:
	velocity = move_direction * flee_speed

	# Fade out while fleeing
	despawn_timer -= get_physics_process_delta_time()
	fade_alpha = max(0.0, despawn_timer / 1.5)
	if body_rect:
		body_rect.modulate.a = fade_alpha

	if despawn_timer <= 0:
		_finish_despawn()

func _process_despawning(delta: float) -> void:
	despawn_timer -= delta
	fade_alpha = max(0.0, despawn_timer / 1.0)
	if body_rect:
		body_rect.modulate.a = fade_alpha
	velocity = Vector2.ZERO

	if despawn_timer <= 0:
		_finish_despawn()

func _start_idle() -> void:
	current_state = State.IDLE
	idle_timer = randf_range(1.0, 3.0)
	velocity = Vector2.ZERO

func _start_moving() -> void:
	current_state = State.MOVING
	move_timer = randf_range(1.0, 3.0)
	move_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
	_clamp_direction_to_bounds()

func _start_flee() -> void:
	if current_state == State.FLEEING:
		return

	current_state = State.FLEEING
	despawn_timer = 1.5  # Time to flee before disappearing

	# Flee away from Charlie
	if charlie_ref:
		move_direction = (global_position - charlie_ref.global_position).normalized()
		# Add some randomness
		move_direction = move_direction.rotated(randf_range(-0.3, 0.3))
	else:
		move_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()

	# Give Charlie entertainment
	if charlie_ref:
		GameState.add_entertainment(entertainment_value)
		print("Charlie spotted %s! Entertainment +%d%%" % [get_wildlife_name(), int(entertainment_value * 100)])

	emit_signal("wildlife_fled", self)

func _start_despawn() -> void:
	current_state = State.DESPAWNING
	despawn_timer = 1.0

func _finish_despawn() -> void:
	emit_signal("wildlife_despawned", self)
	queue_free()

func _clamp_to_bounds() -> void:
	if global_position.x < bounds_min.x or global_position.x > bounds_max.x:
		move_direction.x = -move_direction.x
		global_position.x = clampf(global_position.x, bounds_min.x, bounds_max.x)
	if global_position.y < bounds_min.y or global_position.y > bounds_max.y:
		move_direction.y = -move_direction.y
		global_position.y = clampf(global_position.y, bounds_min.y, bounds_max.y)

func _clamp_direction_to_bounds() -> void:
	# If near edge, bias direction away from edge
	if global_position.x < bounds_min.x + 50:
		move_direction.x = abs(move_direction.x)
	elif global_position.x > bounds_max.x - 50:
		move_direction.x = -abs(move_direction.x)
	if global_position.y < bounds_min.y + 50:
		move_direction.y = abs(move_direction.y)
	elif global_position.y > bounds_max.y - 50:
		move_direction.y = -abs(move_direction.y)
	move_direction = move_direction.normalized()

func set_charlie(charlie: Node2D) -> void:
	charlie_ref = charlie

func get_wildlife_name() -> String:
	return "Wildlife"
