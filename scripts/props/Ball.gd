extends Area2D
class_name Ball
## Ball - A bouncing ball for fetch game with realistic physics

@export var friction: float = 0.985  # Slightly less friction for more bouncing
@export var bounce_factor: float = 0.85  # How much energy retained on bounce
@export var min_velocity: float = 8.0
@export var bounce_gravity: float = 200.0  # Simulated gravity for bounce effect

# Room bounds (walls) - updated for larger house
var bounds_left: float = 20.0
var bounds_right: float = 405.0
var bounds_top: float = 55.0
var bounds_bottom: float = 275.0

# Furniture collision rects (x, y, width, height)
var furniture_rects: Array = [
	Rect2(5, 0, 115, 50),     # Kitchen counter area
	Rect2(155, 115, 90, 50),  # Table
	Rect2(350, 115, 60, 70),  # Sofa
	Rect2(328, 210, 64, 40),  # Basket
]

# Physics
var ball_velocity: Vector2 = Vector2.ZERO
var is_moving: bool = false
var bounce_height: float = 0.0  # Simulated vertical bounce
var bounce_velocity: float = 0.0  # Vertical bounce velocity
var spin: float = 0.0  # Ball spin for visual effect
var last_bounce_time: float = 0.0

# References
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

# Signals
signal ball_stopped
signal ball_bounced

func _ready() -> void:
	add_to_group("interactable")

func _physics_process(delta: float) -> void:
	if not is_moving:
		return

	# Apply friction to horizontal movement
	ball_velocity *= friction

	# Simulate bouncing with gravity
	bounce_velocity -= bounce_gravity * delta
	bounce_height += bounce_velocity * delta

	# Ground bounce
	if bounce_height <= 0:
		bounce_height = 0
		if abs(bounce_velocity) > 30:
			# Bounce up with energy loss
			bounce_velocity = abs(bounce_velocity) * bounce_factor * 0.7
			emit_signal("ball_bounced")
			last_bounce_time = 0.0
		else:
			bounce_velocity = 0

	# Calculate new position
	var new_pos = global_position + ball_velocity * delta
	var bounced = false

	# Bounce off walls with realistic physics
	if new_pos.x <= bounds_left:
		new_pos.x = bounds_left
		ball_velocity.x = abs(ball_velocity.x) * bounce_factor
		bounce_velocity = max(bounce_velocity, 80)
		bounced = true
		spin = -abs(spin) - ball_velocity.length() * 0.1
	elif new_pos.x >= bounds_right:
		new_pos.x = bounds_right
		ball_velocity.x = -abs(ball_velocity.x) * bounce_factor
		bounce_velocity = max(bounce_velocity, 80)
		bounced = true
		spin = abs(spin) + ball_velocity.length() * 0.1

	if new_pos.y <= bounds_top:
		new_pos.y = bounds_top
		ball_velocity.y = abs(ball_velocity.y) * bounce_factor
		bounce_velocity = max(bounce_velocity, 60)
		bounced = true
	elif new_pos.y >= bounds_bottom:
		new_pos.y = bounds_bottom
		ball_velocity.y = -abs(ball_velocity.y) * bounce_factor
		bounce_velocity = max(bounce_velocity, 60)
		bounced = true

	# Check furniture collisions
	var ball_rect = Rect2(new_pos.x - 6, new_pos.y - 6, 12, 12)
	for furn_rect in furniture_rects:
		if ball_rect.intersects(furn_rect):
			# Determine which side we hit and bounce accordingly
			var center = furn_rect.get_center()
			var from_center = new_pos - center

			# Determine if horizontal or vertical collision
			var overlap_x = (ball_rect.size.x / 2 + furn_rect.size.x / 2) - abs(from_center.x)
			var overlap_y = (ball_rect.size.y / 2 + furn_rect.size.y / 2) - abs(from_center.y)

			if overlap_x < overlap_y:
				# Horizontal bounce
				ball_velocity.x = -ball_velocity.x * bounce_factor
				if from_center.x < 0:
					new_pos.x = furn_rect.position.x - 8
				else:
					new_pos.x = furn_rect.position.x + furn_rect.size.x + 8
			else:
				# Vertical bounce
				ball_velocity.y = -ball_velocity.y * bounce_factor
				if from_center.y < 0:
					new_pos.y = furn_rect.position.y - 8
				else:
					new_pos.y = furn_rect.position.y + furn_rect.size.y + 8

			bounce_velocity = max(bounce_velocity, 50)
			bounced = true
			break

	global_position = new_pos

	if bounced:
		emit_signal("ball_bounced")

	# Apply spin decay
	spin *= 0.95

	# Track time since last bounce for animation
	last_bounce_time += delta

	# Update animation based on movement
	_update_animation()

	# Stop when slow enough
	if ball_velocity.length() < min_velocity and bounce_height < 1 and bounce_velocity < 10:
		ball_velocity = Vector2.ZERO
		bounce_velocity = 0
		bounce_height = 0
		is_moving = false
		spin = 0
		if animated_sprite:
			animated_sprite.play("idle")
		emit_signal("ball_stopped")

func throw(direction: Vector2, power: float = 350.0) -> void:
	"""Throw the ball in a direction with given power."""
	ball_velocity = direction.normalized() * power
	# Add some randomness to make it feel more natural
	ball_velocity = ball_velocity.rotated(randf_range(-0.15, 0.15))
	bounce_velocity = randf_range(100, 180)  # Initial bounce height
	bounce_height = 0
	spin = direction.x * power * 0.02
	is_moving = true

func stop() -> void:
	"""Stop the ball immediately."""
	ball_velocity = Vector2.ZERO
	bounce_velocity = 0
	bounce_height = 0
	spin = 0
	is_moving = false

func _update_animation() -> void:
	if not animated_sprite:
		return

	if is_moving and (ball_velocity.length() > 15 or bounce_height > 2):
		# Calculate animation frame based on bounce phase
		var speed_factor = clampf(ball_velocity.length() / 200.0, 0.5, 2.0)
		animated_sprite.speed_scale = speed_factor

		if animated_sprite.animation != "bounce":
			animated_sprite.play("bounce")

		# Scale sprite slightly based on bounce height for squash/stretch effect
		var squash = 1.0 + bounce_height * 0.01
		animated_sprite.scale = Vector2(1.0 / squash, squash).clamp(Vector2(0.8, 0.8), Vector2(1.2, 1.2))

		# Apply rotation based on spin
		animated_sprite.rotation = spin * 0.1
	else:
		animated_sprite.speed_scale = 1.0
		animated_sprite.scale = Vector2.ONE
		animated_sprite.rotation = 0
		if animated_sprite.animation != "idle":
			animated_sprite.play("idle")
