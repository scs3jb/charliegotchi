extends Node2D

func _ready():
    print("--- STARTING FULL PROJECT VERIFICATION ---")
    var scenes = [
        "res://scenes/props/Tree.tscn",
        "res://scenes/House.tscn",
        "res://scenes/Overworld.tscn"
    ]
    
    var failed = false
    
    # Check if Autoloads are actually here
    if not is_instance_valid(get_node_or_null("/root/GameState")):
        print("[FAIL] GameState Autoload is missing!")
        failed = true
    if not is_instance_valid(get_node_or_null("/root/TimeWeather")):
        print("[FAIL] TimeWeather Autoload is missing!")
        failed = true
        
    for scene_path in scenes:
        print("Testing Scene: ", scene_path)
        var scene = load(scene_path)
        if not scene:
            print("[FAIL] Could not load file: ", scene_path)
            failed = true
            continue
            
        var instance = scene.instantiate()
        if not instance:
            print("[FAIL] Could not instantiate: ", scene_path)
            failed = true
        else:
            print("[OK] Instantiated: ", scene_path)
            add_child(instance)
            # Wait a few frames for things to settle
            for i in range(5):
                await get_tree().process_frame
            instance.queue_free()
            # Wait for queue_free to finish
            for i in range(5):
                await get_tree().process_frame
            
    if failed:
        print("!!! VERIFICATION FAILED !!!")
        get_tree().quit(1)
    else:
        print("*** ALL SYSTEMS GO: PROJECT VERIFIED ***")
        # Give a bit more time for everything to clean up
        await get_tree().create_timer(0.5).timeout
        get_tree().quit(0)
