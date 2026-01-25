#!/usr/bin/env python3
"""Generate animated sprite sheets for Charlie's Island Adventure.

Creates high-quality pixel art sprites with smooth animations for:
- Player (blonde girl character)
- Charlie (baby Shih Tzu puppy)
- Ball (bouncing red ball with squash/stretch)
"""

from PIL import Image, ImageDraw
import os
import math

# Output directory
SPRITES_DIR = "assets/sprites/characters"
os.makedirs(SPRITES_DIR, exist_ok=True)

# Sprite dimensions
FRAME_SIZE = 32
FRAMES_PER_DIRECTION = 4  # idle + 3 walk frames


def draw_outlined_ellipse(draw, bbox, fill, outline_color, outline_width=1):
    """Draw an ellipse with outline."""
    x1, y1, x2, y2 = bbox
    # Draw outline first
    draw.ellipse([x1-outline_width, y1-outline_width,
                  x2+outline_width, y2+outline_width], fill=outline_color)
    # Draw fill
    draw.ellipse(bbox, fill=fill)


def draw_outlined_rect(draw, bbox, fill, outline_color, outline_width=1):
    """Draw a rectangle with outline."""
    x1, y1, x2, y2 = bbox
    # Draw outline first
    draw.rectangle([x1-outline_width, y1-outline_width,
                    x2+outline_width, y2+outline_width], fill=outline_color)
    # Draw fill
    draw.rectangle(bbox, fill=fill)


def create_player_spritesheet():
    """Create animated sprite sheet for the player (blonde girl).

    Layout: 4 rows (down, left, right, up) x 4 columns (idle, walk1, walk2, walk3)
    Link to the Past style with outlines and vibrant colors.
    """
    sheet_width = FRAME_SIZE * FRAMES_PER_DIRECTION
    sheet_height = FRAME_SIZE * 4  # 4 directions

    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    # Colors - vibrant Link to the Past style
    skin = (255, 220, 186, 255)
    skin_shadow = (230, 190, 160, 255)
    hair = (255, 220, 100, 255)
    hair_shadow = (230, 185, 70, 255)
    hair_highlight = (255, 240, 150, 255)
    dress = (255, 120, 160, 255)
    dress_shadow = (220, 90, 130, 255)
    dress_highlight = (255, 160, 190, 255)
    eyes = (40, 80, 140, 255)
    eye_white = (255, 255, 255, 255)
    outline = (60, 40, 35, 255)
    shoes = (140, 90, 60, 255)

    directions = ['down', 'left', 'right', 'up']

    for dir_idx, direction in enumerate(directions):
        for frame in range(FRAMES_PER_DIRECTION):
            img = Image.new('RGBA', (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Animation offsets
            bob = 0
            leg_phase = 0
            arm_swing = 0

            if frame > 0:  # Walking frames
                if frame == 1:
                    bob = -1
                    leg_phase = 1
                    arm_swing = 2
                elif frame == 2:
                    bob = 0
                    leg_phase = 0
                    arm_swing = 0
                elif frame == 3:
                    bob = -1
                    leg_phase = -1
                    arm_swing = -2

            cx, cy = 16, 16

            if direction == 'down':
                # Shadow
                draw.ellipse([cx-7, cy+10, cx+7, cy+13], fill=(0, 0, 0, 40))

                # Shoes/feet
                draw.ellipse([cx-6+leg_phase, cy+8+bob, cx-2+leg_phase, cy+12+bob], fill=shoes)
                draw.ellipse([cx+2-leg_phase, cy+8+bob, cx+6-leg_phase, cy+12+bob], fill=shoes)

                # Legs
                draw.rectangle([cx-5, cy+4+bob, cx-2, cy+9+bob+leg_phase], fill=skin)
                draw.rectangle([cx+2, cy+4+bob, cx+5, cy+9+bob-leg_phase], fill=skin)

                # Dress body
                draw.ellipse([cx-8, cy-3+bob, cx+8, cy+7+bob], fill=dress)
                draw.ellipse([cx-6, cy-1+bob, cx+6, cy+5+bob], fill=dress_highlight)
                draw.arc([cx-8, cy+1+bob, cx+8, cy+7+bob], 0, 180, fill=dress_shadow, width=2)

                # Arms
                draw.ellipse([cx-10, cy-1+bob, cx-6, cy+5+bob+arm_swing], fill=skin)
                draw.ellipse([cx+6, cy-1+bob, cx+10, cy+5+bob-arm_swing], fill=skin)

                # Head
                draw.ellipse([cx-7, cy-13+bob, cx+7, cy-2+bob], fill=skin)
                draw.ellipse([cx-6, cy-11+bob, cx+6, cy-4+bob], fill=skin)

                # Hair - flowing blonde
                draw.ellipse([cx-8, cy-15+bob, cx+8, cy-7+bob], fill=hair)
                draw.ellipse([cx-7, cy-14+bob, cx-3, cy-9+bob], fill=hair_highlight)
                # Hair sides
                draw.ellipse([cx-9, cy-12+bob, cx-5, cy-3+bob], fill=hair)
                draw.ellipse([cx+5, cy-12+bob, cx+9, cy-3+bob], fill=hair)
                draw.ellipse([cx-8, cy-11+bob, cx-6, cy-5+bob], fill=hair_shadow)
                draw.ellipse([cx+6, cy-11+bob, cx+8, cy-5+bob], fill=hair_shadow)

                # Face
                # Eyes
                draw.ellipse([cx-5, cy-9+bob, cx-2, cy-5+bob], fill=eye_white)
                draw.ellipse([cx+2, cy-9+bob, cx+5, cy-5+bob], fill=eye_white)
                draw.ellipse([cx-4, cy-8+bob, cx-2, cy-5+bob], fill=eyes)
                draw.ellipse([cx+2, cy-8+bob, cx+4, cy-5+bob], fill=eyes)
                # Eye shine
                draw.point((cx-3, cy-7+bob), fill=(255, 255, 255, 255))
                draw.point((cx+3, cy-7+bob), fill=(255, 255, 255, 255))

                # Blush
                draw.ellipse([cx-6, cy-5+bob, cx-3, cy-3+bob], fill=(255, 180, 180, 100))
                draw.ellipse([cx+3, cy-5+bob, cx+6, cy-3+bob], fill=(255, 180, 180, 100))

                # Mouth
                if frame > 0:  # Smile while walking
                    draw.arc([cx-2, cy-4+bob, cx+2, cy-2+bob], 0, 180, fill=(200, 100, 100, 255))
                else:
                    draw.line([cx-1, cy-3+bob, cx+1, cy-3+bob], fill=(200, 100, 100, 255))

            elif direction == 'up':
                # Shadow
                draw.ellipse([cx-7, cy+10, cx+7, cy+13], fill=(0, 0, 0, 40))

                # Shoes
                draw.ellipse([cx-6+leg_phase, cy+8+bob, cx-2+leg_phase, cy+12+bob], fill=shoes)
                draw.ellipse([cx+2-leg_phase, cy+8+bob, cx+6-leg_phase, cy+12+bob], fill=shoes)

                # Legs
                draw.rectangle([cx-5, cy+4+bob, cx-2, cy+9+bob+leg_phase], fill=skin)
                draw.rectangle([cx+2, cy+4+bob, cx+5, cy+9+bob-leg_phase], fill=skin)

                # Dress
                draw.ellipse([cx-8, cy-3+bob, cx+8, cy+7+bob], fill=dress)
                draw.ellipse([cx-6, cy+1+bob, cx+6, cy+5+bob], fill=dress_shadow)

                # Arms
                draw.ellipse([cx-10, cy-1+bob, cx-6, cy+5+bob+arm_swing], fill=skin)
                draw.ellipse([cx+6, cy-1+bob, cx+10, cy+5+bob-arm_swing], fill=skin)

                # Head (back)
                draw.ellipse([cx-7, cy-13+bob, cx+7, cy-2+bob], fill=hair)

                # Hair - full back view
                draw.ellipse([cx-9, cy-15+bob, cx+9, cy-5+bob], fill=hair)
                draw.ellipse([cx-8, cy-14+bob, cx-2, cy-7+bob], fill=hair_highlight)
                # Hair flowing down back
                draw.ellipse([cx-8, cy-10+bob, cx+8, cy-2+bob], fill=hair)
                draw.ellipse([cx-7, cy-8+bob, cx+7, cy+bob], fill=hair_shadow)

            elif direction == 'left':
                # Shadow
                draw.ellipse([cx-6, cy+10, cx+6, cy+13], fill=(0, 0, 0, 40))

                # Back shoe
                draw.ellipse([cx+1-leg_phase, cy+8+bob, cx+4-leg_phase, cy+12+bob], fill=shoes)

                # Back leg
                draw.rectangle([cx+1, cy+4+bob, cx+4, cy+9+bob-leg_phase], fill=skin_shadow)

                # Dress (side)
                draw.ellipse([cx-5, cy-3+bob, cx+5, cy+7+bob], fill=dress)
                draw.ellipse([cx-3, cy-1+bob, cx+3, cy+5+bob], fill=dress_highlight)

                # Front shoe
                draw.ellipse([cx-4+leg_phase, cy+8+bob, cx-1+leg_phase, cy+12+bob], fill=shoes)

                # Front leg
                draw.rectangle([cx-4, cy+4+bob, cx-1, cy+9+bob+leg_phase], fill=skin)

                # Arm
                draw.ellipse([cx-3, cy-1+bob, cx+1, cy+5+bob+arm_swing], fill=skin)

                # Head
                draw.ellipse([cx-6, cy-13+bob, cx+4, cy-2+bob], fill=skin)

                # Hair
                draw.ellipse([cx-7, cy-15+bob, cx+5, cy-7+bob], fill=hair)
                draw.ellipse([cx-6, cy-14+bob, cx-2, cy-9+bob], fill=hair_highlight)
                draw.ellipse([cx+2, cy-12+bob, cx+6, cy-3+bob], fill=hair)  # Back hair
                draw.ellipse([cx+3, cy-10+bob, cx+5, cy-5+bob], fill=hair_shadow)

                # Eye
                draw.ellipse([cx-4, cy-9+bob, cx-1, cy-5+bob], fill=eye_white)
                draw.ellipse([cx-4, cy-8+bob, cx-2, cy-5+bob], fill=eyes)
                draw.point((cx-3, cy-7+bob), fill=(255, 255, 255, 255))

                # Blush
                draw.ellipse([cx-5, cy-5+bob, cx-2, cy-3+bob], fill=(255, 180, 180, 80))

            elif direction == 'right':
                # Shadow
                draw.ellipse([cx-6, cy+10, cx+6, cy+13], fill=(0, 0, 0, 40))

                # Back shoe
                draw.ellipse([cx-4+leg_phase, cy+8+bob, cx-1+leg_phase, cy+12+bob], fill=shoes)

                # Back leg
                draw.rectangle([cx-4, cy+4+bob, cx-1, cy+9+bob-leg_phase], fill=skin_shadow)

                # Dress
                draw.ellipse([cx-5, cy-3+bob, cx+5, cy+7+bob], fill=dress)
                draw.ellipse([cx-3, cy-1+bob, cx+3, cy+5+bob], fill=dress_highlight)

                # Front shoe
                draw.ellipse([cx+1-leg_phase, cy+8+bob, cx+4-leg_phase, cy+12+bob], fill=shoes)

                # Front leg
                draw.rectangle([cx+1, cy+4+bob, cx+4, cy+9+bob+leg_phase], fill=skin)

                # Arm
                draw.ellipse([cx-1, cy-1+bob, cx+3, cy+5+bob-arm_swing], fill=skin)

                # Head
                draw.ellipse([cx-4, cy-13+bob, cx+6, cy-2+bob], fill=skin)

                # Hair
                draw.ellipse([cx-5, cy-15+bob, cx+7, cy-7+bob], fill=hair)
                draw.ellipse([cx+2, cy-14+bob, cx+6, cy-9+bob], fill=hair_highlight)
                draw.ellipse([cx-6, cy-12+bob, cx-2, cy-3+bob], fill=hair)  # Back hair
                draw.ellipse([cx-5, cy-10+bob, cx-3, cy-5+bob], fill=hair_shadow)

                # Eye
                draw.ellipse([cx+1, cy-9+bob, cx+4, cy-5+bob], fill=eye_white)
                draw.ellipse([cx+2, cy-8+bob, cx+4, cy-5+bob], fill=eyes)
                draw.point((cx+3, cy-7+bob), fill=(255, 255, 255, 255))

                # Blush
                draw.ellipse([cx+2, cy-5+bob, cx+5, cy-3+bob], fill=(255, 180, 180, 80))

            sheet.paste(img, (frame * FRAME_SIZE, dir_idx * FRAME_SIZE))

    sheet.save(os.path.join(SPRITES_DIR, "player_spritesheet.png"))
    print(f"Created player_spritesheet.png ({sheet_width}x{sheet_height})")


def create_charlie_spritesheet():
    """Create animated sprite sheet for Charlie (baby Shih Tzu).

    Layout: 4 rows (down, left, right, up) x 4 columns (idle, walk1, walk2, walk3)
    SUPER cute fluffy Shih Tzu puppy with huge sparkly eyes, fluffy fur, and adorable features!
    """
    sheet_width = FRAME_SIZE * FRAMES_PER_DIRECTION
    sheet_height = FRAME_SIZE * 4

    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    # Colors - adorable cream/white baby Shih Tzu
    fur_white = (255, 253, 250, 255)
    fur_cream = (255, 248, 235, 255)
    fur_light = (252, 245, 230, 255)
    fur_shadow = (240, 225, 205, 255)
    fur_fluff = (255, 252, 248, 255)  # Extra bright fluffy highlights

    # Cute face features
    nose_black = (35, 30, 30, 255)
    nose_shine = (70, 60, 60, 255)
    eye_black = (20, 18, 18, 255)
    eye_brown = (50, 35, 25, 255)
    eye_shine = (255, 255, 255, 255)
    eye_shine2 = (180, 210, 255, 255)  # Blue sparkle
    tongue = (255, 160, 170, 255)
    tongue_dark = (245, 130, 150, 255)
    inner_ear = (255, 215, 215, 255)
    blush = (255, 190, 190, 90)

    directions = ['down', 'left', 'right', 'up']

    for dir_idx, direction in enumerate(directions):
        for frame in range(FRAMES_PER_DIRECTION):
            img = Image.new('RGBA', (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Animation - bouncy and adorable
            bob = 0
            leg_phase = 0
            tail_wag = 0
            ear_flop = 0
            happy = frame > 0

            if frame > 0:
                if frame == 1:
                    bob = -2
                    leg_phase = 2
                    tail_wag = 4
                    ear_flop = 1
                elif frame == 2:
                    bob = 0
                    leg_phase = 0
                    tail_wag = 0
                    ear_flop = 0
                elif frame == 3:
                    bob = -2
                    leg_phase = -2
                    tail_wag = 4
                    ear_flop = -1

            cx, cy = 16, 17

            if direction == 'down':
                # Shadow
                draw.ellipse([cx-8, cy+6, cx+8, cy+10], fill=(0, 0, 0, 25))

                # Fluffy tail wagging behind
                tail_x = cx + 5 + tail_wag
                draw.ellipse([tail_x-4, cy-6+bob, tail_x+4, cy+bob], fill=fur_cream)
                draw.ellipse([tail_x-3, cy-7+bob, tail_x+3, cy-2+bob], fill=fur_white)
                draw.ellipse([tail_x-2, cy-6+bob, tail_x+2, cy-3+bob], fill=fur_fluff)

                # Fluffy round body
                draw.ellipse([cx-9, cy-3+bob, cx+9, cy+6+bob], fill=fur_cream)
                draw.ellipse([cx-7, cy-1+bob, cx+7, cy+4+bob], fill=fur_white)
                draw.ellipse([cx-5, cy+bob, cx+5, cy+3+bob], fill=fur_fluff)

                # Tiny stubby paws
                draw.ellipse([cx-7, cy+4+bob, cx-3, cy+8+bob+leg_phase], fill=fur_light)
                draw.ellipse([cx+3, cy+4+bob, cx+7, cy+8+bob-leg_phase], fill=fur_light)

                # Big fluffy head (the star!)
                draw.ellipse([cx-11, cy-15+bob, cx+11, cy-2+bob], fill=fur_cream)
                draw.ellipse([cx-9, cy-13+bob, cx+9, cy-4+bob], fill=fur_white)

                # Long floppy ears (signature Shih Tzu!)
                draw.ellipse([cx-13, cy-11+bob+ear_flop, cx-5, cy+bob+ear_flop], fill=fur_shadow)
                draw.ellipse([cx-12, cy-10+bob+ear_flop, cx-6, cy-1+bob+ear_flop], fill=fur_cream)
                draw.ellipse([cx-11, cy-9+bob+ear_flop, cx-7, cy-3+bob+ear_flop], fill=inner_ear)

                draw.ellipse([cx+5, cy-11+bob-ear_flop, cx+13, cy+bob-ear_flop], fill=fur_shadow)
                draw.ellipse([cx+6, cy-10+bob-ear_flop, cx+12, cy-1+bob-ear_flop], fill=fur_cream)
                draw.ellipse([cx+7, cy-9+bob-ear_flop, cx+11, cy-3+bob-ear_flop], fill=inner_ear)

                # Top head fluff poof
                draw.ellipse([cx-7, cy-16+bob, cx+7, cy-10+bob], fill=fur_cream)
                draw.ellipse([cx-5, cy-15+bob, cx+5, cy-11+bob], fill=fur_fluff)

                # Face fluff around muzzle
                draw.ellipse([cx-6, cy-9+bob, cx+6, cy-1+bob], fill=fur_white)
                draw.ellipse([cx-4, cy-7+bob, cx+4, cy-2+bob], fill=fur_fluff)

                # HUGE adorable eyes (kawaii style!)
                draw.ellipse([cx-8, cy-12+bob, cx-2, cy-6+bob], fill=eye_brown)
                draw.ellipse([cx+2, cy-12+bob, cx+8, cy-6+bob], fill=eye_brown)
                draw.ellipse([cx-7, cy-11+bob, cx-3, cy-7+bob], fill=eye_black)
                draw.ellipse([cx+3, cy-11+bob, cx+7, cy-7+bob], fill=eye_black)
                # Big sparkly shines!
                draw.ellipse([cx-6, cy-11+bob, cx-4, cy-9+bob], fill=eye_shine)
                draw.ellipse([cx+4, cy-11+bob, cx+6, cy-9+bob], fill=eye_shine)
                draw.ellipse([cx-5, cy-8+bob, cx-4, cy-7+bob], fill=eye_shine2)
                draw.ellipse([cx+4, cy-8+bob, cx+5, cy-7+bob], fill=eye_shine2)

                # Cute blush
                draw.ellipse([cx-9, cy-6+bob, cx-5, cy-4+bob], fill=blush)
                draw.ellipse([cx+5, cy-6+bob, cx+9, cy-4+bob], fill=blush)

                # Tiny button nose
                draw.ellipse([cx-2, cy-4+bob, cx+2, cy-1+bob], fill=nose_black)
                draw.point((cx-1, cy-3+bob), fill=nose_shine)

                # Cute mouth
                if happy:
                    draw.arc([cx-3, cy-2+bob, cx+3, cy+1+bob], 0, 180, fill=tongue_dark, width=1)
                    draw.ellipse([cx-2, cy-1+bob, cx+2, cy+2+bob], fill=tongue)
                else:
                    draw.arc([cx-2, cy-2+bob, cx+2, cy+bob], 0, 180, fill=(60, 50, 50, 255), width=1)

            elif direction == 'up':
                # Shadow
                draw.ellipse([cx-8, cy+6, cx+8, cy+10], fill=(0, 0, 0, 25))

                # Fluffy tail prominent from behind
                tail_x = cx + tail_wag
                draw.ellipse([tail_x-5, cy-12+bob, tail_x+5, cy-4+bob], fill=fur_cream)
                draw.ellipse([tail_x-4, cy-13+bob, tail_x+4, cy-6+bob], fill=fur_white)
                draw.ellipse([tail_x-3, cy-12+bob, tail_x+3, cy-7+bob], fill=fur_fluff)

                # Fluffy body
                draw.ellipse([cx-9, cy-3+bob, cx+9, cy+6+bob], fill=fur_cream)
                draw.ellipse([cx-7, cy-1+bob, cx+7, cy+4+bob], fill=fur_white)

                # Tiny paws
                draw.ellipse([cx-7, cy+4+bob, cx-3, cy+8+bob+leg_phase], fill=fur_light)
                draw.ellipse([cx+3, cy+4+bob, cx+7, cy+8+bob-leg_phase], fill=fur_light)

                # Fluffy head from behind
                draw.ellipse([cx-11, cy-14+bob, cx+11, cy-3+bob], fill=fur_cream)
                draw.ellipse([cx-9, cy-12+bob, cx+9, cy-5+bob], fill=fur_white)

                # Floppy ears from behind
                draw.ellipse([cx-13, cy-10+bob+ear_flop, cx-5, cy-1+bob+ear_flop], fill=fur_shadow)
                draw.ellipse([cx-12, cy-9+bob+ear_flop, cx-6, cy-2+bob+ear_flop], fill=fur_cream)
                draw.ellipse([cx+5, cy-10+bob-ear_flop, cx+13, cy-1+bob-ear_flop], fill=fur_shadow)
                draw.ellipse([cx+6, cy-9+bob-ear_flop, cx+12, cy-2+bob-ear_flop], fill=fur_cream)

                # Top head fluff
                draw.ellipse([cx-6, cy-15+bob, cx+6, cy-9+bob], fill=fur_fluff)

            elif direction == 'left':
                # Shadow
                draw.ellipse([cx-7, cy+6, cx+7, cy+10], fill=(0, 0, 0, 25))

                # Fluffy tail wagging
                tail_y = cy - 5 - tail_wag
                draw.ellipse([cx+4, tail_y+bob, cx+13, tail_y+7+bob], fill=fur_cream)
                draw.ellipse([cx+5, tail_y+1+bob, cx+12, tail_y+5+bob], fill=fur_white)
                draw.ellipse([cx+6, tail_y+2+bob, cx+11, tail_y+4+bob], fill=fur_fluff)

                # Fluffy body
                draw.ellipse([cx-5, cy-3+bob, cx+7, cy+6+bob], fill=fur_cream)
                draw.ellipse([cx-3, cy-1+bob, cx+5, cy+4+bob], fill=fur_white)

                # Tiny paws
                draw.ellipse([cx-5, cy+4+bob, cx-1, cy+8+bob+leg_phase], fill=fur_light)
                draw.ellipse([cx+1, cy+4+bob, cx+5, cy+8+bob-leg_phase], fill=fur_shadow)

                # Big fluffy head looking left
                draw.ellipse([cx-13, cy-14+bob, cx+2, cy-1+bob], fill=fur_cream)
                draw.ellipse([cx-11, cy-12+bob, cx, cy-3+bob], fill=fur_white)

                # Long ear
                draw.ellipse([cx-3, cy-13+bob+ear_flop, cx+5, cy-2+bob+ear_flop], fill=fur_shadow)
                draw.ellipse([cx-2, cy-12+bob+ear_flop, cx+4, cy-3+bob+ear_flop], fill=fur_cream)
                draw.ellipse([cx-1, cy-11+bob+ear_flop, cx+3, cy-4+bob+ear_flop], fill=inner_ear)

                # Top fluff
                draw.ellipse([cx-10, cy-15+bob, cx-3, cy-10+bob], fill=fur_fluff)

                # Face fluff
                draw.ellipse([cx-11, cy-9+bob, cx-4, cy-1+bob], fill=fur_white)
                draw.ellipse([cx-10, cy-8+bob, cx-5, cy-2+bob], fill=fur_fluff)

                # Big eye
                draw.ellipse([cx-10, cy-11+bob, cx-4, cy-5+bob], fill=eye_brown)
                draw.ellipse([cx-9, cy-10+bob, cx-5, cy-6+bob], fill=eye_black)
                draw.ellipse([cx-8, cy-10+bob, cx-6, cy-8+bob], fill=eye_shine)
                draw.ellipse([cx-7, cy-7+bob, cx-6, cy-6+bob], fill=eye_shine2)

                # Blush
                draw.ellipse([cx-12, cy-5+bob, cx-8, cy-3+bob], fill=blush)

                # Muzzle fluff
                draw.ellipse([cx-14, cy-6+bob, cx-7, cy-1+bob], fill=fur_cream)
                draw.ellipse([cx-13, cy-5+bob, cx-8, cy-2+bob], fill=fur_fluff)

                # Nose
                draw.ellipse([cx-14, cy-4+bob, cx-10, cy-1+bob], fill=nose_black)
                draw.point((cx-13, cy-3+bob), fill=nose_shine)

                # Tongue
                if happy:
                    draw.ellipse([cx-12, cy-1+bob, cx-9, cy+2+bob], fill=tongue)

            elif direction == 'right':
                # Shadow
                draw.ellipse([cx-7, cy+6, cx+7, cy+10], fill=(0, 0, 0, 25))

                # Fluffy tail wagging
                tail_y = cy - 5 - tail_wag
                draw.ellipse([cx-13, tail_y+bob, cx-4, tail_y+7+bob], fill=fur_cream)
                draw.ellipse([cx-12, tail_y+1+bob, cx-5, tail_y+5+bob], fill=fur_white)
                draw.ellipse([cx-11, tail_y+2+bob, cx-6, tail_y+4+bob], fill=fur_fluff)

                # Fluffy body
                draw.ellipse([cx-7, cy-3+bob, cx+5, cy+6+bob], fill=fur_cream)
                draw.ellipse([cx-5, cy-1+bob, cx+3, cy+4+bob], fill=fur_white)

                # Tiny paws
                draw.ellipse([cx+1, cy+4+bob, cx+5, cy+8+bob+leg_phase], fill=fur_light)
                draw.ellipse([cx-5, cy+4+bob, cx-1, cy+8+bob-leg_phase], fill=fur_shadow)

                # Big fluffy head looking right
                draw.ellipse([cx-2, cy-14+bob, cx+13, cy-1+bob], fill=fur_cream)
                draw.ellipse([cx, cy-12+bob, cx+11, cy-3+bob], fill=fur_white)

                # Long ear
                draw.ellipse([cx-5, cy-13+bob+ear_flop, cx+3, cy-2+bob+ear_flop], fill=fur_shadow)
                draw.ellipse([cx-4, cy-12+bob+ear_flop, cx+2, cy-3+bob+ear_flop], fill=fur_cream)
                draw.ellipse([cx-3, cy-11+bob+ear_flop, cx+1, cy-4+bob+ear_flop], fill=inner_ear)

                # Top fluff
                draw.ellipse([cx+3, cy-15+bob, cx+10, cy-10+bob], fill=fur_fluff)

                # Face fluff
                draw.ellipse([cx+4, cy-9+bob, cx+11, cy-1+bob], fill=fur_white)
                draw.ellipse([cx+5, cy-8+bob, cx+10, cy-2+bob], fill=fur_fluff)

                # Big eye
                draw.ellipse([cx+4, cy-11+bob, cx+10, cy-5+bob], fill=eye_brown)
                draw.ellipse([cx+5, cy-10+bob, cx+9, cy-6+bob], fill=eye_black)
                draw.ellipse([cx+6, cy-10+bob, cx+8, cy-8+bob], fill=eye_shine)
                draw.ellipse([cx+6, cy-7+bob, cx+7, cy-6+bob], fill=eye_shine2)

                # Blush
                draw.ellipse([cx+8, cy-5+bob, cx+12, cy-3+bob], fill=blush)

                # Muzzle fluff
                draw.ellipse([cx+7, cy-6+bob, cx+14, cy-1+bob], fill=fur_cream)
                draw.ellipse([cx+8, cy-5+bob, cx+13, cy-2+bob], fill=fur_fluff)

                # Nose
                draw.ellipse([cx+10, cy-4+bob, cx+14, cy-1+bob], fill=nose_black)
                draw.point((cx+13, cy-3+bob), fill=nose_shine)

                # Tongue
                if happy:
                    draw.ellipse([cx+9, cy-1+bob, cx+12, cy+2+bob], fill=tongue)

            sheet.paste(img, (frame * FRAME_SIZE, dir_idx * FRAME_SIZE))

    sheet.save(os.path.join(SPRITES_DIR, "charlie_spritesheet.png"))
    print(f"Created charlie_spritesheet.png ({sheet_width}x{sheet_height})")


def create_ball_spritesheet():
    """Create ball sprite with bounce animation frames.

    Layout: 8 frames showing squash/stretch cycle for bouncing.
    """
    size = 16
    frames = 8  # More frames for smoother animation
    sheet = Image.new('RGBA', (size * frames, size), (0, 0, 0, 0))

    # Colors - bright red ball with shine
    ball_red = (255, 70, 70, 255)
    ball_highlight = (255, 150, 150, 255)
    ball_shine = (255, 200, 200, 255)
    ball_shadow = (200, 40, 40, 255)
    ball_dark = (170, 30, 30, 255)

    for frame in range(frames):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = 8, 8

        # Squash/stretch animation cycle
        # 0: normal, 1-2: stretch up, 3: normal, 4-5: squash, 6-7: recover
        phase = frame / frames * 2 * math.pi

        stretch = math.sin(phase) * 0.3
        rx = int(6 * (1 - stretch * 0.5))
        ry = int(6 * (1 + stretch))

        # Vertical position adjustment
        cy_offset = int(stretch * 3)

        # Ground shadow (moves with ball)
        shadow_y = 12
        shadow_rx = max(4, rx)
        draw.ellipse([cx-shadow_rx, shadow_y-1, cx+shadow_rx, shadow_y+1],
                     fill=(0, 0, 0, int(50 * (1 - abs(stretch)))))

        # Main ball body
        draw.ellipse([cx-rx, cy-ry+cy_offset, cx+rx, cy+ry+cy_offset], fill=ball_red)

        # Shading - darker bottom
        if ry > 3:
            draw.arc([cx-rx, cy-ry+cy_offset, cx+rx, cy+ry+cy_offset],
                     20, 160, fill=ball_shadow, width=2)
            draw.arc([cx-rx+1, cy-ry+cy_offset+1, cx+rx-1, cy+ry+cy_offset-1],
                     200, 340, fill=ball_dark, width=1)

        # Highlight - top left shine
        highlight_rx = max(1, rx // 2)
        highlight_ry = max(1, ry // 2)
        draw.ellipse([cx-rx+2, cy-ry+2+cy_offset,
                     cx-rx+2+highlight_rx, cy-ry+2+highlight_ry+cy_offset],
                     fill=ball_shine)
        draw.ellipse([cx-rx+1, cy-ry+3+cy_offset,
                     cx-rx+1+highlight_rx+1, cy-ry+3+highlight_ry+1+cy_offset],
                     fill=ball_highlight)

        sheet.paste(img, (frame * size, 0))

    sheet.save(os.path.join(SPRITES_DIR, "ball_spritesheet.png"))
    print(f"Created ball_spritesheet.png ({size * frames}x{size})")

    # Also create a static ball image
    static = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(static)
    # Shadow
    draw.ellipse([2, 11, 14, 14], fill=(0, 0, 0, 40))
    # Ball
    draw.ellipse([2, 2, 14, 14], fill=ball_red)
    # Shading
    draw.arc([2, 2, 14, 14], 20, 160, fill=ball_shadow, width=2)
    # Highlight
    draw.ellipse([4, 3, 7, 6], fill=ball_shine)
    draw.ellipse([5, 4, 8, 7], fill=ball_highlight)

    static.save(os.path.join(SPRITES_DIR, "ball.png"))
    print(f"Created ball.png ({size}x{size})")


if __name__ == "__main__":
    print("Generating animated sprite sheets...")
    print("-" * 40)
    create_player_spritesheet()
    create_charlie_spritesheet()
    create_ball_spritesheet()
    print("-" * 40)
    print("Done! All sprites saved to:", SPRITES_DIR)
