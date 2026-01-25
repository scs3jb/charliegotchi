# Charlie's Island Adventure - Development Guide

## Project Overview
A 2D top-down pet-care + exploration game starring baby Shih Tzu Charlie.
Built with Godot 4.x and GDScript.

## How to Build and Test

### Opening the Project
1. Open Godot 4.x
2. Click "Import"
3. Navigate to this folder and select `project.godot`
4. Click "Import & Edit"

### Running the Game
1. Press F5 (or click the Play button in top-right)
2. If prompted, select `scenes/MainMenu.tscn` as the main scene

### Testing Individual Scenes
- Press F6 to run the currently open scene
- Or right-click a scene in FileSystem and select "Run This Scene"

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
│       └── UI_HUD.tscn
├── scripts/               # All .gd script files
│   ├── autoload/          # Singleton scripts
│   │   ├── GameState.gd
│   │   └── TimeWeather.gd
│   ├── player/
│   │   └── Player.gd
│   ├── charlie/
│   │   └── Charlie.gd
│   └── ui/
│       └── HUD.gd
├── assets/                # Art, audio, fonts
│   ├── sprites/
│   ├── audio/
│   └── fonts/
└── resources/             # .tres resource files
```

## Development Phases

### Phase 0: Intro Cutscene (Non-Interactive)
- [x] Create intro cutscene scene
- [x] Storm animation with Charlie on raft
- [x] Auto-transition to beach

### Phase 1: House and Bonding
- [ ] Character customization (NOT YET IMPLEMENTED)
- [x] Beach scene - find Charlie
- [x] Food mini-game
- [x] House interior
- [x] Feed, pet, fetch mechanics
- [x] Stats UI (Heart/Entertainment bars)
- [x] Door unlock system

### Phase 2: Outside with Lead
- [x] Lead/harness system
- [x] Outdoor navigation
- [x] Leash behavior physics
- [x] Day/night cycle
- [x] Seasons
- [x] Weather system

### Overworld Features (PARTIALLY IMPLEMENTED)
- [x] Day/night cycle
- [x] Seasons
- [x] Weather system
- [ ] Sniffari mechanic
- [ ] Poop pickup mini-game

### Wildlife Encounters (NOT YET IMPLEMENTED)
- [ ] Tutorial battle screen
- [ ] Animal AI
- [ ] Charlie actions

### Sleep System (NOT YET IMPLEMENTED)
- [ ] First sleep cutscene
- [ ] Quick sleep unlock

## Current Status

**CORE GAME LOOP IS PLAYABLE!**

The game can be played from start through Phase 2:
1. Main Menu -> New Game
2. Intro cutscene (skippable)
3. Beach scene - find Charlie in box, food mini-game
4. House - feed, pet, play fetch to build bonding/entertainment
5. When both stats are 100%, door unlocks
6. Overworld - explore outside with Charlie on leash

### Validation Status (Tested 2026-01-24)
- All scenes load without errors
- Game runs at 165 FPS (Godot 4.5.1)
- Autoload singletons initialize correctly
- Scene transitions configured correctly

### Known Issues / Missing Features
- No collision shapes on characters (need to add in editor)
- Character customization not implemented
- Wildlife encounters not implemented
- Sleep system not implemented
- Sniffari/poop mechanics not implemented
- No audio

## Art Assets

### Generated Pixel Art (2026-01-25)
All sprites generated using PIL/Pillow with Link to the Past-inspired pixel art style.

**Characters:**
- `charlie.png` (32x32) - Baby Shih Tzu puppy sprite
- `charlie_large.png` (48x48) - Larger version for close-ups
- `charlie_in_box.png` (48x48) - Charlie peeking from cardboard box
- `charlie_in_box_large.png` (64x64) - Large version for intro scene
- `player.png` (32x32) - Blonde girl player character
- `player_large.png` (48x48) - Larger version

**Environment - Storm Scene:**
- `storm_sky.png` (426x160) - Dramatic dark stormy sky with layered clouds
- `storm_ocean.png` (426x120) - Turbulent ocean with rolling waves and foam

**Environment - Beach Scene:**
- `beach_sand.png` (426x140) - Detailed sandy beach with grain texture, shells, driftwood, and wet sand gradient
- `beach_ocean.png` (426x80) - Calm beach ocean with gentle waves

**Props:**
- `raft_large.png` (96x96) - Wooden log raft with rope bindings
- `raft.png` (64x64) - Smaller raft version
- `box_closed.png` (40x40) - Cardboard box prop
- `driftwood.png` (48x16) - Beach driftwood
- `shell.png` (12x12) - Seashell decoration

**Effects:**
- `lightning.png` (80x160) - Forked lightning bolt with glow effect
- `rain.png` (64x64) - Rain particle sheet
- `wind_line.png` (100x16) - Horizontal wind streak effect
- `spray.png` (16x16) - Ocean spray particle

### Regenerating Assets
Run the asset generation scripts:
```bash
python generate_assets.py           # Base character/environment assets
python generate_enhanced_assets.py  # Enhanced storm and beach textures
```
Requires: `pip install pillow`

## Controls

| Action | Keyboard | Touch |
|--------|----------|-------|
| Move | WASD / Arrow Keys | Virtual Joystick |
| Interact | E / Space | Tap |
| Open Menu | Escape | Menu Button |

## Creating Assets

### Sprites
- Use 16x16 or 32x32 pixel art for characters
- Link to the Past style: outlined sprites, vibrant colors
- Charlie: Small white/cream Shih Tzu puppy
- Player: Blonde girl with simple outfit

### Importing Sprites
1. Drag PNG files into `assets/sprites/` folder
2. Select sprite in FileSystem
3. In Import tab: Filter = Off (for pixel art)
4. Click "Reimport"

## Common Fixes

### Sprites Look Blurry
- Select sprite → Import tab → Filter: Off → Reimport

### Character Falls Through Floor
- Add CollisionShape2D to both character and floor
- Set proper collision layers/masks

### Scene Won't Load
- Check for circular dependencies
- Verify all referenced resources exist

## Prompts for Future Sessions

### To continue development:
"Continue building Charlie's Island Adventure. Check CLAUDE.md for current progress and pick up where we left off."

### To add a specific feature:
"Add the [FEATURE NAME] to Charlie's Island Adventure following the spec in charlie-island-adventure-spec.md"

### To fix a bug:
"There's a bug in [SCENE/SCRIPT]: [DESCRIPTION]. Please fix it."
