#!/usr/bin/env python3
"""
Generate extended Player spritesheet for Charlie's Island Adventure.
"""

from PIL import Image, ImageDraw
import os
import math

# Output directory (matching existing structure)
SPRITES_DIR = "assets/sprites/characters"
os.makedirs(SPRITES_DIR, exist_ok=True)

FRAME_SIZE = 32

# Colors
SKIN = (255, 220, 186, 255)
SKIN_SHADOW = (230, 190, 160, 255)
HAIR = (255, 220, 100, 255)
HAIR_SHADOW = (230, 185, 70, 255)
HAIR_HIGHLIGHT = (255, 240, 150, 255)
DRESS = (255, 120, 160, 255)
DRESS_SHADOW = (220, 90, 130, 255)
DRESS_HIGHLIGHT = (255, 160, 190, 255)
EYES = (40, 80, 140, 255)
EYE_WHITE = (255, 255, 255, 255)
SHOES = (140, 90, 60, 255)
SHADOW_COLOR = (0, 0, 0, 40)

# Charlie Colors (for holding)
FUR_CREAM = (255, 248, 235, 255)
FUR_WHITE = (255, 253, 250, 255)
FUR_SHADOW = (240, 225, 205, 255)


def draw_charlie_held(draw, cx, cy, bob):
    """Draw Charlie being held in arms."""
    # Simple fluffy ball representation
    # Body
    draw.ellipse([cx-6, cy-6+bob, cx+6, cy+4+bob], fill=FUR_CREAM)
    draw.ellipse([cx-4, cy-4+bob, cx+4, cy+2+bob], fill=FUR_WHITE)
    
    # Head/Ears
    draw.ellipse([cx-6, cy-8+bob, cx-2, cy-2+bob], fill=FUR_SHADOW) # L Ear
    draw.ellipse([cx+2, cy-8+bob, cx+6, cy-2+bob], fill=FUR_SHADOW) # R Ear
    
    # Face
    draw.ellipse([cx-3, cy-5+bob, cx-1, cy-3+bob], fill=(20, 20, 20, 255)) # Eye
    draw.ellipse([cx+1, cy-5+bob, cx+3, cy-3+bob], fill=(20, 20, 20, 255)) # Eye
    draw.ellipse([cx-1, cy-3+bob, cx+1, cy-1+bob], fill=(40, 30, 30, 255)) # Nose

def draw_player(draw, x, y, direction, action, frame):
    """
    Draw the player character.
    x, y: Top-left coordinate of the tile
    direction: 'down', 'up', 'left', 'right'
    action: 'idle', 'walk', 'bored', 'confused', 'pickup', 'hold_idle', 'hold_walk'
    frame: 0-3
    """
    
    # --- Animation State Calculation ---
    bob = 0
    leg_phase = 0
    arm_swing = 0
    eyes_state = "normal"
    mouth_state = "smile"
    holding_height = 0
    pickup_progress = 0
    
    # Walk Cycle
    if "walk" in action and frame > 0:
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
            
    # Idle Cycle (breathing)
    if action == "idle" or action == "hold_idle":
        if frame % 2 == 1: # Frames 1 and 3
            bob = 1 # Breathe down
        if action == "idle" and frame % 2 == 0: # Tongue out occasionally? 
            # Request said: "4 frames showing Player stood still breathing, sticking his tongue out"
            # Let's make tongue out constant or flickering? "sticking his tongue out" implies state.
            mouth_state = "tongue"
            
    # Bored
    if action == "bored":
        eyes_state = "bored"
        mouth_state = "flat"
        if frame == 1: leg_phase = 1 # Tap foot
        if frame == 3: leg_phase = 0
        
    # Confused
    if action == "confused":
        eyes_state = "confused"
        mouth_state = "o"
        # Maybe scratch head?
        if frame > 1:
            arm_swing = 4 # Hand to head
            
    # Pickup
    if action == "pickup":
        # Frame 0: Stand, 1: Bend, 2: Lift, 3: Hold High
        if frame == 1: 
            bob = 4 # crouch
            pickup_progress = 1
        elif frame == 2:
            bob = 2
            pickup_progress = 2
        elif frame == 3:
            bob = 0
            pickup_progress = 3 # Held
            
    # Holding
    is_holding = "hold" in action or (action=="pickup" and frame >= 2)
    
    cx, cy = x + 16, y + 16
    
    # --- DRAWING ---
    
    # Shadow
    draw.ellipse([cx-7, cy+10, cx+7, cy+13], fill=SHADOW_COLOR)

    # SHOES & LEGS
    if direction in ['down', 'up']:
        # Shoes
        draw.ellipse([cx-6+leg_phase, cy+8+bob, cx-2+leg_phase, cy+12+bob], fill=SHOES)
        draw.ellipse([cx+2-leg_phase, cy+8+bob, cx+6-leg_phase, cy+12+bob], fill=SHOES)
        # Legs
        draw.rectangle([cx-5, cy+4+bob, cx-2, cy+9+bob+leg_phase], fill=SKIN)
        draw.rectangle([cx+2, cy+4+bob, cx+5, cy+9+bob-leg_phase], fill=SKIN)
    elif direction == 'left':
        # Side view legs
        draw.ellipse([cx+1-leg_phase, cy+8+bob, cx+4-leg_phase, cy+12+bob], fill=SHOES) # Back
        draw.rectangle([cx+1, cy+4+bob, cx+4, cy+9+bob-leg_phase], fill=SKIN_SHADOW)
        draw.ellipse([cx-4+leg_phase, cy+8+bob, cx-1+leg_phase, cy+12+bob], fill=SHOES) # Front
        draw.rectangle([cx-4, cy+4+bob, cx-1, cy+9+bob+leg_phase], fill=SKIN)
    elif direction == 'right':
        draw.ellipse([cx-4+leg_phase, cy+8+bob, cx-1+leg_phase, cy+12+bob], fill=SHOES) # Back
        draw.rectangle([cx-4, cy+4+bob, cx-1, cy+9+bob-leg_phase], fill=SKIN_SHADOW)
        draw.ellipse([cx+1-leg_phase, cy+8+bob, cx+4-leg_phase, cy+12+bob], fill=SHOES) # Front
        draw.rectangle([cx+1, cy+4+bob, cx+4, cy+9+bob+leg_phase], fill=SKIN)

    # BODY / DRESS
    dress_y = cy + bob
    if direction == 'down':
        draw.ellipse([cx-8, dress_y-3, cx+8, dress_y+7], fill=DRESS)
        draw.ellipse([cx-6, dress_y-1, cx+6, dress_y+5], fill=DRESS_HIGHLIGHT)
    elif direction == 'up':
        draw.ellipse([cx-8, dress_y-3, cx+8, dress_y+7], fill=DRESS)
    elif direction in ['left', 'right']:
        draw.ellipse([cx-5, dress_y-3, cx+5, dress_y+7], fill=DRESS)
        draw.ellipse([cx-3, dress_y-1, cx+3, dress_y+5], fill=DRESS_HIGHLIGHT)
        
    # ARMS (Behind if holding?)
    # If holding, arms are different.
    
    if not is_holding:
        if direction == 'down':
            if action == "confused" and frame > 1: # Scratch head
                 draw.ellipse([cx+6, dress_y-8, cx+10, dress_y], fill=SKIN) # Right arm up
                 draw.ellipse([cx-10, dress_y-1, cx-6, dress_y+5+arm_swing], fill=SKIN) # Left normal
            else:
                draw.ellipse([cx-10, dress_y-1, cx-6, dress_y+5+arm_swing], fill=SKIN)
                draw.ellipse([cx+6, dress_y-1, cx+10, dress_y+5-arm_swing], fill=SKIN)
        elif direction == 'up':
            draw.ellipse([cx-10, dress_y-1, cx-6, dress_y+5+arm_swing], fill=SKIN)
            draw.ellipse([cx+6, dress_y-1, cx+10, dress_y+5-arm_swing], fill=SKIN)
        elif direction == 'left':
            draw.ellipse([cx-3, dress_y-1, cx+1, dress_y+5+arm_swing], fill=SKIN)
        elif direction == 'right':
             draw.ellipse([cx-1, dress_y-1, cx+3, dress_y+5-arm_swing], fill=SKIN)
    else:
        # Holding Arms - wrapped around center
        if direction == 'down':
             draw.ellipse([cx-9, dress_y-2, cx-3, dress_y+3], fill=SKIN) # L
             draw.ellipse([cx+3, dress_y-2, cx+9, dress_y+3], fill=SKIN) # R
        elif direction in ['left', 'right']:
             draw.ellipse([cx-2, dress_y-2, cx+2, dress_y+3], fill=SKIN)

    # CHARLIE (If holding)
    if is_holding and direction != 'up':
        charlie_y = cy + bob + 2
        if action == "pickup":
            if frame == 2: charlie_y += 4
            if frame == 3: charlie_y -= 1
        
        offset_x = 0
        if direction == 'left': offset_x = -4
        if direction == 'right': offset_x = 4
        
        draw_charlie_held(draw, cx + offset_x, charlie_y, 0)
        
    # HEAD
    head_y = cy - 13 + bob
    if action == "pickup" and frame == 1: head_y += 4 # Bend down
    
    if direction == 'down':
        # Face
        draw.ellipse([cx-7, head_y, cx+7, head_y+11], fill=SKIN)
        # Hair Base
        draw.ellipse([cx-8, head_y-2, cx+8, head_y+6], fill=HAIR)
        draw.ellipse([cx-7, head_y-1, cx-3, head_y+4], fill=HAIR_HIGHLIGHT)
        # Sides
        draw.ellipse([cx-9, head_y+1, cx-5, head_y+10], fill=HAIR)
        draw.ellipse([cx+5, head_y+1, cx+9, head_y+10], fill=HAIR)
        
        # Eyes
        if eyes_state == "normal":
            draw.ellipse([cx-5, head_y+4, cx-2, head_y+8], fill=EYE_WHITE)
            draw.ellipse([cx+2, head_y+4, cx+5, head_y+8], fill=EYE_WHITE)
            draw.ellipse([cx-4, head_y+5, cx-2, head_y+8], fill=EYES)
            draw.ellipse([cx+2, head_y+5, cx+4, head_y+8], fill=EYES)
        elif eyes_state == "bored":
            draw.rectangle([cx-5, head_y+5, cx-2, head_y+6], fill=EYES) # Flat lid
            draw.rectangle([cx+2, head_y+5, cx+5, head_y+6], fill=EYES)
        elif eyes_state == "confused":
            draw.ellipse([cx-5, head_y+3, cx-2, head_y+7], fill=EYES) # One high
            draw.ellipse([cx+2, head_y+5, cx+5, head_y+8], fill=EYES) # One low
            
        # Mouth
        if mouth_state == "smile":
             draw.arc([cx-2, head_y+7, cx+2, head_y+9], 0, 180, fill=(200, 100, 100, 255))
        elif mouth_state == "tongue":
             draw.ellipse([cx-1, head_y+9, cx+1, head_y+11], fill=(255, 100, 100, 255))
        elif mouth_state == "flat":
             draw.line([cx-2, head_y+9, cx+2, head_y+9], fill=(200, 100, 100, 255))
        elif mouth_state == "o":
             draw.ellipse([cx-1, head_y+8, cx+1, head_y+10], fill=(200, 100, 100, 255))

        # Blush
        draw.ellipse([cx-6, head_y+8, cx-3, head_y+10], fill=(255, 180, 180, 100))
        draw.ellipse([cx+3, head_y+8, cx+6, head_y+10], fill=(255, 180, 180, 100))
        
        # Question Mark
        if action == "confused":
             draw.text((cx+6, head_y-5), "?", fill=(255, 255, 255, 255))

    elif direction == 'up':
        draw.ellipse([cx-7, head_y, cx+7, head_y+11], fill=HAIR)
        draw.ellipse([cx-9, head_y-2, cx+9, head_y+8], fill=HAIR)
        draw.ellipse([cx-8, head_y-1, cx-2, head_y+6], fill=HAIR_HIGHLIGHT)
        # Ponytail/Back hair
        draw.ellipse([cx-8, head_y+3, cx+8, head_y+11], fill=HAIR)
        
    elif direction == 'left':
        draw.ellipse([cx-6, head_y, cx+4, head_y+11], fill=SKIN)
        draw.ellipse([cx-7, head_y-2, cx+5, head_y+6], fill=HAIR)
        draw.ellipse([cx-6, head_y-1, cx-2, head_y+4], fill=HAIR_HIGHLIGHT)
        draw.ellipse([cx+2, head_y+1, cx+6, head_y+10], fill=HAIR) # Back hair
        
        # Profile Eye
        draw.ellipse([cx-4, head_y+4, cx-1, head_y+8], fill=EYE_WHITE)
        draw.ellipse([cx-4, head_y+5, cx-2, head_y+8], fill=EYES)
        
    elif direction == 'right':
        draw.ellipse([cx-4, head_y, cx+6, head_y+11], fill=SKIN)
        draw.ellipse([cx-5, head_y-2, cx+7, head_y+6], fill=HAIR)
        draw.ellipse([cx+2, head_y-1, cx+6, head_y+4], fill=HAIR_HIGHLIGHT)
        draw.ellipse([cx-6, head_y+1, cx-2, head_y+10], fill=HAIR) # Back hair
        
        # Profile Eye
        draw.ellipse([cx+1, head_y+4, cx+4, head_y+8], fill=EYE_WHITE)
        draw.ellipse([cx+2, head_y+5, cx+4, head_y+8], fill=EYES)
        
    # CHARLIE (If holding UP, draw him on top of player)
    # Actually, if UP, Charlie is behind head usually, or obscured.
    # User said "Holding Charlie Walking Up". Usually you see the held object's top or it's obscured.
    # Let's assume obscured by head if held against chest, or visible if held high.
    # Zelda holds things high. Let's make it visible above head (Zelda lift style) or chest?
    # Requirement: "Holding Charlie".
    # If walking UP holding something, usually it's hidden or just peek of top. 
    # Let's draw peeking top if 'up'.
    if is_holding and direction == 'up':
        # Draw just ears/top behind head?
        # Actually in Zelda, when holding normal items, you hold them over head. But a dog?
        # Let's assume carrying in arms. So blocked by player's back/head.
        # Maybe just draw little paws sticking out side?
        pass


def generate_extended_sheet():
    # 13 rows, 4 frames each
    rows = [
        ("idle", "down"),           # Row 0
        ("bored", "down"),          # Row 1
        ("confused", "down"),       # Row 2
        ("walk", "left"),           # Row 3
        ("walk", "right"),          # Row 4
        ("walk", "up"),             # Row 5
        ("walk", "down"),           # Row 6
        ("pickup", "down"),         # Row 7
        ("hold_idle", "down"),      # Row 8
        ("hold_walk", "left"),      # Row 9
        ("hold_walk", "right"),     # Row 10
        ("hold_walk", "up"),        # Row 11
        ("hold_walk", "down"),      # Row 12
    ]
    
    sheet_width = FRAME_SIZE * 4
    sheet_height = FRAME_SIZE * len(rows)
    
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    
    for row_idx, (action, direction) in enumerate(rows):
        y = row_idx * FRAME_SIZE
        print(f"Generating Row {row_idx}: {action} {direction}")
        
        for col in range(4):
            x = col * FRAME_SIZE
            draw_player(d, x, y, direction, action, col)
            
    outfile = os.path.join(SPRITES_DIR, "player_spritesheet.png")
    sheet.save(outfile)
    print(f"Saved to {outfile}")

if __name__ == "__main__":
    generate_extended_sheet()
