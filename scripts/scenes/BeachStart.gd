extends Node2D
## BeachStart - Phase 1 beginning: Find Charlie in the box, coax him with food

@onready var player: CharacterBody2D = $Player
@onready var box: StaticBody2D = $Box
@onready var charlie: CharacterBody2D = $Charlie
@onready var dialogue_panel: Panel = $CanvasLayer/DialoguePanel
@onready var dialogue_label: Label = $CanvasLayer/DialoguePanel/DialogueLabel
@onready var interaction_prompt: Label = $CanvasLayer/InteractionPrompt
@onready var food_minigame: Control = $CanvasLayer/FoodMiniGame
@onready var food_progress: ProgressBar = $CanvasLayer/FoodMiniGame/ProgressBar
@onready var thrown_steak: Node2D = $ThrownSteak

enum BeachState { EXPLORING, FOUND_BOX, MINIGAME, CHARLIE_OUT, PICKUP_CHARLIE, GOING_HOME }
var current_state: BeachState = BeachState.EXPLORING

var dialogue_queue: Array = []
var food_clicks: int = 0
const FOOD_CLICKS_NEEDED: int = 5
var is_throwing: bool = false

func _ready() -> void:
	# Connect player interaction
	player.interact_pressed.connect(_on_interact_pressed)

	# Check if already found Charlie (continuing game)
	if GameState.charlie_found and not GameState.charlie_coaxed:
		current_state = BeachState.FOUND_BOX
	elif GameState.charlie_coaxed:
		_show_charlie_out()

func _process(_delta: float) -> void:
	_update_interaction_prompt()

func _update_interaction_prompt() -> void:
	if current_state != BeachState.EXPLORING and current_state != BeachState.CHARLIE_OUT:
		interaction_prompt.visible = false
		return

	var player_pos = player.global_position

	# Check distance to box
	if current_state == BeachState.EXPLORING:
		var dist_to_box = player_pos.distance_to(box.global_position)
		if dist_to_box < 50:
			interaction_prompt.text = "[E] Investigate box"
			interaction_prompt.visible = true
		else:
			interaction_prompt.visible = false

	# Check distance to Charlie after he's out
	elif current_state == BeachState.CHARLIE_OUT:
		var dist_to_charlie = player_pos.distance_to(charlie.global_position)
		if dist_to_charlie < 40:
			interaction_prompt.text = "[E] Pick up Charlie"
			interaction_prompt.visible = true
		else:
			interaction_prompt.visible = false

func _on_interact_pressed() -> void:
	# Handle dialogue continuation
	if dialogue_panel.visible:
		_advance_dialogue()
		return

	match current_state:
		BeachState.EXPLORING:
			var dist = player.global_position.distance_to(box.global_position)
			if dist < 50:
				_investigate_box()
		BeachState.CHARLIE_OUT:
			var dist = player.global_position.distance_to(charlie.global_position)
			if dist < 40:
				_pickup_charlie()

func _investigate_box() -> void:
	GameState.charlie_found = true
	current_state = BeachState.FOUND_BOX

	dialogue_queue = [
		"You notice a cardboard box washed up on the beach.",
		"It's soggy from the storm, but something inside is moving!",
		"You peek inside and see... a tiny puppy!",
		"He looks scared and hungry.",
		"Maybe if you had some food..."
	]
	_show_next_dialogue()

func _show_next_dialogue() -> void:
	if dialogue_queue.size() > 0:
		dialogue_label.text = dialogue_queue.pop_front()
		dialogue_panel.visible = true
		player.set_can_move(false)
	else:
		dialogue_panel.visible = false
		player.set_can_move(true)
		_after_dialogue()

func _advance_dialogue() -> void:
	_show_next_dialogue()

func _after_dialogue() -> void:
	match current_state:
		BeachState.FOUND_BOX:
			_start_food_minigame()
		BeachState.PICKUP_CHARLIE:
			_go_to_house()

func _start_food_minigame() -> void:
	current_state = BeachState.MINIGAME
	food_minigame.visible = true
	food_clicks = 0
	food_progress.value = 0
	player.set_can_move(false)

func _on_food_clicked() -> void:
	if is_throwing:
		return

	is_throwing = true
	_throw_steak_to_box()

func _throw_steak_to_box() -> void:
	# Position steak at player's hand
	var start_pos = player.global_position + Vector2(8, -4)
	var end_pos = box.global_position + Vector2(0, -5)

	thrown_steak.global_position = start_pos
	thrown_steak.visible = true
	thrown_steak.rotation = 0

	# Create arc animation using tweens
	var tween = create_tween()
	tween.set_parallel(true)

	# Horizontal movement
	tween.tween_property(thrown_steak, "global_position:x", end_pos.x, 0.5).set_ease(Tween.EASE_OUT)

	# Vertical arc (go up then down)
	var arc_height = -40.0
	var mid_y = min(start_pos.y, end_pos.y) + arc_height
	tween.tween_property(thrown_steak, "global_position:y", mid_y, 0.25).set_ease(Tween.EASE_OUT)
	tween.chain().tween_property(thrown_steak, "global_position:y", end_pos.y, 0.25).set_ease(Tween.EASE_IN)

	# Spin the steak
	tween.tween_property(thrown_steak, "rotation", TAU, 0.5)

	# When animation finishes
	tween.chain().tween_callback(_on_steak_landed)

func _on_steak_landed() -> void:
	thrown_steak.visible = false
	is_throwing = false

	food_clicks += 1
	food_progress.value = (float(food_clicks) / FOOD_CLICKS_NEEDED) * 100

	if food_clicks >= FOOD_CLICKS_NEEDED:
		_complete_minigame()

func _complete_minigame() -> void:
	food_minigame.visible = false
	GameState.charlie_coaxed = true
	_show_charlie_out()

	dialogue_queue = [
		"Charlie slowly emerges from the box!",
		"He sniffs the food and cautiously takes a bite.",
		"His little tail starts to wag...",
		"Charlie seems to trust you now!"
	]
	current_state = BeachState.CHARLIE_OUT
	_show_next_dialogue()

func _show_charlie_out() -> void:
	charlie.visible = true
	# Move Charlie slightly away from box
	charlie.global_position = box.global_position + Vector2(30, 0)

func _pickup_charlie() -> void:
	current_state = BeachState.PICKUP_CHARLIE

	# Use the player's pickup method which plays the pickup animation
	# and transitions to hold animations
	player.pickup(charlie)

	# Prevent player from dropping Charlie until scene transition
	player.can_drop = false

	dialogue_queue = [
		"You gently pick up Charlie.",
		"He nestles into your arms, exhausted from his ordeal.",
		"You should take him home where it's safe and warm."
	]
	_show_next_dialogue()

func _go_to_house() -> void:
	current_state = BeachState.GOING_HOME
	GameState.save_game()
	get_tree().change_scene_to_file("res://scenes/House.tscn")
