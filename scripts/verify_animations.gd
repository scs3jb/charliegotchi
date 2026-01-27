extends SceneTree

func _init():
    print("Starting Animation Verification...")
    var failed = false

    # Load Resources
    var player_script = load("res://scripts/player/Player.gd")
    var sprite_frames = load("res://resources/sprites/player_frames.tres")
    
    if not player_script:
        print("[FAIL] Could not load Player.gd")
        quit(1)
        return
        
    if not sprite_frames:
        print("[FAIL] Could not load player_frames.tres")
        quit(1)
        return

    # Create Player Mock
    var player = player_script.new()
    var anim_sprite = AnimatedSprite2D.new()
    anim_sprite.name = "AnimatedSprite2D"
    anim_sprite.sprite_frames = sprite_frames
    player.add_child(anim_sprite)
    
    # We need to add to tree to get _ready to run, or just manually set it up
    # Player.gd _ready puts it in group, gets ref. Let's just manually set ref.
    player.animated_sprite = anim_sprite
    
    print("Verifying Animations...")
    
    # Define test cases
    # Format: [Case Name, Input Vector, IsHolding, Expected Animation]
    var tests = [
        ["Idle Down", Vector2.ZERO, false, "idle_down"],
        ["Walk Down", Vector2.DOWN, false, "walk_down"],
        ["Walk Left", Vector2.LEFT, false, "walk_left"],
        ["Idle Left (Standard)", Vector2.ZERO, false, "idle_left"], # Assumes set from prev move
        
        # Holding Tests
        ["Hold Idle Down", Vector2.ZERO, true, "hold_idle_down"],
        ["Hold Walk Down", Vector2.DOWN, true, "hold_walk_down"],
        ["Hold Walk Up", Vector2.UP, true, "hold_walk_up"],
        ["Hold Walk Left", Vector2.LEFT, true, "hold_walk_left"],
        ["Hold Walk Right", Vector2.RIGHT, true, "hold_walk_right"],
        
        # The Critical Tests (Flashing Fix)
        ["Hold Idle Up", Vector2.ZERO, true, "hold_idle_up"],
        ["Hold Idle Left", Vector2.ZERO, true, "hold_idle_left"],
        ["Hold Idle Right", Vector2.ZERO, true, "hold_idle_right"]
    ]
    
    # Helper to set facing direction
    # Player.gd logic: facing updated in process if input != zero. 
    # If input == zero, it keeps previous.
    
    for start_facing in [Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT, Vector2.UP]:
        player.facing_direction = start_facing
        
        for t in tests:
            var case_name = t[0]
            var input = t[1]
            var holding = t[2]
            var expected_base = t[3]
            
            # Setup State
            player.held_object = Node2D.new() if holding else null
            
            # If test relies on facing direction (idle), skip if facing doesn't match context
            # Test cases above are a bit generic, let's refine logic:
            
            # We want to verify that GIVEN a facing direction and input, we get a valid animation
            
            # Simulate _update_animation directly
            # Update facing first if moving
            if input != Vector2.ZERO:
                player.facing_direction = input
            
            player._update_animation(input)
            
            var selected_anim = anim_sprite.animation
            
            # Check if animation exists in resource
            if not sprite_frames.has_animation(selected_anim):
                print("  [FAIL] Animation '%s' selected but MISSING in resource (Ctx: %s, Facing: %s)" % [selected_anim, case_name, player.facing_direction])
                failed = true
            else:
                # print("  [OK] Animation '%s' exists" % selected_anim)
                pass
                
            # Verify correctness for specific known states
            # e.g. if holding and idle and facing UP, MUST be hold_idle_up
            if holding and input == Vector2.ZERO:
                var expected = "hold_idle_"
                if player.facing_direction.y > 0: expected += "down"
                elif player.facing_direction.y < 0: expected += "up"
                elif player.facing_direction.x > 0: expected += "right"
                elif player.facing_direction.x < 0: expected += "left"
                
                if selected_anim != expected:
                     print("  [FAIL] Wrong animation selected. Expected '%s', Got '%s' (Holding, Facing: %s)" % [expected, selected_anim, player.facing_direction])
                     failed = true
                else:
                    pass # Correct

    if failed:
        print("VERIFICATION FAILED")
        quit(1)
    else:
        print("ALL ANIMATIONS VERIFIED SUCCESSFUL")
        quit(0)
