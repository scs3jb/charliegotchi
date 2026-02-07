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
## Key Files
- `scripts/generate_populated_overworld.py` - Generates `scenes/Overworld.tscn` with all props. ~1288 props across 24 screens (6x4 grid). Uses smart placement helpers (rejection sampling, Gaussian clusters, wall formations).
- `generate_scene()` in that file contains the full .tscn template including Charlie atlas textures, HUD, Player, etc. Only prop generation functions above it should be modified for density/placement changes.

## Architecture Notes
- House is at position (640, 320) in the Overworld scene. Exclusion zone for props: (580, 260) to (700, 420).
- Biome grid is 6 cols x 4 rows, each screen 426x240px, total world 2556x960px.
- Props use PackedScene instances (Tree, Rock, Bush, Fence, FlowerPatch, WaterBody, MountainWall, CliffWall, PathTile, BridgeTile, Signpost).

### Automated Verification
Automated verificaiton should be run everytime assets or scenes are changed.
Also delete assets in .godot/imported and reimport to make sure they work.
Claude must always verify the integrity of animations and scenes (headless mode):
```bash
godot -s scripts/verify_animations.gd --headless  # Checks Player.gd animation logic
godot -s test_scenes.gd --headless            # Checks scene loading
```
- Always `rm -rf .godot/imported && godot --headless --import` after asset changes.
- Autoload errors in headless mode ("Identifier not found: GameState/TimeWeather") are expected and benign — the scenes still load fine.
- Animation must be smooth with no visual issues.

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
│   │   ├── characters/
│   │   │   ├── player_spritesheet.png  # Generated 128x416 sheet
│   │   │   ├── charlie_spritesheet.png # Generated sheet
│   │   │   └── ball_spritesheet.png
│   │   └── tiles/
│   │       └── terrain_atlas.png       # Generated 256x256 tileset
├── scenes/
│   └── props/
│       ├── Tree.tscn      # Interactable tree with trunk/canopy split
│       ├── Rock.tscn      # Impassable rock cluster
│       ├── Bush.tscn      # Dense blocking bush
│       └── Fence.tscn     # Wooden fence section
└── resources/             # .tres resource files
    ├── sprites/
    │   └── player_frames.tres # Maps animations to player_spritesheet.png
    └── tilesets/
        └── overworld_tileset.tres # TileSet resource for terrain
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
.venv/bin/python scripts/generate_tileset.py          # Generates terrain_atlas.png (16x16 tiles)
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

### Terrain Tileset (`assets/sprites/tiles/terrain_atlas.png`)
Generated 256x256 atlas with 16x16 tiles. Run `scripts/generate_tileset.py` to regenerate.

**Tile Index Reference**:
| Index Range | Tile Type |
|-------------|-----------|
| 0-15 | Grass variants (0=base, 1=light, 2=dark, 3-6=flowers) |
| 16-31 | Dirt/path (16=base, 17-24=edges) |
| 32-47 | Sand (32=base, 33-40=edges) |
| 48-55 | Water (48-51=shallow animated, 52-55=deep animated) |
| 56-79 | Water edges |
| 80-95 | Cliff/mountain (80=base, 81=top with grass) |
| 96-97 | Bridge (96=horizontal, 97=vertical) |

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

### Sniffari Mechanic
A specialized exploration mode where Charlie leads the player.
-   **Trigger**: Press **[F]** when near Charlie in the Overworld (if available).
-   **Availability**: Every **3 in-game hours**.
-   **Full Bonding Rule**: If full bonding (1.0) is reached after a Sniffari, another cannot be started until the **next in-game day**.
-   **Duration**: 50 seconds.
-   **Behavior**: Charlie automatically visits trees, pees, chases wildlife, or sniffs grass.
-   **Follow Logic**: Player automatically follows Charlie at leash distance with smooth interpolation.
-   **Rewards**: **+20% Bonding** every 10 seconds (total +100% possible).

### Tree Interactions & Peeing
Charlie naturally interacts with trees in the Overworld.
-   **Boredom Trigger**: Charlie seeks a tree after 5s of being idle or wandering.
-   **On-Leash Behavior**: Charlie will actively pull toward a tree if leashed, slowing the player.
-   **Peeing Duration**: 6 to 8 seconds.
-   **Visuals**: Subtle yellow particle stream and a temporary puddle (3-4s lifetime).
-   **Refractory Period**: Charlie will not pee on the same tree again for **4 in-game hours**.
-   **Interruption**: Picking Charlie up or starting a Sniffari cancels peeing and leaves a small "partial" puddle.

## Scene-Specific Rules

### Environment & Layering (Y-Sorting)
See [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) for full details.
-   **Origins**: Must be at the "feet" or "base" of the object for correct Y-sorting.
-   **Trees**: Use a split-sprite system (Trunk at `z_index 0`, Canopy at `z_index 1`).
-   **Background**: Tiles/Large areas must be at `z_index -1`.
-   **Leash**: Align points to the new feet-based origins (Hand: `Vector2(8, -14)`, Collar: `Vector2(0, -20)`).

### Intro Cutscene (`Cutscene_Intro.tscn`)
- Shake effects only apply to `SceneContent` node
- `NarrationPanel` and `SkipButton` remain stationary for readability

### Beach Scene (`Beach_Start.tscn`)
- Player cannot enter deep water (dark blue) or go off top of screen
- Invisible `StaticBody2D` boundaries constrain movement
- When picking up Charlie, `player.can_drop = false` until scene transition
- Uses full animated player sprite (not placeholder)

### Overworld (`Overworld.tscn`)
- **Multi-Screen World**: 6x4 grid of screens (2556x960 pixels total)
- **Screen Size**: 426x240 pixels (viewport size)
- **Zelda-style Transitions**: Camera scrolls when player crosses screen boundaries
- Charlie is always on leash
- `LeashLine` (Line2D) renders between player hand and Charlie collar
- Player speed reduces based on Charlie's resistance
- `WildlifeSpawner` node manages wildlife spawning (per-screen bounds)
- Wildlife (butterflies, birds, squirrels) spawn periodically
- Charlie gets excited and pulls toward nearby wildlife
- Leash color changes to orange when Charlie spots wildlife

**Biome Layout (6x4 grid)**:
```
[Beach ] [Meadow] [Meadow] [Forest] [Forest] [Mountain]
[Beach ] [Home  ] [Meadow] [Forest] [Lake  ] [Mountain]
[Beach ] [Meadow] [Path  ] [Path  ] [Lake  ] [Mountain]
[Cliffs] [Cliffs] [Bridge] [Path  ] [Forest] [Mountain]
```

**Screen Transition Behavior**:
- Player/Charlie movement frozen during 0.4s transition
- Camera limits tween to new screen bounds
- Charlie pulled along with player through transitions
- Wildlife spawner bounds updated per-screen
- Position saved to GameState for persistence

### Pending Features
- Sleep system
- Paint tiles in TileMap (currently using fallback ColorRect background)
- Add collision shapes to water/cliff tiles in TileSet
