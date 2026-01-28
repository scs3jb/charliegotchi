extends CharacterBody2D
class_name Charlie
## Charlie - The baby Shih Tzu companion

@export var speed: float = 60.0
@export var follow_distance: float = 30.0  # How close to stay to player
@export var leash_max_distance: float = 96.0  # Max distance when on leash (3 Charlie lengths)

# References
var animated_sprite: AnimatedSprite2D = null

# State
enum State { IDLE, FOLLOWING, WANDERING, FETCHING, KEEP_AWAY, ON_LEASH, HELD }
var current_state: State = State.IDLE
var is_on_leash: bool = false
var target_position: Vector2 = Vector2.ZERO
var player_ref: Node2D = null

# Fetch game
var ball_ref: Node2D = null
var has_ball: bool = false
var returning_ball: bool = false

# Keep-away behavior
var keep_away_timer: float = 0.0
var flee_direction: Vector2 = Vector2.ZERO

# Wander behavior
var wander_timer: float = 0.0
var wander_direction: Vector2 = Vector2.ZERO

# Leash resistance (for slowing player)
var is_resisting: bool = false
var resistance_amount: float = 0.0  # 0.0 to 1.0, how much Charlie is resisting
var leash_wander_timer: float = 0.0
var leash_wander_direction: Vector2 = Vector2.ZERO

# Animation
var facing_direction: String = "down"

signal reached_player
signal picked_up_ball
signal charlie_interacted

# Spritesheet configuration
# Spritesheet configuration
# const FRAME_SIZE: int = 32 # Deprecated, using SpriteFrames resource

func _ready() -> void:
	add_to_group("charlie")
	add_to_group("interactable")
	_setup_animated_sprite()


func _setup_animated_sprite() -> void:
	# Check if AnimatedSprite2D already exists
	animated_sprite = get_node_or_null("AnimatedSprite2D")

	if animated_sprite == null:
		# Create AnimatedSprite2D dynamically
		animated_sprite = AnimatedSprite2D.new()
		animated_sprite.name = "AnimatedSprite2D"
		animated_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST  # Pixel art
		animated_sprite.scale = Vector2(0.25, 0.25)  # Scale down 128px to 32px display size
		add_child(animated_sprite)

		# Remove any ColorRect children (old placeholder graphics)
		for child in get_children():
			if child is ColorRect:
				child.queue_free()
	else:
		# Ensure pixel art filtering and correct scale for existing sprite
		# Ensure pixel art filtering
		animated_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		# Scale is now handled in the scene (should be 1.0 for 32px assets)

	# Note: SpriteFrames are now appointed in the editor via charlie_sprite_frames.tres
	# We rely on the scene configuration rather than building it at runtime.
	
	if animated_sprite.sprite_frames == null:
		push_warning("Charlie: AnimatedSprite2D has no SpriteFrames assigned!")
	
	# Start idle
	animated_sprite.play("idle_down")

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
		State.KEEP_AWAY:
			_process_keep_away(delta)
		State.ON_LEASH:
			_process_on_leash(delta)
		State.HELD:
			# Do nothing, position controlled by player animation (implied)
			pass

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
			velocity = direction * speed * 1.2  # Faster when chasing ball
		else:
			# Pick up ball
			has_ball = true
			ball_ref.visible = false
			emit_signal("picked_up_ball")

			# Check if Charlie returns ball or plays keep-away
			if GameState.charlie_returns_ball:
				returning_ball = true
			else:
				# Start keep-away behavior!
				current_state = State.KEEP_AWAY
				keep_away_timer = randf_range(5.0, 10.0)  # Play for 5-10 seconds
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

func _process_keep_away(delta: float) -> void:
	if not player_ref or not has_ball:
		current_state = State.WANDERING
		return

	keep_away_timer -= delta

	var distance_to_player = global_position.distance_to(player_ref.global_position)

	# Get player velocity for prediction
	var player_velocity = Vector2.ZERO
	if player_ref.has_method("get_velocity"):
		player_velocity = player_ref.velocity
	elif player_ref is CharacterBody2D:
		player_velocity = player_ref.velocity

	# Predict where player is heading
	var player_predicted_pos = player_ref.global_position + player_velocity * 0.5

	# If player gets close, run away with excitement!
	if distance_to_player < 70:
		# Flee from predicted player position
		flee_direction = (global_position - player_predicted_pos).normalized()

		# Add playful zigzag movement
		var zigzag = sin(Time.get_ticks_msec() * 0.008) * 0.6
		flee_direction = flee_direction.rotated(zigzag)

		# Run fast with occasional speed bursts!
		var speed_mult = 1.6
		if randf() < 0.05:  # Occasional speed burst
			speed_mult = 2.2

		velocity = flee_direction * speed * speed_mult

		# Avoid corners - if near wall, try to go along it
		var new_pos = global_position + velocity * delta
		var wall_avoid = Vector2.ZERO

		if new_pos.x < 45:
			wall_avoid.x = 1.0
			flee_direction.x = abs(flee_direction.x) * 0.5 + wall_avoid.x * 0.5
		elif new_pos.x > 380:
			wall_avoid.x = -1.0
			flee_direction.x = -abs(flee_direction.x) * 0.5 + wall_avoid.x * 0.5

		if new_pos.y < 45:
			wall_avoid.y = 1.0
			flee_direction.y = abs(flee_direction.y) * 0.5 + wall_avoid.y * 0.5
		elif new_pos.y > 200:
			wall_avoid.y = -1.0
			flee_direction.y = -abs(flee_direction.y) * 0.5 + wall_avoid.y * 0.5

		if wall_avoid != Vector2.ZERO:
			# When cornered, try to slip past player
			var perpendicular = Vector2(-flee_direction.y, flee_direction.x)
			if randf() > 0.5:
				perpendicular = -perpendicular
			flee_direction = (flee_direction + perpendicular).normalized()

		velocity = flee_direction * speed * speed_mult

	elif distance_to_player < 120:
		# Medium distance - playful dodging
		flee_direction = (global_position - player_ref.global_position).normalized()

		# Circle around player sometimes
		if randf() < 0.1:
			var perpendicular = Vector2(-flee_direction.y, flee_direction.x)
			flee_direction = (flee_direction * 0.3 + perpendicular * 0.7).normalized()

		velocity = flee_direction * speed * 1.0

	else:
		# Far from player - taunt by pausing, then making small movements
		if keep_away_timer < 2.0:
			# Taunt: stop and look at player
			velocity = velocity.lerp(Vector2.ZERO, 0.2)

			# Occasionally do a playful hop in place
			if randf() < 0.03:
				# Small excited movement
				flee_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
				velocity = flee_direction * speed * 0.5
		else:
			# Wander slowly while watching player
			if randf() < 0.03:
				flee_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
			velocity = flee_direction * speed * 0.35

	# Clamp to room bounds
	global_position.x = clampf(global_position.x, 30, 395)
	global_position.y = clampf(global_position.y, 25, 210)

	# After timer expires, reset for next taunt cycle
	if keep_away_timer <= 0:
		keep_away_timer = randf_range(2.5, 5.0)

func _process_on_leash(delta: float) -> void:
	if not player_ref:
		return

	var distance_to_player = global_position.distance_to(player_ref.global_position)
	var direction_to_player = (player_ref.global_position - global_position).normalized()
	var leash_tension = distance_to_player / leash_max_distance  # 0.0 to 1.0+

	# Get player's movement direction
	var player_velocity = Vector2.ZERO
	if player_ref is CharacterBody2D:
		player_velocity = player_ref.velocity

	# Reset resistance
	is_resisting = false
	resistance_amount = 0.0

	# High bonding (>= 0.5): Charlie follows the player nicely
	if GameState.bonding >= 0.5:
		# Match player position with offset
		var target = player_ref.global_position + Vector2(20, 20)
		if global_position.distance_to(target) > 5:
			var direction = (target - global_position).normalized()
			velocity = direction * speed
		else:
			velocity = Vector2.ZERO
	else:
		# Low bonding: Charlie wanders randomly
		leash_wander_timer -= delta

		if leash_wander_timer <= 0:
			# Pick new random direction or stop
			if randf() < 0.3:
				leash_wander_direction = Vector2.ZERO
			else:
				leash_wander_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
			leash_wander_timer = randf_range(1.0, 3.0)

		# Movement based on leash tension
		if distance_to_player >= leash_max_distance:
			# At max leash length - must follow player, can't go further
			velocity = direction_to_player * speed * 0.5
		elif leash_tension > 0.7:
			# Getting tight - reduce wandering, bias toward player
			var wander_factor = 1.0 - ((leash_tension - 0.7) / 0.3)  # 1.0 at 70%, 0.0 at 100%
			var wander_velocity = leash_wander_direction * speed * 0.4 * wander_factor
			var pull_velocity = direction_to_player * speed * 0.3 * (1.0 - wander_factor)
			velocity = wander_velocity + pull_velocity
		else:
			# Free to wander within leash range
			velocity = leash_wander_direction * speed * 0.5

	# Calculate resistance: only when leash is taut (>70%) AND player moving AWAY from Charlie
	if leash_tension >= 0.7 and player_velocity.length() > 5:
		var player_dir = player_velocity.normalized()
		# direction_to_player points FROM Charlie TO Player
		# If player moves in same direction as direction_to_player, they're moving AWAY from Charlie
		# If player moves opposite to direction_to_player, they're moving TOWARD Charlie
		var moving_away_factor = player_dir.dot(direction_to_player)

		if moving_away_factor > 0.2:  # Player moving away from Charlie
			# Resistance scales from 0 at 70% to full at 100%
			var tension_factor = clampf((leash_tension - 0.7) / 0.3, 0.0, 1.0)
			resistance_amount = tension_factor * moving_away_factor
			is_resisting = resistance_amount > 0.1

func _update_animation() -> void:
	if not animated_sprite or not animated_sprite.sprite_frames:
		return

	var anim_name: String = ""
	var is_moving: bool = velocity.length() >= 5

	# Determine facing direction
	if is_moving:
		if abs(velocity.x) > abs(velocity.y):
			facing_direction = "right" if velocity.x > 0 else "left"
		else:
			facing_direction = "down" if velocity.y > 0 else "up"

	# Build animation name
	var action: String = "walk" if is_moving else "idle"
	anim_name = action + "_" + facing_direction

	# Add ball suffix if Charlie has the ball
	if has_ball:
		var ball_anim: String = anim_name + "_ball"
		# Check if ball animation exists (we have ball anims for down, left, right but not up)
		if animated_sprite.sprite_frames.has_animation(ball_anim):
			anim_name = ball_anim
		elif facing_direction == "up" and has_ball:
			# Fallback to down_ball for up direction
			anim_name = action + "_down_ball"

	# Only play if animation exists
	if animated_sprite.sprite_frames.has_animation(anim_name):
		if animated_sprite.animation != anim_name:
			animated_sprite.play(anim_name)
	else:
		# Fallback to idle_down
		if animated_sprite.animation != "idle_down":
			animated_sprite.play("idle_down")

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
	is_resisting = false
	resistance_amount = 0.0
	current_state = State.FOLLOWING

func is_leash_resisting() -> bool:
	return is_on_leash and is_resisting

func get_leash_resistance() -> float:
	if is_on_leash:
		return resistance_amount
	return 0.0

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
	elif player.has_method("pickup") and player.held_object == null:
		player.pickup(self)

func get_picked_up() -> void:
	current_state = State.HELD
	visible = false
	$CollisionShape2D.set_deferred("disabled", true)
	emit_signal("charlie_interacted") # Feedback?

func get_dropped(drop_pos: Vector2) -> void:
	current_state = State.IDLE
	global_position = drop_pos
	visible = true
	$CollisionShape2D.set_deferred("disabled", false)
