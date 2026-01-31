extends Node2D
## Overworld - Phase 2: Outdoor exploration with Charlie on leash
## Multi-screen world with Zelda-style screen transitions

# Screen/World Constants
const SCREEN_WIDTH: int = 426
const SCREEN_HEIGHT: int = 240
const GRID_COLS: int = 6
const GRID_ROWS: int = 4
const WORLD_WIDTH: int = SCREEN_WIDTH * GRID_COLS  # 2556
const WORLD_HEIGHT: int = SCREEN_HEIGHT * GRID_ROWS  # 960
const TRANSITION_DURATION: float = 0.4

# Screen transition state
var current_screen: Vector2i = Vector2i(1, 1)  # Start at home screen (col 1, row 1)
var is_transitioning: bool = false
var transition_direction: Vector2 = Vector2.ZERO

@onready var player: CharacterBody2D = $Player
@onready var charlie: Charlie = $Charlie
@onready var house: Area2D = $House
@onready var leash_line: Line2D = $LeashLine
@onready var ambient_light: CanvasModulate = $AmbientLight
@onready var hud: CanvasLayer = $HUD
@onready var interaction_prompt: Label = $HUD/InteractionPrompt
@onready var weather_label: Label = $HUD/MarginContainer/VBoxContainer/WeatherLabel
@onready var wildlife_spawner: Node2D = $WildlifeSpawner
@onready var message_panel: Panel = $HUD/MessagePanel
@onready var message_label: Label = $HUD/MessagePanel/MessageLabel
@onready var screen_label: Label = $HUD/ScreenLabel
@onready var camera: Camera2D = $Player/Camera2D

var nearby_interactable: Node = null
var dialogue_queue: Array = []
var is_showing_dialogue: bool = false
var is_sniffari_active: bool = false

func _ready() -> void:
	charlie.set_player(player)
	charlie.equip_leash()
	player.set_charlie(charlie)
	if wildlife_spawner:
		wildlife_spawner.set_charlie(charlie)
		wildlife_spawner.set_player(player)
		charlie.set_wildlife_spawner(wildlife_spawner)
	player.interact_pressed.connect(_on_interact_pressed)
	charlie.sniffari_finished.connect(_on_sniffari_finished)
	TimeWeather.time_updated.connect(_on_time_updated)
	TimeWeather.weather_changed.connect(_on_weather_changed)
	_update_weather_display()
	_update_ambient_lighting()

	# Initialize screen position from GameState or defaults
	if GameState.current_screen != Vector2i(-1, -1):
		current_screen = GameState.current_screen
	if GameState.player_world_position != Vector2(-1, -1):
		player.global_position = GameState.player_world_position
		charlie.global_position = GameState.player_world_position + Vector2(30, 15)

	_update_camera_limits(current_screen, true)
	_update_screen_label()

	if not GameState.first_overworld_complete: _show_first_visit_welcome()

func _process(delta: float) -> void:
	if is_transitioning:
		return

	if is_sniffari_active: _process_sniffari_follow(delta)
	_update_leash_visual()
	_update_interaction_prompt()
	_update_ambient_lighting()
	_check_screen_boundary()

func _input(event: InputEvent) -> void:
	if is_transitioning:
		return
	if event is InputEventKey and event.pressed and event.keycode == KEY_F:
		if not is_sniffari_active and GameState.is_sniffari_available() and charlie.current_state != charlie.State.HELD:
			var charlie_dist = player.global_position.distance_to(charlie.global_position)
			if charlie_dist < 60: _start_sniffari()

func _check_screen_boundary() -> void:
	"""Check if player has crossed a screen boundary and trigger transition."""
	var pos = player.global_position
	var screen_left = current_screen.x * SCREEN_WIDTH
	var screen_right = (current_screen.x + 1) * SCREEN_WIDTH
	var screen_top = current_screen.y * SCREEN_HEIGHT
	var screen_bottom = (current_screen.y + 1) * SCREEN_HEIGHT

	var new_screen = current_screen
	var nudge = Vector2.ZERO

	# Check horizontal boundaries
	if pos.x < screen_left and current_screen.x > 0:
		new_screen.x -= 1
		nudge = Vector2(-20, 0)
		transition_direction = Vector2.LEFT
	elif pos.x > screen_right and current_screen.x < GRID_COLS - 1:
		new_screen.x += 1
		nudge = Vector2(20, 0)
		transition_direction = Vector2.RIGHT

	# Check vertical boundaries
	if pos.y < screen_top and current_screen.y > 0:
		new_screen.y -= 1
		nudge = Vector2(0, -20)
		transition_direction = Vector2.UP
	elif pos.y > screen_bottom and current_screen.y < GRID_ROWS - 1:
		new_screen.y += 1
		nudge = Vector2(0, 20)
		transition_direction = Vector2.DOWN

	# Clamp player to world bounds if at edge
	if new_screen == current_screen:
		if current_screen.x == 0:
			player.global_position.x = max(pos.x, 16)
		if current_screen.x == GRID_COLS - 1:
			player.global_position.x = min(pos.x, WORLD_WIDTH - 16)
		if current_screen.y == 0:
			player.global_position.y = max(pos.y, 16)
		if current_screen.y == GRID_ROWS - 1:
			player.global_position.y = min(pos.y, WORLD_HEIGHT - 16)
		return

	# Trigger transition
	_start_screen_transition(new_screen, nudge)

func _start_screen_transition(new_screen: Vector2i, nudge: Vector2) -> void:
	"""Begin a screen transition to the new screen."""
	is_transitioning = true

	# Freeze player and Charlie movement
	player.set_can_move(false)
	player.velocity = Vector2.ZERO
	charlie.set_physics_process(false)

	# Nudge player into new screen
	var target_pos = player.global_position + nudge

	# Create transition tween
	var tween = create_tween()
	tween.set_parallel(true)

	# Tween player position
	tween.tween_property(player, "global_position", target_pos, TRANSITION_DURATION).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)

	# Pull Charlie along
	var charlie_offset = charlie.global_position - player.global_position
	var charlie_target = target_pos + charlie_offset.normalized() * min(charlie_offset.length(), charlie.leash_max_distance * 0.8)
	tween.tween_property(charlie, "global_position", charlie_target, TRANSITION_DURATION).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)

	# Tween camera limits
	tween.set_parallel(false)
	tween.tween_callback(_update_camera_limits.bind(new_screen, false))
	tween.tween_interval(TRANSITION_DURATION * 0.5)
	tween.tween_callback(_finish_transition.bind(new_screen))

func _update_camera_limits(screen: Vector2i, instant: bool) -> void:
	"""Update camera limits to the specified screen."""
	var new_left = screen.x * SCREEN_WIDTH
	var new_right = (screen.x + 1) * SCREEN_WIDTH
	var new_top = screen.y * SCREEN_HEIGHT
	var new_bottom = (screen.y + 1) * SCREEN_HEIGHT

	if instant or not camera:
		camera.limit_left = new_left
		camera.limit_right = new_right
		camera.limit_top = new_top
		camera.limit_bottom = new_bottom
	else:
		# Smooth camera limit transition
		var tween = create_tween()
		tween.set_parallel(true)
		tween.tween_property(camera, "limit_left", new_left, TRANSITION_DURATION * 0.5)
		tween.tween_property(camera, "limit_right", new_right, TRANSITION_DURATION * 0.5)
		tween.tween_property(camera, "limit_top", new_top, TRANSITION_DURATION * 0.5)
		tween.tween_property(camera, "limit_bottom", new_bottom, TRANSITION_DURATION * 0.5)

func _finish_transition(new_screen: Vector2i) -> void:
	"""Complete the screen transition."""
	current_screen = new_screen
	is_transitioning = false
	transition_direction = Vector2.ZERO

	# Update GameState
	GameState.current_screen = current_screen
	GameState.player_world_position = player.global_position

	# Resume movement
	player.set_can_move(true)
	charlie.set_physics_process(true)

	# Update wildlife spawner bounds for new screen
	_update_wildlife_spawner_bounds()
	_update_screen_label()

func _update_wildlife_spawner_bounds() -> void:
	"""Update the wildlife spawner to use current screen bounds."""
	if wildlife_spawner:
		wildlife_spawner.spawn_min = Vector2(
			current_screen.x * SCREEN_WIDTH + 50,
			current_screen.y * SCREEN_HEIGHT + 50
		)
		wildlife_spawner.spawn_max = Vector2(
			(current_screen.x + 1) * SCREEN_WIDTH - 50,
			(current_screen.y + 1) * SCREEN_HEIGHT - 50
		)

func _update_screen_label() -> void:
	"""Update the screen position indicator."""
	if screen_label:
		# Get biome name for current screen
		var biome = _get_biome_name(current_screen)
		screen_label.text = "%s (%d, %d)" % [biome, current_screen.x, current_screen.y]

func _get_biome_name(screen: Vector2i) -> String:
	"""Get the biome name for a screen coordinate."""
	var biomes = [
		["Beach", "Meadow", "Meadow", "Forest", "Forest", "Mountain"],
		["Beach", "Home", "Meadow", "Forest", "Lake", "Mountain"],
		["Beach", "Meadow", "Path", "Path", "Lake", "Mountain"],
		["Cliffs", "Cliffs", "Bridge", "Path", "Forest", "Mountain"],
	]
	if screen.y >= 0 and screen.y < biomes.size() and screen.x >= 0 and screen.x < biomes[screen.y].size():
		return biomes[screen.y][screen.x]
	return "Unknown"

func _process_sniffari_follow(delta: float) -> void:
	var dist = player.global_position.distance_to(charlie.global_position)
	var leash_limit = charlie.leash_max_distance
	var ideal_dist = leash_limit * 0.4

	if dist > ideal_dist:
		var dir = (charlie.global_position - player.global_position).normalized()
		var t = clampf((dist - ideal_dist) / (leash_limit - ideal_dist), 0.0, 1.0)
		var target_vel = dir * charlie.speed * lerpf(1.2, 4.0, t)
		player.velocity = player.velocity.lerp(target_vel, delta * 15.0)
		player.move_and_slide()
		if player.has_method("_update_animation"):
			player._update_animation(player.velocity)
	else:
		player.velocity = player.velocity.lerp(Vector2.ZERO, delta * 15.0)
		player.move_and_slide()
		if player.has_method("_update_animation"):
			player._update_animation(player.velocity if player.velocity.length() > 5 else Vector2.ZERO)

func _update_leash_visual() -> void:
	if not leash_line: return
	if charlie.current_state == charlie.State.HELD:
		leash_line.visible = false
		return
	leash_line.visible = true
	leash_line.clear_points()
	var player_leash_point = player.global_position + player.get_leash_hand_offset()
	var charlie_leash_point = charlie.global_position + Vector2(0, -20)
	leash_line.add_point(player_leash_point)
	leash_line.add_point(charlie_leash_point)
	var excitement = charlie.get_wildlife_excitement() if charlie.has_method("get_wildlife_excitement") else 0.0
	var resistance = charlie.get_leash_resistance()
	if resistance > 0.1:
		var taut_color = Color(0.5, 0.25, 0.15, 1).lerp(Color(0.6, 0.2, 0.1, 1), resistance)
		if excitement > 0.2: taut_color = taut_color.lerp(Color(0.9, 0.5, 0.1, 1), excitement * 0.5)
		leash_line.default_color = taut_color
		leash_line.width = 2.0 + resistance
	elif excitement > 0.2:
		leash_line.default_color = Color(0.4, 0.3, 0.2, 1).lerp(Color(0.8, 0.5, 0.2, 1), excitement * 0.6)
		leash_line.width = 2.0
	else:
		leash_line.default_color = Color(0.4, 0.3, 0.2, 1)
		leash_line.width = 2.0

func _update_interaction_prompt() -> void:
	if is_showing_dialogue:
		interaction_prompt.text = "[E] Continue"
		interaction_prompt.visible = true
		return
	if is_sniffari_active:
		interaction_prompt.text = "Sniffari! Charlie is exploring..."
		interaction_prompt.visible = true
		return

	var player_pos = player.global_position
	nearby_interactable = null

	var charlie_dist = player_pos.distance_to(charlie.global_position)
	var house_dist = player_pos.distance_to(house.global_position + Vector2(0, 40))

	# Priority 1: Charlie Interactions
	if charlie_dist < 50 and charlie.current_state != charlie.State.HELD:
		var prompts = []
		prompts.append("[E] Pick up Charlie")

		if GameState.is_sniffari_available():
			prompts.append("[F] Start Sniffari!")

		interaction_prompt.text = " | ".join(prompts)
		interaction_prompt.visible = true
		nearby_interactable = charlie
		return

	# Priority 2: House Interaction (only on home screen)
	if current_screen == Vector2i(1, 1) and house_dist < 50:
		interaction_prompt.text = "[E] Enter House"
		interaction_prompt.visible = true
		nearby_interactable = house
		return

	interaction_prompt.visible = false

func _start_sniffari() -> void:
	is_sniffari_active = true
	player.set_can_move(false)
	charlie.start_sniffari()
	GameState.record_sniffari()
	hud.show_message("Charlie is taking you on a Sniffari!", 3.0)

func _on_sniffari_finished() -> void:
	is_sniffari_active = false
	player.set_can_move(true)
	hud.show_message("Sniffari complete! You feel closer to Charlie.", 3.0)

func _on_interact_pressed() -> void:
	if is_transitioning: return
	if is_showing_dialogue: _advance_dialogue(); return
	if nearby_interactable == charlie: charlie.interact(player)
	elif nearby_interactable == house: _enter_house()

func _enter_house() -> void:
	GameState.player_world_position = player.global_position
	GameState.current_screen = current_screen
	GameState.save_game()
	get_tree().change_scene_to_file("res://scenes/House.tscn")

func _on_time_updated(_hour: float) -> void: _update_ambient_lighting()
func _on_weather_changed(_weather) -> void: _update_weather_display()
func _update_weather_display() -> void: if weather_label: weather_label.text = "%s - %s" % [TimeWeather.get_weather_string(), TimeWeather.get_season_string()]
func _update_ambient_lighting() -> void: if ambient_light: ambient_light.color = TimeWeather.current_ambient

func _show_first_visit_welcome() -> void:
	GameState.bonding = 0.0; GameState.emit_signal("stats_changed")
	dialogue_queue = [
		"Welcome to the island, Charlie!",
		"This is your new home. Feel free to explore!",
		"The island is big - walk to the edge of the screen to explore more areas!",
		"Every 3 hours, you can go on a Sniffari!",
		"Press [F] near Charlie to let him lead the way.",
		"You'll gain bonding while he explores!"
	]
	_show_next_dialogue()

func _show_next_dialogue() -> void:
	if dialogue_queue.size() > 0:
		message_label.text = dialogue_queue.pop_front(); message_panel.visible = true; is_showing_dialogue = true; player.set_can_move(false)
	else: message_panel.visible = false; is_showing_dialogue = false; player.set_can_move(true); _on_dialogue_finished()

func _advance_dialogue() -> void: _show_next_dialogue()

func _on_dialogue_finished() -> void:
	if not GameState.first_overworld_complete:
		GameState.first_overworld_complete = true; TimeWeather.start_time_for_overworld(); GameState.save_game()
