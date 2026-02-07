#!/usr/bin/env python3
"""
Generate food tile spritesheet for the feeding minigame.
Creates a 196x28 atlas (7 tiles, each 28x28) in retro pixel art style.

Tile order (left to right):
  0: Kibble Brown  - round brown kibble nugget
  1: Kibble Salmon - pink fish-shaped piece
  2: Kibble Green  - green pea/broccoli piece
  3: Kibble Orange - orange carrot chunk
  4: Kibble Blue   - blue berry
  5: Chicken       - yellow chicken drumstick (allergen!)
  6: Mushroom      - purple/red toadstool (allergen!)
"""

from PIL import Image, ImageDraw
import os
import random

OUTPUT_DIR = "assets/sprites/ui"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TILE = 28
COLS = 7

# Palettes (R, G, B, A)
# Brown kibble
BROWN_BASE   = (140, 90, 50, 255)
BROWN_LIGHT  = (170, 115, 70, 255)
BROWN_DARK   = (105, 65, 35, 255)
BROWN_SHINE  = (190, 140, 95, 255)

# Salmon kibble
SALMON_BASE  = (215, 125, 125, 255)
SALMON_LIGHT = (235, 155, 145, 255)
SALMON_DARK  = (180, 95, 100, 255)
SALMON_SHINE = (245, 185, 175, 255)
SALMON_EYE   = (60, 40, 40, 255)

# Green kibble
GREEN_BASE   = (90, 165, 75, 255)
GREEN_LIGHT  = (120, 195, 100, 255)
GREEN_DARK   = (60, 130, 50, 255)
GREEN_SHINE  = (150, 215, 130, 255)

# Orange kibble
ORANGE_BASE  = (230, 150, 50, 255)
ORANGE_LIGHT = (245, 180, 80, 255)
ORANGE_DARK  = (195, 120, 35, 255)
ORANGE_SHINE = (255, 210, 120, 255)
ORANGE_LEAF  = (70, 150, 55, 255)

# Blue kibble
BLUE_BASE    = (100, 110, 200, 255)
BLUE_LIGHT   = (130, 140, 225, 255)
BLUE_DARK    = (70, 80, 165, 255)
BLUE_SHINE   = (165, 175, 240, 255)
BLUE_STEM    = (80, 140, 70, 255)

# Chicken (the bad one)
CHICK_BASE   = (240, 215, 100, 255)
CHICK_LIGHT  = (250, 235, 140, 255)
CHICK_DARK   = (210, 180, 70, 255)
CHICK_BONE   = (245, 240, 230, 255)
CHICK_BONE_D = (210, 200, 185, 255)
CHICK_OUTLINE= (180, 140, 50, 255)
CHICK_WARN   = (220, 60, 60, 255)

# Mushroom (allergen)
MUSH_CAP     = (180, 60, 70, 255)
MUSH_CAP_LT  = (210, 90, 95, 255)
MUSH_CAP_DK  = (140, 40, 50, 255)
MUSH_SPOTS   = (240, 230, 210, 255)
MUSH_STEM    = (230, 220, 200, 255)
MUSH_STEM_DK = (195, 185, 165, 255)
MUSH_WARN    = (220, 60, 60, 255)

TRANSPARENT  = (0, 0, 0, 0)
BG_TILE      = (40, 50, 40, 255)


def draw_ellipse_filled(draw, cx, cy, rx, ry, color):
    """Draw a filled ellipse centered at (cx, cy)."""
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)


def add_pixel_noise(img, x0, y0, w, h, colors, density=0.12):
    """Scatter random pixels for dithering texture."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if random.random() < density:
                cur = img.getpixel((x, y))
                if cur[3] > 0:  # only on non-transparent
                    img.putpixel((x, y), random.choice(colors))


def draw_brown_kibble(img, draw, ox, oy):
    """Round kibble nugget with a cross-hatch score mark."""
    cx, cy = ox + 14, oy + 14

    # Rounded square body
    draw.rounded_rectangle([ox + 4, oy + 5, ox + 24, oy + 23], radius=5, fill=BROWN_BASE)
    # Highlight top-left
    draw.rounded_rectangle([ox + 5, oy + 6, ox + 16, oy + 14], radius=3, fill=BROWN_LIGHT)
    # Shadow bottom-right
    draw.line([(ox + 8, oy + 22), (ox + 23, oy + 22)], fill=BROWN_DARK, width=1)
    draw.line([(ox + 23, oy + 8), (ox + 23, oy + 22)], fill=BROWN_DARK, width=1)
    # Shine dot
    img.putpixel((ox + 8, oy + 8), BROWN_SHINE)
    img.putpixel((ox + 9, oy + 8), BROWN_SHINE)
    img.putpixel((ox + 8, oy + 9), BROWN_SHINE)
    # Cross score mark
    draw.line([(ox + 10, oy + 11), (ox + 18, oy + 19)], fill=BROWN_DARK, width=1)
    draw.line([(ox + 18, oy + 11), (ox + 10, oy + 19)], fill=BROWN_DARK, width=1)

    add_pixel_noise(img, ox + 4, oy + 5, 20, 18, [BROWN_LIGHT, BROWN_DARK], 0.08)


def draw_salmon_kibble(img, draw, ox, oy):
    """Fish-shaped kibble piece."""
    # Fish body (oval)
    draw.ellipse([ox + 3, oy + 8, ox + 21, oy + 22], fill=SALMON_BASE)
    # Highlight
    draw.ellipse([ox + 5, oy + 9, ox + 15, oy + 16], fill=SALMON_LIGHT)
    # Tail (triangle)
    draw.polygon([(ox + 20, oy + 12), (ox + 20, oy + 20), (ox + 27, oy + 16)], fill=SALMON_BASE)
    draw.polygon([(ox + 21, oy + 13), (ox + 21, oy + 17), (ox + 25, oy + 15)], fill=SALMON_LIGHT)
    # Eye
    img.putpixel((ox + 7, oy + 13), SALMON_EYE)
    img.putpixel((ox + 8, oy + 13), SALMON_EYE)
    img.putpixel((ox + 7, oy + 14), SALMON_EYE)
    # Shine on eye
    img.putpixel((ox + 7, oy + 13), (255, 255, 255, 255))
    # Mouth line
    draw.line([(ox + 4, oy + 16), (ox + 8, oy + 16)], fill=SALMON_DARK, width=1)
    # Shadow bottom
    draw.arc([ox + 3, oy + 8, ox + 21, oy + 23], 20, 160, fill=SALMON_DARK)
    # Fin on top
    draw.polygon([(ox + 11, oy + 8), (ox + 14, oy + 4), (ox + 17, oy + 8)], fill=SALMON_DARK)

    add_pixel_noise(img, ox + 3, oy + 8, 18, 14, [SALMON_LIGHT, SALMON_DARK], 0.06)


def draw_green_kibble(img, draw, ox, oy):
    """Broccoli / pea cluster piece."""
    # Main cluster of circles (broccoli florets)
    for (dx, dy, r) in [(12, 10, 5), (8, 14, 5), (16, 14, 5), (12, 17, 4), (18, 10, 3)]:
        draw_ellipse_filled(draw, ox + dx, oy + dy, r, r, GREEN_BASE)
    # Lighter tops
    for (dx, dy, r) in [(11, 9, 3), (7, 13, 3), (15, 12, 3)]:
        draw_ellipse_filled(draw, ox + dx, oy + dy, r, r, GREEN_LIGHT)
    # Stem
    draw.rectangle([ox + 11, oy + 19, ox + 14, oy + 25], fill=GREEN_DARK)
    draw.rectangle([ox + 12, oy + 19, ox + 13, oy + 24], fill=(80, 140, 55, 255))
    # Shine dots
    img.putpixel((ox + 10, oy + 8), GREEN_SHINE)
    img.putpixel((ox + 6, oy + 12), GREEN_SHINE)
    img.putpixel((ox + 16, oy + 10), GREEN_SHINE)
    # Texture bumps
    for (dx, dy) in [(13, 12), (9, 16), (15, 16), (11, 14)]:
        img.putpixel((ox + dx, oy + dy), GREEN_DARK)

    add_pixel_noise(img, ox + 4, oy + 6, 18, 16, [GREEN_LIGHT, GREEN_DARK], 0.06)


def draw_orange_kibble(img, draw, ox, oy):
    """Carrot chunk."""
    # Carrot body (tapered triangle-ish with rounded top)
    # Draw as a polygon that's wide at top, narrow at bottom
    draw.polygon([
        (ox + 8, oy + 6),
        (ox + 20, oy + 6),
        (ox + 17, oy + 24),
        (ox + 11, oy + 24),
    ], fill=ORANGE_BASE)
    # Round the top
    draw.ellipse([ox + 8, oy + 4, ox + 20, oy + 10], fill=ORANGE_BASE)
    # Highlight stripe
    draw.line([(ox + 12, oy + 7), (ox + 12, oy + 22)], fill=ORANGE_LIGHT, width=1)
    draw.line([(ox + 13, oy + 7), (ox + 13, oy + 20)], fill=ORANGE_LIGHT, width=1)
    # Shadow stripe
    draw.line([(ox + 17, oy + 8), (ox + 16, oy + 22)], fill=ORANGE_DARK, width=1)
    # Score lines (horizontal dashes)
    for y in [11, 15, 19]:
        draw.line([(ox + 10, oy + y), (ox + 18, oy + y)], fill=ORANGE_DARK, width=1)
    # Leaf top
    draw.polygon([(ox + 12, oy + 5), (ox + 10, oy + 1), (ox + 14, oy + 3)], fill=ORANGE_LEAF)
    draw.polygon([(ox + 15, oy + 5), (ox + 18, oy + 1), (ox + 14, oy + 3)], fill=ORANGE_LEAF)
    # Shine
    img.putpixel((ox + 11, oy + 8), ORANGE_SHINE)
    img.putpixel((ox + 12, oy + 8), ORANGE_SHINE)

    add_pixel_noise(img, ox + 8, oy + 6, 12, 18, [ORANGE_LIGHT, ORANGE_DARK], 0.06)


def draw_blue_kibble(img, draw, ox, oy):
    """Blueberry piece."""
    cx, cy = ox + 14, oy + 15
    # Main berry body
    draw.ellipse([ox + 5, oy + 6, ox + 23, oy + 24], fill=BLUE_BASE)
    # Highlight (upper left)
    draw.ellipse([ox + 7, oy + 8, ox + 16, oy + 16], fill=BLUE_LIGHT)
    # Shadow (lower right)
    draw.arc([ox + 5, oy + 6, ox + 23, oy + 24], 10, 170, fill=BLUE_DARK, width=2)
    # Crown (star pattern on top of berry)
    for dx in [-2, 0, 2]:
        img.putpixel((cx + dx, oy + 7), BLUE_DARK)
    for dx in [-3, -1, 1, 3]:
        img.putpixel((cx + dx, oy + 8), BLUE_DARK)
    # Shine dots
    img.putpixel((ox + 9, oy + 10), BLUE_SHINE)
    img.putpixel((ox + 10, oy + 10), BLUE_SHINE)
    img.putpixel((ox + 10, oy + 11), BLUE_SHINE)
    # Tiny stem
    draw.line([(cx, oy + 5), (cx, oy + 7)], fill=BLUE_STEM, width=1)
    img.putpixel((cx - 1, oy + 5), BLUE_STEM)

    add_pixel_noise(img, ox + 6, oy + 7, 16, 16, [BLUE_LIGHT, BLUE_DARK], 0.06)


def draw_chicken(img, draw, ox, oy):
    """Chicken drumstick - the allergen! Drawn with warning coloring."""
    # Drumstick meat (big round part)
    draw.ellipse([ox + 2, oy + 4, ox + 18, oy + 22], fill=CHICK_BASE)
    # Highlight
    draw.ellipse([ox + 4, oy + 6, ox + 13, oy + 15], fill=CHICK_LIGHT)
    # Shadow
    draw.arc([ox + 2, oy + 4, ox + 18, oy + 22], 20, 160, fill=CHICK_DARK, width=1)

    # Bone sticking out
    draw.rectangle([ox + 17, oy + 10, ox + 24, oy + 14], fill=CHICK_BONE)
    draw.rectangle([ox + 17, oy + 11, ox + 24, oy + 13], fill=CHICK_BONE)
    # Bone knob at end
    draw.ellipse([ox + 22, oy + 8, ox + 27, oy + 16], fill=CHICK_BONE)
    draw.ellipse([ox + 23, oy + 9, ox + 26, oy + 15], fill=CHICK_BONE_D)
    # Bone shadow
    draw.line([(ox + 17, oy + 14), (ox + 23, oy + 14)], fill=CHICK_BONE_D, width=1)

    # Red warning "X" marks
    draw.line([(ox + 3, oy + 2), (ox + 6, oy + 5)], fill=CHICK_WARN, width=1)
    draw.line([(ox + 6, oy + 2), (ox + 3, oy + 5)], fill=CHICK_WARN, width=1)

    # Outline for extra visibility
    # Top arc
    draw.arc([ox + 1, oy + 3, ox + 19, oy + 23], 200, 360, fill=CHICK_OUTLINE, width=1)

    add_pixel_noise(img, ox + 3, oy + 5, 15, 16, [CHICK_LIGHT, CHICK_DARK], 0.06)


def draw_mushroom(img, draw, ox, oy):
    """Toadstool mushroom - allergen! Red cap with white spots."""
    # Stem
    draw.rectangle([ox + 10, oy + 14, ox + 17, oy + 25], fill=MUSH_STEM)
    draw.rectangle([ox + 11, oy + 15, ox + 16, oy + 24], fill=MUSH_STEM)
    # Stem shadow
    draw.line([(ox + 16, oy + 15), (ox + 16, oy + 24)], fill=MUSH_STEM_DK, width=1)
    draw.line([(ox + 10, oy + 24), (ox + 17, oy + 24)], fill=MUSH_STEM_DK, width=1)
    # Stem ring (skirt)
    draw.line([(ox + 9, oy + 16), (ox + 18, oy + 16)], fill=MUSH_STEM, width=1)
    draw.line([(ox + 8, oy + 17), (ox + 19, oy + 17)], fill=MUSH_STEM_DK, width=1)

    # Cap (dome shape)
    draw.ellipse([ox + 3, oy + 2, ox + 25, oy + 17], fill=MUSH_CAP)
    # Cap highlight
    draw.ellipse([ox + 5, oy + 3, ox + 17, oy + 12], fill=MUSH_CAP_LT)
    # Cap shadow at bottom
    draw.arc([ox + 3, oy + 2, ox + 25, oy + 17], 10, 170, fill=MUSH_CAP_DK, width=2)

    # White spots on cap
    for (dx, dy, r) in [(9, 6, 2), (16, 8, 2), (12, 10, 1), (20, 6, 1), (7, 11, 1)]:
        draw_ellipse_filled(draw, ox + dx, oy + dy, r, r, MUSH_SPOTS)

    # Red warning "X" mark (top-right)
    draw.line([(ox + 21, oy + 1), (ox + 24, oy + 4)], fill=MUSH_WARN, width=1)
    draw.line([(ox + 24, oy + 1), (ox + 21, oy + 4)], fill=MUSH_WARN, width=1)

    # Shine dot
    img.putpixel((ox + 8, oy + 5), (255, 200, 200, 255))
    img.putpixel((ox + 9, oy + 5), (255, 200, 200, 255))

    add_pixel_noise(img, ox + 4, oy + 3, 20, 13, [MUSH_CAP_LT, MUSH_CAP_DK], 0.06)


def main():
    random.seed(42)  # Reproducible output

    img = Image.new("RGBA", (COLS * TILE, TILE), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Draw tile backgrounds (slightly rounded dark squares)
    for i in range(COLS):
        ox = i * TILE
        draw.rounded_rectangle([ox + 1, 1, ox + TILE - 2, TILE - 2], radius=3, fill=BG_TILE)

    # Draw each food type
    draw_brown_kibble(img, draw, 0 * TILE, 0)
    draw_salmon_kibble(img, draw, 1 * TILE, 0)
    draw_green_kibble(img, draw, 2 * TILE, 0)
    draw_orange_kibble(img, draw, 3 * TILE, 0)
    draw_blue_kibble(img, draw, 4 * TILE, 0)
    draw_chicken(img, draw, 5 * TILE, 0)
    draw_mushroom(img, draw, 6 * TILE, 0)

    output_path = os.path.join(OUTPUT_DIR, "food_tiles.png")
    img.save(output_path)
    print(f"Generated {output_path} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
