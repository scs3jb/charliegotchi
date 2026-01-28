extends SceneTree
## Test script for House scene physics and behaviors
## Run with: godot -s scripts/test_house.gd --headless

var tests_passed: int = 0
var tests_failed: int = 0
var test_results: Array = []

func _init() -> void:
	print("\n============================================================")
	print("HOUSE SCENE TESTS")
	print("============================================================\n")

	# Run all tests
	test_ball_room_bounds()
	test_ball_furniture_collision()
	test_charlie_obstacle_avoidance()
	test_basket_position()
	test_player_starting_position()

	# Print summary
	print("\n============================================================")
	print("TEST SUMMARY")
	print("============================================================")
	print("Passed: %d" % tests_passed)
	print("Failed: %d" % tests_failed)

	for result in test_results:
		print(result)

	if tests_failed > 0:
		print("\nSOME TESTS FAILED")
	else:
		print("\nALL TESTS PASSED")

	quit()

func assert_true(condition: bool, test_name: String) -> void:
	if condition:
		tests_passed += 1
		test_results.append("[PASS] " + test_name)
		print("[PASS] " + test_name)
	else:
		tests_failed += 1
		test_results.append("[FAIL] " + test_name)
		print("[FAIL] " + test_name)

func assert_in_range(value: float, min_val: float, max_val: float, test_name: String) -> void:
	var in_range = value >= min_val and value <= max_val
	if in_range:
		tests_passed += 1
		test_results.append("[PASS] " + test_name + " (value: %.1f)" % value)
		print("[PASS] " + test_name + " (value: %.1f)" % value)
	else:
		tests_failed += 1
		test_results.append("[FAIL] " + test_name + " (value: %.1f, expected: %.1f-%.1f)" % [value, min_val, max_val])
		print("[FAIL] " + test_name + " (value: %.1f, expected: %.1f-%.1f)" % [value, min_val, max_val])

func test_ball_room_bounds() -> void:
	print("\n--- Ball Room Bounds Tests ---")

	# Test ball bounds are set correctly for the larger room
	var ball_script = load("res://scripts/props/Ball.gd")
	var ball = ball_script.new()

	# Room should be larger now (approx 426x290 with walls)
	assert_in_range(ball.bounds_left, 15.0, 30.0, "Ball bounds_left")
	assert_in_range(ball.bounds_right, 390.0, 420.0, "Ball bounds_right")
	assert_in_range(ball.bounds_top, 50.0, 65.0, "Ball bounds_top")
	assert_in_range(ball.bounds_bottom, 260.0, 290.0, "Ball bounds_bottom")

	ball.free()

func test_ball_furniture_collision() -> void:
	print("\n--- Ball Furniture Collision Tests ---")

	var ball_script = load("res://scripts/props/Ball.gd")
	var ball = ball_script.new()

	# Test that furniture rects are defined
	assert_true(ball.furniture_rects.size() > 0, "Ball has furniture collision rects")

	# Test kitchen area is in furniture rects
	var has_kitchen = false
	for rect in ball.furniture_rects:
		if rect.position.x < 20 and rect.size.x > 80:
			has_kitchen = true
			break
	assert_true(has_kitchen, "Kitchen collision rect exists")

	# Test table is in furniture rects
	var has_table = false
	for rect in ball.furniture_rects:
		if rect.position.x > 140 and rect.position.x < 170 and rect.size.x > 80:
			has_table = true
			break
	assert_true(has_table, "Table collision rect exists")

	# Test sofa is in furniture rects
	var has_sofa = false
	for rect in ball.furniture_rects:
		if rect.position.x > 340:
			has_sofa = true
			break
	assert_true(has_sofa, "Sofa collision rect exists")

	ball.free()

func test_charlie_obstacle_avoidance() -> void:
	print("\n--- Charlie Obstacle Avoidance Tests ---")

	# Load and check Charlie script source for obstacle avoidance code
	var script_file = FileAccess.open("res://scripts/charlie/Charlie.gd", FileAccess.READ)
	assert_true(script_file != null, "Charlie script file readable")

	if script_file:
		var source = script_file.get_as_text()
		script_file.close()

		# Check that obstacle avoidance code exists in the script
		assert_true(source.contains("furniture_rects"), "Charlie script has furniture_rects")
		assert_true(source.contains("stuck_timer"), "Charlie script has stuck_timer")
		assert_true(source.contains("is_avoiding"), "Charlie script has is_avoiding")
		assert_true(source.contains("_get_avoidance_direction"), "Charlie has avoidance direction function")
		assert_true(source.contains("_steer_around_obstacles"), "Charlie has steer around obstacles function")
		assert_true(source.contains("_is_direction_clear"), "Charlie has direction clear check function")

	# Load the scene to check Charlie node exists
	var house_scene = load("res://scenes/House.tscn")
	assert_true(house_scene != null, "House scene loads successfully")

	var house = house_scene.instantiate()
	var charlie = house.get_node_or_null("Charlie")
	assert_true(charlie != null, "Charlie node exists in House scene")

	house.free()

func test_basket_position() -> void:
	print("\n--- Basket Position Tests ---")

	var house_scene = load("res://scenes/House.tscn")
	var house = house_scene.instantiate()

	var basket = house.get_node_or_null("CharlieBasket")
	assert_true(basket != null, "CharlieBasket node exists")

	if basket:
		# Basket should be in the room, not overlapping with other furniture
		assert_in_range(basket.position.x, 300.0, 400.0, "Basket X position")
		assert_in_range(basket.position.y, 200.0, 270.0, "Basket Y position")

	house.free()

func test_player_starting_position() -> void:
	print("\n--- Player Starting Position Tests ---")

	var house_scene = load("res://scenes/House.tscn")
	var house = house_scene.instantiate()

	var player = house.get_node_or_null("Player")
	assert_true(player != null, "Player node exists")

	if player:
		# Player should start in a valid position (not inside furniture)
		assert_in_range(player.position.x, 100.0, 350.0, "Player starting X")
		assert_in_range(player.position.y, 180.0, 270.0, "Player starting Y")

		# Verify player is not inside table (155, 115) to (245, 165)
		var in_table = player.position.x > 155 and player.position.x < 245 and \
					   player.position.y > 115 and player.position.y < 165
		assert_true(not in_table, "Player not starting inside table")

	var charlie = house.get_node_or_null("Charlie")
	assert_true(charlie != null, "Charlie node exists")

	if charlie:
		# Charlie should start in a valid position
		assert_in_range(charlie.position.x, 100.0, 400.0, "Charlie starting X")
		assert_in_range(charlie.position.y, 100.0, 270.0, "Charlie starting Y")

	house.free()
