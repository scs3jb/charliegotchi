#!/usr/bin/env python3
"""
Generate detailed animated Charlie (Shih Tzu) spritesheet
Higher resolution (128x128) with multiple animation frames including ball-in-mouth
"""

from PIL import Image, ImageDraw, ImageFilter
import math

# Create output directories
import os
os.makedirs("assets/sprites/characters", exist_ok=True)

# Colors - softer, cuter palette for a cream/white Shih Tzu
CREAM = (252, 248, 242)
CREAM_LIGHT = (255, 253, 250)
CREAM_MID = (245, 238, 228)
CREAM_SHADOW = (232, 222, 205)
CREAM_DARK = (215, 200, 180)

# Accent colors
PINK_EAR = (255, 215, 210)
PINK_TONGUE = (255, 150, 160)
PINK_TONGUE_LIGHT = (255, 185, 190)
PINK_PAW = (255, 205, 200)
PINK_BLUSH = (255, 190, 190, 60)  # Semi-transparent blush

# Features
NOSE_BLACK = (30, 25, 25)
NOSE_HIGHLIGHT = (65, 60, 60)
EYE_BLACK = (20, 15, 15)
EYE_DARK = (40, 35, 35)
EYE_SHINE = (255, 255, 255)
EYE_SHINE2 = (210, 225, 255)  # Slight blue tint for sparkle

# Ball color
BALL_RED = (230, 70, 70)
BALL_LIGHT = (255, 120, 120)
BALL_DARK = (180, 45, 45)

# Outline for definition
OUTLINE = (195, 185, 170)


def draw_fluffy_edge(draw, cx, cy, radius, color, num_tufts=12):
    """Draw fluffy fur tufts around an edge"""
    for i in range(num_tufts):
        angle = (i / num_tufts) * 2 * math.pi + (i % 2) * 0.15
        # Vary the tuft distance
        dist = radius + (2 if i % 2 == 0 else 4)
        fx = cx + int(dist * math.cos(angle))
        fy = cy + int(dist * math.sin(angle))
        tuft_size = 4 + (i % 3)
        draw.ellipse([fx - tuft_size, fy - tuft_size,
                      fx + tuft_size, fy + tuft_size], fill=color)


def draw_shih_tzu_eye(draw, cx, cy, radius, looking_dir=0):
    """Draw a cute, sparkly Shih Tzu eye"""
    r = radius

    # Outer eye (round, Shih Tzus have prominent round eyes)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=EYE_BLACK)

    # Inner gradient ring
    inner = r * 0.85
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=EYE_DARK)

    # Main highlight (large, positioned for cute look)
    h_offset_x = -r * 0.25 + looking_dir * 2
    h_offset_y = -r * 0.25
    h_size = r * 0.5
    draw.ellipse([cx + h_offset_x - h_size, cy + h_offset_y - h_size,
                  cx + h_offset_x + h_size, cy + h_offset_y + h_size], fill=EYE_SHINE)

    # Secondary sparkle highlight (smaller, different position)
    h2_x = cx + r * 0.3
    h2_y = cy + r * 0.3
    h2_size = r * 0.2
    draw.ellipse([h2_x - h2_size, h2_y - h2_size,
                  h2_x + h2_size, h2_y + h2_size], fill=EYE_SHINE2)

    # Tiny tertiary sparkle
    h3_x = cx - r * 0.1
    h3_y = cy + r * 0.15
    h3_size = r * 0.12
    draw.ellipse([h3_x - h3_size, h3_y - h3_size,
                  h3_x + h3_size, h3_y + h3_size], fill=(255, 255, 255, 180))


def draw_shih_tzu_nose(draw, cx, cy, width, height):
    """Draw a cute button nose"""
    # Main nose shape (slightly heart-shaped)
    draw.ellipse([cx - width, cy - height*0.6, cx + width, cy + height*0.6], fill=NOSE_BLACK)

    # Subtle nostril indications
    nostril_y = cy + height * 0.1
    draw.ellipse([cx - width*0.5, nostril_y - 2, cx - width*0.15, nostril_y + 2], fill=(15, 10, 10))
    draw.ellipse([cx + width*0.15, nostril_y - 2, cx + width*0.5, nostril_y + 2], fill=(15, 10, 10))

    # Highlight
    draw.ellipse([cx - width*0.35, cy - height*0.35, cx + width*0.1, cy], fill=NOSE_HIGHLIGHT)


def draw_charlie_frame(size=128, direction="down", frame=0, has_ball=False, mouth_open=True):
    """
    Draw a single frame of Charlie the Shih Tzu
    direction: "down", "up", "left", "right"
    frame: animation frame (0-3 for walk cycle)
    has_ball: whether Charlie is holding a ball
    mouth_open: for panting animation
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor (base design is for 128px)
    s = size / 128

    # Animation offsets
    bob = int(math.sin(frame * math.pi / 2) * 3 * s)  # Bouncy walk
    ear_bob = int(math.sin(frame * math.pi / 2 + 0.5) * 2 * s)  # Ears lag slightly
    tail_wag = int(math.sin(frame * math.pi) * 4 * s)  # Tail wagging

    # Paw positions for walk cycle
    paw_offsets = [
        (0, 0, 0, 0),
        (-3, 2, 3, -2),
        (0, 0, 0, 0),
        (3, -2, -3, 2),
    ]
    paw_off = paw_offsets[frame % 4]

    if direction == "down":
        # Front-facing view
        body_y = 76 * s + bob
        head_y = 44 * s + bob

        # BODY (fluffy oval)
        draw.ellipse([int(36*s), int(body_y - 20*s), int(92*s), int(body_y + 20*s)], fill=CREAM_MID)
        draw.ellipse([int(40*s), int(body_y - 16*s), int(88*s), int(body_y + 14*s)], fill=CREAM)
        draw.ellipse([int(36*s), int(body_y + 4*s), int(92*s), int(body_y + 20*s)], fill=CREAM_SHADOW)
        # Body fluff
        draw_fluffy_edge(draw, int(64*s), int(body_y), int(26*s), CREAM, 16)

        # TAIL (fluffy poof, curled up)
        tail_x = int(88*s + tail_wag)
        tail_y = int(body_y - 14*s)
        draw.ellipse([tail_x - int(10*s), tail_y - int(8*s), tail_x + int(10*s), tail_y + int(8*s)], fill=CREAM)
        draw.ellipse([tail_x - int(7*s), tail_y - int(10*s), tail_x + int(7*s), tail_y - int(2*s)], fill=CREAM_LIGHT)
        draw_fluffy_edge(draw, tail_x, tail_y, int(8*s), CREAM, 8)

        # EARS (floppy, behind head)
        # Left ear
        ear_l_x, ear_l_y = int(28*s), int(head_y + 4*s + ear_bob)
        draw.ellipse([ear_l_x - int(14*s), ear_l_y - int(6*s), ear_l_x + int(6*s), ear_l_y + int(26*s)], fill=CREAM_SHADOW)
        draw.ellipse([ear_l_x - int(11*s), ear_l_y - int(3*s), ear_l_x + int(3*s), ear_l_y + int(22*s)], fill=CREAM_MID)
        draw.ellipse([ear_l_x - int(8*s), ear_l_y + int(4*s), ear_l_x, ear_l_y + int(16*s)], fill=PINK_EAR)
        # Ear fluff
        for fy in range(int(ear_l_y + 12*s), int(ear_l_y + 26*s), int(5*s)):
            draw.ellipse([ear_l_x - int(13*s), fy - int(3*s), ear_l_x - int(7*s), fy + int(3*s)], fill=CREAM)

        # Right ear
        ear_r_x, ear_r_y = int(100*s), int(head_y + 4*s + ear_bob)
        draw.ellipse([ear_r_x - int(6*s), ear_r_y - int(6*s), ear_r_x + int(14*s), ear_r_y + int(26*s)], fill=CREAM_SHADOW)
        draw.ellipse([ear_r_x - int(3*s), ear_r_y - int(3*s), ear_r_x + int(11*s), ear_r_y + int(22*s)], fill=CREAM_MID)
        draw.ellipse([ear_r_x, ear_r_y + int(4*s), ear_r_x + int(8*s), ear_r_y + int(16*s)], fill=PINK_EAR)
        for fy in range(int(ear_r_y + 12*s), int(ear_r_y + 26*s), int(5*s)):
            draw.ellipse([ear_r_x + int(7*s), fy - int(3*s), ear_r_x + int(13*s), fy + int(3*s)], fill=CREAM)

        # HEAD (big fluffy ball)
        draw.ellipse([int(32*s), int(head_y - 26*s), int(96*s), int(head_y + 26*s)], fill=CREAM)
        draw.ellipse([int(36*s), int(head_y - 22*s), int(92*s), int(head_y + 20*s)], fill=CREAM_LIGHT)
        draw_fluffy_edge(draw, int(64*s), int(head_y), int(30*s), CREAM, 20)

        # TOPKNOT (signature Shih Tzu poof)
        topknot_y = int(head_y - 26*s)
        draw.ellipse([int(48*s), topknot_y - int(8*s), int(80*s), topknot_y + int(14*s)], fill=CREAM)
        draw.ellipse([int(52*s), topknot_y - int(12*s), int(76*s), topknot_y + int(6*s)], fill=CREAM_LIGHT)
        # Tufts on top
        draw.ellipse([int(52*s), topknot_y - int(16*s), int(64*s), topknot_y - int(4*s)], fill=CREAM)
        draw.ellipse([int(64*s), topknot_y - int(18*s), int(76*s), topknot_y - int(6*s)], fill=CREAM)
        draw.ellipse([int(58*s), topknot_y - int(14*s), int(70*s), topknot_y - int(2*s)], fill=CREAM_LIGHT)

        # CHEEK FLUFF
        draw.ellipse([int(24*s), int(head_y - 4*s), int(48*s), int(head_y + 18*s)], fill=CREAM)
        draw.ellipse([int(80*s), int(head_y - 4*s), int(104*s), int(head_y + 18*s)], fill=CREAM)

        # SNOUT area (lighter, protruding)
        snout_y = int(head_y + 10*s)
        draw.ellipse([int(48*s), snout_y - int(12*s), int(80*s), snout_y + int(10*s)], fill=CREAM_LIGHT)

        # EYES (big, round, sparkly)
        eye_y = int(head_y - 4*s)
        draw_shih_tzu_eye(draw, int(48*s), eye_y, int(10*s))
        draw_shih_tzu_eye(draw, int(80*s), eye_y, int(10*s))

        # EYEBROWS (fur tufts)
        draw.ellipse([int(40*s), eye_y - int(14*s), int(56*s), eye_y - int(6*s)], fill=CREAM)
        draw.ellipse([int(72*s), eye_y - int(14*s), int(88*s), eye_y - int(6*s)], fill=CREAM)

        # BLUSH
        blush_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        blush_draw = ImageDraw.Draw(blush_img)
        blush_draw.ellipse([int(28*s), int(head_y + 4*s), int(44*s), int(head_y + 14*s)], fill=PINK_BLUSH)
        blush_draw.ellipse([int(84*s), int(head_y + 4*s), int(100*s), int(head_y + 14*s)], fill=PINK_BLUSH)
        img = Image.alpha_composite(img, blush_img)
        draw = ImageDraw.Draw(img)

        # NOSE
        nose_y = int(head_y + 10*s)
        draw_shih_tzu_nose(draw, int(64*s), nose_y, int(7*s), int(5*s))

        # MOUTH
        mouth_y = int(nose_y + 8*s)
        if has_ball:
            # Ball in mouth
            ball_y = int(mouth_y + 6*s)
            draw.ellipse([int(52*s), ball_y - int(10*s), int(76*s), ball_y + int(10*s)], fill=BALL_RED)
            draw.ellipse([int(56*s), ball_y - int(7*s), int(66*s), ball_y - int(1*s)], fill=BALL_LIGHT)
            draw.ellipse([int(62*s), ball_y + int(3*s), int(72*s), ball_y + int(8*s)], fill=BALL_DARK)
        elif mouth_open:
            # Happy panting mouth
            draw.arc([int(52*s), mouth_y - int(6*s), int(64*s), mouth_y + int(4*s)], 0, 180, fill=OUTLINE, width=int(2*s))
            draw.arc([int(64*s), mouth_y - int(6*s), int(76*s), mouth_y + int(4*s)], 0, 180, fill=OUTLINE, width=int(2*s))
            # Tongue
            tongue_y = int(mouth_y + 5*s)
            draw.ellipse([int(58*s), tongue_y - int(3*s), int(70*s), tongue_y + int(10*s)], fill=PINK_TONGUE)
            draw.ellipse([int(60*s), tongue_y - int(3*s), int(68*s), tongue_y + int(3*s)], fill=PINK_TONGUE_LIGHT)
        else:
            # Closed smile
            draw.arc([int(52*s), mouth_y - int(6*s), int(64*s), mouth_y + int(2*s)], 0, 180, fill=OUTLINE, width=int(2*s))
            draw.arc([int(64*s), mouth_y - int(6*s), int(76*s), mouth_y + int(2*s)], 0, 180, fill=OUTLINE, width=int(2*s))

        # PAWS
        paw_y = int(104*s + bob)
        # Left front
        lf_x = int(44*s + paw_off[0]*s)
        draw.ellipse([lf_x - int(9*s), paw_y - int(7*s), lf_x + int(9*s), paw_y + int(7*s)], fill=CREAM)
        draw.ellipse([lf_x - int(6*s), paw_y + int(1*s), lf_x + int(6*s), paw_y + int(7*s)], fill=PINK_PAW)
        # Right front
        rf_x = int(84*s + paw_off[1]*s)
        draw.ellipse([rf_x - int(9*s), paw_y - int(7*s), rf_x + int(9*s), paw_y + int(7*s)], fill=CREAM)
        draw.ellipse([rf_x - int(6*s), paw_y + int(1*s), rf_x + int(6*s), paw_y + int(7*s)], fill=PINK_PAW)

    elif direction == "up":
        # Back view
        body_y = 76 * s + bob
        head_y = 44 * s + bob

        # TAIL (prominent from back, happy curl)
        tail_x = int(64*s + tail_wag)
        tail_y = int(body_y - 26*s)
        draw.ellipse([tail_x - int(14*s), tail_y - int(10*s), tail_x + int(14*s), tail_y + int(10*s)], fill=CREAM)
        draw.ellipse([tail_x - int(10*s), tail_y - int(12*s), tail_x + int(10*s), tail_y - int(2*s)], fill=CREAM_LIGHT)
        draw_fluffy_edge(draw, tail_x, tail_y, int(12*s), CREAM, 10)

        # BODY
        draw.ellipse([int(36*s), int(body_y - 20*s), int(92*s), int(body_y + 20*s)], fill=CREAM_MID)
        draw.ellipse([int(40*s), int(body_y - 16*s), int(88*s), int(body_y + 14*s)], fill=CREAM)
        draw_fluffy_edge(draw, int(64*s), int(body_y), int(26*s), CREAM_MID, 16)

        # EARS (visible from back)
        ear_l_x = int(28*s)
        draw.ellipse([ear_l_x - int(12*s), int(head_y - 4*s + ear_bob), ear_l_x + int(6*s), int(head_y + 24*s + ear_bob)], fill=CREAM_SHADOW)
        ear_r_x = int(100*s)
        draw.ellipse([ear_r_x - int(6*s), int(head_y - 4*s + ear_bob), ear_r_x + int(12*s), int(head_y + 24*s + ear_bob)], fill=CREAM_SHADOW)

        # HEAD (back)
        draw.ellipse([int(32*s), int(head_y - 26*s), int(96*s), int(head_y + 26*s)], fill=CREAM_MID)
        draw.ellipse([int(36*s), int(head_y - 22*s), int(92*s), int(head_y + 20*s)], fill=CREAM)
        draw_fluffy_edge(draw, int(64*s), int(head_y), int(30*s), CREAM_MID, 20)

        # TOPKNOT from back
        topknot_y = int(head_y - 26*s)
        draw.ellipse([int(48*s), topknot_y - int(8*s), int(80*s), topknot_y + int(14*s)], fill=CREAM)
        draw.ellipse([int(54*s), topknot_y - int(10*s), int(74*s), topknot_y + int(4*s)], fill=CREAM_LIGHT)

        # PAWS
        paw_y = int(104*s + bob)
        draw.ellipse([int(44*s) - int(9*s), paw_y - int(7*s), int(44*s) + int(9*s), paw_y + int(7*s)], fill=CREAM_SHADOW)
        draw.ellipse([int(84*s) - int(9*s), paw_y - int(7*s), int(84*s) + int(9*s), paw_y + int(7*s)], fill=CREAM_SHADOW)

    elif direction == "left":
        # Side view facing left
        body_y = 76 * s + bob
        head_x = 48 * s
        head_y = 44 * s + bob

        # TAIL (right side)
        tail_x = int(104*s)
        tail_y = int(body_y - 12*s + tail_wag)
        draw.ellipse([tail_x - int(10*s), tail_y - int(10*s), tail_x + int(10*s), tail_y + int(8*s)], fill=CREAM)
        draw.ellipse([tail_x - int(6*s), tail_y - int(14*s), tail_x + int(8*s), tail_y - int(2*s)], fill=CREAM_LIGHT)

        # BODY (side profile)
        draw.ellipse([int(40*s), int(body_y - 22*s), int(100*s), int(body_y + 22*s)], fill=CREAM_MID)
        draw.ellipse([int(44*s), int(body_y - 18*s), int(96*s), int(body_y + 16*s)], fill=CREAM)
        draw.ellipse([int(40*s), int(body_y + 4*s), int(100*s), int(body_y + 22*s)], fill=CREAM_SHADOW)

        # BACK LEG
        bl_x = int(88*s + paw_off[2]*s)
        draw.ellipse([bl_x - int(9*s), int(96*s + bob), bl_x + int(9*s), int(112*s + bob)], fill=CREAM_SHADOW)
        draw.ellipse([bl_x - int(6*s), int(104*s + bob), bl_x + int(6*s), int(112*s + bob)], fill=PINK_PAW)

        # EAR (far side, partially visible)
        ear_far_x = int(head_x + 10*s)
        draw.ellipse([ear_far_x - int(4*s), int(head_y - 4*s + ear_bob), ear_far_x + int(8*s), int(head_y + 22*s + ear_bob)], fill=CREAM_DARK)

        # HEAD (side profile)
        draw.ellipse([int(head_x - 26*s), int(head_y - 26*s), int(head_x + 26*s), int(head_y + 26*s)], fill=CREAM)
        draw.ellipse([int(head_x - 22*s), int(head_y - 22*s), int(head_x + 18*s), int(head_y + 18*s)], fill=CREAM_LIGHT)

        # EAR (near side)
        ear_x = int(head_x + 6*s)
        draw.ellipse([ear_x - int(6*s), int(head_y - 6*s + ear_bob), ear_x + int(10*s), int(head_y + 26*s + ear_bob)], fill=CREAM_SHADOW)
        draw.ellipse([ear_x - int(2*s), int(head_y + 4*s + ear_bob), ear_x + int(6*s), int(head_y + 18*s + ear_bob)], fill=PINK_EAR)

        # TOPKNOT
        draw.ellipse([int(head_x - 10*s), int(head_y - 34*s), int(head_x + 14*s), int(head_y - 14*s)], fill=CREAM)
        draw.ellipse([int(head_x - 6*s), int(head_y - 38*s), int(head_x + 6*s), int(head_y - 22*s)], fill=CREAM_LIGHT)

        # SNOUT (side profile)
        snout_x = int(head_x - 18*s)
        snout_y = int(head_y + 8*s)
        draw.ellipse([snout_x - int(12*s), snout_y - int(10*s), snout_x + int(14*s), snout_y + int(10*s)], fill=CREAM_LIGHT)

        # EYE (one visible)
        eye_x = int(head_x - 6*s)
        eye_y = int(head_y - 4*s)
        draw_shih_tzu_eye(draw, eye_x, eye_y, int(10*s), looking_dir=-1)

        # Eyebrow
        draw.ellipse([eye_x - int(10*s), eye_y - int(16*s), eye_x + int(6*s), eye_y - int(8*s)], fill=CREAM)

        # NOSE
        nose_x = int(snout_x - 4*s)
        draw.ellipse([nose_x - int(5*s), snout_y - int(4*s), nose_x + int(5*s), snout_y + int(5*s)], fill=NOSE_BLACK)
        draw.ellipse([nose_x - int(2*s), snout_y - int(3*s), nose_x + int(1*s), snout_y], fill=NOSE_HIGHLIGHT)

        # MOUTH
        mouth_y = int(snout_y + 10*s)
        if has_ball:
            ball_x = int(snout_x - 2*s)
            draw.ellipse([ball_x - int(10*s), mouth_y - int(6*s), ball_x + int(10*s), mouth_y + int(14*s)], fill=BALL_RED)
            draw.ellipse([ball_x - int(7*s), mouth_y - int(3*s), ball_x + int(1*s), mouth_y + int(3*s)], fill=BALL_LIGHT)
        elif mouth_open:
            draw.arc([snout_x - int(8*s), mouth_y - int(6*s), snout_x + int(4*s), mouth_y + int(4*s)], 0, 180, fill=OUTLINE, width=int(2*s))
            draw.ellipse([snout_x - int(4*s), mouth_y + int(1*s), snout_x + int(4*s), mouth_y + int(10*s)], fill=PINK_TONGUE)

        # FRONT LEG
        fl_x = int(52*s + paw_off[0]*s)
        draw.ellipse([fl_x - int(9*s), int(96*s + bob), fl_x + int(9*s), int(112*s + bob)], fill=CREAM)
        draw.ellipse([fl_x - int(6*s), int(104*s + bob), fl_x + int(6*s), int(112*s + bob)], fill=PINK_PAW)

    elif direction == "right":
        # Side view facing right (mirror of left)
        body_y = 76 * s + bob
        head_x = 80 * s
        head_y = 44 * s + bob

        # TAIL (left side)
        tail_x = int(24*s)
        tail_y = int(body_y - 12*s + tail_wag)
        draw.ellipse([tail_x - int(10*s), tail_y - int(10*s), tail_x + int(10*s), tail_y + int(8*s)], fill=CREAM)
        draw.ellipse([tail_x - int(8*s), tail_y - int(14*s), tail_x + int(6*s), tail_y - int(2*s)], fill=CREAM_LIGHT)

        # BODY
        draw.ellipse([int(28*s), int(body_y - 22*s), int(88*s), int(body_y + 22*s)], fill=CREAM_MID)
        draw.ellipse([int(32*s), int(body_y - 18*s), int(84*s), int(body_y + 16*s)], fill=CREAM)
        draw.ellipse([int(28*s), int(body_y + 4*s), int(88*s), int(body_y + 22*s)], fill=CREAM_SHADOW)

        # BACK LEG
        bl_x = int(40*s + paw_off[3]*s)
        draw.ellipse([bl_x - int(9*s), int(96*s + bob), bl_x + int(9*s), int(112*s + bob)], fill=CREAM_SHADOW)
        draw.ellipse([bl_x - int(6*s), int(104*s + bob), bl_x + int(6*s), int(112*s + bob)], fill=PINK_PAW)

        # EAR (far side)
        ear_far_x = int(head_x - 10*s)
        draw.ellipse([ear_far_x - int(8*s), int(head_y - 4*s + ear_bob), ear_far_x + int(4*s), int(head_y + 22*s + ear_bob)], fill=CREAM_DARK)

        # HEAD
        draw.ellipse([int(head_x - 26*s), int(head_y - 26*s), int(head_x + 26*s), int(head_y + 26*s)], fill=CREAM)
        draw.ellipse([int(head_x - 18*s), int(head_y - 22*s), int(head_x + 22*s), int(head_y + 18*s)], fill=CREAM_LIGHT)

        # EAR (near side)
        ear_x = int(head_x - 6*s)
        draw.ellipse([ear_x - int(10*s), int(head_y - 6*s + ear_bob), ear_x + int(6*s), int(head_y + 26*s + ear_bob)], fill=CREAM_SHADOW)
        draw.ellipse([ear_x - int(6*s), int(head_y + 4*s + ear_bob), ear_x + int(2*s), int(head_y + 18*s + ear_bob)], fill=PINK_EAR)

        # TOPKNOT
        draw.ellipse([int(head_x - 14*s), int(head_y - 34*s), int(head_x + 10*s), int(head_y - 14*s)], fill=CREAM)
        draw.ellipse([int(head_x - 6*s), int(head_y - 38*s), int(head_x + 6*s), int(head_y - 22*s)], fill=CREAM_LIGHT)

        # SNOUT
        snout_x = int(head_x + 18*s)
        snout_y = int(head_y + 8*s)
        draw.ellipse([snout_x - int(14*s), snout_y - int(10*s), snout_x + int(12*s), snout_y + int(10*s)], fill=CREAM_LIGHT)

        # EYE
        eye_x = int(head_x + 6*s)
        eye_y = int(head_y - 4*s)
        draw_shih_tzu_eye(draw, eye_x, eye_y, int(10*s), looking_dir=1)

        # Eyebrow
        draw.ellipse([eye_x - int(6*s), eye_y - int(16*s), eye_x + int(10*s), eye_y - int(8*s)], fill=CREAM)

        # NOSE
        nose_x = int(snout_x + 4*s)
        draw.ellipse([nose_x - int(5*s), snout_y - int(4*s), nose_x + int(5*s), snout_y + int(5*s)], fill=NOSE_BLACK)
        draw.ellipse([nose_x - int(1*s), snout_y - int(3*s), nose_x + int(2*s), snout_y], fill=NOSE_HIGHLIGHT)

        # MOUTH
        mouth_y = int(snout_y + 10*s)
        if has_ball:
            ball_x = int(snout_x + 2*s)
            draw.ellipse([ball_x - int(10*s), mouth_y - int(6*s), ball_x + int(10*s), mouth_y + int(14*s)], fill=BALL_RED)
            draw.ellipse([ball_x - int(1*s), mouth_y - int(3*s), ball_x + int(7*s), mouth_y + int(3*s)], fill=BALL_LIGHT)
        elif mouth_open:
            draw.arc([snout_x - int(4*s), mouth_y - int(6*s), snout_x + int(8*s), mouth_y + int(4*s)], 0, 180, fill=OUTLINE, width=int(2*s))
            draw.ellipse([snout_x - int(4*s), mouth_y + int(1*s), snout_x + int(4*s), mouth_y + int(10*s)], fill=PINK_TONGUE)

        # FRONT LEG
        fl_x = int(76*s + paw_off[1]*s)
        draw.ellipse([fl_x - int(9*s), int(96*s + bob), fl_x + int(9*s), int(112*s + bob)], fill=CREAM)
        draw.ellipse([fl_x - int(6*s), int(104*s + bob), fl_x + int(6*s), int(112*s + bob)], fill=PINK_PAW)

    return img


def create_charlie_spritesheet(frame_size=128):
    """Create a complete spritesheet with all animations"""
    # Animations layout:
    # Row 0: idle_down (4 frames)
    # Row 1: idle_up (4 frames)
    # Row 2: idle_left (4 frames)
    # Row 3: idle_right (4 frames)
    # Row 4: walk_down (4 frames)
    # Row 5: walk_up (4 frames)
    # Row 6: walk_left (4 frames)
    # Row 7: walk_right (4 frames)
    # Row 8: idle_down_ball (4 frames)
    # Row 9: walk_down_ball (4 frames)
    # Row 10: walk_left_ball (4 frames)
    # Row 11: walk_right_ball (4 frames)

    rows = 12
    cols = 4

    sheet = Image.new('RGBA', (frame_size * cols, frame_size * rows), (0, 0, 0, 0))

    animations = [
        ("down", False, False),   # Row 0
        ("up", False, False),     # Row 1
        ("left", False, False),   # Row 2
        ("right", False, False),  # Row 3
        ("down", True, False),    # Row 4
        ("up", True, False),      # Row 5
        ("left", True, False),    # Row 6
        ("right", True, False),   # Row 7
        ("down", False, True),    # Row 8
        ("down", True, True),     # Row 9
        ("left", True, True),     # Row 10
        ("right", True, True),    # Row 11
    ]

    for row, (direction, is_walk, has_ball) in enumerate(animations):
        for col in range(4):
            if not is_walk:
                frame = 0
                mouth_open = col < 2  # Panting animation for idle
            else:
                frame = col
                mouth_open = True

            img = draw_charlie_frame(
                size=frame_size,
                direction=direction,
                frame=frame if is_walk else 0,
                has_ball=has_ball,
                mouth_open=mouth_open
            )
            sheet.paste(img, (col * frame_size, row * frame_size))

    return sheet


def draw_charlie_in_box(size=128):
    """Draw Charlie peeking adorably out of a cardboard box"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size / 128

    # Box colors
    BOX_MAIN = (180, 150, 110)
    BOX_DARK = (150, 120, 85)
    BOX_LIGHT = (200, 175, 140)

    # Box back
    draw.rectangle([int(16*s), int(64*s), int(112*s), int(120*s)], fill=BOX_DARK)

    # Box front
    draw.rectangle([int(16*s), int(76*s), int(112*s), int(120*s)], fill=BOX_MAIN)

    # Box sides
    draw.rectangle([int(16*s), int(76*s), int(26*s), int(120*s)], fill=BOX_DARK)
    draw.rectangle([int(102*s), int(76*s), int(112*s), int(120*s)], fill=BOX_DARK)

    # Box flaps
    draw.polygon([
        (int(16*s), int(76*s)), (int(28*s), int(60*s)),
        (int(48*s), int(68*s)), (int(36*s), int(84*s))
    ], fill=BOX_LIGHT)
    draw.polygon([
        (int(112*s), int(76*s)), (int(100*s), int(60*s)),
        (int(80*s), int(68*s)), (int(92*s), int(84*s))
    ], fill=BOX_LIGHT)

    head_y = 40 * s

    # EARS (behind head)
    # Left ear
    draw.ellipse([int(20*s), int(head_y - 8*s), int(44*s), int(head_y + 48*s)], fill=CREAM_SHADOW)
    draw.ellipse([int(24*s), int(head_y - 4*s), int(40*s), int(head_y + 44*s)], fill=CREAM_MID)
    draw.ellipse([int(28*s), int(head_y + 8*s), int(36*s), int(head_y + 32*s)], fill=PINK_EAR)

    # Right ear
    draw.ellipse([int(84*s), int(head_y - 8*s), int(108*s), int(head_y + 48*s)], fill=CREAM_SHADOW)
    draw.ellipse([int(88*s), int(head_y - 4*s), int(104*s), int(head_y + 44*s)], fill=CREAM_MID)
    draw.ellipse([int(92*s), int(head_y + 8*s), int(100*s), int(head_y + 32*s)], fill=PINK_EAR)

    # HEAD
    draw.ellipse([int(32*s), int(head_y - 24*s), int(96*s), int(head_y + 36*s)], fill=CREAM)
    draw.ellipse([int(36*s), int(head_y - 20*s), int(92*s), int(head_y + 28*s)], fill=CREAM_LIGHT)

    # TOPKNOT
    draw.ellipse([int(44*s), int(head_y - 36*s), int(84*s), int(head_y - 8*s)], fill=CREAM)
    draw.ellipse([int(50*s), int(head_y - 44*s), int(78*s), int(head_y - 16*s)], fill=CREAM_LIGHT)
    draw.ellipse([int(52*s), int(head_y - 48*s), int(66*s), int(head_y - 32*s)], fill=CREAM)
    draw.ellipse([int(62*s), int(head_y - 50*s), int(76*s), int(head_y - 34*s)], fill=CREAM)

    # CHEEK FLUFF
    draw.ellipse([int(24*s), int(head_y + 4*s), int(48*s), int(head_y + 32*s)], fill=CREAM)
    draw.ellipse([int(80*s), int(head_y + 4*s), int(104*s), int(head_y + 32*s)], fill=CREAM)

    # SNOUT
    draw.ellipse([int(48*s), int(head_y + 8*s), int(80*s), int(head_y + 32*s)], fill=CREAM_LIGHT)

    # EYES
    eye_y = int(head_y + 4*s)
    draw_shih_tzu_eye(draw, int(48*s), eye_y, int(10*s))
    draw_shih_tzu_eye(draw, int(80*s), eye_y, int(10*s))

    # EYEBROWS
    draw.ellipse([int(40*s), eye_y - int(14*s), int(56*s), eye_y - int(6*s)], fill=CREAM)
    draw.ellipse([int(72*s), eye_y - int(14*s), int(88*s), eye_y - int(6*s)], fill=CREAM)

    # BLUSH
    blush_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    blush_draw = ImageDraw.Draw(blush_img)
    blush_draw.ellipse([int(32*s), int(head_y + 16*s), int(48*s), int(head_y + 26*s)], fill=PINK_BLUSH)
    blush_draw.ellipse([int(80*s), int(head_y + 16*s), int(96*s), int(head_y + 26*s)], fill=PINK_BLUSH)
    img = Image.alpha_composite(img, blush_img)
    draw = ImageDraw.Draw(img)

    # NOSE
    draw_shih_tzu_nose(draw, int(64*s), int(head_y + 18*s), int(7*s), int(5*s))

    # MOUTH with tongue
    mouth_y = int(head_y + 26*s)
    draw.arc([int(54*s), mouth_y - int(6*s), int(64*s), mouth_y + int(4*s)], 0, 180, fill=OUTLINE, width=int(2*s))
    draw.arc([int(64*s), mouth_y - int(6*s), int(74*s), mouth_y + int(4*s)], 0, 180, fill=OUTLINE, width=int(2*s))
    draw.ellipse([int(58*s), mouth_y + int(2*s), int(70*s), mouth_y + int(14*s)], fill=PINK_TONGUE)
    draw.ellipse([int(60*s), mouth_y + int(2*s), int(68*s), mouth_y + int(6*s)], fill=PINK_TONGUE_LIGHT)

    # PAWS on box edge
    paw_y = int(72*s)
    draw.ellipse([int(40*s), paw_y - int(8*s), int(56*s), paw_y + int(10*s)], fill=CREAM)
    draw.ellipse([int(72*s), paw_y - int(8*s), int(88*s), paw_y + int(10*s)], fill=CREAM)
    draw.ellipse([int(44*s), paw_y + int(2*s), int(52*s), paw_y + int(10*s)], fill=PINK_PAW)
    draw.ellipse([int(76*s), paw_y + int(2*s), int(84*s), paw_y + int(10*s)], fill=PINK_PAW)

    return img


# Generate assets
print("Generating detailed Charlie spritesheet (128x128 frames)...")

# Main spritesheet
FRAME_SIZE = 128
spritesheet = create_charlie_spritesheet(FRAME_SIZE)
spritesheet.save("assets/sprites/characters/charlie_spritesheet.png")
print(f"  Created charlie_spritesheet.png ({FRAME_SIZE*4}x{FRAME_SIZE*12} pixels, {FRAME_SIZE}x{FRAME_SIZE} frames)")

# Static sprites
static = draw_charlie_frame(size=128, direction="down", frame=0, has_ball=False, mouth_open=True)
static.save("assets/sprites/characters/charlie.png")
print("  Created charlie.png (128x128)")

static_large = draw_charlie_frame(size=96, direction="down", frame=0, has_ball=False, mouth_open=True)
static_large.save("assets/sprites/characters/charlie_large.png")
print("  Created charlie_large.png (96x96)")

# With ball
charlie_ball = draw_charlie_frame(size=128, direction="down", frame=0, has_ball=True)
charlie_ball.save("assets/sprites/characters/charlie_with_ball.png")
print("  Created charlie_with_ball.png (128x128)")

# In box
charlie_box = draw_charlie_in_box(128)
charlie_box.save("assets/sprites/characters/charlie_in_box.png")
print("  Created charlie_in_box.png (128x128)")

charlie_box_large = draw_charlie_in_box(160)
charlie_box_large.save("assets/sprites/characters/charlie_in_box_large.png")
print("  Created charlie_in_box_large.png (160x160)")

print("\nDone! Frame size:", FRAME_SIZE, "x", FRAME_SIZE)
print("Spritesheet layout (12 rows x 4 columns):")
print("  Row 0: idle_down")
print("  Row 1: idle_up")
print("  Row 2: idle_left")
print("  Row 3: idle_right")
print("  Row 4: walk_down")
print("  Row 5: walk_up")
print("  Row 6: walk_left")
print("  Row 7: walk_right")
print("  Row 8: idle_down_ball")
print("  Row 9: walk_down_ball")
print("  Row 10: walk_left_ball")
print("  Row 11: walk_right_ball")
