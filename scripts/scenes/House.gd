extends Node2D
## House - Phase 1 main scene: Feed, pet, and play fetch with Charlie

@onready var player: CharacterBody2D = $Player
@onready var charlie: CharacterBody2D = $Charlie
@onready var food_bowl: Area2D = $FoodBowl
@onready var pet_bed: Area2D = $PetBed
@onready var ball: Area2D = $Ball
@onready var door: Area2D = $Door
@onready var hud: CanvasLayer = $HUD
@onready var interaction_prompt: Label = $HUD/InteractionPrompt

var nearby_interactable: Node = null
var ball_thrown: bool = false
var original_ball_position: Vector2

func _ready() -> void:
	# Set up Charlie
	charlie.set_player(player)
	charlie.start_wandering()

	# Store original ball position
	original_ball_position = ball.global_position

	# Connect signals
	player.interact_pressed.connect(_on_interact_pressed)
	charlie.charlie_interacted.connect(_on_charlie_interacted)
	GameState.charlie_trust_unlocked.connect(_on_trust_unlocked)

	# Update HUD with current stats
	_update_hud()

func _process(_delta: float) -> void:
	_update_interaction_prompt()

func _update_interaction_prompt() -> void:
	var player_pos = player.global_position
	var closest_dist = 999.0
	var closest_name = ""
	nearby_interactable = null

	# Check distance to food bowl
	var dist = player_pos.distance_to(food_bowl.global_position)
	if dist < 40 and dist < closest_dist:
		closest_dist = dist
		closest_name = "[E] Feed Charlie"
		nearby_interactable = food_bowl

	# Check distance to pet bed (for petting)
	dist = player_pos.distance_to(pet_bed.global_position)
	if dist < 40 and dist < closest_dist:
		closest_dist = dist
		closest_name = "[E] Pet Charlie"
		nearby_interactable = pet_bed

	# Check distance to ball
	if not ball_thrown:
		dist = player_pos.distance_to(ball.global_position)
		if dist < 40 and dist < closest_dist:
			closest_dist = dist
			closest_name = "[E] Throw Ball"
			nearby_interactable = ball
	else:
		# Ball was thrown, check if we can take it from Charlie
		if charlie.has_ball:
			dist = player_pos.distance_to(charlie.global_position)
			if dist < 40 and dist < closest_dist:
				closest_dist = dist
				closest_name = "[E] Take Ball"
				nearby_interactable = charlie

	# Check distance to door
	dist = player_pos.distance_to(door.global_position)
	if dist < 40 and dist < closest_dist:
		closest_dist = dist
		if GameState.charlie_trusts_player:
			closest_name = "[E] Go Outside"
		else:
			closest_name = "[E] Door (Locked)"
		nearby_interactable = door

	if nearby_interactable:
		interaction_prompt.text = closest_name
		interaction_prompt.visible = true
	else:
		interaction_prompt.visible = false

func _on_interact_pressed() -> void:
	if not nearby_interactable:
		return

	if nearby_interactable == food_bowl:
		_feed_charlie()
	elif nearby_interactable == pet_bed:
		_pet_charlie()
	elif nearby_interactable == ball:
		_throw_ball()
	elif nearby_interactable == charlie and charlie.has_ball:
		_take_ball_from_charlie()
	elif nearby_interactable == door:
		_try_exit_door()

func _feed_charlie() -> void:
	GameState.do_feed()
	hud.show_message("You fed Charlie! He wags his tail happily.", 2.0)

	# Make Charlie come to food bowl
	charlie.target_position = food_bowl.global_position
	charlie.start_following()

	# After a moment, return to wandering
	await get_tree().create_timer(2.0).timeout
	charlie.start_wandering()

func _pet_charlie() -> void:
	GameState.do_pet()
	hud.show_message("You pet Charlie! He leans into your hand.", 2.0)

	# Make Charlie come to pet bed area
	charlie.target_position = pet_bed.global_position
	charlie.start_following()

	await get_tree().create_timer(2.0).timeout
	charlie.start_wandering()

func _throw_ball() -> void:
	ball_thrown = true

	# Move ball to a random position
	var throw_direction = player.facing_direction.normalized()
	var throw_distance = randf_range(80, 150)
	var target_pos = player.global_position + throw_direction * throw_distance

	# Clamp to room bounds
	target_pos.x = clampf(target_pos.x, 40, 360)
	target_pos.y = clampf(target_pos.y, 40, 260)

	ball.global_position = target_pos

	# Tell Charlie to fetch
	charlie.fetch_ball(ball)

	hud.show_message("You threw the ball!", 1.5)

func _take_ball_from_charlie() -> void:
	if charlie.take_ball_from_charlie():
		ball_thrown = false
		ball.visible = true
		ball.global_position = original_ball_position

		GameState.do_fetch_success()

		if GameState.charlie_returns_ball:
			hud.show_message("Charlie brought you the ball! Good boy!", 2.0)
		else:
			hud.show_message("You took the ball from Charlie.", 2.0)

		charlie.start_wandering()

func _on_charlie_interacted() -> void:
	# Called when player directly interacts with Charlie
	if charlie.has_ball:
		_take_ball_from_charlie()

func _try_exit_door() -> void:
	if GameState.charlie_trusts_player:
		# Can go outside - transition to Phase 2
		GameState.set_phase(2)
		GameState.save_game()
		get_tree().change_scene_to_file("res://scenes/Overworld.tscn")
	else:
		var bonding_pct = int(GameState.bonding * 100)
		var ent_pct = int(GameState.entertainment * 100)
		hud.show_message("Charlie isn't ready to go outside yet.\nBonding: %d%% Entertainment: %d%%" % [bonding_pct, ent_pct], 3.0)

func _on_trust_unlocked() -> void:
	hud.show_message("Charlie now trusts you enough to explore outside!", 5.0)

func _update_hud() -> void:
	# HUD auto-updates via signals, but we can force refresh here if needed
	pass
