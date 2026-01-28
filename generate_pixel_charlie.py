#!/usr/bin/env python3
"""
Generate pixel-art style Charlie (Shih Tzu) spritesheet.
Draws at 32x32 resolution matching Link to the Past style, then scales up.
"""

from PIL import Image, ImageDraw
import os

# Configuration
BASE_SIZE = 32  # Draw at this size
SCALE = 4       # Scale up by this factor (resulting in 128x128 sprites)
OUTPUT_DIR = "assets/sprites/characters"

# Colors (Zelda ALttP inspired palette)
CREAM_LIGHT = (255, 250, 240, 255)
CREAM_MID   = (240, 225, 200, 255)
CREAM_DARK  = (210, 190, 160, 255)
SHADOW      = (180, 160, 130, 255)

PINK_EAR    = (240, 180, 180, 255)
PINK_TONGUE = (255, 120, 140, 255)
NOSE        = (60, 40, 40, 255)
EYES        = (40, 20, 20, 255)

BALL_RED    = (230, 60, 60, 255)
BONE_WHITE  = (240, 240, 235, 255)
MEAT_BROWN  = (200, 120, 60, 255)

OUTLINE     = (0, 0, 0, 0) # Transparent for now, or colored outline

def draw_charlie(draw, x, y, direction, frame_idx, emotion="happy", item=None):
    """
    Draw Charlie at pixel coords x,y.
    direction: 0=down, 1=up, 2=left, 3=right
    frame_idx: 0=stand, 1=walk1, 2=walk2, 3=walk3
    """
    
    # Offsets for animation
    bob_y = 0
    if frame_idx % 2 == 1:
        bob_y = -1 # Bob up
        
    # Base positions
    cx, cy = x + 16, y + 24 # Feet center
    
    # --- FEET ---
    # Down/Up
    if direction in [0, 1]:
        foot_sep = 3
        # Walk cycle foot offsets
        l_off = 0
        r_off = 0
        if frame_idx == 1: l_off = -2
        if frame_idx == 3: r_off = -2
        
        # Feet
        draw.rectangle([cx - foot_sep - 2, cy - 2 + l_off, cx - foot_sep + 1, cy + l_off], fill=CREAM_DARK)
        draw.rectangle([cx + foot_sep - 1, cy - 2 + r_off, cx + foot_sep + 2, cy + r_off], fill=CREAM_DARK)
        
    # Left (front legs toward head on left, back legs toward tail on right)
    elif direction == 2:
        draw.rectangle([cx + 2 + (frame_idx%2)*2, cy - 2, cx + 5 + (frame_idx%2)*2, cy], fill=CREAM_DARK) # Back legs
        draw.rectangle([cx - 6 - (frame_idx%2)*2, cy - 2, cx - 3 - (frame_idx%2)*2, cy], fill=CREAM_DARK) # Front legs

    # Right (front legs toward head on right, back legs toward tail on left)
    elif direction == 3:
        draw.rectangle([cx - 5 + (frame_idx%2)*2, cy - 2, cx - 2 + (frame_idx%2)*2, cy], fill=CREAM_DARK) # Back legs
        draw.rectangle([cx + 3 - (frame_idx%2)*2, cy - 2, cx + 6 - (frame_idx%2)*2, cy], fill=CREAM_DARK) # Front legs

    # --- BODY ---
    by = y + 16 + bob_y
    if direction == 0: # Down
        draw.rectangle([cx - 5, by - 4, cx + 5, by + 5], fill=CREAM_MID)
        draw.rectangle([cx - 4, by - 3, cx + 4, by + 4], fill=CREAM_LIGHT)
    elif direction == 1: # Up
        draw.rectangle([cx - 5, by - 4, cx + 5, by + 5], fill=CREAM_MID)
        # Tail
        tail_off = (frame_idx % 2) * 2 - 1
        draw.rectangle([cx - 2 + tail_off, by - 6, cx + 2 + tail_off, by - 2], fill=CREAM_LIGHT)
    elif direction == 2: # Left
        # Longer body for side view (12 pixels wide)
        draw.rectangle([cx - 6, by - 4, cx + 6, by + 4], fill=CREAM_MID)
        draw.rectangle([cx - 5, by - 3, cx + 5, by + 3], fill=CREAM_LIGHT)
        # Tail Left (positioned at back of longer body)
        draw.rectangle([cx + 5, by - 5, cx + 8, by - 2], fill=CREAM_LIGHT)
    elif direction == 3: # Right
        # Longer body for side view (12 pixels wide)
        draw.rectangle([cx - 6, by - 4, cx + 6, by + 4], fill=CREAM_MID)
        draw.rectangle([cx - 5, by - 3, cx + 5, by + 3], fill=CREAM_LIGHT)
        # Tail Right (positioned at back of longer body)
        draw.rectangle([cx - 8, by - 5, cx - 5, by - 2], fill=CREAM_LIGHT)

    # --- HEAD ---
    hy = by - 8
    hx = cx
    if direction == 2: hx -= 2
    if direction == 3: hx += 2
    
    # Head Shape
    draw.rectangle([hx - 6, hy - 5, hx + 6, hy + 5], fill=CREAM_MID)
    draw.rectangle([hx - 5, hy - 4, hx + 5, hy + 4], fill=CREAM_LIGHT) # Face face
    
    # Ears
    if direction == 0:
        draw.rectangle([hx - 8, hy - 2, hx - 6, hy + 4], fill=CREAM_DARK) # L
        draw.rectangle([hx + 6, hy - 2, hx + 8, hy + 4], fill=CREAM_DARK) # R
        draw.rectangle([hx - 7, hy + 2, hx - 6, hy + 4], fill=PINK_EAR) # L tip
        draw.rectangle([hx + 6, hy + 2, hx + 7, hy + 4], fill=PINK_EAR) # R tip
    elif direction == 1:
        draw.rectangle([hx - 7, hy - 2, hx - 5, hy + 3], fill=CREAM_DARK)
        draw.rectangle([hx + 5, hy - 2, hx + 7, hy + 3], fill=CREAM_DARK)

    # Face Details (Front)
    if direction == 0:
        # Eyes
        if emotion == "bored":
             draw.rectangle([hx - 3, hy - 1, hx - 1, hy], fill=EYES) # Flat
             draw.rectangle([hx + 1, hy - 1, hx + 3, hy], fill=EYES)
        elif emotion == "confused":
             draw.point((hx - 2, hy - 2), fill=EYES) # High Left
             draw.point((hx + 2, hy), fill=EYES)     # Normal Right
        else: # Happy
            draw.point((hx - 2, hy - 1), fill=EYES)
            draw.point((hx + 2, hy - 1), fill=EYES)
            
        # Nose
        draw.rectangle([hx - 1, hy + 1, hx + 1, hy + 2], fill=NOSE)
        
        # Mouth / Tongue
        mouth_y = hy + 4
        if item:
            if item == "ball":
                draw.rectangle([hx - 2, mouth_y - 2, hx + 2, mouth_y + 2], fill=BALL_RED)
                draw.point((hx - 1, mouth_y - 1), fill=(255, 200, 200, 255)) # Shine
            elif item == "bone":
                draw.rectangle([hx - 4, mouth_y - 1, hx + 4, mouth_y + 1], fill=BONE_WHITE)
                draw.point((hx - 4, mouth_y - 2), fill=BONE_WHITE)
                draw.point((hx + 4, mouth_y - 2), fill=BONE_WHITE)
            elif item == "drumstick":
                draw.rectangle([hx - 2, mouth_y - 2, hx + 2, mouth_y + 2], fill=MEAT_BROWN)
                draw.rectangle([hx + 2, mouth_y - 1, hx + 4, mouth_y], fill=BONE_WHITE)
                
        elif emotion == "happy" and frame_idx % 2 == 1: # Panting
             draw.rectangle([hx - 1, mouth_y, hx + 1, mouth_y + 2], fill=PINK_TONGUE)

    # Face (Side)
    elif direction == 2: # Left
        draw.point((hx - 3, hy - 1), fill=EYES)
        draw.point((hx - 5, hy + 1), fill=NOSE)
        if item == "ball":
             draw.rectangle([hx - 6, hy + 2, hx - 2, hy + 5], fill=BALL_RED)
        elif item == "bone":
             draw.rectangle([hx - 7, hy + 3, hx - 2, hy + 4], fill=BONE_WHITE)
        elif item == "drumstick":
             draw.rectangle([hx - 6, hy + 2, hx - 2, hy + 5], fill=MEAT_BROWN)
    
    elif direction == 3: # Right
        draw.point((hx + 3, hy - 1), fill=EYES)
        draw.point((hx + 5, hy + 1), fill=NOSE)
        if item == "ball":
             draw.rectangle([hx + 2, hy + 2, hx + 6, hy + 5], fill=BALL_RED)
        elif item == "bone":
             draw.rectangle([hx + 2, hy + 3, hx + 7, hy + 4], fill=BONE_WHITE)
        elif item == "drumstick":
             draw.rectangle([hx + 2, hy + 2, hx + 6, hy + 5], fill=MEAT_BROWN)

    # Topknot
    draw.rectangle([hx - 1, hy - 7, hx + 1, hy - 5], fill=CREAM_LIGHT)
    draw.point((hx, hy - 5), fill=PINK_EAR) # Bow

# Configuration
BASE_SIZE = 32  # Draw at this size
SCALE = 1       # Keep 1x scale (32x32) for compatibility with existing Godot setup
OUTPUT_DIR = "assets/sprites/characters"

# ... (Colors remain the same) ...

# ... (draw_charlie remains the same) ...

def generate_sheet():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Layout matching Overworld.tscn expectations:
    # Row 0: Down (Idle, Walk1, Walk2, Walk3)
    # Row 1: Left (Idle, Walk1, Walk2, Walk3)
    # Row 2: Right (Idle, Walk1, Walk2, Walk3)
    # Row 3: Up (Idle, Walk1, Walk2, Walk3)
    # followed by extra animations
    
    # Format: (anim_type, direction, emotion, item)
    # We will generate 4 frames per row.
    # For standard rows: Frame 0 is Idle, Frames 1-3 are Walk cycle.
    
    standard_rows = [
        ("down", "happy", None),  # Row 0
        ("left", "happy", None),  # Row 1
        ("right", "happy", None), # Row 2
        ("up", "happy", None),    # Row 3
    ]
    
    extra_rows = [
        # Extras - Just using walk cycle format for now (0=Idle/Stand, 1-3=Walk)
        # Bored/Confused (Down only for now)
        ("down", "bored", None),     # Row 4
        ("down", "confused", None),  # Row 5
        
        # With Ball
        ("down", "happy", "ball"),   # Row 6
        ("left", "happy", "ball"),   # Row 7
        ("right", "happy", "ball"),  # Row 8
        ("up", "happy", "ball"),     # Row 9
        
        # With Bone
        ("down", "happy", "bone"),   # Row 10
        ("left", "happy", "bone"),   # Row 11
        ("right", "happy", "bone"),  # Row 12
        ("up", "happy", "bone"),     # Row 13
        
        # With Drumstick
        ("down", "happy", "drumstick"),   # Row 14
        ("left", "happy", "drumstick"),   # Row 15
        ("right", "happy", "drumstick"),  # Row 16
        ("up", "happy", "drumstick"),     # Row 17
    ]
    
    sheet_w = 4 * BASE_SIZE * SCALE
    sheet_h = (len(standard_rows) + len(extra_rows)) * BASE_SIZE * SCALE
    
    img = Image.new('RGBA', (sheet_w, sheet_h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    dir_map = {"down": 0, "up": 1, "left": 2, "right": 3}
    
    current_row = 0
    
    # 1. Standard Rows (Hybrid Idle/Walk)
    for dirname, emotion, item in standard_rows:
        y = current_row * BASE_SIZE * SCALE
        d = dir_map[dirname]
        
        # Col 0: Idle
        draw_charlie(draw, 0, y, d, 0, emotion, item)
        
        # Col 1-3: Walk
        for col in range(1, 4):
            x = col * BASE_SIZE * SCALE
            # frame_idx mapping: 1->1, 2->2, 3->3 (walk frames) + offset if needed
            # In draw_charlie, frame_idx 0=stand, 1=walk1, 2=walk2, 3=walk3
            draw_charlie(draw, x, y, d, col, emotion, item)
            
        current_row += 1

    # 2. Extra Rows
    for dirname, emotion, item in extra_rows:
        y = current_row * BASE_SIZE * SCALE
        d = dir_map[dirname]
        
        # Col 0: Idle/Stand
        draw_charlie(draw, 0, y, d, 0, emotion, item)
        
        # Col 1-3: Walk
        for col in range(1, 4):
            x = col * BASE_SIZE * SCALE
            draw_charlie(draw, x, y, d, col, emotion, item)
            
        current_row += 1

    # Scale up? No, SCALE is applied during drawing coords if we wanted global scale
    # But draw_charlie uses raw coords. 
    # If SCALE > 1, we should draw small then resize. 
    # But here we want output to be 32x32.
    
    outfile = os.path.join(OUTPUT_DIR, "charlie_spritesheet.png")
    img.save(outfile)
    print(f"Generated {outfile} ({sheet_w}x{sheet_h})")

if __name__ == "__main__":
    generate_sheet()
