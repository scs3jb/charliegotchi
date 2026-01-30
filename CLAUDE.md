# Charlie's Island Adventure - Development Guide

## Project Overview
A 2D top-down pet-care + exploration game starring baby Shih Tzu Charlie.
Built with Godot 4.x and GDScript.

## How to Build and Test

### Running the Game
To run the game run godot from the commandline
```bash
godot
```

### Automated Verification
Automated verificaiton should be run everytime assets or scenes are changed.
Also delete assets in .godot/imported and reimport to make sure they work.
Claude must always verify the integrity of animations and scenes (headless mode):
```bash
godot -s scripts/verify_animations.gd --headless  # Checks Player.gd animation logic
godot -s test_scenes.gd --headless            # Checks scene loading
```
Animation must be smooth with no visual issues.

## Project Structure

```
charligotchi/
├── project.godot          # Godot project file
├── scenes/                # All .tscn scene files
│   ├── MainMenu.tscn
│   ├── Cutscene_Intro.tscn
│   ├── Beach_Start.tscn
│   ├── House.tscn
│   ├── Overworld.tscn
│   ├── Battle_Tutorial.tscn
│   └── ui/
├── scripts/               # All .gd script files
│   ├── autoload/          # Singleton scripts
│   │   ├── GameState.gd   # Charlie stats, save/load, game progress
│   │   ├── TimeWeather.gd # Day/night cycle, weather, seasons
│   │   └── DebugMenu.gd   # F3 debug overlay for testing
│   ├── player/
│   │   └── Player.gd      # Handles movement, pickup, and animation state
│   ├── charlie/
│   │   └── Charlie.gd     # Handles AI states (follow, fetch, keep-away, wildlife attraction)
│   ├── wildlife/          # Wildlife encounter system
│   │   ├── Wildlife.gd    # Base class for all wildlife
│   │   ├── Butterfly.gd   # Flutter movement, wing animation
│   │   ├── Bird.gd        # Hopping/flying, pecking animation
│   │   ├── Squirrel.gd    # Fast scurrying, foraging behavior
│   │   └── WildlifeSpawner.gd  # Manages wildlife spawning
│   └── ui/
├── assets/                # Art, audio, fonts
│   ├── sprites/
│   │   └── characters/
│   │       ├── player_spritesheet.png  # Generated 128x416 sheet
│   │       ├── charlie_spritesheet.png # Generated sheet
│   │       └── ball_spritesheet.png
└── resources/             # .tres resource files
    └── sprites/
        └── player_frames.tres # Maps animations to player_spritesheet.png
```

## Dev Status: Pixel Art Integration
**(Updated 2026-01-30)**

High-quality, retro-style pixel art is now generated procedurally using Python (PIL).

### Generation Scripts
Run these scripts to regenerate assets if needed. First set up the Python environment:
```bash
uv venv && source .venv/bin/activate && uv pip install pillow
```

Then run the generators:
```bash
.venv/bin/python scripts/generate_player_extended.py  # Generates player_spritesheet.png (13 rows)
.venv/bin/python generate_pixel_charlie.py            # Generates charlie_spritesheet.png
```

After regenerating, reimport assets and run verification:
```bash
rm -rf .godot/imported
godot --headless --import
godot -s scripts/verify_animations.gd --headless
godot -s test_scenes.gd --headless
```

### Sprite Sheet Layout (Player)
The `player_spritesheet.png` (128x416) contains 13 rows, each with 4 frames (32x32):
1.  **Idle Down** (Breathing)
2.  **Bored** (Tapping foot)
3.  **Confused** (Question mark)
4.  **Walk Left**
5.  **Walk Right**
6.  **Walk Up**
7.  **Walk Down**
8.  **Pickup** (Bending down)
9.  **Hold Idle** (Standing holding Charlie)
10. **Hold Walk Left**
11. **Hold Walk Right**
12. **Hold Walk Up**
13. **Hold Walk Down**

## Common Fixes & Troubleshooting

### Sprites Flickering / Wrong Animation
If the player sprite flickers or shows the wrong frame:
1.  **Check Resources**: Ensure `resources/sprites/player_frames.tres` has the animation defined.
2.  **Clear Cache**: Sometimes imports get stuck. Run:
    ```bash
    rm -rf .godot/imported
    ```
    Then reopen Godot to force a reimport.
3.  **Verify Logic**: Run `godot -s scripts/verify_animations.gd --headless` to check if `Player.gd` is requesting valid animations.

### "Identifier Not Found" Errors
If loading scenes fails with "Identifier not found: GameState":
- This usually happens in headless test scripts if Autoloads aren't initialized manually.
- The game itself should run fine as `project.godot` handles Autoloads.

## Current Status (Playable)

1.  **Start**: Intro cutscene -> Beach.
2.  **Beach**: Find Charlie in the box.
3.  **House**: Feed, pet, play fetch.
    *   Pick up Charlie (Interact 'E') and walk him around.
    *   Drop Charlie (Interact 'E' while holding).
4.  **Overworld**: Explore with Charlie on leash.
    *   Wildlife (butterflies, birds, squirrels) spawn periodically.
    *   Charlie spots wildlife and pulls toward them.
    *   When Charlie gets close, wildlife flees and Charlie gains entertainment.

## Game Systems

### Charlie's Stats
Charlie has three core stats stored in `GameState.gd` (values 0.0 to 1.0):

| Stat | Decay Rate | Description |
|------|------------|-------------|
| **Hunger** | -5% every 8 game hours | 1.0 = full, 0.0 = starving |
| **Entertainment** | -1% every 8 game hours | How entertained Charlie is |
| **Bonding** | -2% every 24 game hours | Relationship with player |

Stats affect Charlie's behavior:
- **High bonding (≥0.5)**: Charlie follows player nicely on leash, less distracted by wildlife
- **Low bonding (<0.5)**: Charlie wanders randomly, resists leash strongly, very distracted by wildlife

Increasing stats:
- **Petting**: Press E near Charlie in Overworld to pet (+5% bonding)
- **Wildlife**: Let Charlie chase wildlife in Overworld (+2-6% entertainment depending on type)

### Debug Menu (F3)
Press F3 to toggle the debug overlay. Features:
- Sliders to adjust bonding, entertainment, hunger
- Time skip buttons (+1 hour, +1 day)
- Fill/Empty buttons for quick testing
- Leash tension/resistance display when in Overworld

### Leash Mechanics
When Charlie is on leash in the Overworld (`scripts/charlie/Charlie.gd`):

| Parameter | Value | Description |
|-----------|-------|-------------|
| `leash_max_distance` | 96px | 3x Charlie's body length |
| Resistance threshold | 70% tension | No resistance below this |
| Full resistance | 100% tension | Maximum player slowdown |

Resistance rules:
- Only applies when player walks **away** from Charlie
- Walking toward Charlie = no resistance
- At max leash length: Charlie gets **dragged** reluctantly, player speed drops to ~15px/s
- Leash visual changes color/thickness when taut
- Leash attaches to player's hand (offset varies by facing direction)
- Leash attaches to Charlie's collar (below head)

### Day/Night Cycle
Configured in `TimeWeather.gd`:
- `time_scale = 15.0`: 1 real second = 0.25 game minutes
- Full day cycle takes ~96 real minutes
- Ambient lighting changes based on time of day

### Wildlife Encounters
Wildlife spawns in the Overworld for Charlie to spot and chase (`scripts/wildlife/`).

| Wildlife Type | Speed | Flee Speed | Detection | Entertainment |
|---------------|-------|------------|-----------|---------------|
| **Butterfly** | 25 | 80 | 50px | +2% |
| **Bird** | 35 | 150 | 70px | +4% |
| **Squirrel** | 55 | 180 | 90px | +6% |

Spawning rules (`WildlifeSpawner.gd`):
- Max 4 wildlife at once
- Spawn interval: 8-15 seconds
- Weighted selection: butterflies (50%), birds (30%), squirrels (20%)
- Reduced spawns at night (70% skip chance)
- Reduced spawns in rain (60% skip chance)
- Reduced spawns in snow (80% skip chance)

Charlie's attraction behavior:
- `wildlife_attraction_radius = 120px`: Charlie notices wildlife within this range
- `wildlife_excitement`: 0.0 to 1.0 based on proximity to wildlife
- Higher bonding = less distraction (trained dogs focus better)
- Charlie pulls toward wildlife, increasing leash tension
- Leash turns orange when Charlie is excited about wildlife

When Charlie gets close enough:
- Wildlife flees (state changes to FLEEING)
- Charlie gains entertainment based on wildlife type
- Wildlife fades out and despawns after 1.5 seconds

## Scene-Specific Rules

### Intro Cutscene (`Cutscene_Intro.tscn`)
- Shake effects only apply to `SceneContent` node
- `NarrationPanel` and `SkipButton` remain stationary for readability

### Beach Scene (`Beach_Start.tscn`)
- Player cannot enter deep water (dark blue) or go off top of screen
- Invisible `StaticBody2D` boundaries constrain movement
- When picking up Charlie, `player.can_drop = false` until scene transition
- Uses full animated player sprite (not placeholder)

### Overworld (`Overworld.tscn`)
- Charlie is always on leash
- `LeashLine` (Line2D) renders between player hand and Charlie collar
- Player speed reduces based on Charlie's resistance
- `WildlifeSpawner` node manages wildlife spawning
- Wildlife (butterflies, birds, squirrels) spawn periodically
- Charlie gets excited and pulls toward nearby wildlife
- Leash color changes to orange when Charlie spots wildlife

### Pending Features
- Sleep system
- Sniffari mechanics
