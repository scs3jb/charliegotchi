extends SceneTree
## Test script to verify all scenes load without errors

var scenes_to_test = [
	"res://scenes/MainMenu.tscn",
	"res://scenes/Cutscene_Intro.tscn",
	"res://scenes/Beach_Start.tscn",
	"res://scenes/House.tscn",
	"res://scenes/Overworld.tscn",
	"res://scenes/props/Tree.tscn",
	"res://scenes/props/Rock.tscn",
	"res://scenes/props/Bush.tscn",
	"res://scenes/props/Fence.tscn",
	"res://scenes/minigames/FeedingMinigame.tscn",
]

var passed = 0
var failed = 0

func _init():
	print("=== Scene Loading Tests ===")
	print("")

	for scene_path in scenes_to_test:
		test_scene_load(scene_path)

	print("")
	print("=== Results ===")
	print("Passed: %d" % passed)
	print("Failed: %d" % failed)
	print("")

	if failed > 0:
		print("TESTS FAILED!")
		quit(1)
	else:
		print("All tests passed!")
		quit(0)

func test_scene_load(path: String) -> void:
	if not ResourceLoader.exists(path):
		print("[FAIL] %s - File not found" % path)
		failed += 1
		return

	var scene = load(path)
	if scene == null:
		print("[FAIL] %s - Failed to load" % path)
		failed += 1
		return

	# Try to instantiate
	var instance = scene.instantiate()
	if instance == null:
		print("[FAIL] %s - Failed to instantiate" % path)
		failed += 1
		return

	# Clean up
	instance.queue_free()

	print("[PASS] %s" % path)
	passed += 1
