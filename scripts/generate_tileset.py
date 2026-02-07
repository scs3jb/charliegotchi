#!/usr/bin/env python3
"""
Generate terrain tileset for Charlie's Island Adventure.
Creates a 256x256 pixel atlas with 16x16 tiles in a retro pixel art style.
"""

from PIL import Image, ImageDraw
import os
import random

# Output
OUTPUT_DIR = "assets/sprites/tiles"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TILE_SIZE = 16
ATLAS_SIZE = 256  # 16x16 tiles

# Color Palettes
# Grass
GRASS_BASE = (76, 140, 64, 255)
GRASS_LIGHT = (92, 160, 80, 255)
GRASS_DARK = (60, 120, 52, 255)
GRASS_ACCENT = (100, 176, 92, 255)

# Dirt/Path
DIRT_BASE = (140, 112, 80, 255)
DIRT_LIGHT = (164, 132, 96, 255)
DIRT_DARK = (116, 92, 68, 255)

# Sand
SAND_BASE = (224, 204, 160, 255)
SAND_LIGHT = (240, 220, 180, 255)
SAND_DARK = (200, 180, 140, 255)

# Water
WATER_BASE = (64, 120, 180, 255)
WATER_LIGHT = (80, 140, 200, 255)
WATER_DARK = (48, 100, 160, 255)
WATER_DEEP = (32, 80, 140, 255)
WATER_FOAM = (200, 220, 240, 255)

# Cliff/Mountain
CLIFF_BASE = (96, 88, 80, 255)
CLIFF_LIGHT = (116, 108, 100, 255)
CLIFF_DARK = (76, 68, 60, 255)
CLIFF_HIGHLIGHT = (140, 132, 124, 255)

# Flowers
FLOWER_RED = (220, 80, 80, 255)
FLOWER_YELLOW = (240, 220, 80, 255)
FLOWER_BLUE = (100, 140, 220, 255)
FLOWER_WHITE = (240, 240, 240, 255)


def add_noise(draw, x, y, w, h, base_color, light_color, dark_color, density=0.15):
    """Add pixel noise/dithering to an area."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            if random.random() < density:
                color = light_color if random.random() < 0.5 else dark_color
                draw.point((px, py), fill=color)


def draw_grass_base(draw, x, y):
    """Draw a basic grass tile."""
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=GRASS_BASE)
    add_noise(draw, x, y, TILE_SIZE, TILE_SIZE, GRASS_BASE, GRASS_LIGHT, GRASS_DARK, 0.2)


def draw_grass_flowers(draw, x, y, flower_color):
    """Draw grass with small flowers."""
    draw_grass_base(draw, x, y)
    # Add 2-3 small flowers
    for _ in range(random.randint(2, 3)):
        fx = x + random.randint(2, TILE_SIZE - 4)
        fy = y + random.randint(2, TILE_SIZE - 4)
        draw.point((fx, fy), fill=flower_color)
        # Tiny leaves
        draw.point((fx - 1, fy + 1), fill=GRASS_ACCENT)
        draw.point((fx + 1, fy + 1), fill=GRASS_ACCENT)


def draw_dirt_base(draw, x, y):
    """Draw a basic dirt/path tile."""
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=DIRT_BASE)
    add_noise(draw, x, y, TILE_SIZE, TILE_SIZE, DIRT_BASE, DIRT_LIGHT, DIRT_DARK, 0.25)


def draw_dirt_edge(draw, x, y, edge):
    """Draw dirt tile with grass edge. edge: 'top', 'bottom', 'left', 'right', or combinations."""
    draw_dirt_base(draw, x, y)

    # Add grass edges
    if 'top' in edge:
        draw.rectangle([x, y, x + TILE_SIZE - 1, y + 3], fill=GRASS_BASE)
        add_noise(draw, x, y, TILE_SIZE, 4, GRASS_BASE, GRASS_LIGHT, GRASS_DARK, 0.2)
    if 'bottom' in edge:
        draw.rectangle([x, y + TILE_SIZE - 4, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=GRASS_BASE)
        add_noise(draw, x, y + TILE_SIZE - 4, TILE_SIZE, 4, GRASS_BASE, GRASS_LIGHT, GRASS_DARK, 0.2)
    if 'left' in edge:
        draw.rectangle([x, y, x + 3, y + TILE_SIZE - 1], fill=GRASS_BASE)
        add_noise(draw, x, y, 4, TILE_SIZE, GRASS_BASE, GRASS_LIGHT, GRASS_DARK, 0.2)
    if 'right' in edge:
        draw.rectangle([x + TILE_SIZE - 4, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=GRASS_BASE)
        add_noise(draw, x + TILE_SIZE - 4, y, 4, TILE_SIZE, GRASS_BASE, GRASS_LIGHT, GRASS_DARK, 0.2)


def draw_sand_base(draw, x, y):
    """Draw a basic sand tile."""
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=SAND_BASE)
    add_noise(draw, x, y, TILE_SIZE, TILE_SIZE, SAND_BASE, SAND_LIGHT, SAND_DARK, 0.15)


def draw_sand_edge(draw, x, y, edge):
    """Draw sand with grass edge."""
    draw_sand_base(draw, x, y)

    if 'top' in edge:
        draw.rectangle([x, y, x + TILE_SIZE - 1, y + 3], fill=GRASS_BASE)
        add_noise(draw, x, y, TILE_SIZE, 4, GRASS_BASE, GRASS_LIGHT, GRASS_DARK, 0.2)
    if 'bottom' in edge:
        draw.rectangle([x, y + TILE_SIZE - 4, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=GRASS_BASE)
    if 'left' in edge:
        draw.rectangle([x, y, x + 3, y + TILE_SIZE - 1], fill=GRASS_BASE)
    if 'right' in edge:
        draw.rectangle([x + TILE_SIZE - 4, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=GRASS_BASE)


def draw_water_base(draw, x, y, frame=0):
    """Draw a basic water tile with animation frame."""
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=WATER_BASE)

    # Animated wave pattern
    offset = (frame * 4) % TILE_SIZE
    for i in range(0, TILE_SIZE, 4):
        wave_y = y + ((i + offset) % TILE_SIZE)
        draw.line([x, wave_y, x + TILE_SIZE - 1, wave_y], fill=WATER_LIGHT)


def draw_water_deep(draw, x, y, frame=0):
    """Draw deep water (impassable)."""
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=WATER_DEEP)
    offset = (frame * 3) % TILE_SIZE
    for i in range(0, TILE_SIZE, 5):
        wave_y = y + ((i + offset) % TILE_SIZE)
        draw.line([x, wave_y, x + TILE_SIZE - 1, wave_y], fill=WATER_BASE)


def draw_water_edge(draw, x, y, edge, frame=0):
    """Draw water with land edge (sand/grass showing)."""
    draw_water_base(draw, x, y, frame)

    # Add foam/edge
    if 'top' in edge:
        draw.rectangle([x, y, x + TILE_SIZE - 1, y + 2], fill=SAND_BASE)
        draw.line([x, y + 3, x + TILE_SIZE - 1, y + 3], fill=WATER_FOAM)
    if 'bottom' in edge:
        draw.rectangle([x, y + TILE_SIZE - 3, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=SAND_BASE)
        draw.line([x, y + TILE_SIZE - 4, x + TILE_SIZE - 1, y + TILE_SIZE - 4], fill=WATER_FOAM)
    if 'left' in edge:
        draw.rectangle([x, y, x + 2, y + TILE_SIZE - 1], fill=SAND_BASE)
        draw.line([x + 3, y, x + 3, y + TILE_SIZE - 1], fill=WATER_FOAM)
    if 'right' in edge:
        draw.rectangle([x + TILE_SIZE - 3, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=SAND_BASE)
        draw.line([x + TILE_SIZE - 4, y, x + TILE_SIZE - 4, y + TILE_SIZE - 1], fill=WATER_FOAM)


def draw_cliff_base(draw, x, y):
    """Draw a basic cliff/mountain tile (impassable)."""
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=CLIFF_BASE)
    add_noise(draw, x, y, TILE_SIZE, TILE_SIZE, CLIFF_BASE, CLIFF_LIGHT, CLIFF_DARK, 0.3)

    # Add some texture lines
    for i in range(2, TILE_SIZE - 2, 4):
        draw.line([x + 1, y + i, x + 3, y + i + 2], fill=CLIFF_HIGHLIGHT)


def draw_cliff_top(draw, x, y):
    """Draw cliff top edge (grass on top)."""
    draw_cliff_base(draw, x, y)
    # Add grass on top
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + 4], fill=GRASS_BASE)
    add_noise(draw, x, y, TILE_SIZE, 5, GRASS_BASE, GRASS_LIGHT, GRASS_DARK, 0.2)
    # Edge shadow
    draw.line([x, y + 5, x + TILE_SIZE - 1, y + 5], fill=CLIFF_DARK)


def draw_cliff_side(draw, x, y, side='left'):
    """Draw cliff side edge."""
    draw_cliff_base(draw, x, y)
    if side == 'left':
        draw.line([x, y, x, y + TILE_SIZE - 1], fill=CLIFF_DARK)
    else:
        draw.line([x + TILE_SIZE - 1, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=CLIFF_HIGHLIGHT)


def generate_tileset():
    """Generate the complete tileset atlas."""
    random.seed(42)  # Consistent generation

    atlas = Image.new('RGBA', (ATLAS_SIZE, ATLAS_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)

    # Tile layout (16x16 grid = 256 tiles possible)
    # Row 0: Grass variants (0-15)
    # Row 1: Dirt/path variants (16-31)
    # Row 2: Sand variants (32-47)
    # Row 3-4: Water variants + animation frames (48-79)
    # Row 5-6: Cliff/mountain variants (80-111)
    # Row 7+: Autotile edges and corners

    tile_index = 0

    def get_tile_pos(index):
        return (index % 16) * TILE_SIZE, (index // 16) * TILE_SIZE

    # === Row 0: Grass ===
    # 0: Base grass
    x, y = get_tile_pos(0)
    draw_grass_base(draw, x, y)

    # 1: Grass light variant
    x, y = get_tile_pos(1)
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=GRASS_LIGHT)
    add_noise(draw, x, y, TILE_SIZE, TILE_SIZE, GRASS_LIGHT, GRASS_ACCENT, GRASS_BASE, 0.15)

    # 2: Grass dark variant
    x, y = get_tile_pos(2)
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=GRASS_DARK)
    add_noise(draw, x, y, TILE_SIZE, TILE_SIZE, GRASS_DARK, GRASS_BASE, (48, 100, 44, 255), 0.15)

    # 3-6: Grass with flowers
    for i, color in enumerate([FLOWER_RED, FLOWER_YELLOW, FLOWER_BLUE, FLOWER_WHITE]):
        x, y = get_tile_pos(3 + i)
        random.seed(42 + i)
        draw_grass_flowers(draw, x, y, color)

    # 7-15: Reserved grass variants
    for i in range(7, 16):
        x, y = get_tile_pos(i)
        draw_grass_base(draw, x, y)

    # === Row 1: Dirt/Path ===
    # 16: Base dirt
    x, y = get_tile_pos(16)
    draw_dirt_base(draw, x, y)

    # 17-24: Dirt with edges (for autotiling)
    edges = ['top', 'bottom', 'left', 'right', 'top,left', 'top,right', 'bottom,left', 'bottom,right']
    for i, edge in enumerate(edges):
        x, y = get_tile_pos(17 + i)
        draw_dirt_edge(draw, x, y, edge)

    # 25-31: More dirt variants
    for i in range(25, 32):
        x, y = get_tile_pos(i)
        draw_dirt_base(draw, x, y)

    # === Row 2: Sand ===
    # 32: Base sand
    x, y = get_tile_pos(32)
    draw_sand_base(draw, x, y)

    # 33-40: Sand with edges
    for i, edge in enumerate(edges):
        x, y = get_tile_pos(33 + i)
        draw_sand_edge(draw, x, y, edge)

    # 41-47: Sand variants
    for i in range(41, 48):
        x, y = get_tile_pos(i)
        draw_sand_base(draw, x, y)

    # === Row 3-4: Water ===
    # 48-51: Base water animation (4 frames)
    for frame in range(4):
        x, y = get_tile_pos(48 + frame)
        draw_water_base(draw, x, y, frame)

    # 52-55: Deep water animation (4 frames)
    for frame in range(4):
        x, y = get_tile_pos(52 + frame)
        draw_water_deep(draw, x, y, frame)

    # 56-63: Water edges (with frame 0)
    for i, edge in enumerate(edges):
        x, y = get_tile_pos(56 + i)
        draw_water_edge(draw, x, y, edge, 0)

    # 64-79: More water edge variants for other frames
    for frame in range(1, 4):
        for i in range(4):
            x, y = get_tile_pos(64 + (frame - 1) * 4 + i)
            edge = edges[i]
            draw_water_edge(draw, x, y, edge, frame)

    # Fill remaining water row slots
    for i in range(76, 80):
        x, y = get_tile_pos(i)
        draw_water_base(draw, x, y, 0)

    # === Row 5-6: Cliffs/Mountains ===
    # 80: Base cliff
    x, y = get_tile_pos(80)
    draw_cliff_base(draw, x, y)

    # 81: Cliff top (walkable grass on top)
    x, y = get_tile_pos(81)
    draw_cliff_top(draw, x, y)

    # 82: Cliff left side
    x, y = get_tile_pos(82)
    draw_cliff_side(draw, x, y, 'left')

    # 83: Cliff right side
    x, y = get_tile_pos(83)
    draw_cliff_side(draw, x, y, 'right')

    # 84-95: Cliff corner and variants
    for i in range(84, 96):
        x, y = get_tile_pos(i)
        draw_cliff_base(draw, x, y)

    # === Row 7+: Bridge/Special tiles ===
    # 96: Wooden bridge horizontal
    x, y = get_tile_pos(96)
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=WATER_BASE)
    draw.rectangle([x, y + 4, x + TILE_SIZE - 1, y + TILE_SIZE - 5], fill=DIRT_BASE)
    # Planks
    for px in range(x + 2, x + TILE_SIZE - 2, 4):
        draw.line([px, y + 4, px, y + TILE_SIZE - 5], fill=DIRT_DARK)

    # 97: Wooden bridge vertical
    x, y = get_tile_pos(97)
    draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=WATER_BASE)
    draw.rectangle([x + 4, y, x + TILE_SIZE - 5, y + TILE_SIZE - 1], fill=DIRT_BASE)
    for py in range(y + 2, y + TILE_SIZE - 2, 4):
        draw.line([x + 4, py, x + TILE_SIZE - 5, py], fill=DIRT_DARK)

    # Fill remaining tiles with grass for now
    for i in range(98, 256):
        x, y = get_tile_pos(i)
        if atlas.getpixel((x, y))[3] == 0:  # Only if transparent
            draw_grass_base(draw, x, y)

    # Save
    output_path = os.path.join(OUTPUT_DIR, "terrain_atlas.png")
    atlas.save(output_path)
    print(f"Generated tileset: {output_path}")
    print(f"Atlas size: {ATLAS_SIZE}x{ATLAS_SIZE} ({ATLAS_SIZE // TILE_SIZE}x{ATLAS_SIZE // TILE_SIZE} tiles)")

    # Print tile index reference
    print("\nTile Index Reference:")
    print("  0-15:   Grass variants (0=base, 3-6=flowers)")
    print("  16-31:  Dirt/path (16=base, 17-24=edges)")
    print("  32-47:  Sand (32=base, 33-40=edges)")
    print("  48-55:  Water (48-51=shallow animated, 52-55=deep animated)")
    print("  56-79:  Water edges")
    print("  80-95:  Cliff/mountain (80=base, 81=top)")
    print("  96-97:  Bridge (96=horizontal, 97=vertical)")


if __name__ == "__main__":
    generate_tileset()
