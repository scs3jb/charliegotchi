extends Node2D
## House - Phase 1 main scene: Feed, pet, and play fetch with Charlie

@onready var player: CharacterBody2D = $Player
@onready var charlie: CharacterBody2D = $Charlie
@onready var food_bowl: Area2D = $FoodBowl
@onready var pet_bed: Area2D = $PetBed
@onready var charlie_basket: Area2D = $CharlieBasket
@onready var ball: Area2D = $Ball
@onready var door: Area2D = $Door
@onready var hud: CanvasLayer = $HUD
@onready var interaction_prompt: Label = $HUD/InteractionPrompt

var nearby_interactable: Node = null
var ball_thrown: bool = false
var original_ball_position: Vector2
var waiting_for_ball_stop: bool = false

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

func _process(delta: float) -> void:
	_update_interaction_prompt()
	_process_basket(delta)

	# Check if ball stopped bouncing so Charlie can fetch
	if waiting_for_ball_stop and "is_moving" in ball:
		if not ball.is_moving:
			waiting_for_ball_stop = false
			charlie.fetch_ball(ball)

	# Check for collision during keep-away - player can catch Charlie by touching
	if charlie.has_ball and charlie.current_state == charlie.State.KEEP_AWAY:
		var catch_distance = 25.0  # Close enough to grab Charlie
		var dist = player.global_position.distance_to(charlie.global_position)
		if dist < catch_distance:
			_take_ball_from_charlie()

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

	# Check distance to basket (send Charlie to rest or wake him)
	dist = player_pos.distance_to(charlie_basket.global_position)
	if dist < 45 and dist < closest_dist:
		closest_dist = dist
		if charlie_in_basket:
			closest_name = "[E] Wake Charlie"
		else:
			closest_name = "[E] Send to Basket"
		nearby_interactable = charlie_basket

	# Check distance to ball - can throw if ball is visible (not in Charlie's mouth)
	if ball.visible:
		dist = player_pos.distance_to(ball.global_position)
		if dist < 40 and dist < closest_dist:
			closest_dist = dist
			closest_name = "[E] Throw Ball"
			nearby_interactable = ball

	# If Charlie has the ball, player can try to catch him
	if charlie.has_ball:
		dist = player_pos.distance_to(charlie.global_position)
		if dist < 50 and dist < closest_dist:  # Slightly larger range to catch Charlie
			closest_dist = dist
			closest_name = "[E] Catch Charlie!"
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
	elif nearby_interactable == charlie_basket:
		_send_to_basket()
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

var charlie_in_basket: bool = false
var basket_rest_time: float = 0.0
var basket_bonding_timer: float = 0.0
const BASKET_MIN_TIME: float = 6.0  # Minimum 6 seconds in basket
const BASKET_MAX_TIME: float = 15.0  # Maximum time before Charlie leaves on his own

func _send_to_basket() -> void:
	if charlie_in_basket:
		# Wake Charlie up from basket
		hud.show_message("Charlie hops out of his basket!", 2.0)
		_exit_basket()
		return

	hud.show_message("Charlie trots to his cozy basket!", 2.0)

	# Make Charlie go to the basket
	charlie.target_position = charlie_basket.global_position
	charlie.start_following()

	# Wait for Charlie to actually reach the basket (check distance)
	var wait_time = 0.0
	var max_wait = 5.0  # Max time to wait for Charlie to reach basket
	while wait_time < max_wait:
		await get_tree().create_timer(0.1).timeout
		wait_time += 0.1
		var dist = charlie.global_position.distance_to(charlie_basket.global_position)
		if dist < 25.0:
			break

	# Charlie has arrived - position him in the basket
	charlie.global_position = charlie_basket.global_position
	charlie.velocity = Vector2.ZERO
	charlie.stop_moving()
	charlie_in_basket = true
	basket_rest_time = 0.0
	basket_bonding_timer = 0.0

	# Play idle animation (sitting/curled up)
	if charlie.has_node("AnimatedSprite2D"):
		charlie.get_node("AnimatedSprite2D").play("idle_down")

	hud.show_message("Charlie curls up in his basket. So cute!", 2.0)

func _exit_basket(start_wander: bool = true) -> void:
	charlie_in_basket = false
	basket_rest_time = 0.0
	basket_bonding_timer = 0.0
	if start_wander:
		charlie.start_wandering()

func _process_basket(delta: float) -> void:
	if not charlie_in_basket:
		return

	basket_rest_time += delta
	basket_bonding_timer += delta

	# Keep Charlie in position
	charlie.global_position = charlie_basket.global_position
	charlie.velocity = Vector2.ZERO

	# Give 1% bonding per second
	if basket_bonding_timer >= 1.0:
		basket_bonding_timer -= 1.0
		GameState.bonding = minf(GameState.bonding + 0.01, 1.0)
		GameState.emit_signal("stats_changed")

	# After max time, Charlie leaves on his own
	if basket_rest_time >= BASKET_MAX_TIME:
		hud.show_message("Charlie stretches and hops out of his basket.", 2.0)
		_exit_basket()

func _throw_ball() -> void:
	ball_thrown = true

	# Stop ball if it's currently moving
	if ball.has_method("stop"):
		ball.stop()

	# Position ball at player before throwing
	ball.global_position = player.global_position
	ball.visible = true

	# Cancel basket behavior if Charlie is in/going to basket
	if charlie_in_basket:
		_exit_basket(false)  # Don't start wandering, he'll fetch instead

	# Interrupt Charlie if he was fetching
	if charlie.current_state == charlie.State.FETCHING:
		charlie.start_wandering()

	# Throw ball with physics - it bounces around!
	var throw_direction = player.facing_direction.normalized()

	# If ball has throw method, use physics
	if ball.has_method("throw"):
		var throw_power = randf_range(280, 420)
		ball.throw(throw_direction, throw_power)
		waiting_for_ball_stop = true  # Wait for ball to stop before Charlie fetches
		hud.show_message("You threw the ball!", 1.5)
	else:
		# Fallback: instant position (old behavior)
		var throw_distance = randf_range(80, 150)
		var target_pos = player.global_position + throw_direction * throw_distance
		target_pos.x = clampf(target_pos.x, 40, 360)
		target_pos.y = clampf(target_pos.y, 40, 200)
		ball.global_position = target_pos
		charlie.fetch_ball(ball)
		hud.show_message("You threw the ball!", 1.5)

func _take_ball_from_charlie() -> void:
	if charlie.take_ball_from_charlie():
		ball_thrown = false
		ball.visible = true

		# Place ball near player so they can throw again immediately
		ball.global_position = player.global_position + Vector2(20, 0)

		# Stop ball movement if it has the method
		if ball.has_method("stop"):
			ball.stop()

		GameState.do_fetch_success()

		if GameState.charlie_returns_ball:
			hud.show_message("Charlie brought you the ball! Good boy!", 2.0)
		else:
			hud.show_message("You caught Charlie and got the ball!", 2.0)

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
