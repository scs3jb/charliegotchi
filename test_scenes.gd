extends SceneTree

func _init():
    var scenes = [
        "res://scenes/MainMenu.tscn",
        "res://scenes/Overworld.tscn",
        "res://scenes/House.tscn",
        "res://scenes/Beach_Start.tscn",
        "res://scenes/Cutscene_Intro.tscn"
    ]
    
    var failed = false
    
    for scene_path in scenes:
        print("Testing load: " + scene_path)
        if ResourceLoader.exists(scene_path):
            var scene = load(scene_path)
            if scene:
                print("  [OK] Loaded successfully")
                var instance = scene.instantiate()
                instance.free()
            else:
                print("  [FAIL] Failed to load resource (null)")
                failed = true
        else:
            print("  [FAIL] Resource does not exist")
            failed = true
            
    if failed:
        print("SOME TESTS FAILED")
        quit(1)
    else:
        print("ALL SCENES PASSED")
        quit(0)
