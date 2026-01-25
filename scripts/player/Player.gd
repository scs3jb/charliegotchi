extends CharacterBody2D
class_name Player
## Player - The main character (blonde girl)

@export var speed: float = 80.0

# References
@onready var animation_player: AnimationPlayer = $AnimationPlayer
@onready var interaction_area: Area2D = $InteractionArea

# State
var can_move: bool = true
var facing_direction: Vector2 = Vector2.DOWN
var nearby_interactable: Node = null

signal interact_pressed

func _ready() -> void:
	add_to_group("player")

func _physics_process(_delta: float) -> void:
	if not can_move:
		velocity = Vector2.ZERO
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

	# Apply movement
	velocity = input_dir * speed
	move_and_slide()

	# Update animation
	_update_animation(input_dir)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact"):
		_try_interact()

func _update_animation(movement: Vector2) -> void:
	if not animation_player:
		return

	# Skip if no animations are defined
	if animation_player.get_animation_list().is_empty():
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

	# Only play if animation exists
	if animation_player.has_animation(anim_name):
		animation_player.play(anim_name)

func _try_interact() -> void:
	emit_signal("interact_pressed")

	if nearby_interactable and nearby_interactable.has_method("interact"):
		nearby_interactable.interact(self)

func set_can_move(value: bool) -> void:
	can_move = value
	if not can_move:
		velocity = Vector2.ZERO

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
