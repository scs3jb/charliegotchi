extends Node2D
## FeedingMinigame - Match-3 feeding minigame scene controller
## Handles rendering, input, animations, tutorial, and results.

const MatchBoardScript = preload("res://scripts/minigames/MatchBoard.gd")
const FOOD_TILES_TEX = preload("res://assets/sprites/ui/food_tiles.png")

# Tile names for legend display
const TILE_NAMES: Array = ["Kibble", "Salmon", "Veggie", "Carrot", "Berry", "Chicken!", "Mushroom!"]
const ALLERGEN_INDICES: Array = [5, 6]  # Chicken, Mushroom

const TILE_SIZE: int = 28
const TILE_GAP: int = 2
const TILE_STEP: int = 30  # TILE_SIZE + TILE_GAP
const BOARD_ORIGIN: Vector2 = Vector2(95, 16)

var board: RefCounted  # MatchBoard instance
var tile_nodes: Dictionary = {}  # Vector2i -> TextureRect
var selected_tile: Vector2i = Vector2i(-1, -1)
var is_animating: bool = false
var game_started: bool = false
var game_ended: bool = false

# UI references
var board_container: Node2D
var bowl_bar: ProgressBar
var moves_label: Label
var charlie_portrait: ColorRect
var reaction_label: Label
var exit_button: Button
var confirm_panel: Panel
var tutorial_overlay: ColorRect
var tutorial_panel: Panel
var tutorial_page: int = 0
var results_overlay: ColorRect
var results_panel: Panel
var bg_rect: ColorRect

func _ready() -> void:
	board = MatchBoardScript.new()
	_build_ui()

	if GameState.has_seen_feeding_tutorial:
		_start_game()
	else:
		_show_tutorial()

func _build_ui() -> void:
	# Background
	bg_rect = ColorRect.new()
	bg_rect.color = Color(0.18, 0.22, 0.18)
	bg_rect.position = Vector2.ZERO
	bg_rect.size = Vector2(426, 240)
	add_child(bg_rect)

	# Board container
	board_container = Node2D.new()
	board_container.position = BOARD_ORIGIN
	add_child(board_container)

	# Charlie portrait area (left side)
	charlie_portrait = ColorRect.new()
	charlie_portrait.color = Color(0.8, 0.7, 0.55)
	charlie_portrait.position = Vector2(10, 30)
	charlie_portrait.size = Vector2(40, 40)
	add_child(charlie_portrait)

	var charlie_label = Label.new()
	charlie_label.text = "Charlie"
	charlie_label.position = Vector2(10, 12)
	charlie_label.add_theme_font_size_override("font_size", 10)
	add_child(charlie_label)

	reaction_label = Label.new()
	reaction_label.text = ""
	reaction_label.position = Vector2(10, 78)
	reaction_label.add_theme_font_size_override("font_size", 12)
	reaction_label.add_theme_color_override("font_color", Color.RED)
	add_child(reaction_label)

	# Right side UI
	var right_x = 320

	var bowl_label = Label.new()
	bowl_label.text = "Bowl"
	bowl_label.position = Vector2(right_x, 8)
	bowl_label.add_theme_font_size_override("font_size", 10)
	add_child(bowl_label)

	bowl_bar = ProgressBar.new()
	bowl_bar.position = Vector2(right_x, 24)
	bowl_bar.size = Vector2(90, 16)
	bowl_bar.min_value = 0.0
	bowl_bar.max_value = 1.0
	bowl_bar.value = 0.0
	bowl_bar.show_percentage = false
	add_child(bowl_bar)

	moves_label = Label.new()
	moves_label.text = "Moves: 20"
	moves_label.position = Vector2(right_x, 48)
	moves_label.add_theme_font_size_override("font_size", 12)
	add_child(moves_label)

	# Tile type legend with food sprites
	var legend_y = 80
	for i in TILE_NAMES.size():
		var swatch = TextureRect.new()
		swatch.texture = _make_tile_atlas(i)
		swatch.position = Vector2(right_x, legend_y)
		swatch.size = Vector2(14, 14)
		swatch.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		add_child(swatch)
		var lbl = Label.new()
		lbl.text = TILE_NAMES[i]
		lbl.position = Vector2(right_x + 18, legend_y)
		lbl.add_theme_font_size_override("font_size", 8)
		if i in ALLERGEN_INDICES:
			lbl.add_theme_color_override("font_color", Color(0.9, 0.2, 0.2))
		add_child(lbl)
		legend_y += 18

	# Exit button
	exit_button = Button.new()
	exit_button.text = "X"
	exit_button.position = Vector2(396, 4)
	exit_button.size = Vector2(24, 24)
	exit_button.pressed.connect(_on_exit_pressed)
	add_child(exit_button)

	# Confirm exit panel (hidden)
	confirm_panel = Panel.new()
	confirm_panel.position = Vector2(113, 70)
	confirm_panel.size = Vector2(200, 100)
	confirm_panel.visible = false
	add_child(confirm_panel)

	var confirm_label = Label.new()
	confirm_label.text = "Quit? This counts\nas a failed attempt."
	confirm_label.position = Vector2(20, 10)
	confirm_label.add_theme_font_size_override("font_size", 11)
	confirm_panel.add_child(confirm_label)

	var yes_btn = Button.new()
	yes_btn.text = "Quit"
	yes_btn.position = Vector2(20, 60)
	yes_btn.size = Vector2(70, 28)
	yes_btn.pressed.connect(_on_confirm_quit)
	confirm_panel.add_child(yes_btn)

	var no_btn = Button.new()
	no_btn.text = "Cancel"
	no_btn.position = Vector2(110, 60)
	no_btn.size = Vector2(70, 28)
	no_btn.pressed.connect(func(): confirm_panel.visible = false)
	confirm_panel.add_child(no_btn)

func _show_tutorial() -> void:
	tutorial_overlay = ColorRect.new()
	tutorial_overlay.color = Color(0, 0, 0, 0.6)
	tutorial_overlay.position = Vector2.ZERO
	tutorial_overlay.size = Vector2(426, 240)
	add_child(tutorial_overlay)

	tutorial_panel = Panel.new()
	tutorial_panel.position = Vector2(53, 20)
	tutorial_panel.size = Vector2(320, 200)
	tutorial_overlay.add_child(tutorial_panel)

	_show_tutorial_page(0)

func _show_tutorial_page(page: int) -> void:
	tutorial_page = page
	# Clear old children of tutorial_panel
	for child in tutorial_panel.get_children():
		child.queue_free()

	var pages = [
		"Charlie is allergic to almost\neverything - especially chicken\nand mushrooms!\n\nThey make him itchy\nand he scratches like crazy.",
		"Match 3 or more kibble tiles\nby clicking two adjacent tiles\nto swap them.\n\nFill Charlie's bowl to win!",
		"Watch out for chicken and\nmushroom tiles - matching\nthem reduces the bowl meter!\n\nYou have 20 moves. Good luck!",
	]

	var text_label = Label.new()
	text_label.text = pages[page]
	text_label.position = Vector2(20, 15)
	text_label.add_theme_font_size_override("font_size", 12)
	tutorial_panel.add_child(text_label)

	if page < pages.size() - 1:
		var next_btn = Button.new()
		next_btn.text = "Next"
		next_btn.position = Vector2(220, 160)
		next_btn.size = Vector2(80, 28)
		next_btn.pressed.connect(func(): _show_tutorial_page(page + 1))
		tutorial_panel.add_child(next_btn)
	else:
		var start_btn = Button.new()
		start_btn.text = "Let's eat!"
		start_btn.position = Vector2(190, 160)
		start_btn.size = Vector2(110, 28)
		start_btn.pressed.connect(_on_tutorial_done)
		tutorial_panel.add_child(start_btn)

func _on_tutorial_done() -> void:
	GameState.has_seen_feeding_tutorial = true
	tutorial_overlay.queue_free()
	tutorial_overlay = null
	tutorial_panel = null
	_start_game()

func _start_game() -> void:
	board.initialize_board()
	game_started = true
	game_ended = false
	_build_tile_nodes()
	_update_ui()

func _build_tile_nodes() -> void:
	# Clear old tiles
	for key in tile_nodes:
		if is_instance_valid(tile_nodes[key]):
			tile_nodes[key].queue_free()
	tile_nodes.clear()

	for col in board.board_cols:
		for row in board.board_rows:
			_create_tile_node(col, row, board.grid[col][row])

func _make_tile_atlas(tile_type: int) -> AtlasTexture:
	var atlas = AtlasTexture.new()
	atlas.atlas = FOOD_TILES_TEX
	atlas.region = Rect2(tile_type * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
	return atlas

func _create_tile_node(col: int, row: int, tile_type: int) -> TextureRect:
	var tile = TextureRect.new()
	tile.texture = _make_tile_atlas(tile_type)
	tile.size = Vector2(TILE_SIZE, TILE_SIZE)
	tile.position = Vector2(col * TILE_STEP, row * TILE_STEP)
	tile.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	tile.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

	board_container.add_child(tile)
	tile_nodes[Vector2i(col, row)] = tile
	return tile

func _update_ui() -> void:
	bowl_bar.value = board.bowl_fill
	moves_label.text = "Moves: %d" % board.moves_remaining

func _input(event: InputEvent) -> void:
	if not game_started or game_ended or is_animating:
		return
	if confirm_panel.visible:
		return

	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var local_pos = event.position - BOARD_ORIGIN
		var col = int(local_pos.x / TILE_STEP)
		var row = int(local_pos.y / TILE_STEP)

		# Check click is within a tile (not in the gap)
		var tile_local_x = local_pos.x - col * TILE_STEP
		var tile_local_y = local_pos.y - row * TILE_STEP
		if tile_local_x < 0 or tile_local_x > TILE_SIZE or tile_local_y < 0 or tile_local_y > TILE_SIZE:
			return
		if col < 0 or col >= board.board_cols or row < 0 or row >= board.board_rows:
			return

		var clicked = Vector2i(col, row)

		if selected_tile == Vector2i(-1, -1):
			# Select first tile
			selected_tile = clicked
			_highlight_tile(clicked, true)
		elif clicked == selected_tile:
			# Deselect
			_highlight_tile(selected_tile, false)
			selected_tile = Vector2i(-1, -1)
		else:
			# Try to swap
			var diff = clicked - selected_tile
			if absi(diff.x) + absi(diff.y) == 1:
				_highlight_tile(selected_tile, false)
				_do_swap(selected_tile, clicked)
				selected_tile = Vector2i(-1, -1)
			else:
				# Not adjacent - move selection
				_highlight_tile(selected_tile, false)
				selected_tile = clicked
				_highlight_tile(clicked, true)

func _highlight_tile(pos: Vector2i, highlight: bool) -> void:
	if not tile_nodes.has(pos):
		return
	var tile = tile_nodes[pos]
	if not is_instance_valid(tile):
		return
	if highlight:
		tile.modulate = Color(1.3, 1.3, 0.7)
	else:
		tile.modulate = Color.WHITE

func _do_swap(a: Vector2i, b: Vector2i) -> void:
	is_animating = true

	# Try the swap on the data model
	var valid = board.try_swap(a, b)

	if valid:
		# Animate swap
		await _animate_swap(a, b)
		# Process cascade
		await _process_cascade()
		# Check for deadlock
		if not board.has_any_valid_moves():
			board.shuffle_board()
			_build_tile_nodes()
		# Check game end
		var end_state = board.check_game_end()
		if end_state != "":
			_end_game(end_state)
	else:
		# Animate invalid swap (swap and swap back)
		await _animate_swap(a, b)
		await _animate_swap(b, a)

	_update_ui()
	is_animating = false

func _animate_swap(a: Vector2i, b: Vector2i) -> void:
	var tile_a = tile_nodes.get(a)
	var tile_b = tile_nodes.get(b)
	if not is_instance_valid(tile_a) or not is_instance_valid(tile_b):
		return

	var pos_a = Vector2(a.x * TILE_STEP, a.y * TILE_STEP)
	var pos_b = Vector2(b.x * TILE_STEP, b.y * TILE_STEP)

	var tween = create_tween().set_parallel(true)
	tween.tween_property(tile_a, "position", pos_b, 0.15)
	tween.tween_property(tile_b, "position", pos_a, 0.15)
	await tween.finished

	# Update node references
	tile_nodes[a] = tile_b
	tile_nodes[b] = tile_a

func _process_cascade() -> void:
	while true:
		var result = board.process_matches()
		if not result.had_matches:
			break

		# Animate match clear
		await _animate_clear_matches()

		# Show chicken reaction
		if result.chicken_count > 0:
			_show_chicken_reaction()

		# Apply gravity
		var movements = board.apply_gravity()
		_sync_tile_nodes_after_gravity()
		await _animate_gravity(movements)

		# Refill board
		var new_tiles = board.refill_board()
		await _animate_refill(new_tiles)

		_update_ui()

func _animate_clear_matches() -> void:
	# Find tiles that are now EMPTY in the board but still have nodes
	var to_clear: Array = []
	for pos in tile_nodes:
		if board.get_tile(pos.x, pos.y) == -1:  # EMPTY
			to_clear.append(pos)

	if to_clear.size() == 0:
		return

	var tween = create_tween().set_parallel(true)
	for pos in to_clear:
		var tile = tile_nodes[pos]
		if is_instance_valid(tile):
			tween.tween_property(tile, "scale", Vector2.ZERO, 0.2)
			tween.tween_property(tile, "modulate", Color.WHITE * 2, 0.2)
	await tween.finished

	# Remove cleared nodes
	for pos in to_clear:
		if tile_nodes.has(pos) and is_instance_valid(tile_nodes[pos]):
			tile_nodes[pos].queue_free()
			tile_nodes.erase(pos)

func _sync_tile_nodes_after_gravity() -> void:
	# Rebuild tile_nodes dictionary to match current grid state
	# Tiles have fallen - we need to re-map nodes to new positions
	var old_nodes: Dictionary = tile_nodes.duplicate()
	tile_nodes.clear()

	# Collect all valid remaining tile nodes
	var available_nodes: Array = []
	for pos in old_nodes:
		if is_instance_valid(old_nodes[pos]):
			available_nodes.append(old_nodes[pos])

	# Map existing nodes to grid positions that have tiles
	var node_idx = 0
	for col in board.board_cols:
		for row in range(board.board_rows - 1, -1, -1):
			if board.grid[col][row] != -1:  # Not empty
				if node_idx < available_nodes.size():
					var node = available_nodes[node_idx]
					tile_nodes[Vector2i(col, row)] = node
					# Update texture to match new grid position
					node.texture = _make_tile_atlas(board.grid[col][row])
					node_idx += 1

func _animate_gravity(movements: Array) -> void:
	if movements.size() == 0:
		return
	var tween = create_tween().set_parallel(true)
	for pos in tile_nodes:
		var tile = tile_nodes[pos]
		if is_instance_valid(tile):
			var target = Vector2(pos.x * TILE_STEP, pos.y * TILE_STEP)
			tween.tween_property(tile, "position", target, 0.15)
			tile.scale = Vector2.ONE
			tile.modulate = Color.WHITE
	await tween.finished

func _animate_refill(new_tiles: Array) -> void:
	if new_tiles.size() == 0:
		return

	for tile_data in new_tiles:
		var col = tile_data.col
		var row = tile_data.row
		var tile_type = tile_data.type
		var node = _create_tile_node(col, row, tile_type)
		# Start above board
		node.position.y = -TILE_STEP
		node.scale = Vector2.ONE

	var tween = create_tween().set_parallel(true)
	for tile_data in new_tiles:
		var pos = Vector2i(tile_data.col, tile_data.row)
		if tile_nodes.has(pos) and is_instance_valid(tile_nodes[pos]):
			var target_y = tile_data.row * TILE_STEP
			tween.tween_property(tile_nodes[pos], "position:y", target_y, 0.15)
	await tween.finished

func _show_chicken_reaction() -> void:
	reaction_label.text = "BARK!"
	# Flash the board red briefly
	var flash = ColorRect.new()
	flash.color = Color(1, 0, 0, 0.2)
	flash.position = Vector2.ZERO
	flash.size = Vector2(board.board_cols * TILE_STEP, board.board_rows * TILE_STEP)
	board_container.add_child(flash)

	# Shake charlie portrait
	var orig_pos = charlie_portrait.position
	var tween = create_tween()
	tween.tween_property(charlie_portrait, "position", orig_pos + Vector2(3, 0), 0.05)
	tween.tween_property(charlie_portrait, "position", orig_pos - Vector2(3, 0), 0.05)
	tween.tween_property(charlie_portrait, "position", orig_pos + Vector2(2, 0), 0.05)
	tween.tween_property(charlie_portrait, "position", orig_pos, 0.05)
	await tween.finished

	# Fade out flash and reaction
	var fade_tween = create_tween()
	fade_tween.tween_property(flash, "modulate:a", 0.0, 0.3)
	await fade_tween.finished
	flash.queue_free()

	# Clear reaction after a moment
	await get_tree().create_timer(0.5).timeout
	reaction_label.text = ""

func _on_exit_pressed() -> void:
	if game_ended:
		get_tree().change_scene_to_file("res://scenes/House.tscn")
		return
	confirm_panel.visible = true

func _on_confirm_quit() -> void:
	confirm_panel.visible = false
	# Treat as failure
	GameState.do_feed_fail(board.fail_bonding_penalty, board.fail_entertainment_penalty)
	get_tree().change_scene_to_file("res://scenes/House.tscn")

func _end_game(state: String) -> void:
	game_ended = true

	if state == "won":
		GameState.do_feed_win()
	else:
		GameState.do_feed_fail(board.fail_bonding_penalty, board.fail_entertainment_penalty)

	_show_results(state)

func _show_results(state: String) -> void:
	results_overlay = ColorRect.new()
	results_overlay.color = Color(0, 0, 0, 0.5)
	results_overlay.position = Vector2.ZERO
	results_overlay.size = Vector2(426, 240)
	add_child(results_overlay)

	results_panel = Panel.new()
	results_panel.position = Vector2(63, 30)
	results_panel.size = Vector2(300, 180)
	results_overlay.add_child(results_panel)

	var title = Label.new()
	title.add_theme_font_size_override("font_size", 16)
	title.position = Vector2(20, 10)

	var body = Label.new()
	body.add_theme_font_size_override("font_size", 10)
	body.position = Vector2(20, 40)

	if state == "won":
		title.text = "Yummy!"
		title.add_theme_color_override("font_color", Color(0.2, 0.8, 0.2))
		body.text = "Charlie loved his meal!\n\nKibble matched: %d\nChicken cleared: %d\nBowl fill: %d%%\n\nHunger and entertainment set to full!\nBonding +25%%" % [
			board.total_safe_matched,
			board.total_chicken_matched,
			int(board.bowl_fill * 100),
		]
	else:
		title.text = "Oh no..."
		title.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))
		body.text = "Charlie's bowl isn't full enough.\n\nKibble matched: %d\nChicken cleared: %d\nBowl fill: %d%%\n\nBonding -%d%%, Entertainment -%d%%" % [
			board.total_safe_matched,
			board.total_chicken_matched,
			int(board.bowl_fill * 100),
			int(board.fail_bonding_penalty * 100),
			int(board.fail_entertainment_penalty * 100),
		]

	results_panel.add_child(title)
	results_panel.add_child(body)

	var back_btn = Button.new()
	back_btn.text = "Back to House"
	back_btn.position = Vector2(20, 142)
	back_btn.size = Vector2(120, 28)
	back_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/House.tscn"))
	results_panel.add_child(back_btn)

	if state == "lost":
		var retry_btn = Button.new()
		retry_btn.text = "Try Again"
		retry_btn.position = Vector2(160, 142)
		retry_btn.size = Vector2(120, 28)
		retry_btn.pressed.connect(_retry_game)
		results_panel.add_child(retry_btn)

func _retry_game() -> void:
	if results_overlay:
		results_overlay.queue_free()
		results_overlay = null
		results_panel = null
	game_ended = false
	_start_game()
