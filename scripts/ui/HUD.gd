extends CanvasLayer
## HUD - Displays stats, time, and contextual UI

@onready var bonding_bar: ProgressBar = $MarginContainer/VBoxContainer/BondingBar
@onready var entertainment_bar: ProgressBar = $MarginContainer/VBoxContainer/EntertainmentBar
@onready var time_label: Label = $MarginContainer/VBoxContainer/TimeLabel
@onready var interaction_prompt: Label = $InteractionPrompt
@onready var message_panel: Panel = $MessagePanel
@onready var message_label: Label = $MessagePanel/MessageLabel

var message_timer: float = 0.0

func _ready() -> void:
	GameState.stats_changed.connect(_on_stats_changed)
	GameState.charlie_trust_unlocked.connect(_on_trust_unlocked)
	TimeWeather.time_updated.connect(_on_time_updated)

	_update_stats_display()
	hide_interaction_prompt()
	hide_message()

func _process(delta: float) -> void:
	if message_timer > 0:
		message_timer -= delta
		if message_timer <= 0:
			hide_message()

func _on_stats_changed() -> void:
	_update_stats_display()

func _update_stats_display() -> void:
	if bonding_bar:
		bonding_bar.value = GameState.bonding * 100
	if entertainment_bar:
		entertainment_bar.value = GameState.entertainment * 100

func _on_time_updated(_hour: float) -> void:
	if time_label:
		time_label.text = TimeWeather.get_time_string()

func _on_trust_unlocked() -> void:
	show_message("Charlie now trusts you enough to explore outside!", 5.0)

func show_interaction_prompt(text: String) -> void:
	if interaction_prompt:
		interaction_prompt.text = text
		interaction_prompt.visible = true

func hide_interaction_prompt() -> void:
	if interaction_prompt:
		interaction_prompt.visible = false

func show_message(text: String, duration: float = 3.0) -> void:
	if message_panel and message_label:
		message_label.text = text
		message_panel.visible = true
		message_timer = duration

func hide_message() -> void:
	if message_panel:
		message_panel.visible = false

func set_stats_visible(visible: bool) -> void:
	if bonding_bar:
		bonding_bar.get_parent().visible = visible
