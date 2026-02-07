extends RefCounted
## MatchBoard - Pure data model for match-3 feeding minigame
## No visuals or scene tree dependency. Used by FeedingMinigame.gd.

enum TileType {
	KIBBLE_BROWN,
	KIBBLE_SALMON,
	KIBBLE_GREEN,
	KIBBLE_ORANGE,
	KIBBLE_BLUE,
	CHICKEN,
	MUSHROOM,
	EMPTY = -1
}

const ALLERGEN_TYPES: Array = [TileType.CHICKEN, TileType.MUSHROOM]

# Board config
var board_cols: int = 7
var board_rows: int = 7
var move_limit: int = 20

# Scoring
var bowl_fill_per_tile: float = 0.04
var chicken_penalty_per_tile: float = 0.03
var fail_bonding_penalty: float = 0.10
var fail_entertainment_penalty: float = 0.05

# Tile weights (higher = more common)
var tile_weights: Dictionary = {
	TileType.KIBBLE_BROWN: 16,
	TileType.KIBBLE_SALMON: 16,
	TileType.KIBBLE_GREEN: 16,
	TileType.KIBBLE_ORANGE: 16,
	TileType.KIBBLE_BLUE: 12,
	TileType.CHICKEN: 14,
	TileType.MUSHROOM: 10,
}

# State
var grid: Array = []  # 2D array: grid[col][row]
var moves_remaining: int = 0
var bowl_fill: float = 0.0
var total_safe_matched: int = 0
var total_chicken_matched: int = 0

func initialize_board() -> void:
	moves_remaining = move_limit
	bowl_fill = 0.0
	total_safe_matched = 0
	total_chicken_matched = 0
	grid.clear()
	grid.resize(board_cols)
	for col in board_cols:
		grid[col] = []
		grid[col].resize(board_rows)
		for row in board_rows:
			grid[col][row] = _pick_tile_no_match(col, row)

func _pick_tile_no_match(col: int, row: int) -> int:
	# Pick a random tile that doesn't create an initial match of 3
	var attempts = 0
	while attempts < 50:
		var tile = _weighted_random_tile()
		# Check 2 to the left
		if col >= 2 and grid[col - 1][row] == tile and grid[col - 2][row] == tile:
			attempts += 1
			continue
		# Check 2 above
		if row >= 2 and grid[col][row - 1] == tile and grid[col][row - 2] == tile:
			attempts += 1
			continue
		return tile
	# Fallback: just return whatever (extremely rare)
	return _weighted_random_tile()

func _weighted_random_tile() -> int:
	var total_weight = 0
	for w in tile_weights.values():
		total_weight += w
	var roll = randi() % total_weight
	var cumulative = 0
	for tile_type in tile_weights:
		cumulative += tile_weights[tile_type]
		if roll < cumulative:
			return tile_type
	return TileType.KIBBLE_BROWN

func try_swap(a: Vector2i, b: Vector2i) -> bool:
	# Validate adjacency
	var diff = b - a
	if absi(diff.x) + absi(diff.y) != 1:
		return false
	# Validate bounds
	if not _in_bounds(a) or not _in_bounds(b):
		return false

	# Temporarily swap
	var temp = grid[a.x][a.y]
	grid[a.x][a.y] = grid[b.x][b.y]
	grid[b.x][b.y] = temp

	# Check for matches at both positions
	var matches = find_all_matches()
	if matches.size() == 0:
		# Swap back - invalid move
		grid[b.x][b.y] = grid[a.x][a.y]
		grid[a.x][a.y] = temp
		return false

	# Valid swap - decrement moves
	moves_remaining -= 1
	return true

func _in_bounds(pos: Vector2i) -> bool:
	return pos.x >= 0 and pos.x < board_cols and pos.y >= 0 and pos.y < board_rows

func find_all_matches() -> Array:
	var match_groups: Array = []

	# Horizontal scan
	for row in board_rows:
		var run_start = 0
		for col in range(1, board_cols):
			if grid[col][row] == grid[run_start][row] and grid[col][row] != TileType.EMPTY:
				continue
			else:
				var run_length = col - run_start
				if run_length >= 3:
					var group: Array = []
					for c in range(run_start, col):
						group.append(Vector2i(c, row))
					match_groups.append(group)
				run_start = col
		# Check final run
		var run_length = board_cols - run_start
		if run_length >= 3 and grid[run_start][row] != TileType.EMPTY:
			var group: Array = []
			for c in range(run_start, board_cols):
				group.append(Vector2i(c, row))
			match_groups.append(group)

	# Vertical scan
	for col in board_cols:
		var run_start = 0
		for row in range(1, board_rows):
			if grid[col][row] == grid[col][run_start] and grid[col][row] != TileType.EMPTY:
				continue
			else:
				var run_length_v = row - run_start
				if run_length_v >= 3:
					var group: Array = []
					for r in range(run_start, row):
						group.append(Vector2i(col, r))
					match_groups.append(group)
				run_start = row
		# Check final run
		var run_length_v = board_rows - run_start
		if run_length_v >= 3 and grid[col][run_start] != TileType.EMPTY:
			var group: Array = []
			for r in range(run_start, board_rows):
				group.append(Vector2i(col, r))
			match_groups.append(group)

	return match_groups

func process_matches() -> Dictionary:
	var result = {"safe_count": 0, "chicken_count": 0, "had_matches": false}
	var matches = find_all_matches()
	if matches.size() == 0:
		return result

	result.had_matches = true

	# Deduplicate positions and score
	var cleared: Dictionary = {}  # Vector2i -> true
	for group in matches:
		for pos in group:
			if not cleared.has(pos):
				cleared[pos] = true
				var tile = grid[pos.x][pos.y]
				if tile in ALLERGEN_TYPES:
					result.chicken_count += 1
					total_chicken_matched += 1
				else:
					result.safe_count += 1
					total_safe_matched += 1

	# Apply scoring
	bowl_fill += result.safe_count * bowl_fill_per_tile
	bowl_fill -= result.chicken_count * chicken_penalty_per_tile
	bowl_fill = clampf(bowl_fill, 0.0, 1.0)

	# Clear matched cells
	for pos in cleared:
		grid[pos.x][pos.y] = TileType.EMPTY

	return result

func apply_gravity() -> Array:
	var movements: Array = []  # [{from: Vector2i, to: Vector2i}]
	for col in board_cols:
		var write_row = board_rows - 1
		for row in range(board_rows - 1, -1, -1):
			if grid[col][row] != TileType.EMPTY:
				if row != write_row:
					grid[col][write_row] = grid[col][row]
					grid[col][row] = TileType.EMPTY
					movements.append({"from": Vector2i(col, row), "to": Vector2i(col, write_row)})
				write_row -= 1
	return movements

func refill_board() -> Array:
	var new_tiles: Array = []  # [{col: int, row: int, type: int}]
	for col in board_cols:
		for row in board_rows:
			if grid[col][row] == TileType.EMPTY:
				var tile = _weighted_random_tile()
				grid[col][row] = tile
				new_tiles.append({"col": col, "row": row, "type": tile})
	return new_tiles

func has_any_valid_moves() -> bool:
	for col in board_cols:
		for row in board_rows:
			# Try swap right
			if col < board_cols - 1:
				_swap(col, row, col + 1, row)
				if find_all_matches().size() > 0:
					_swap(col, row, col + 1, row)
					return true
				_swap(col, row, col + 1, row)
			# Try swap down
			if row < board_rows - 1:
				_swap(col, row, col, row + 1)
				if find_all_matches().size() > 0:
					_swap(col, row, col, row + 1)
					return true
				_swap(col, row, col, row + 1)
	return false

func _swap(c1: int, r1: int, c2: int, r2: int) -> void:
	var temp = grid[c1][r1]
	grid[c1][r1] = grid[c2][r2]
	grid[c2][r2] = temp

func shuffle_board() -> void:
	# Collect all tiles
	var all_tiles: Array = []
	for col in board_cols:
		for row in board_rows:
			all_tiles.append(grid[col][row])
	# Shuffle
	all_tiles.shuffle()
	# Re-place
	var idx = 0
	for col in board_cols:
		for row in board_rows:
			grid[col][row] = all_tiles[idx]
			idx += 1
	# If still no valid moves, just reinitialize
	if not has_any_valid_moves():
		initialize_board()
		moves_remaining = moves_remaining  # Keep current moves

func check_game_end() -> String:
	if bowl_fill >= 1.0:
		return "won"
	if moves_remaining <= 0:
		return "lost"
	return ""

func get_tile(col: int, row: int) -> int:
	if col >= 0 and col < board_cols and row >= 0 and row < board_rows:
		return grid[col][row]
	return TileType.EMPTY
