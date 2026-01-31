# Environment & Layering Guide

This guide explains how to add new environmental objects (like trees) and maintain the pixel-perfect Y-sorting system in Charlie's Island Adventure.

## 1. The Y-Sorting System

To achieve realistic 2D depth where characters can walk both in front of and behind objects, we use **Godot 4's Y-Sorting**.

### Core Requirements:
1.  **Feet-Based Origins**: Every character and environmental object must have its `position` (0,0) at its "feet" or "ground contact point".
2.  **Parent Y-Sort Enabled**: The root node of the scene (e.g., `Overworld`) and any container nodes must have `y_sort_enabled = true`.
3.  **Child Sprite Settings**: 
    *   Child sprites should have `y_sort_enabled = false`.
    *   Sprites must be offset vertically so that their visual bottom aligns with the parent's (0,0) origin.

### Character Example (Player/Charlie):
*   **Node**: `CharacterBody2D` (Position: ground level)
*   **Sprite**: `AnimatedSprite2D` (Position: `Vector2(0, -16)` for 32x32 sprites)
*   **Collision**: `CollisionShape2D` (Position: `Vector2(0, -2)` for feet-only collision)

---

## 2. Adding a New Tree

Trees use a **Split-Sprite System** to ensure characters can walk behind the trunk while the leaves always stay in the foreground.

### Tree Scene Structure (`Tree.tscn`):
1.  **StaticBody2D** (Root)
    *   `y_sort_enabled = true`
2.  **TrunkSprite** (Child of Root)
    *   `y_sort_enabled = false`
    *   `z_index = 0`
    *   `texture_filter = Nearest`
    *   `region_enabled = true` (Select only the trunk pixels)
    *   Position: Offset so the bottom of the trunk is at `(0,0)`.
3.  **CanopySprite** (Child of Root)
    *   `z_index = 1` (Always stays in front of the player)
    *   `texture_filter = Nearest`
    *   `region_enabled = true` (Select only the leaf pixels)
    *   Position: Placed relative to the trunk.
4.  **CollisionShape2D** (Child of Root)
    *   Shape: `CircleShape2D`
    *   Position: `(0, -2)` (Center of the trunk base)
5.  **InteractionArea** (Area2D)
    *   Used for Charlie's interest/peeing behavior.

### Checklist for New Trees:
- [ ] Origin at the bottom of the trunk.
- [ ] Trunk at `z_index = 0`.
- [ ] Leaves at `z_index = 1`.
- [ ] `y_sort_enabled = true` on the root `StaticBody2D`.
- [ ] Added to the "trees" group in `Tree.gd`.

---

## 3. Fixing Clipping Issues

If a character "pops" in front of a tree too early:
1.  **Check Origin**: Ensure the character's origin is at its feet, not its center.
2.  **Check Sprite Offset**: Ensure the sprite is moved UP so its feet are at (0,0).
3.  **Check Y-Sort Settings**: Ensure `y_sort_enabled` is OFF on the Sprite but ON on the Parent Node.
4.  **Background Conflict**: Ensure large background elements (Grass/Paths) are at `z_index = -1` so they don't interfere with Y-sorting.

---

## 4. Leash Alignment

When character origins change, the leash hand offsets must be updated in `scripts/player/Player.gd`:

```gdscript
func get_leash_hand_offset() -> Vector2:
    # All offsets are relative to the FEET origin (0,0)
    return Vector2(8, -14) # Standard hand height
```

Update `charlie_leash_point` in `Overworld.gd` similarly (roughly `Vector2(0, -20)` from feet).
