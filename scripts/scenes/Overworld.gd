extends Node2D
## Overworld - Phase 2: Outdoor exploration with Charlie on leash

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
	if not GameState.first_overworld_complete: _show_first_visit_welcome()

func _process(delta: float) -> void:
	if is_sniffari_active: _process_sniffari_follow(delta)
	_update_leash_visual()
	_update_interaction_prompt()
	_update_ambient_lighting()

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_F:
		if not is_sniffari_active and GameState.is_sniffari_available() and charlie.current_state != charlie.State.HELD:
			var charlie_dist = player.global_position.distance_to(charlie.global_position)
			if charlie_dist < 60: _start_sniffari()

func _process_sniffari_follow(delta: float) -> void:
	var dist = player.global_position.distance_to(charlie.global_position)
	var leash_limit = charlie.leash_max_distance
	var ideal_dist = leash_limit * 0.4
	
	if dist > ideal_dist:
		var dir = (charlie.global_position - player.global_position).normalized()
		
		# Speed up more aggressively as we approach the leash limit
		# t represents how close we are to the limit (0 at ideal_dist, 1 at leash_limit)
		var t = clampf((dist - ideal_dist) / (leash_limit - ideal_dist), 0.0, 1.0)
		
		# Base speed is at least Charlie's max speed, mult scales up to 4x to ensure we catch up
		var target_vel = dir * charlie.speed * lerpf(1.2, 4.0, t)
		
		# Instant responsiveness (higher lerp weight) to prevent lag
		player.velocity = player.velocity.lerp(target_vel, delta * 15.0)
		player.move_and_slide()
		
		# Ensure animation reflects actual movement
		if player.has_method("_update_animation"): 
			player._update_animation(player.velocity)
	else:
		# Close enough, slow to stop
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
		
	# Priority 2: House Interaction
	if house_dist < 50:
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
	if is_showing_dialogue: _advance_dialogue(); return
	if nearby_interactable == charlie: charlie.interact(player)
	elif nearby_interactable == house: _enter_house()

func _enter_house() -> void: GameState.save_game(); get_tree().change_scene_to_file("res://scenes/House.tscn")
func _on_time_updated(_hour: float) -> void: _update_ambient_lighting()
func _on_weather_changed(_weather) -> void: _update_weather_display()
func _update_weather_display() -> void: if weather_label: weather_label.text = "%s - %s" % [TimeWeather.get_weather_string(), TimeWeather.get_season_string()]
func _update_ambient_lighting() -> void: if ambient_light: ambient_light.color = TimeWeather.current_ambient
func _show_first_visit_welcome() -> void:
	GameState.bonding = 0.0; GameState.emit_signal("stats_changed")
	dialogue_queue = ["Welcome to the island, Charlie!", "This is your new home. Feel free to explore!", "Every 3 hours, you can go on a Sniffari!", "Press [F] near Charlie to let him lead the way.", "You'll gain bonding while he explores!"]
	_show_next_dialogue()
func _show_next_dialogue() -> void:
	if dialogue_queue.size() > 0:
		message_label.text = dialogue_queue.pop_front(); message_panel.visible = true; is_showing_dialogue = true; player.set_can_move(false)
	else: message_panel.visible = false; is_showing_dialogue = false; player.set_can_move(true); _on_dialogue_finished()
func _advance_dialogue() -> void: _show_next_dialogue()
func _on_dialogue_finished() -> void:
	if not GameState.first_overworld_complete:
		GameState.first_overworld_complete = true; TimeWeather.start_time_for_overworld(); GameState.save_game()