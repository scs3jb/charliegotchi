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
│   ├── player/
│   │   └── Player.gd      # Handles movement, pickup, and animation state
│   ├── charlie/
│   │   └── Charlie.gd     # Handles AI states (follow, fetch, keep-away)
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
 **(Updated 2026-01-27)**

High-quality, retro-style pixel art is now generated procedurally using Python (PIL).

### Generation Scripts
Run these scripts to regenerate assets if needed (requires `pip install pillow`):
- `python scripts/generate_player_extended.py`: Generates `player_spritesheet.png` (13 rows).
- `python generate_charlie_spritesheet.py`: Generates `charlie_spritesheet.png`.

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
    *   **New**: Pick up Charlie (Interact 'E') and walk him around.
    *   **New**: Drop Charlie (Interact 'E' while holding).
4.  **Overworld**: Explore with Charlie following.

### Pending Features
- Wildlife encounters
- Sleep system
- Sniffari mechanics
