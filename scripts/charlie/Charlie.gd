extends CharacterBody2D
class_name Charlie
## Charlie - The baby Shih Tzu companion

@export var speed: float = 60.0
@export var follow_distance: float = 30.0  # How close to stay to player
@export var leash_max_distance: float = 60.0  # Max distance when on leash

# References
@onready var animation_player: AnimationPlayer = $AnimationPlayer

# State
enum State { IDLE, FOLLOWING, WANDERING, FETCHING, ON_LEASH }
var current_state: State = State.IDLE
var is_on_leash: bool = false
var target_position: Vector2 = Vector2.ZERO
var player_ref: Node2D = null

# Fetch game
var ball_ref: Node2D = null
var has_ball: bool = false
var returning_ball: bool = false

# Wander behavior
var wander_timer: float = 0.0
var wander_direction: Vector2 = Vector2.ZERO

signal reached_player
signal picked_up_ball
signal charlie_interacted

func _ready() -> void:
	add_to_group("charlie")
	add_to_group("interactable")

func _physics_process(delta: float) -> void:
	match current_state:
		State.IDLE:
			_process_idle(delta)
		State.FOLLOWING:
			_process_following(delta)
		State.WANDERING:
			_process_wandering(delta)
		State.FETCHING:
			_process_fetching(delta)
		State.ON_LEASH:
			_process_on_leash(delta)

	move_and_slide()
	_update_animation()

func _process_idle(_delta: float) -> void:
	velocity = Vector2.ZERO

func _process_following(delta: float) -> void:
	if not player_ref:
		return

	var distance_to_player = global_position.distance_to(player_ref.global_position)

	if distance_to_player > follow_distance:
		var direction = (player_ref.global_position - global_position).normalized()
		velocity = direction * speed
	else:
		velocity = Vector2.ZERO
		emit_signal("reached_player")

func _process_wandering(delta: float) -> void:
	wander_timer -= delta

	if wander_timer <= 0:
		# Pick new random direction or stop
		if randf() < 0.3:
			wander_direction = Vector2.ZERO
		else:
			wander_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
		wander_timer = randf_range(1.0, 3.0)

	# If near player and on leash, don't wander too far
	if is_on_leash and player_ref:
		var distance_to_player = global_position.distance_to(player_ref.global_position)
		if distance_to_player > leash_max_distance * 0.8:
			# Turn back toward player
			wander_direction = (player_ref.global_position - global_position).normalized()

	velocity = wander_direction * speed * 0.5

func _process_fetching(_delta: float) -> void:
	if not ball_ref:
		current_state = State.IDLE
		return

	if not has_ball:
		# Move toward ball
		var distance_to_ball = global_position.distance_to(ball_ref.global_position)
		if distance_to_ball > 10:
			var direction = (ball_ref.global_position - global_position).normalized()
			velocity = direction * speed
		else:
			# Pick up ball
			has_ball = true
			ball_ref.visible = false
			emit_signal("picked_up_ball")

			# Check if Charlie returns ball or player must come get it
			if GameState.charlie_returns_ball:
				returning_ball = true
			else:
				current_state = State.IDLE
				velocity = Vector2.ZERO
	elif returning_ball and player_ref:
		# Return ball to player
		var distance_to_player = global_position.distance_to(player_ref.global_position)
		if distance_to_player > follow_distance:
			var direction = (player_ref.global_position - global_position).normalized()
			velocity = direction * speed
		else:
			# Arrived at player
			velocity = Vector2.ZERO
			current_state = State.IDLE
			returning_ball = false
	else:
		velocity = Vector2.ZERO

func _process_on_leash(_delta: float) -> void:
	if not player_ref:
		return

	var distance_to_player = global_position.distance_to(player_ref.global_position)

	# High bonding = walk in sync with player
	if GameState.bonding >= 0.75:
		# Match player position with offset
		var target = player_ref.global_position + Vector2(20, 20)
		if global_position.distance_to(target) > 5:
			var direction = (target - global_position).normalized()
			velocity = direction * speed
		else:
			velocity = Vector2.ZERO
	elif distance_to_player > leash_max_distance:
		# Pull toward player when too far
		var direction = (player_ref.global_position - global_position).normalized()
		velocity = direction * speed * 1.2
	elif distance_to_player < follow_distance:
		# Too close, slight wander
		velocity = velocity.lerp(Vector2.ZERO, 0.1)
	else:
		# Normal following
		var direction = (player_ref.global_position - global_position).normalized()
		velocity = direction * speed * 0.8

func _update_animation() -> void:
	if not animation_player:
		return

	# Skip if no animations are defined
	if animation_player.get_animation_list().is_empty():
		return

	var anim_name: String = ""

	if velocity.length() < 5:
		anim_name = "idle"
	else:
		if abs(velocity.x) > abs(velocity.y):
			if velocity.x > 0:
				anim_name = "walk_right"
			else:
				anim_name = "walk_left"
		else:
			if velocity.y > 0:
				anim_name = "walk_down"
			else:
				anim_name = "walk_up"

	# Only play if animation exists
	if animation_player.has_animation(anim_name):
		animation_player.play(anim_name)

# Public methods
func set_player(player: Node2D) -> void:
	player_ref = player

func start_following() -> void:
	current_state = State.FOLLOWING

func start_wandering() -> void:
	current_state = State.WANDERING
	wander_timer = 0.0

func stop_moving() -> void:
	current_state = State.IDLE
	velocity = Vector2.ZERO

func fetch_ball(ball: Node2D) -> void:
	ball_ref = ball
	has_ball = false
	returning_ball = false
	current_state = State.FETCHING

func equip_leash() -> void:
	is_on_leash = true
	current_state = State.ON_LEASH

func remove_leash() -> void:
	is_on_leash = false
	current_state = State.FOLLOWING

func take_ball_from_charlie() -> bool:
	if has_ball:
		has_ball = false
		return true
	return false

func interact(player: Node2D) -> void:
	emit_signal("charlie_interacted")

	# If Charlie has ball, take it
	if has_ball:
		take_ball_from_charlie()
		GameState.do_fetch_success()
