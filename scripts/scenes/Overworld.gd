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

var nearby_interactable: Node = null

func _ready() -> void:
	# Set up Charlie with leash
	charlie.set_player(player)
	charlie.equip_leash()

	# Connect signals
	player.interact_pressed.connect(_on_interact_pressed)
	TimeWeather.time_updated.connect(_on_time_updated)
	TimeWeather.weather_changed.connect(_on_weather_changed)

	# Resume time if paused
	TimeWeather.resume_time()

	# Initial update
	_update_weather_display()
	_update_ambient_lighting()

func _process(_delta: float) -> void:
	_update_leash_visual()
	_update_interaction_prompt()
	_update_ambient_lighting()

func _update_leash_visual() -> void:
	if not leash_line:
		return

	# Draw line from player to Charlie
	leash_line.clear_points()
	leash_line.add_point(player.global_position + Vector2(0, 10))
	leash_line.add_point(charlie.global_position + Vector2(0, -5))

func _update_interaction_prompt() -> void:
	var player_pos = player.global_position
	nearby_interactable = null

	# Check distance to house door
	var dist = player_pos.distance_to(house.global_position + Vector2(0, 40))
	if dist < 50:
		interaction_prompt.text = "[E] Enter House"
		interaction_prompt.visible = true
		nearby_interactable = house
	else:
		interaction_prompt.visible = false

func _on_interact_pressed() -> void:
	if nearby_interactable == house:
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
