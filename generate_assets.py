#!/usr/bin/env python3
"""
Generate pixel art assets for Charlie's Island Adventure
"""

from PIL import Image, ImageDraw
import os
import random

# Ensure assets directories exist
os.makedirs("assets/sprites/characters", exist_ok=True)
os.makedirs("assets/sprites/environment", exist_ok=True)
os.makedirs("assets/sprites/effects", exist_ok=True)
os.makedirs("assets/sprites/ui", exist_ok=True)

# Color palettes
COLORS = {
    # Charlie (cream Shih Tzu puppy)
    'charlie_body': (242, 235, 224),
    'charlie_body_shadow': (220, 210, 195),
    'charlie_nose': (40, 30, 30),
    'charlie_eye': (50, 40, 35),
    'charlie_tongue': (255, 150, 150),

    # Player (blonde girl)
    'player_skin': (255, 220, 190),
    'player_skin_shadow': (235, 190, 160),
    'player_hair': (255, 215, 100),
    'player_hair_shadow': (230, 180, 70),
    'player_eye': (80, 130, 180),
    'player_dress': (100, 180, 230),
    'player_dress_shadow': (70, 140, 190),

    # Environment - Storm
    'storm_sky_dark': (30, 35, 50),
    'storm_sky_mid': (45, 55, 75),
    'storm_sky_light': (60, 75, 100),
    'storm_cloud_dark': (40, 45, 55),
    'storm_cloud_mid': (55, 60, 75),
    'storm_cloud_light': (75, 85, 100),
    'lightning': (255, 255, 220),
    'lightning_glow': (200, 200, 255),

    # Ocean - Storm
    'ocean_storm_dark': (25, 50, 80),
    'ocean_storm_mid': (35, 70, 110),
    'ocean_storm_light': (50, 90, 130),
    'ocean_storm_foam': (180, 200, 220),
    'ocean_storm_spray': (220, 235, 245),

    # Ocean - Calm (beach)
    'ocean_deep': (50, 100, 150),
    'ocean_mid': (70, 140, 190),
    'ocean_shallow': (100, 180, 220),
    'ocean_foam': (240, 250, 255),

    # Beach
    'sand_light': (240, 220, 175),
    'sand_mid': (225, 200, 155),
    'sand_dark': (200, 175, 130),
    'sand_wet': (180, 160, 120),
    'shell_pink': (255, 220, 210),
    'shell_white': (250, 245, 240),
    'driftwood': (140, 120, 100),
    'driftwood_light': (170, 150, 130),

    # Raft
    'wood_dark': (90, 65, 45),
    'wood_mid': (120, 90, 60),
    'wood_light': (150, 120, 85),
    'rope': (180, 160, 120),

    # Box
    'cardboard': (180, 150, 110),
    'cardboard_dark': (150, 120, 85),
    'cardboard_light': (200, 175, 140),

    # Rain
    'rain_light': (180, 200, 230),
    'rain_dark': (140, 160, 200),

    # Transparent
    'transparent': (0, 0, 0, 0),
}


def create_charlie_sprite(size=32):
    """Create Charlie the baby Shih Tzu sprite - cute and fluffy!"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor
    s = size // 32

    # Colors for cuter appearance
    cream = COLORS['charlie_body']
    cream_shadow = COLORS['charlie_body_shadow']
    cream_highlight = (255, 250, 245)
    pink_inner_ear = (255, 210, 200)
    nose_black = COLORS['charlie_nose']
    eye_black = (30, 25, 25)
    eye_shine = (255, 255, 255)
    tongue_pink = COLORS['charlie_tongue']
    outline = (180, 170, 160)

    # Fluffy body (solid base, then add texture)
    draw.ellipse([9*s, 16*s, 23*s, 28*s], fill=cream)
    draw.ellipse([10*s, 17*s, 22*s, 26*s], fill=cream_highlight)
    draw.ellipse([9*s, 20*s, 23*s, 28*s], fill=cream_shadow)

    # Add fluffy texture to body edges
    for i in range(8):
        angle = i * 45
        import math
        bx = int(16*s + 7*s * math.cos(math.radians(angle + 180)))
        by = int(22*s + 5*s * math.sin(math.radians(angle + 180)))
        if 0 <= bx < size and 0 <= by < size:
            draw.ellipse([bx-1*s, by-1*s, bx+2*s, by+2*s], fill=cream)

    # Floppy ears (behind head) - characteristic Shih Tzu floppy ears
    # Left ear
    draw.ellipse([2*s, 8*s, 10*s, 20*s], fill=cream_shadow)
    draw.ellipse([3*s, 9*s, 9*s, 18*s], fill=cream)
    draw.ellipse([4*s, 10*s, 8*s, 16*s], fill=pink_inner_ear)
    # Ear fluff
    for fy in range(12*s, 19*s, 2*s):
        draw.ellipse([2*s, fy, 5*s, fy+3*s], fill=cream)

    # Right ear
    draw.ellipse([22*s, 8*s, 30*s, 20*s], fill=cream_shadow)
    draw.ellipse([23*s, 9*s, 29*s, 18*s], fill=cream)
    draw.ellipse([24*s, 10*s, 28*s, 16*s], fill=pink_inner_ear)
    # Ear fluff
    for fy in range(12*s, 19*s, 2*s):
        draw.ellipse([27*s, fy, 30*s, fy+3*s], fill=cream)

    # Big fluffy head (Shih Tzus have round fluffy faces)
    draw.ellipse([6*s, 4*s, 26*s, 20*s], fill=cream)
    draw.ellipse([7*s, 5*s, 25*s, 18*s], fill=cream_highlight)

    # Forehead fluff (topknot - signature Shih Tzu feature)
    draw.ellipse([10*s, 2*s, 22*s, 10*s], fill=cream)
    draw.ellipse([12*s, 1*s, 20*s, 7*s], fill=cream_highlight)
    # Little fluff tufts on top
    draw.ellipse([13*s, 0*s, 16*s, 4*s], fill=cream)
    draw.ellipse([16*s, 0*s, 19*s, 4*s], fill=cream)

    # Cheek fluff
    draw.ellipse([4*s, 10*s, 12*s, 18*s], fill=cream)
    draw.ellipse([20*s, 10*s, 28*s, 18*s], fill=cream)

    # Snout area (lighter, slightly protruding)
    draw.ellipse([11*s, 12*s, 21*s, 19*s], fill=cream_highlight)

    # BIG cute eyes (larger = cuter, Shih Tzus have big round eyes)
    # Left eye
    draw.ellipse([8*s, 8*s, 14*s, 14*s], fill=eye_black)
    draw.ellipse([9*s, 9*s, 13*s, 13*s], fill=(50, 45, 45))  # Slight gradient
    # Eye shine (multiple highlights for sparkle)
    draw.ellipse([10*s, 9*s, 12*s, 11*s], fill=eye_shine)
    draw.point((12*s, 12*s), fill=(200, 200, 200))  # Small secondary highlight

    # Right eye
    draw.ellipse([18*s, 8*s, 24*s, 14*s], fill=eye_black)
    draw.ellipse([19*s, 9*s, 23*s, 13*s], fill=(50, 45, 45))
    # Eye shine
    draw.ellipse([20*s, 9*s, 22*s, 11*s], fill=eye_shine)
    draw.point((22*s, 12*s), fill=(200, 200, 200))

    # Cute button nose (heart-shaped for extra cuteness)
    draw.ellipse([14*s, 13*s, 18*s, 16*s], fill=nose_black)
    # Nose highlight
    draw.ellipse([15*s, 13*s, 16*s, 14*s], fill=(80, 75, 75))

    # Happy little mouth with tongue
    draw.arc([13*s, 15*s, 16*s, 18*s], 0, 180, fill=outline, width=s)
    draw.arc([16*s, 15*s, 19*s, 18*s], 0, 180, fill=outline, width=s)
    # Little pink tongue poking out
    draw.ellipse([15*s, 17*s, 17*s, 20*s], fill=tongue_pink)
    draw.ellipse([15*s, 17*s, 17*s, 18*s], fill=(255, 180, 180))

    # Tiny paws peeking out
    draw.ellipse([10*s, 25*s, 14*s, 29*s], fill=cream)
    draw.ellipse([18*s, 25*s, 22*s, 29*s], fill=cream)
    # Paw pads (tiny pink dots)
    draw.ellipse([11*s, 27*s, 13*s, 29*s], fill=pink_inner_ear)
    draw.ellipse([19*s, 27*s, 21*s, 29*s], fill=pink_inner_ear)

    # Fluffy tail (curled up - Shih Tzus have curled tails)
    draw.ellipse([23*s, 18*s, 29*s, 24*s], fill=cream)
    draw.ellipse([24*s, 17*s, 28*s, 21*s], fill=cream_highlight)

    return img


def create_charlie_in_box(size=48):
    """Create Charlie peeking out of cardboard box - adorable version!"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size // 48

    # Colors
    cream = COLORS['charlie_body']
    cream_shadow = COLORS['charlie_body_shadow']
    cream_highlight = (255, 250, 245)
    pink_inner_ear = (255, 210, 200)
    nose_black = COLORS['charlie_nose']
    eye_black = (30, 25, 25)
    eye_shine = (255, 255, 255)
    tongue_pink = COLORS['charlie_tongue']

    # Box back
    draw.rectangle([4*s, 24*s, 44*s, 46*s], fill=COLORS['cardboard_dark'])

    # Box front
    draw.rectangle([4*s, 30*s, 44*s, 46*s], fill=COLORS['cardboard'])

    # Box sides shading
    draw.rectangle([4*s, 30*s, 8*s, 46*s], fill=COLORS['cardboard_dark'])
    draw.rectangle([40*s, 30*s, 44*s, 46*s], fill=COLORS['cardboard_dark'])

    # Box flap left
    points = [(4*s, 30*s), (8*s, 24*s), (16*s, 26*s), (12*s, 32*s)]
    draw.polygon(points, fill=COLORS['cardboard_light'])

    # Box flap right
    points = [(44*s, 30*s), (40*s, 24*s), (32*s, 26*s), (36*s, 32*s)]
    draw.polygon(points, fill=COLORS['cardboard_light'])

    # Floppy ears (behind head)
    # Left ear - drooping down
    draw.ellipse([6*s, 12*s, 16*s, 28*s], fill=cream_shadow)
    draw.ellipse([7*s, 13*s, 15*s, 26*s], fill=cream)
    draw.ellipse([8*s, 14*s, 14*s, 22*s], fill=pink_inner_ear)

    # Right ear
    draw.ellipse([32*s, 12*s, 42*s, 28*s], fill=cream_shadow)
    draw.ellipse([33*s, 13*s, 41*s, 26*s], fill=cream)
    draw.ellipse([34*s, 14*s, 40*s, 22*s], fill=pink_inner_ear)

    # Big fluffy head
    draw.ellipse([12*s, 6*s, 36*s, 28*s], fill=cream)
    draw.ellipse([14*s, 8*s, 34*s, 26*s], fill=cream_highlight)

    # Forehead fluff (topknot)
    draw.ellipse([16*s, 2*s, 32*s, 14*s], fill=cream)
    draw.ellipse([18*s, 1*s, 30*s, 10*s], fill=cream_highlight)
    # Tufts
    draw.ellipse([19*s, 0*s, 24*s, 6*s], fill=cream)
    draw.ellipse([24*s, 0*s, 29*s, 6*s], fill=cream)

    # Cheek fluff
    draw.ellipse([10*s, 14*s, 20*s, 24*s], fill=cream)
    draw.ellipse([28*s, 14*s, 38*s, 24*s], fill=cream)

    # Snout area
    draw.ellipse([17*s, 16*s, 31*s, 26*s], fill=cream_highlight)

    # BIG cute eyes
    # Left eye
    draw.ellipse([14*s, 12*s, 22*s, 20*s], fill=eye_black)
    draw.ellipse([15*s, 13*s, 21*s, 19*s], fill=(50, 45, 45))
    draw.ellipse([16*s, 13*s, 19*s, 16*s], fill=eye_shine)
    draw.point((19*s, 17*s), fill=(200, 200, 200))

    # Right eye
    draw.ellipse([26*s, 12*s, 34*s, 20*s], fill=eye_black)
    draw.ellipse([27*s, 13*s, 33*s, 19*s], fill=(50, 45, 45))
    draw.ellipse([28*s, 13*s, 31*s, 16*s], fill=eye_shine)
    draw.point((31*s, 17*s), fill=(200, 200, 200))

    # Cute button nose
    draw.ellipse([21*s, 18*s, 27*s, 23*s], fill=nose_black)
    draw.ellipse([22*s, 18*s, 24*s, 20*s], fill=(80, 75, 75))

    # Happy mouth with tongue
    draw.arc([19*s, 21*s, 23*s, 26*s], 0, 180, fill=(180, 170, 160), width=s)
    draw.arc([25*s, 21*s, 29*s, 26*s], 0, 180, fill=(180, 170, 160), width=s)
    # Tongue
    draw.ellipse([22*s, 24*s, 26*s, 29*s], fill=tongue_pink)
    draw.ellipse([23*s, 24*s, 25*s, 26*s], fill=(255, 180, 180))

    # Cute paws resting on box edge
    draw.ellipse([14*s, 28*s, 22*s, 36*s], fill=cream)
    draw.ellipse([26*s, 28*s, 34*s, 36*s], fill=cream)
    # Paw pads
    draw.ellipse([16*s, 32*s, 20*s, 36*s], fill=pink_inner_ear)
    draw.ellipse([28*s, 32*s, 32*s, 36*s], fill=pink_inner_ear)

    return img


def create_raft(size=64):
    """Create wooden raft with logs and rope"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size // 64

    # Main logs (horizontal)
    for i, y_offset in enumerate([20, 28, 36, 44, 52]):
        y = y_offset * s
        shade = COLORS['wood_mid'] if i % 2 == 0 else COLORS['wood_dark']
        draw.rectangle([4*s, y, 60*s, y + 6*s], fill=shade)
        # Wood grain
        for gx in range(8*s, 58*s, 8*s):
            draw.line([(gx, y+1*s), (gx+4*s, y+5*s)], fill=COLORS['wood_light'], width=s)

    # Cross beams
    draw.rectangle([12*s, 18*s, 18*s, 56*s], fill=COLORS['wood_light'])
    draw.rectangle([46*s, 18*s, 52*s, 56*s], fill=COLORS['wood_light'])

    # Rope bindings
    for rx in [14*s, 48*s]:
        for ry in [22*s, 34*s, 46*s]:
            draw.ellipse([rx-2*s, ry, rx+4*s, ry+4*s], fill=COLORS['rope'])
            draw.arc([rx-2*s, ry, rx+4*s, ry+4*s], 0, 180, fill=COLORS['driftwood'], width=s)

    return img


def create_storm_sky(width=426, height=160):
    """Create stormy sky with dark clouds"""
    img = Image.new('RGBA', (width, height), COLORS['storm_sky_dark'])
    draw = ImageDraw.Draw(img)

    # Gradient sky
    for y in range(height):
        ratio = y / height
        r = int(COLORS['storm_sky_dark'][0] * (1-ratio) + COLORS['storm_sky_mid'][0] * ratio)
        g = int(COLORS['storm_sky_dark'][1] * (1-ratio) + COLORS['storm_sky_mid'][1] * ratio)
        b = int(COLORS['storm_sky_dark'][2] * (1-ratio) + COLORS['storm_sky_mid'][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Storm clouds - multiple layers
    random.seed(42)  # Reproducible
    for _ in range(15):
        cx = random.randint(0, width)
        cy = random.randint(0, height // 2)
        for i in range(5):
            rx = cx + random.randint(-40, 40)
            ry = cy + random.randint(-15, 15)
            rw = random.randint(30, 80)
            rh = random.randint(20, 40)
            color = random.choice([COLORS['storm_cloud_dark'], COLORS['storm_cloud_mid'], COLORS['storm_cloud_light']])
            draw.ellipse([rx, ry, rx+rw, ry+rh], fill=color)

    return img


def create_storm_ocean(width=426, height=120):
    """Create stormy ocean with waves"""
    img = Image.new('RGBA', (width, height), COLORS['ocean_storm_dark'])
    draw = ImageDraw.Draw(img)

    # Base gradient
    for y in range(height):
        ratio = y / height
        r = int(COLORS['ocean_storm_dark'][0] * (1-ratio*0.5) + COLORS['ocean_storm_mid'][0] * ratio*0.5)
        g = int(COLORS['ocean_storm_dark'][1] * (1-ratio*0.5) + COLORS['ocean_storm_mid'][1] * ratio*0.5)
        b = int(COLORS['ocean_storm_dark'][2] * (1-ratio*0.5) + COLORS['ocean_storm_mid'][2] * ratio*0.5)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Waves
    random.seed(123)
    for wave_y in range(0, height, 12):
        wave_height = random.randint(4, 10)
        for x in range(0, width, 2):
            import math
            offset = int(math.sin(x * 0.05 + wave_y * 0.1) * wave_height)
            y = wave_y + offset
            if 0 <= y < height:
                draw.line([(x, y), (x+2, y)], fill=COLORS['ocean_storm_light'], width=2)
                if y > 0:
                    draw.point((x, y-1), fill=COLORS['ocean_storm_foam'])

    return img


def create_lightning(width=64, height=128):
    """Create lightning bolt sprite"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Main bolt
    points = [
        (32, 0), (28, 30), (38, 35), (25, 70), (35, 75), (20, 128)
    ]

    # Glow
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=COLORS['lightning_glow'], width=8)

    # Core
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=COLORS['lightning'], width=3)

    # Branch
    branch_points = [(28, 30), (45, 50), (50, 80)]
    for i in range(len(branch_points) - 1):
        draw.line([branch_points[i], branch_points[i+1]], fill=COLORS['lightning_glow'], width=4)
        draw.line([branch_points[i], branch_points[i+1]], fill=COLORS['lightning'], width=2)

    return img


def create_rain_particle(size=16):
    """Create rain drop/streak sprite"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Diagonal rain streak
    draw.line([(4, 0), (12, 16)], fill=(*COLORS['rain_light'], 200), width=2)
    draw.line([(5, 0), (13, 16)], fill=(*COLORS['rain_dark'], 150), width=1)

    return img


def create_wind_line(width=64, height=8):
    """Create wind effect line"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Curved wind line with fade
    for x in range(width):
        alpha = int(255 * (1 - abs(x - width//2) / (width//2)))
        y = height // 2 + int(2 * ((x / width) - 0.5))
        if 0 <= y < height:
            draw.point((x, y), fill=(*COLORS['ocean_storm_foam'], alpha))
            draw.point((x, y+1), fill=(*COLORS['ocean_storm_foam'], alpha//2))

    return img


def create_beach_sand(width=426, height=120):
    """Create sandy beach texture"""
    img = Image.new('RGBA', (width, height), COLORS['sand_mid'])
    draw = ImageDraw.Draw(img)

    # Base gradient (wet near water)
    for y in range(height):
        ratio = y / height
        if ratio < 0.3:
            # Wet sand near top (water line)
            r = int(COLORS['sand_wet'][0] + (COLORS['sand_mid'][0] - COLORS['sand_wet'][0]) * (ratio / 0.3))
            g = int(COLORS['sand_wet'][1] + (COLORS['sand_mid'][1] - COLORS['sand_wet'][1]) * (ratio / 0.3))
            b = int(COLORS['sand_wet'][2] + (COLORS['sand_mid'][2] - COLORS['sand_wet'][2]) * (ratio / 0.3))
        else:
            r, g, b = COLORS['sand_mid']
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Sand texture - random dots
    random.seed(456)
    for _ in range(800):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        color = random.choice([COLORS['sand_light'], COLORS['sand_dark'], COLORS['sand_mid']])
        size = random.randint(1, 3)
        draw.ellipse([x, y, x+size, y+size], fill=color)

    # Scattered shells
    for _ in range(12):
        x = random.randint(10, width-20)
        y = random.randint(30, height-20)
        color = random.choice([COLORS['shell_pink'], COLORS['shell_white']])
        # Simple shell shape
        draw.ellipse([x, y, x+6, y+4], fill=color)
        draw.arc([x, y, x+6, y+4], 0, 180, fill=COLORS['sand_dark'])

    # Small pebbles
    for _ in range(20):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        draw.ellipse([x, y, x+2, y+2], fill=COLORS['driftwood'])

    return img


def create_beach_ocean(width=426, height=80):
    """Create calm beach ocean with waves"""
    img = Image.new('RGBA', (width, height), COLORS['ocean_deep'])
    draw = ImageDraw.Draw(img)

    # Gradient from deep to shallow
    for y in range(height):
        ratio = y / height
        if ratio < 0.5:
            r = int(COLORS['ocean_deep'][0] + (COLORS['ocean_mid'][0] - COLORS['ocean_deep'][0]) * (ratio * 2))
            g = int(COLORS['ocean_deep'][1] + (COLORS['ocean_mid'][1] - COLORS['ocean_deep'][1]) * (ratio * 2))
            b = int(COLORS['ocean_deep'][2] + (COLORS['ocean_mid'][2] - COLORS['ocean_deep'][2]) * (ratio * 2))
        else:
            r = int(COLORS['ocean_mid'][0] + (COLORS['ocean_shallow'][0] - COLORS['ocean_mid'][0]) * ((ratio - 0.5) * 2))
            g = int(COLORS['ocean_mid'][1] + (COLORS['ocean_shallow'][1] - COLORS['ocean_mid'][1]) * ((ratio - 0.5) * 2))
            b = int(COLORS['ocean_mid'][2] + (COLORS['ocean_shallow'][2] - COLORS['ocean_mid'][2]) * ((ratio - 0.5) * 2))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Gentle waves
    import math
    for wave_y in range(10, height, 15):
        for x in range(0, width):
            offset = int(math.sin(x * 0.03) * 3)
            y = wave_y + offset
            if 0 <= y < height:
                draw.point((x, y), fill=(*COLORS['ocean_shallow'], 180))

    # Foam at shore (bottom)
    for x in range(width):
        import math
        foam_height = 8 + int(math.sin(x * 0.05) * 4)
        for y in range(height - foam_height, height):
            alpha = int(255 * (y - (height - foam_height)) / foam_height)
            draw.point((x, y), fill=(*COLORS['ocean_foam'], alpha))

    return img


def create_player_sprite(size=32):
    """Create player character (blonde girl) sprite"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size // 32

    # Hair back (behind head)
    draw.ellipse([8*s, 2*s, 24*s, 14*s], fill=COLORS['player_hair'])

    # Body/dress
    draw.rectangle([10*s, 14*s, 22*s, 26*s], fill=COLORS['player_dress'])
    draw.rectangle([10*s, 20*s, 22*s, 26*s], fill=COLORS['player_dress_shadow'])

    # Head
    draw.ellipse([10*s, 4*s, 22*s, 16*s], fill=COLORS['player_skin'])

    # Hair front
    draw.arc([8*s, 2*s, 24*s, 14*s], 180, 360, fill=COLORS['player_hair'], width=3*s)
    # Side hair
    draw.ellipse([6*s, 6*s, 10*s, 18*s], fill=COLORS['player_hair'])
    draw.ellipse([22*s, 6*s, 26*s, 18*s], fill=COLORS['player_hair'])

    # Eyes
    draw.ellipse([12*s, 8*s, 14*s, 11*s], fill=COLORS['player_eye'])
    draw.ellipse([18*s, 8*s, 20*s, 11*s], fill=COLORS['player_eye'])
    # Eye highlights
    draw.point((12*s, 8*s), fill=(255, 255, 255))
    draw.point((18*s, 8*s), fill=(255, 255, 255))

    # Mouth (small smile)
    draw.arc([14*s, 10*s, 18*s, 14*s], 0, 180, fill=COLORS['player_skin_shadow'], width=s)

    # Arms
    draw.rectangle([6*s, 14*s, 10*s, 22*s], fill=COLORS['player_skin'])
    draw.rectangle([22*s, 14*s, 26*s, 22*s], fill=COLORS['player_skin'])

    # Legs
    draw.rectangle([12*s, 26*s, 15*s, 30*s], fill=COLORS['player_skin'])
    draw.rectangle([17*s, 26*s, 20*s, 30*s], fill=COLORS['player_skin'])

    return img


def create_driftwood(width=48, height=16):
    """Create driftwood piece"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Main log
    draw.ellipse([0, 4, width, height-2], fill=COLORS['driftwood'])
    draw.ellipse([2, 5, width-2, height-4], fill=COLORS['driftwood_light'])

    # Wood grain
    for i in range(5, width-5, 8):
        draw.line([(i, 6), (i+3, height-5)], fill=COLORS['driftwood'], width=1)

    # Branch stub
    draw.ellipse([width-12, 0, width-4, 6], fill=COLORS['driftwood'])

    return img


def create_shell(size=12):
    """Create seashell sprite"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Shell body
    draw.ellipse([1, 2, size-1, size-1], fill=COLORS['shell_pink'])
    draw.ellipse([2, 3, size-2, size-2], fill=COLORS['shell_white'])

    # Shell ridges
    for i in range(3, size//2, 2):
        if size - i > i:  # Ensure x1 > x0
            draw.arc([i, 3, size-i, size-2], 0, 180, fill=COLORS['shell_pink'])

    return img


def create_box_closed(size=40):
    """Create closed cardboard box"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size // 40

    # Box body
    draw.rectangle([4*s, 12*s, 36*s, 36*s], fill=COLORS['cardboard'])

    # Side shading
    draw.rectangle([4*s, 12*s, 8*s, 36*s], fill=COLORS['cardboard_dark'])

    # Top flaps (closed)
    draw.polygon([(4*s, 12*s), (20*s, 6*s), (36*s, 12*s), (20*s, 16*s)], fill=COLORS['cardboard_light'])
    draw.line([(4*s, 12*s), (20*s, 6*s), (36*s, 12*s)], fill=COLORS['cardboard_dark'], width=s)

    # Question mark
    draw.text((15*s, 20*s), "?", fill=COLORS['cardboard_dark'])

    return img


def create_spray_particle(size=8):
    """Create ocean spray particle"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse([1, 1, size-1, size-1], fill=(*COLORS['ocean_storm_spray'], 200))
    draw.ellipse([2, 2, size-2, size-2], fill=(*COLORS['ocean_storm_foam'], 150))

    return img


# Generate all assets
print("Generating pixel art assets...")

# Characters
print("  Creating Charlie sprite...")
create_charlie_sprite(32).save("assets/sprites/characters/charlie.png")
create_charlie_sprite(48).save("assets/sprites/characters/charlie_large.png")

print("  Creating Charlie in box...")
create_charlie_in_box(48).save("assets/sprites/characters/charlie_in_box.png")
create_charlie_in_box(64).save("assets/sprites/characters/charlie_in_box_large.png")

print("  Creating player sprite...")
create_player_sprite(32).save("assets/sprites/characters/player.png")
create_player_sprite(48).save("assets/sprites/characters/player_large.png")

# Environment - Storm
print("  Creating storm sky...")
create_storm_sky(426, 160).save("assets/sprites/environment/storm_sky.png")

print("  Creating storm ocean...")
create_storm_ocean(426, 120).save("assets/sprites/environment/storm_ocean.png")

# Environment - Beach
print("  Creating beach sand...")
create_beach_sand(426, 120).save("assets/sprites/environment/beach_sand.png")

print("  Creating beach ocean...")
create_beach_ocean(426, 80).save("assets/sprites/environment/beach_ocean.png")

# Props
print("  Creating raft...")
create_raft(64).save("assets/sprites/environment/raft.png")
create_raft(96).save("assets/sprites/environment/raft_large.png")

print("  Creating driftwood...")
create_driftwood(48, 16).save("assets/sprites/environment/driftwood.png")

print("  Creating shell...")
create_shell(12).save("assets/sprites/environment/shell.png")

print("  Creating closed box...")
create_box_closed(40).save("assets/sprites/environment/box_closed.png")

# Effects
print("  Creating lightning...")
create_lightning(64, 128).save("assets/sprites/effects/lightning.png")

print("  Creating rain particle...")
create_rain_particle(16).save("assets/sprites/effects/rain.png")

print("  Creating wind line...")
create_wind_line(64, 8).save("assets/sprites/effects/wind_line.png")

print("  Creating spray particle...")
create_spray_particle(8).save("assets/sprites/effects/spray.png")

print("\nAll assets generated successfully!")
print("\nGenerated files:")
for root, dirs, files in os.walk("assets/sprites"):
    for f in files:
        print(f"  {os.path.join(root, f)}")
