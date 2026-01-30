extends CanvasLayer
## DebugMenu - Toggle with F3 to modify Charlie's stats

const Butterfly = preload("res://scripts/wildlife/Butterfly.gd")
const Bird = preload("res://scripts/wildlife/Bird.gd")
const Squirrel = preload("res://scripts/wildlife/Squirrel.gd")

var panel: Panel
var bonding_slider: HSlider
var entertainment_slider: HSlider
var hunger_slider: HSlider
var bonding_label: Label
var entertainment_label: Label
var hunger_label: Label
var time_label: Label
var leash_label: Label
var wildlife_label: Label

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
	# Main panel - compact size
	panel = Panel.new()
	panel.custom_minimum_size = Vector2(130, 195)
	panel.position = Vector2(5, 5)
	add_child(panel)

	var vbox = VBoxContainer.new()
	vbox.position = Vector2(4, 4)
	vbox.custom_minimum_size = Vector2(122, 187)
	vbox.add_theme_constant_override("separation", 1)
	panel.add_child(vbox)

	# Title + Close button row
	var title_hbox = HBoxContainer.new()
	vbox.add_child(title_hbox)
	var title = Label.new()
	title.text = "F3 Debug"
	title.add_theme_font_size_override("font_size", 8)
	title_hbox.add_child(title)
	title_hbox.add_spacer(false)
	var close_btn = Button.new()
	close_btn.text = "X"
	close_btn.custom_minimum_size = Vector2(18, 14)
	close_btn.add_theme_font_size_override("font_size", 7)
	close_btn.pressed.connect(_toggle_menu)
	title_hbox.add_child(close_btn)

	# Time row: label + buttons
	var time_hbox = HBoxContainer.new()
	vbox.add_child(time_hbox)
	time_label = Label.new()
	time_label.text = "D1 8:00"
	time_label.add_theme_font_size_override("font_size", 7)
	time_hbox.add_child(time_label)
	time_hbox.add_spacer(false)
	var skip_hour_btn = Button.new()
	skip_hour_btn.text = "+1h"
	skip_hour_btn.custom_minimum_size = Vector2(28, 14)
	skip_hour_btn.add_theme_font_size_override("font_size", 7)
	skip_hour_btn.pressed.connect(_on_skip_hour)
	time_hbox.add_child(skip_hour_btn)
	var skip_day_btn = Button.new()
	skip_day_btn.text = "+1d"
	skip_day_btn.custom_minimum_size = Vector2(28, 14)
	skip_day_btn.add_theme_font_size_override("font_size", 7)
	skip_day_btn.pressed.connect(_on_skip_day)
	time_hbox.add_child(skip_day_btn)

	# Bonding row
	var bond_hbox = HBoxContainer.new()
	vbox.add_child(bond_hbox)
	bonding_label = Label.new()
	bonding_label.text = "Bnd 0%"
	bonding_label.custom_minimum_size = Vector2(40, 0)
	bonding_label.add_theme_font_size_override("font_size", 7)
	bond_hbox.add_child(bonding_label)
	bonding_slider = HSlider.new()
	bonding_slider.min_value = 0.0
	bonding_slider.max_value = 1.0
	bonding_slider.step = 0.05
	bonding_slider.custom_minimum_size = Vector2(75, 10)
	bonding_slider.value_changed.connect(_on_bonding_changed)
	bond_hbox.add_child(bonding_slider)

	# Entertainment row
	var ent_hbox = HBoxContainer.new()
	vbox.add_child(ent_hbox)
	entertainment_label = Label.new()
	entertainment_label.text = "Ent 0%"
	entertainment_label.custom_minimum_size = Vector2(40, 0)
	entertainment_label.add_theme_font_size_override("font_size", 7)
	ent_hbox.add_child(entertainment_label)
	entertainment_slider = HSlider.new()
	entertainment_slider.min_value = 0.0
	entertainment_slider.max_value = 1.0
	entertainment_slider.step = 0.05
	entertainment_slider.custom_minimum_size = Vector2(75, 10)
	entertainment_slider.value_changed.connect(_on_entertainment_changed)
	ent_hbox.add_child(entertainment_slider)

	# Hunger row
	var hunger_hbox = HBoxContainer.new()
	vbox.add_child(hunger_hbox)
	hunger_label = Label.new()
	hunger_label.text = "Hun 100%"
	hunger_label.custom_minimum_size = Vector2(40, 0)
	hunger_label.add_theme_font_size_override("font_size", 7)
	hunger_hbox.add_child(hunger_label)
	hunger_slider = HSlider.new()
	hunger_slider.min_value = 0.0
	hunger_slider.max_value = 1.0
	hunger_slider.step = 0.05
	hunger_slider.custom_minimum_size = Vector2(75, 10)
	hunger_slider.value_changed.connect(_on_hunger_changed)
	hunger_hbox.add_child(hunger_slider)

	# Fill/Empty buttons
	var btn_hbox = HBoxContainer.new()
	vbox.add_child(btn_hbox)
	var fill_btn = Button.new()
	fill_btn.text = "Fill All"
	fill_btn.custom_minimum_size = Vector2(55, 16)
	fill_btn.add_theme_font_size_override("font_size", 7)
	fill_btn.pressed.connect(_on_fill_all)
	btn_hbox.add_child(fill_btn)
	var empty_btn = Button.new()
	empty_btn.text = "Empty All"
	empty_btn.custom_minimum_size = Vector2(55, 16)
	empty_btn.add_theme_font_size_override("font_size", 7)
	empty_btn.pressed.connect(_on_empty_all)
	btn_hbox.add_child(empty_btn)

	# Wildlife spawn buttons
	var wildlife_hbox = HBoxContainer.new()
	vbox.add_child(wildlife_hbox)
	var spawn_label = Label.new()
	spawn_label.text = "Spawn:"
	spawn_label.add_theme_font_size_override("font_size", 7)
	wildlife_hbox.add_child(spawn_label)
	var butterfly_btn = Button.new()
	butterfly_btn.text = "Bfly"
	butterfly_btn.custom_minimum_size = Vector2(28, 14)
	butterfly_btn.add_theme_font_size_override("font_size", 7)
	butterfly_btn.pressed.connect(_on_spawn_butterfly)
	wildlife_hbox.add_child(butterfly_btn)
	var bird_btn = Button.new()
	bird_btn.text = "Bird"
	bird_btn.custom_minimum_size = Vector2(28, 14)
	bird_btn.add_theme_font_size_override("font_size", 7)
	bird_btn.pressed.connect(_on_spawn_bird)
	wildlife_hbox.add_child(bird_btn)
	var squirrel_btn = Button.new()
	squirrel_btn.text = "Sqrl"
	squirrel_btn.custom_minimum_size = Vector2(28, 14)
	squirrel_btn.add_theme_font_size_override("font_size", 7)
	squirrel_btn.pressed.connect(_on_spawn_squirrel)
	wildlife_hbox.add_child(squirrel_btn)

	# Leash/Wildlife info (combined)
	leash_label = Label.new()
	leash_label.text = "Leash: --"
	leash_label.add_theme_font_size_override("font_size", 7)
	vbox.add_child(leash_label)

	wildlife_label = Label.new()
	wildlife_label.text = "Excite: --"
	wildlife_label.add_theme_font_size_override("font_size", 7)
	vbox.add_child(wildlife_label)

func _sync_sliders_to_stats() -> void:
	bonding_slider.value = GameState.bonding
	entertainment_slider.value = GameState.entertainment
	hunger_slider.value = GameState.hunger

func _update_labels() -> void:
	bonding_label.text = "Bnd %d%%" % int(GameState.bonding * 100)
	entertainment_label.text = "Ent %d%%" % int(GameState.entertainment * 100)
	hunger_label.text = "Hun %d%%" % int(GameState.hunger * 100)
	time_label.text = "D%d %s" % [GameState.current_day, TimeWeather.get_time_string()]

	# Update leash debug info if Charlie exists in scene
	var charlie = get_tree().get_first_node_in_group("charlie")
	var player = get_tree().get_first_node_in_group("player")
	if charlie and player:
		if charlie.is_on_leash:
			var distance = charlie.global_position.distance_to(player.global_position)
			var tension = distance / charlie.leash_max_distance * 100
			var resistance = charlie.get_leash_resistance() * 100
			leash_label.text = "Leash: %dT %dR" % [int(tension), int(resistance)]
		elif charlie.current_state == charlie.State.HELD:
			leash_label.text = "State: Held"
		else:
			leash_label.text = "Leash: off"

		# Update wildlife excitement
		if charlie.has_method("get_wildlife_excitement"):
			var excitement = charlie.get_wildlife_excitement() * 100
			if excitement > 1:
				wildlife_label.text = "Excite: %d%%" % int(excitement)
			else:
				wildlife_label.text = "Excite: --"
		else:
			wildlife_label.text = "Excite: --"
	else:
		leash_label.text = "Leash: --"
		wildlife_label.text = "Excite: --"

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

func _on_spawn_butterfly() -> void:
	_spawn_wildlife("butterfly")

func _on_spawn_bird() -> void:
	_spawn_wildlife("bird")

func _on_spawn_squirrel() -> void:
	_spawn_wildlife("squirrel")

func _spawn_wildlife(wildlife_type: String) -> void:
	var player = get_tree().get_first_node_in_group("player")
	var charlie = get_tree().get_first_node_in_group("charlie")

	if not player:
		print("Debug: No player found to spawn wildlife near")
		return

	# Create the wildlife
	var wildlife: CharacterBody2D = CharacterBody2D.new()

	match wildlife_type:
		"butterfly":
			wildlife.set_script(Butterfly)
		"bird":
			wildlife.set_script(Bird)
		"squirrel":
			wildlife.set_script(Squirrel)

	# Spawn 80 pixels away from player in a random direction
	var spawn_offset = Vector2(80, 0).rotated(randf() * TAU)
	wildlife.global_position = player.global_position + spawn_offset

	# Give it a reference to Charlie
	if charlie:
		wildlife.set_charlie(charlie)

	# Add to the scene - prefer adding to WildlifeSpawner if it exists
	var spawner = get_tree().get_first_node_in_group("wildlife_spawner")
	if not spawner:
		# Try to find it by name in the current scene
		var root = get_tree().current_scene
		if root:
			spawner = root.get_node_or_null("WildlifeSpawner")

	if spawner:
		spawner.add_child(wildlife)
		# Register with spawner's tracking if possible
		if spawner.has_method("get_active_wildlife_count"):
			spawner.active_wildlife.append(wildlife)
	elif get_tree().current_scene:
		get_tree().current_scene.add_child(wildlife)
	else:
		wildlife.queue_free()
		print("Debug: No valid scene to spawn wildlife in")
		return

	print("Debug: Spawned %s near player at %s" % [wildlife_type, wildlife.global_position])
