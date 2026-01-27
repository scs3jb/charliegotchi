extends CanvasLayer
## DebugMenu - Toggle with F3 to modify Charlie's stats

var panel: Panel
var bonding_slider: HSlider
var entertainment_slider: HSlider
var hunger_slider: HSlider
var bonding_label: Label
var entertainment_label: Label
var hunger_label: Label
var time_label: Label

var is_visible: bool = false

func _ready() -> void:
	layer = 100  # Render on top of everything
	_create_ui()
	panel.visible = false
	print("DebugMenu initialized (F3 to toggle)")

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_F3:
		_toggle_menu()

func _process(_delta: float) -> void:
	if is_visible:
		_update_labels()

func _toggle_menu() -> void:
	is_visible = not is_visible
	panel.visible = is_visible
	if is_visible:
		_sync_sliders_to_stats()

func _create_ui() -> void:
	# Main panel
	panel = Panel.new()
	panel.custom_minimum_size = Vector2(250, 280)
	panel.position = Vector2(10, 10)
	add_child(panel)

	var vbox = VBoxContainer.new()
	vbox.position = Vector2(10, 10)
	vbox.custom_minimum_size = Vector2(230, 260)
	panel.add_child(vbox)

	# Title
	var title = Label.new()
	title.text = "Debug Menu (F3)"
	title.add_theme_font_size_override("font_size", 14)
	vbox.add_child(title)

	# Separator
	var sep1 = HSeparator.new()
	vbox.add_child(sep1)

	# Time display
	time_label = Label.new()
	time_label.text = "Day 1 - 8:00 AM"
	time_label.add_theme_font_size_override("font_size", 11)
	vbox.add_child(time_label)

	# Time controls
	var time_hbox = HBoxContainer.new()
	vbox.add_child(time_hbox)

	var skip_hour_btn = Button.new()
	skip_hour_btn.text = "+1 Hour"
	skip_hour_btn.pressed.connect(_on_skip_hour)
	time_hbox.add_child(skip_hour_btn)

	var skip_day_btn = Button.new()
	skip_day_btn.text = "+1 Day"
	skip_day_btn.pressed.connect(_on_skip_day)
	time_hbox.add_child(skip_day_btn)

	# Separator
	var sep2 = HSeparator.new()
	vbox.add_child(sep2)

	# Bonding
	bonding_label = Label.new()
	bonding_label.text = "Bonding: 0%"
	bonding_label.add_theme_font_size_override("font_size", 11)
	vbox.add_child(bonding_label)

	bonding_slider = HSlider.new()
	bonding_slider.min_value = 0.0
	bonding_slider.max_value = 1.0
	bonding_slider.step = 0.01
	bonding_slider.custom_minimum_size = Vector2(200, 20)
	bonding_slider.value_changed.connect(_on_bonding_changed)
	vbox.add_child(bonding_slider)

	# Entertainment
	entertainment_label = Label.new()
	entertainment_label.text = "Entertainment: 0%"
	entertainment_label.add_theme_font_size_override("font_size", 11)
	vbox.add_child(entertainment_label)

	entertainment_slider = HSlider.new()
	entertainment_slider.min_value = 0.0
	entertainment_slider.max_value = 1.0
	entertainment_slider.step = 0.01
	entertainment_slider.custom_minimum_size = Vector2(200, 20)
	entertainment_slider.value_changed.connect(_on_entertainment_changed)
	vbox.add_child(entertainment_slider)

	# Hunger
	hunger_label = Label.new()
	hunger_label.text = "Hunger: 100%"
	hunger_label.add_theme_font_size_override("font_size", 11)
	vbox.add_child(hunger_label)

	hunger_slider = HSlider.new()
	hunger_slider.min_value = 0.0
	hunger_slider.max_value = 1.0
	hunger_slider.step = 0.01
	hunger_slider.custom_minimum_size = Vector2(200, 20)
	hunger_slider.value_changed.connect(_on_hunger_changed)
	vbox.add_child(hunger_slider)

	# Separator
	var sep3 = HSeparator.new()
	vbox.add_child(sep3)

	# Quick set buttons
	var btn_hbox = HBoxContainer.new()
	vbox.add_child(btn_hbox)

	var fill_btn = Button.new()
	fill_btn.text = "Fill All"
	fill_btn.pressed.connect(_on_fill_all)
	btn_hbox.add_child(fill_btn)

	var empty_btn = Button.new()
	empty_btn.text = "Empty All"
	empty_btn.pressed.connect(_on_empty_all)
	btn_hbox.add_child(empty_btn)

	# Close button
	var close_btn = Button.new()
	close_btn.text = "Close (F3)"
	close_btn.pressed.connect(_toggle_menu)
	vbox.add_child(close_btn)

func _sync_sliders_to_stats() -> void:
	bonding_slider.value = GameState.bonding
	entertainment_slider.value = GameState.entertainment
	hunger_slider.value = GameState.hunger

func _update_labels() -> void:
	bonding_label.text = "Bonding: %d%%" % int(GameState.bonding * 100)
	entertainment_label.text = "Entertainment: %d%%" % int(GameState.entertainment * 100)
	hunger_label.text = "Hunger: %d%%" % int(GameState.hunger * 100)
	time_label.text = "Day %d - %s" % [GameState.current_day, TimeWeather.get_time_string()]

func _on_bonding_changed(value: float) -> void:
	GameState.bonding = value
	GameState.emit_signal("stats_changed")

func _on_entertainment_changed(value: float) -> void:
	GameState.entertainment = value
	GameState.emit_signal("stats_changed")

func _on_hunger_changed(value: float) -> void:
	GameState.hunger = value
	GameState.emit_signal("stats_changed")

func _on_fill_all() -> void:
	GameState.bonding = 1.0
	GameState.entertainment = 1.0
	GameState.hunger = 1.0
	_sync_sliders_to_stats()
	GameState.emit_signal("stats_changed")

func _on_empty_all() -> void:
	GameState.bonding = 0.0
	GameState.entertainment = 0.0
	GameState.hunger = 0.0
	_sync_sliders_to_stats()
	GameState.emit_signal("stats_changed")

func _on_skip_hour() -> void:
	GameState.current_hour += 1.0
	if GameState.current_hour >= 24.0:
		GameState.current_hour -= 24.0
		GameState.current_day += 1

func _on_skip_day() -> void:
	GameState.current_day += 1
