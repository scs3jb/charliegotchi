extends SceneTree
## Test: MatchBoard.grid_pos_from_local()
## Verifies that board-local coordinates map to the correct grid cell.
## Run: godot -s scripts/tests/test_feeding_grid.gd --headless

const MatchBoardScript = preload("res://scripts/minigames/MatchBoard.gd")

# Rendering constants matching FeedingMinigame.gd
const TILE_SIZE: int = 28
const TILE_STEP: int = 30

var passed: int = 0
var failed: int = 0

func _init() -> void:
	var board = MatchBoardScript.new()
	board.initialize_board()

	print("\n=== Grid Position Mapping Tests ===\n")

	# --- Tile center tests ---
	# Every tile center should map to the correct (col, row)
	for col in 7:
		for row in 7:
			var center = Vector2(col * TILE_STEP + TILE_SIZE * 0.5, row * TILE_STEP + TILE_SIZE * 0.5)
			var result = board.grid_pos_from_local(center, TILE_SIZE, TILE_STEP)
			_assert_eq(result, Vector2i(col, row), "Tile center (%d, %d)" % [col, row])

	# --- Tile corner tests ---
	# Top-left corner of tile (0, 0) at (0.0, 0.0)
	_assert_eq(board.grid_pos_from_local(Vector2(0.0, 0.0), TILE_SIZE, TILE_STEP), Vector2i(0, 0), "Top-left corner (0,0)")
	# Bottom-right edge of tile (0, 0) at (28, 28)
	_assert_eq(board.grid_pos_from_local(Vector2(28.0, 28.0), TILE_SIZE, TILE_STEP), Vector2i(0, 0), "Bottom-right of (0,0) at exact TILE_SIZE")
	# Top-left corner of tile (3, 4)
	_assert_eq(board.grid_pos_from_local(Vector2(90.0, 120.0), TILE_SIZE, TILE_STEP), Vector2i(3, 4), "Top-left corner (3,4)")
	# Last tile (6, 6) center
	_assert_eq(board.grid_pos_from_local(Vector2(6 * 30 + 14, 6 * 30 + 14), TILE_SIZE, TILE_STEP), Vector2i(6, 6), "Last tile (6,6) center")

	# --- Gap rejection tests ---
	# Position in the 2px gap between col 0 and col 1 (x = 28.5)
	_assert_eq(board.grid_pos_from_local(Vector2(28.5, 14.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Horizontal gap at x=28.5")
	# Position in the 2px gap between row 0 and row 1 (y = 29.0)
	_assert_eq(board.grid_pos_from_local(Vector2(14.0, 29.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Vertical gap at y=29.0")
	# Corner of gaps (both x and y in gap)
	_assert_eq(board.grid_pos_from_local(Vector2(29.0, 29.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Corner gap at (29, 29)")

	# --- Out-of-bounds tests ---
	# Negative coordinates
	_assert_eq(board.grid_pos_from_local(Vector2(-1.0, 14.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Negative x")
	_assert_eq(board.grid_pos_from_local(Vector2(14.0, -1.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Negative y")
	_assert_eq(board.grid_pos_from_local(Vector2(-10.0, -10.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Both negative")
	# Beyond board right edge (col 7+)
	_assert_eq(board.grid_pos_from_local(Vector2(210.0, 14.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Beyond right edge col=7")
	# Beyond board bottom edge (row 7+)
	_assert_eq(board.grid_pos_from_local(Vector2(14.0, 210.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Beyond bottom edge row=7")

	# --- Boundary precision tests ---
	# Just inside tile at tile start (x = col * TILE_STEP + 0.001)
	_assert_eq(board.grid_pos_from_local(Vector2(30.001, 14.0), TILE_SIZE, TILE_STEP), Vector2i(1, 0), "Just inside tile (1,0) start")
	# Just inside tile at tile end (x = col * TILE_STEP + TILE_SIZE - 0.001)
	_assert_eq(board.grid_pos_from_local(Vector2(57.999, 14.0), TILE_SIZE, TILE_STEP), Vector2i(1, 0), "Just inside tile (1,0) end")
	# Just past tile into gap (x = col * TILE_STEP + TILE_SIZE + 0.001)
	_assert_eq(board.grid_pos_from_local(Vector2(58.001, 14.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Just past tile (1,0) into gap")

	# --- floori vs int() regression test ---
	# With int(), -0.5/30 truncates to 0 (wrong). With floori(), it becomes -1 (correct, caught by bounds).
	_assert_eq(board.grid_pos_from_local(Vector2(-0.5, 14.0), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Negative fractional x rejected")
	_assert_eq(board.grid_pos_from_local(Vector2(14.0, -0.5), TILE_SIZE, TILE_STEP), Vector2i(-1, -1), "Negative fractional y rejected")

	# ============================================
	# Gravity node-sync regression tests
	# ============================================
	print("\n=== Gravity Node Sync Tests ===\n")

	# Simulate the tile_nodes dict and _apply_gravity_to_nodes logic
	# to verify nodes track correct grid positions after gravity.

	# Test 1: Basic gravity - tiles fall to fill gap at bottom
	# Column 0: rows 0-4 have tiles, rows 5-6 were cleared
	# After gravity: tiles shift down by 2
	var fake_nodes_1: Dictionary = {}
	for r in 5:
		fake_nodes_1[Vector2i(0, r)] = "node_%d" % r  # placeholder "nodes"
	var movements_1: Array = [
		{"from": Vector2i(0, 4), "to": Vector2i(0, 6)},
		{"from": Vector2i(0, 3), "to": Vector2i(0, 5)},
		{"from": Vector2i(0, 2), "to": Vector2i(0, 4)},
		{"from": Vector2i(0, 1), "to": Vector2i(0, 3)},
		{"from": Vector2i(0, 0), "to": Vector2i(0, 2)},
	]
	_apply_movements(fake_nodes_1, movements_1)
	_assert_eq(fake_nodes_1.get(Vector2i(0, 6)), "node_4", "Gravity: row 4 falls to row 6")
	_assert_eq(fake_nodes_1.get(Vector2i(0, 5)), "node_3", "Gravity: row 3 falls to row 5")
	_assert_eq(fake_nodes_1.get(Vector2i(0, 4)), "node_2", "Gravity: row 2 falls to row 4")
	_assert_eq(fake_nodes_1.get(Vector2i(0, 3)), "node_1", "Gravity: row 1 falls to row 3")
	_assert_eq(fake_nodes_1.get(Vector2i(0, 2)), "node_0", "Gravity: row 0 falls to row 2")
	_assert_eq(fake_nodes_1.has(Vector2i(0, 0)), false, "Gravity: row 0 now empty")
	_assert_eq(fake_nodes_1.has(Vector2i(0, 1)), false, "Gravity: row 1 now empty")

	# Test 2: No movements - nodes should stay in place (regression for early-return bug)
	var fake_nodes_2: Dictionary = {}
	for r in 7:
		fake_nodes_2[Vector2i(0, r)] = "node_%d" % r
	_apply_movements(fake_nodes_2, [])  # Empty movements
	for r in 7:
		_assert_eq(fake_nodes_2.get(Vector2i(0, r)), "node_%d" % r, "No-gravity: row %d unchanged" % r)

	# Test 3: Partial gravity - middle of column cleared
	# Rows 0,1,2,5,6 have tiles. Rows 3,4 cleared.
	# After gravity: rows 0,1,2 fall by 2
	var fake_nodes_3: Dictionary = {}
	fake_nodes_3[Vector2i(0, 0)] = "top0"
	fake_nodes_3[Vector2i(0, 1)] = "top1"
	fake_nodes_3[Vector2i(0, 2)] = "top2"
	fake_nodes_3[Vector2i(0, 5)] = "bot5"
	fake_nodes_3[Vector2i(0, 6)] = "bot6"
	var movements_3: Array = [
		{"from": Vector2i(0, 2), "to": Vector2i(0, 4)},
		{"from": Vector2i(0, 1), "to": Vector2i(0, 3)},
		{"from": Vector2i(0, 0), "to": Vector2i(0, 2)},
	]
	_apply_movements(fake_nodes_3, movements_3)
	_assert_eq(fake_nodes_3.get(Vector2i(0, 6)), "bot6", "Partial: bottom row 6 unmoved")
	_assert_eq(fake_nodes_3.get(Vector2i(0, 5)), "bot5", "Partial: bottom row 5 unmoved")
	_assert_eq(fake_nodes_3.get(Vector2i(0, 4)), "top2", "Partial: row 2 falls to row 4")
	_assert_eq(fake_nodes_3.get(Vector2i(0, 3)), "top1", "Partial: row 1 falls to row 3")
	_assert_eq(fake_nodes_3.get(Vector2i(0, 2)), "top0", "Partial: row 0 falls to row 2")

	# Test 4: Full board gravity integration test with MatchBoard
	var board2 = MatchBoardScript.new()
	board2.initialize_board()
	# Force a known column state: set col 0 to specific types
	# Clear top 2 rows to simulate a match
	var saved_tiles: Array = []
	for r in board2.board_rows:
		saved_tiles.append(board2.grid[0][r])
	board2.grid[0][0] = -1  # EMPTY
	board2.grid[0][1] = -1  # EMPTY
	# Build fake node dict for col 0
	var fake_nodes_4: Dictionary = {}
	for r in range(2, 7):
		fake_nodes_4[Vector2i(0, r)] = "node_0_%d" % r
	# Also add other columns (unchanged)
	for c in range(1, 7):
		for r in 7:
			fake_nodes_4[Vector2i(c, r)] = "node_%d_%d" % [c, r]
	var movements_4 = board2.apply_gravity()
	_apply_movements(fake_nodes_4, movements_4)
	# Col 0: tiles at rows 2-6 should now be at rows 4-6 (shifted down by 2)
	# Wait - only the tiles that MOVED are updated. Rows 2-6 had tiles.
	# After gravity: rows 0,1 empty, row 2 gets old row 0 (empty->still processed)
	# Actually gravity shifts non-empty tiles down. Rows 2-6 (5 tiles) fill rows 2-6.
	# Only rows 0,1 were empty. Tiles at 2-6 don't need to move since there's nothing below them that's empty.
	# Wait no - rows 0,1 are empty (above), rows 2-6 have tiles. Gravity moves tiles DOWN to fill gaps BELOW.
	# Since empty rows are ABOVE the tiles, nothing falls. Movements for col 0 should be empty!
	# This is the exact scenario that triggered the old bug.
	_assert_eq(fake_nodes_4.get(Vector2i(0, 2)), "node_0_2", "Integration: top-clear col 0 row 2 unchanged")
	_assert_eq(fake_nodes_4.get(Vector2i(0, 6)), "node_0_6", "Integration: top-clear col 0 row 6 unchanged")

	# --- Summary ---
	print("\n=== Results ===")
	print("Passed: %d" % passed)
	print("Failed: %d" % failed)
	if failed == 0:
		print("\nAll tests passed!")
	else:
		print("\nSOME TESTS FAILED!")
	quit()

## Mirrors FeedingMinigame._apply_gravity_to_nodes() logic for testing
func _apply_movements(nodes: Dictionary, movements: Array) -> void:
	for move in movements:
		var from_pos: Vector2i = move["from"]
		var to_pos: Vector2i = move["to"]
		if nodes.has(from_pos):
			var node = nodes[from_pos]
			nodes.erase(from_pos)
			nodes[to_pos] = node

func _assert_eq(actual, expected, label: String) -> void:
	if actual == expected:
		print("[PASS] %s" % label)
		passed += 1
	else:
		print("[FAIL] %s: expected %s, got %s" % [label, str(expected), str(actual)])
		failed += 1
