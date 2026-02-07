extends SceneTree
## Verify Player.gd animation logic

# Expected animations from player_frames.tres
var expected_animations = [
	"idle_down",
	"bored",
	"confused",
	"walk_left",
	"walk_right",
	"walk_up",
	"walk_down",
	"pickup",
	"hold_idle",
	"hold_walk_left",
	"hold_walk_right",
	"hold_walk_up",
	"hold_walk_down",
]

# Charlie animations
var expected_charlie_animations = [
	"idle_down",
	"idle_left",
	"idle_right",
	"idle_up",
	"walk_down",
	"walk_left",
	"walk_right",
	"walk_up",
]

var passed = 0
var failed = 0

func _init():
	print("=== Animation Verification ===")
	print("")

	# Test player frames resource
	print("--- Player Frames Resource ---")
	test_player_frames()

	# Test Charlie frames resource
	print("")
	print("--- Charlie Frames Resource ---")
	test_charlie_frames()

	print("")
	print("=== Results ===")
	print("Passed: %d" % passed)
	print("Failed: %d" % failed)
	print("")

	if failed > 0:
		print("VERIFICATION FAILED!")
		quit(1)
	else:
		print("All verifications passed!")
		quit(0)

func test_player_frames():
	var path = "res://resources/sprites/player_frames.tres"
	if not ResourceLoader.exists(path):
		print("[FAIL] Player frames resource not found: %s" % path)
		failed += 1
		return

	var frames = load(path)
	if frames == null:
		print("[FAIL] Could not load player frames")
		failed += 1
		return

	if not frames is SpriteFrames:
		print("[FAIL] Resource is not SpriteFrames")
		failed += 1
		return

	# Check each expected animation
	for anim_name in expected_animations:
		if frames.has_animation(anim_name):
			var frame_count = frames.get_frame_count(anim_name)
			if frame_count > 0:
				print("[PASS] %s (%d frames)" % [anim_name, frame_count])
				passed += 1
			else:
				print("[FAIL] %s - No frames" % anim_name)
				failed += 1
		else:
			print("[FAIL] %s - Animation not found" % anim_name)
			failed += 1

func test_charlie_frames():
	var path = "res://assets/sprites/characters/charlie_sprite_frames.tres"
	if not ResourceLoader.exists(path):
		print("[WARN] Charlie frames resource not found: %s" % path)
		print("[INFO] Checking alternate location...")

		# Try alternate path
		path = "res://resources/sprites/charlie_frames.tres"
		if not ResourceLoader.exists(path):
			print("[SKIP] Charlie frames not found, skipping")
			return

	var frames = load(path)
	if frames == null:
		print("[FAIL] Could not load Charlie frames")
		failed += 1
		return

	if not frames is SpriteFrames:
		print("[FAIL] Resource is not SpriteFrames")
		failed += 1
		return

	# Check each expected animation
	for anim_name in expected_charlie_animations:
		if frames.has_animation(anim_name):
			var frame_count = frames.get_frame_count(anim_name)
			if frame_count > 0:
				print("[PASS] %s (%d frames)" % [anim_name, frame_count])
				passed += 1
			else:
				print("[FAIL] %s - No frames" % anim_name)
				failed += 1
		else:
			print("[FAIL] %s - Animation not found" % anim_name)
			failed += 1
