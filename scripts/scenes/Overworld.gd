extends Node2D
## Overworld - Phase 2: Outdoor exploration with Charlie on leash

@onready var player: CharacterBody2D = $Player
@onready var charlie: CharacterBody2D = $Charlie
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

func _ready() -> void:
	# Set up Charlie with leash
	charlie.set_player(player)
	charlie.equip_leash()

	# Give player reference to Charlie for leash mechanics
	player.set_charlie(charlie)

	# Set up wildlife spawner
	if wildlife_spawner:
		wildlife_spawner.set_charlie(charlie)
		wildlife_spawner.set_player(player)
		charlie.set_wildlife_spawner(wildlife_spawner)

	# Connect signals
	player.interact_pressed.connect(_on_interact_pressed)
	TimeWeather.time_updated.connect(_on_time_updated)
	TimeWeather.weather_changed.connect(_on_weather_changed)

	# Initial update
	_update_weather_display()
	_update_ambient_lighting()

	# First time visiting the overworld - show welcome message
	if not GameState.first_overworld_complete:
		_show_first_visit_welcome()

func _process(_delta: float) -> void:
	_update_leash_visual()
	_update_interaction_prompt()
	_update_ambient_lighting()

func _update_leash_visual() -> void:
	if not leash_line:
		return

	# Hide leash if Charlie is being held
	if charlie.current_state == charlie.State.HELD:
		leash_line.visible = false
		return
	else:
		leash_line.visible = true

	# Draw line from player's hand to Charlie's collar
	leash_line.clear_points()

	# Get player's hand position based on facing direction
	var hand_offset = player.get_leash_hand_offset()
	var player_leash_point = player.global_position + hand_offset

	# Charlie's collar position (neck area, below head)
	var charlie_leash_point = charlie.global_position + Vector2(0, -2)

	leash_line.add_point(player_leash_point)
	leash_line.add_point(charlie_leash_point)

	# Get excitement level for wildlife
	var excitement = charlie.get_wildlife_excitement() if charlie.has_method("get_wildlife_excitement") else 0.0

	# Change leash color and width based on resistance and excitement
	var resistance = charlie.get_leash_resistance()
	if resistance > 0.1:
		# Taut/stressed - darker color, scales with resistance
		var taut_color = Color(0.5, 0.25, 0.15, 1).lerp(Color(0.6, 0.2, 0.1, 1), resistance)
		# Add orange tint when excited about wildlife
		if excitement > 0.2:
			var excited_color = Color(0.9, 0.5, 0.1, 1)  # Orange
			taut_color = taut_color.lerp(excited_color, excitement * 0.5)
		leash_line.default_color = taut_color
		leash_line.width = 2.0 + resistance  # Slightly thicker when taut
	elif excitement > 0.2:
		# Not taut but excited - show orange tint
		var normal_color = Color(0.4, 0.3, 0.2, 1)
		var excited_color = Color(0.8, 0.5, 0.2, 1)  # Light orange
		leash_line.default_color = normal_color.lerp(excited_color, excitement * 0.6)
		leash_line.width = 2.0
	else:
		leash_line.default_color = Color(0.4, 0.3, 0.2, 1)  # Normal color
		leash_line.width = 2.0

func _update_interaction_prompt() -> void:
	# Show continue prompt during dialogue
	if is_showing_dialogue:
		interaction_prompt.text = "[E] Continue"
		interaction_prompt.visible = true
		return

	var player_pos = player.global_position
	nearby_interactable = null

	# Check distance to house door first (priority over petting)
	var house_dist = player_pos.distance_to(house.global_position + Vector2(0, 40))
	if house_dist < 50:
		interaction_prompt.text = "[E] Enter House"
		interaction_prompt.visible = true
		nearby_interactable = house
		return

	# Check distance to Charlie (pickup)
	var charlie_dist = player_pos.distance_to(charlie.global_position)
	if charlie_dist < 40 and charlie.current_state != charlie.State.HELD:
		interaction_prompt.text = "[E] Pick up Charlie"
		interaction_prompt.visible = true
		nearby_interactable = charlie
		return

	interaction_prompt.visible = false

func _on_interact_pressed() -> void:
	# Handle dialogue advancement first
	if is_showing_dialogue:
		_advance_dialogue()
		return

	if nearby_interactable == charlie:
		charlie.interact(player)
	elif nearby_interactable == house:
		_enter_house()

func _enter_house() -> void:
	GameState.save_game()
	get_tree().change_scene_to_file("res://scenes/House.tscn")

func _on_time_updated(_hour: float) -> void:
	_update_ambient_lighting()

func _on_weather_changed(_weather) -> void:
	_update_weather_display()

func _update_weather_display() -> void:
	if weather_label:
		weather_label.text = "%s - %s" % [TimeWeather.get_weather_string(), TimeWeather.get_season_string()]

func _update_ambient_lighting() -> void:
	if ambient_light:
		ambient_light.color = TimeWeather.current_ambient

func _show_first_visit_welcome() -> void:
	# Reset bonding to 0 for first outdoor adventure
	GameState.bonding = 0.0
	GameState.emit_signal("stats_changed")

	# Show welcome dialogue
	dialogue_queue = [
		"Welcome to the island, Charlie!",
		"This is your new home. Feel free to explore!",
		"Charlie is still getting used to you...",
		"He might get distracted by birds and squirrels.",
		"Spend time with Charlie to increase your bond.",
		"The stronger your bond, the less distracted he'll be!"
	]
	_show_next_dialogue()

func _show_next_dialogue() -> void:
	if dialogue_queue.size() > 0:
		message_label.text = dialogue_queue.pop_front()
		message_panel.visible = true
		is_showing_dialogue = true
		player.set_can_move(false)
	else:
		message_panel.visible = false
		is_showing_dialogue = false
		player.set_can_move(true)
		_on_dialogue_finished()

func _advance_dialogue() -> void:
	_show_next_dialogue()

func _on_dialogue_finished() -> void:
	# Mark first overworld visit as complete
	if not GameState.first_overworld_complete:
		GameState.first_overworld_complete = true
		TimeWeather.start_time_for_overworld()
		GameState.save_game()
