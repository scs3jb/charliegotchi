# Feeding Minigame (Match-3) Implementation Plan

## Context
The food bowl interaction in the House scene currently calls `GameState.do_feed()` with a one-line message. We're replacing it with a Candy Crush-style match-3 minigame per the spec in `feeding-mini-game.md`. Charlie is allergic to chicken — matching chicken tiles is bad, matching safe kibble fills his bowl.

## New Files (4)

### `scripts/minigames/MatchBoard.gd` — Pure data model
Core match-3 logic with no visuals. Extends `RefCounted` (no scene tree needed).

**Exported config** (all tunable):
- `board_cols = 7`, `board_rows = 7`
- `move_limit = 20`
- `bowl_fill_per_tile = 0.04` (each safe tile in a match adds ~4%, so a 3-match = 12%)
- `chicken_penalty_per_tile = 0.03`
- `fail_bonding_penalty = 0.10`, `fail_entertainment_penalty = 0.05`
- Tile weights: brown=20, salmon=20, green=20, orange=20, blue=15, chicken=5

**TileType enum**: KIBBLE_BROWN, KIBBLE_SALMON, KIBBLE_GREEN, KIBBLE_ORANGE, KIBBLE_BLUE, CHICKEN

**Key methods**:
- `initialize_board()` — Fill 7x7 grid with weighted random tiles, avoiding initial matches (check 2 left + 2 above when placing each tile)
- `try_swap(a: Vector2i, b: Vector2i) -> bool` — Validate adjacency, temporarily swap in grid, check for matches at both positions, swap back if invalid. If valid: decrement moves, return true
- `find_all_matches() -> Array[Array]` — Horizontal scan: track runs per row; Vertical scan: track runs per column. Return groups of 3+ positions
- `process_matches() -> Dictionary` — Loop: find matches → score (safe vs chicken) → clear cells to -1 → gravity (compact each column downward) → refill empty cells from top → repeat until no matches. Returns `{safe_count, chicken_count, had_matches}`
- `apply_gravity() -> Array` — Per column bottom-to-top: shift non-empty cells down. Returns `[{from, to}]`
- `refill_board() -> Array` — Fill remaining -1 cells with weighted random tiles. Returns `[{col, row, type}]`
- `has_any_valid_moves() -> bool` — Check every adjacent pair for potential matches. If none, reshuffle board
- `check_game_end() -> String` — Returns "won" if bowl_fill >= 1.0, "lost" if moves_remaining <= 0, "" otherwise

**State vars**: `grid: Array` (2D int array), `moves_remaining: int`, `bowl_fill: float`

### `scripts/minigames/FeedingMinigame.gd` — Scene controller + rendering
Extends `Node2D`. Attached to the scene root. Handles all visuals, input, UI, tutorial, results.

**Tile rendering**: Creates ColorRect nodes as children of a `board_container` Node2D. Each tile is 28x28px with 2px gap. Board pixel size = 7×30-2 = 208px. Board positioned center-left of viewport. Tile colors:
- Brown: `Color(0.55, 0.35, 0.2)`, Salmon: `Color(0.85, 0.5, 0.5)`, Green: `Color(0.35, 0.65, 0.3)`
- Orange: `Color(0.9, 0.6, 0.2)`, Blue: `Color(0.4, 0.45, 0.8)`, Chicken: `Color(0.95, 0.85, 0.4)` with red border

**Input**: Click tile A to select (yellow highlight border), click adjacent tile B to swap. If swap invalid, briefly shake both tiles. Input blocked during animations (`is_animating` flag).

**Animations** (all via `create_tween()`):
- Swap: tween positions of two tiles (0.15s)
- Clear: scale tiles to 0 + modulate to white (0.2s)
- Fall: tween tiles to new positions (0.15s)
- Spawn: new tiles start above board, tween down (0.15s)
- Chicken match: flash board red briefly, shake Charlie portrait

**UI elements** (built in `_ready()`):
- Right side: Bowl fill ProgressBar (vertical) + "Moves: N" Label
- Left side: Charlie portrait (small colored rect) + reaction Label ("BARK!" on chicken)
- Top-right: Exit "X" Button → shows confirm Panel

**Tutorial** (shown once):
- Checks `GameState.has_seen_feeding_tutorial`
- If false: semi-transparent overlay + multi-page Panel explaining mechanics
- "Next" / "Let's eat!" button to advance pages
- Sets flag to true when dismissed
- Emits signal to start game

**Results overlay**:
- Win: "Yummy! Charlie loved his meal!" + stats summary + "Back to House" button
- Fail: "Oh no..." + penalty summary + "Back to House" + "Try Again" buttons
- Calls `GameState.do_feed_win()` or `GameState.do_feed_fail()` before showing

### `scenes/minigames/FeedingMinigame.tscn` — Minimal scene
Just the root `Node2D` with `FeedingMinigame.gd` attached. All child nodes created dynamically in `_ready()` to keep the scene file small and the layout logic centralized in one script.

### (No separate UI/tutorial/results scripts — all handled by FeedingMinigame.gd to keep file count low)

## Modified Files (3)

### `scripts/autoload/GameState.gd`
- Add `var has_seen_feeding_tutorial: bool = false`
- Add `do_feed_win()`: sets `hunger = 1.0`, `entertainment = 1.0`, calls `add_bonding(0.25)`, increments `feed_count`
- Add `do_feed_fail(bonding_penalty, entertainment_penalty)`: calls `add_bonding(-penalty)`, `add_entertainment(-penalty)`, increments `feed_count`
- Add `has_seen_feeding_tutorial` to `save_game()` dict, `load_game()` with `.get()` default `false`, and `reset_game()`

### `scripts/scenes/House.gd`
- Replace `_feed_charlie()` body (lines 131-141): show brief message, make Charlie walk to bowl, then `get_tree().change_scene_to_file("res://scenes/minigames/FeedingMinigame.tscn")`

### `test_scenes.gd`
- Add `"res://scenes/minigames/FeedingMinigame.tscn"` to `scenes_to_test` array

## Match-3 Algorithm Detail

**Match detection** (`find_all_matches`):
1. Horizontal: for each row, scan left→right tracking runs of same type. When run length ≥ 3, collect all positions
2. Vertical: same for each column top→bottom
3. Return array of match groups (positions may overlap for L/T shapes — that's fine, we deduplicate when clearing)

**Cascade loop** (`process_matches`):
```
while find_all_matches() has results:
    score matches (safe += bowl, chicken -= bowl)
    clear matched cells (set grid to -1)
    apply_gravity (compact columns downward)
    refill_board (fill -1 cells from top)
    # loop catches chain reactions from new tiles
check for deadlock (no valid moves → shuffle)
check_game_end()
```

**Animation sequencing**: FeedingMinigame.gd calls `try_swap()` on board, then if valid, runs the visual cascade loop with `await` between each phase (swap anim → clear anim → fall anim → spawn anim → check for more matches).

## Board Layout (426x240 viewport)

```
+--Charlie--+------Board (208x208)------+--Bowl--+
|  portrait |                            |  meter |
|   40x40   |   7x7 grid of 28px tiles  |  bar   |
|           |   with 2px gaps            | moves  |
|  [BARK!]  |                            | label  |
|           |                            |  [X]   |
+-----------+----------------------------+--------+
     80px            220px                  126px
```

Board origin: x=95, y=16 (centered vertically with top margin for UI)

## Transition Flow
1. Player presses E at food bowl → House.gd shows message, Charlie walks to bowl
2. After 1s delay → `change_scene_to_file("res://scenes/minigames/FeedingMinigame.tscn")`
3. Minigame loads → tutorial (first time) → board initializes → play
4. Win/Fail → results overlay → "Back to House" button → `change_scene_to_file("res://scenes/House.tscn")`
5. "Try Again" (fail only) → reinitializes board, hides results

## Verification
```bash
rm -rf .godot/imported && godot --headless --import
godot -s scripts/verify_animations.gd --headless   # 21 checks pass
godot -s test_scenes.gd --headless                  # 10 checks pass (9 existing + 1 new)
```
