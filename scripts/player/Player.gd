extends CharacterBody2D
class_name Player
## Player - The main character (blonde girl)

@export var speed: float = 80.0
@export var leash_drag_speed: float = 15.0  # Speed when dragging resistant Charlie (very slow)

# References
var animated_sprite: AnimatedSprite2D = null
@onready var interaction_area: Area2D = $InteractionArea
var charlie_ref: Node2D = null  # Reference to Charlie for leash mechanics

# State
var can_move: bool = true
var can_drop: bool = true
var facing_direction: Vector2 = Vector2.DOWN
var held_object: Node2D = null
var is_picking_up: bool = false
var nearby_interactable: Node = null

signal interact_pressed

func _ready() -> void:
	add_to_group("player")
	# Get AnimatedSprite2D if it exists (some scenes use ColorRect placeholders)
	animated_sprite = get_node_or_null("AnimatedSprite2D")

func _physics_process(_delta: float) -> void:
	if not can_move or is_picking_up:
		velocity = Vector2.ZERO
		if not is_picking_up:
			_update_animation(Vector2.ZERO)
		return

	# Get input direction
	var input_dir = Vector2.ZERO
	input_dir.x = Input.get_axis("move_left", "move_right")
	input_dir.y = Input.get_axis("move_up", "move_down")

	# Normalize to prevent faster diagonal movement
	if input_dir.length() > 1.0:
		input_dir = input_dir.normalized()

	# Update facing direction (for animations)
	if input_dir != Vector2.ZERO:
		facing_direction = input_dir.normalized()

	# Check if Charlie is resisting on the leash
	var current_speed = speed
	if charlie_ref and charlie_ref.has_method("get_leash_resistance"):
		var resistance = charlie_ref.get_leash_resistance()
		if resistance > 0:
			# Lerp between normal speed and drag speed based on resistance
			current_speed = lerpf(speed, leash_drag_speed, resistance)

	# Apply movement
	velocity = input_dir * current_speed
	move_and_slide()

	# Update animation
	_update_animation(input_dir)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact"):
		if held_object and can_move and can_drop:
			drop()
		else:
			_try_interact()

func _update_animation(movement: Vector2) -> void:
	if not animated_sprite:
		return

	var anim_name: String = ""

	if movement == Vector2.ZERO:
		# Idle animation based on facing direction
		if abs(facing_direction.x) > abs(facing_direction.y):
			if facing_direction.x > 0:
				anim_name = "idle_right"
			else:
				anim_name = "idle_left"
		else:
			if facing_direction.y > 0:
				anim_name = "idle_down"
			else:
				anim_name = "idle_up"
	else:
		# Walk animation based on movement direction
		if abs(movement.x) > abs(movement.y):
			if movement.x > 0:
				anim_name = "walk_right"
			else:
				anim_name = "walk_left"
		else:
			if movement.y > 0:
				anim_name = "walk_down"
			else:
				anim_name = "walk_up"

	if held_object:
		anim_name = "hold_" + anim_name

	# Safegaurd: if picking up, don't interrupt
	if is_picking_up:
		return

	# Only play if animation exists
	if animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation(anim_name):
		if animated_sprite.animation != anim_name:
			animated_sprite.play(anim_name)

func _try_interact() -> void:
	emit_signal("interact_pressed")

	if nearby_interactable and nearby_interactable.has_method("interact"):
		nearby_interactable.interact(self)

func pickup(target: Node2D) -> void:
	if held_object or is_picking_up:
		return
	
	is_picking_up = true
	can_move = false
	
	# Play pickup animation
	if animated_sprite.sprite_frames.has_animation("pickup"):
		animated_sprite.play("pickup")
		
		# Wait for close to end of animation frame to visually "grab"
		# Or just wait for animation_finished. 
		# For simplicity, we can yield to animation_finished
		if not animated_sprite.is_connected("animation_finished", _on_pickup_finished):
			animated_sprite.connect("animation_finished", _on_pickup_finished.bind(target), CONNECT_ONE_SHOT)
	else:
		# Fallback if no animation
		_on_pickup_finished(target)

func _on_pickup_finished(target: Node2D = null) -> void:
	is_picking_up = false
	can_move = true
	held_object = target
	
	# Notify target it's been picked up
	if target and target.has_method("get_picked_up"):
		target.get_picked_up()

func drop() -> void:
	if not held_object:
		return
		
	# Determine drop position (in front of player)
	var drop_pos = global_position + facing_direction * 20.0
	
	if held_object.has_method("get_dropped"):
		held_object.get_dropped(drop_pos)
	
	held_object = null

func set_can_move(value: bool) -> void:
	can_move = value
	if not can_move:
		velocity = Vector2.ZERO

func set_charlie(charlie: Node2D) -> void:
	charlie_ref = charlie

func get_leash_hand_offset() -> Vector2:
	# Return offset from player center to hand position based on facing direction
	if abs(facing_direction.x) > abs(facing_direction.y):
		if facing_direction.x > 0:
			return Vector2(10, 4)  # Right hand when facing right
		else:
			return Vector2(-10, 4)  # Left hand when facing left
	else:
		if facing_direction.y > 0:
			return Vector2(8, 8)  # Hand when facing down (visible at side)
		else:
			return Vector2(-8, 4)  # Hand when facing up (visible at side)

func _on_interaction_area_body_entered(body: Node2D) -> void:
	if body.is_in_group("interactable"):
		nearby_interactable = body

func _on_interaction_area_area_entered(area: Area2D) -> void:
	if area.is_in_group("interactable"):
		nearby_interactable = area.get_parent()

func _on_interaction_area_body_exited(body: Node2D) -> void:
	if body == nearby_interactable:
		nearby_interactable = null

func _on_interaction_area_area_exited(area: Area2D) -> void:
	if area.get_parent() == nearby_interactable:
		nearby_interactable = null
