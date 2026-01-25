#!/usr/bin/env python3
"""
Generate enhanced pixel art assets for Charlie's Island Adventure
Epic storm effects and detailed beach textures
"""

from PIL import Image, ImageDraw, ImageFilter
import os
import random
import math

# Ensure assets directories exist
os.makedirs("assets/sprites/environment", exist_ok=True)
os.makedirs("assets/sprites/effects", exist_ok=True)

# Enhanced color palettes
COLORS = {
    # Storm sky - darker and more dramatic
    'storm_sky_top': (15, 18, 35),
    'storm_sky_mid': (25, 35, 55),
    'storm_sky_low': (35, 50, 75),
    'storm_cloud_dark': (20, 25, 40),
    'storm_cloud_mid': (35, 40, 55),
    'storm_cloud_light': (50, 60, 80),
    'storm_cloud_highlight': (70, 85, 110),

    # Lightning
    'lightning_core': (255, 255, 255),
    'lightning_bright': (255, 255, 230),
    'lightning_glow': (180, 190, 255),
    'lightning_outer': (120, 140, 200),

    # Storm ocean - turbulent and dark
    'ocean_storm_deep': (15, 35, 60),
    'ocean_storm_mid': (25, 55, 90),
    'ocean_storm_light': (40, 80, 120),
    'ocean_storm_crest': (70, 110, 150),
    'ocean_foam': (180, 200, 220),
    'ocean_spray': (220, 235, 250),

    # Rain
    'rain_heavy': (150, 170, 210),
    'rain_light': (180, 200, 230),

    # Wind streaks
    'wind_light': (150, 170, 200),
    'wind_dark': (100, 120, 160),

    # Beach sand - detailed texture
    'sand_light': (245, 225, 180),
    'sand_mid': (230, 205, 160),
    'sand_dark': (210, 185, 140),
    'sand_wet': (180, 160, 120),
    'sand_pebble': (160, 140, 110),
    'sand_grain_light': (255, 240, 200),
    'sand_grain_dark': (200, 175, 135),

    # Shells
    'shell_white': (250, 245, 240),
    'shell_pink': (255, 220, 215),
    'shell_tan': (235, 210, 180),

    # Driftwood
    'wood_light': (170, 150, 130),
    'wood_mid': (140, 120, 100),
    'wood_dark': (110, 90, 75),

    # Raft
    'raft_log_light': (160, 130, 95),
    'raft_log_mid': (130, 100, 70),
    'raft_log_dark': (100, 75, 50),
    'rope': (190, 170, 130),
    'rope_dark': (150, 130, 100),
}


def create_epic_storm_sky(width=426, height=160):
    """Create dramatic stormy sky with layered clouds"""
    img = Image.new('RGBA', (width, height), COLORS['storm_sky_top'])
    draw = ImageDraw.Draw(img)

    # Multi-layer gradient sky
    for y in range(height):
        ratio = y / height
        if ratio < 0.4:
            # Top section - very dark
            t = ratio / 0.4
            r = int(COLORS['storm_sky_top'][0] * (1-t) + COLORS['storm_sky_mid'][0] * t)
            g = int(COLORS['storm_sky_top'][1] * (1-t) + COLORS['storm_sky_mid'][1] * t)
            b = int(COLORS['storm_sky_top'][2] * (1-t) + COLORS['storm_sky_mid'][2] * t)
        else:
            # Lower section - slightly lighter
            t = (ratio - 0.4) / 0.6
            r = int(COLORS['storm_sky_mid'][0] * (1-t) + COLORS['storm_sky_low'][0] * t)
            g = int(COLORS['storm_sky_mid'][1] * (1-t) + COLORS['storm_sky_low'][1] * t)
            b = int(COLORS['storm_sky_mid'][2] * (1-t) + COLORS['storm_sky_low'][2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Storm clouds - multiple layers for depth
    random.seed(42)

    # Background cloud layer (distant, lighter)
    for _ in range(12):
        cx = random.randint(-50, width + 50)
        cy = random.randint(5, height // 3)
        for _ in range(8):
            rx = cx + random.randint(-60, 60)
            ry = cy + random.randint(-20, 20)
            rw = random.randint(50, 120)
            rh = random.randint(25, 50)
            draw.ellipse([rx, ry, rx+rw, ry+rh], fill=COLORS['storm_cloud_light'])

    # Mid cloud layer
    for _ in range(15):
        cx = random.randint(-30, width + 30)
        cy = random.randint(10, height // 2)
        for _ in range(6):
            rx = cx + random.randint(-50, 50)
            ry = cy + random.randint(-15, 15)
            rw = random.randint(40, 90)
            rh = random.randint(20, 40)
            draw.ellipse([rx, ry, rx+rw, ry+rh], fill=COLORS['storm_cloud_mid'])

    # Foreground clouds (closest, darkest)
    for _ in range(10):
        cx = random.randint(0, width)
        cy = random.randint(20, height * 2 // 3)
        for _ in range(5):
            rx = cx + random.randint(-40, 40)
            ry = cy + random.randint(-12, 12)
            rw = random.randint(35, 70)
            rh = random.randint(15, 35)
            draw.ellipse([rx, ry, rx+rw, ry+rh], fill=COLORS['storm_cloud_dark'])

    # Cloud highlights (lightning-lit edges)
    for _ in range(8):
        cx = random.randint(0, width)
        cy = random.randint(30, height // 2)
        rw = random.randint(20, 40)
        rh = random.randint(10, 20)
        # Subtle highlight
        for i in range(3):
            alpha = 30 - i * 10
            draw.ellipse([cx-i, cy-i, cx+rw+i, cy+rh+i],
                        fill=(*COLORS['storm_cloud_highlight'], alpha))

    return img


def create_epic_storm_ocean(width=426, height=120):
    """Create turbulent stormy ocean with large waves"""
    img = Image.new('RGBA', (width, height), COLORS['ocean_storm_deep'])
    draw = ImageDraw.Draw(img)

    random.seed(789)

    # Base gradient - darker at top (horizon)
    for y in range(height):
        ratio = y / height
        r = int(COLORS['ocean_storm_deep'][0] + (COLORS['ocean_storm_mid'][0] - COLORS['ocean_storm_deep'][0]) * ratio * 0.6)
        g = int(COLORS['ocean_storm_deep'][1] + (COLORS['ocean_storm_mid'][1] - COLORS['ocean_storm_deep'][1]) * ratio * 0.6)
        b = int(COLORS['ocean_storm_deep'][2] + (COLORS['ocean_storm_mid'][2] - COLORS['ocean_storm_deep'][2]) * ratio * 0.6)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Large rolling waves
    for wave_idx, wave_y in enumerate([8, 28, 50, 75, 100]):
        wave_height = 6 + wave_idx * 2
        wave_freq = 0.02 + wave_idx * 0.005
        phase = wave_idx * 1.5

        for x in range(0, width):
            # Main wave shape
            offset = int(math.sin(x * wave_freq + phase) * wave_height)
            offset2 = int(math.sin(x * wave_freq * 2.3 + phase) * (wave_height // 2))
            total_offset = offset + offset2
            y = wave_y + total_offset

            if 0 <= y < height:
                # Wave body
                draw.line([(x, y), (x, min(y + 4 + wave_idx, height))],
                         fill=COLORS['ocean_storm_light'])

                # Wave crest (white foam)
                if y > 0:
                    # Foam at crest
                    foam_alpha = int(200 - wave_idx * 30)
                    draw.point((x, y-1), fill=(*COLORS['ocean_foam'], foam_alpha))
                    if random.random() > 0.5:
                        draw.point((x, y-2), fill=(*COLORS['ocean_spray'], foam_alpha // 2))

    # Spray and foam patches
    for _ in range(50):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        size = random.randint(2, 5)
        alpha = random.randint(50, 150)
        draw.ellipse([x, y, x+size, y+size//2], fill=(*COLORS['ocean_foam'], alpha))

    # Wind-driven spray streaks
    for _ in range(20):
        x = random.randint(0, width-30)
        y = random.randint(0, height//2)
        length = random.randint(15, 40)
        for i in range(length):
            alpha = int(100 * (1 - i / length))
            draw.point((x + i, y + random.randint(-1, 1)), fill=(*COLORS['ocean_spray'], alpha))

    return img


def create_lightning_bolt(width=80, height=160):
    """Create dramatic forked lightning bolt"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def draw_bolt(start, end, thickness=3, glow=True):
        """Draw a lightning segment with glow"""
        if glow:
            # Outer glow
            for offset in range(6, 0, -2):
                alpha = 30 + (6 - offset) * 20
                draw.line([start, end], fill=(*COLORS['lightning_outer'], alpha), width=thickness + offset)
            # Mid glow
            draw.line([start, end], fill=COLORS['lightning_glow'], width=thickness + 2)
        # Core
        draw.line([start, end], fill=COLORS['lightning_bright'], width=thickness)
        draw.line([start, end], fill=COLORS['lightning_core'], width=max(1, thickness - 1))

    # Main bolt path with jagged segments
    random.seed(999)
    points = [(width // 2, 0)]
    y = 0
    while y < height - 10:
        y += random.randint(12, 25)
        x_offset = random.randint(-15, 15)
        x = max(10, min(width - 10, points[-1][0] + x_offset))
        points.append((x, min(y, height)))

    # Draw main bolt
    for i in range(len(points) - 1):
        thickness = max(1, 4 - i // 3)
        draw_bolt(points[i], points[i+1], thickness)

    # Fork branches
    for branch_start_idx in [1, 3, 5]:
        if branch_start_idx < len(points):
            start = points[branch_start_idx]
            branch_len = random.randint(3, 5)
            branch_points = [start]
            for _ in range(branch_len):
                x_off = random.choice([-1, 1]) * random.randint(8, 20)
                y_off = random.randint(10, 20)
                new_x = max(5, min(width - 5, branch_points[-1][0] + x_off))
                new_y = min(height - 5, branch_points[-1][1] + y_off)
                branch_points.append((new_x, new_y))

            for i in range(len(branch_points) - 1):
                draw_bolt(branch_points[i], branch_points[i+1], max(1, 2 - i), glow=(i < 2))

    return img


def create_rain_sheet(width=64, height=64):
    """Create rain particle sheet with angled heavy rain"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(111)

    # Dense rain streaks at an angle (wind-driven)
    for _ in range(40):
        x = random.randint(0, width)
        y = random.randint(0, height // 2)
        length = random.randint(10, 25)
        alpha = random.randint(100, 200)
        color = COLORS['rain_heavy'] if random.random() > 0.4 else COLORS['rain_light']

        # Angled rain (wind from left)
        end_x = x + length // 3
        end_y = y + length

        # Gradient fade
        for i in range(length):
            t = i / length
            px = int(x + (end_x - x) * t)
            py = int(y + (end_y - y) * t)
            point_alpha = int(alpha * (1 - t * 0.5))
            if 0 <= px < width and 0 <= py < height:
                draw.point((px, py), fill=(*color, point_alpha))

    return img


def create_wind_streaks(width=100, height=16):
    """Create horizontal wind effect streaks"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Multiple wind lines
    for y_off in [3, 7, 11]:
        # Curved wind line with fade at ends
        for x in range(width):
            # S-curve
            wave = math.sin(x * 0.08) * 2
            y = int(y_off + wave)

            # Fade at edges
            fade = 1.0
            if x < 15:
                fade = x / 15
            elif x > width - 15:
                fade = (width - x) / 15

            alpha = int(180 * fade)

            if 0 <= y < height:
                draw.point((x, y), fill=(*COLORS['wind_light'], alpha))
                if y + 1 < height:
                    draw.point((x, y + 1), fill=(*COLORS['wind_dark'], alpha // 2))

    return img


def create_ocean_spray(size=16):
    """Create ocean spray particle effect"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(222)

    # Central burst
    center = size // 2
    for _ in range(15):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(2, size // 2 - 1)
        x = int(center + math.cos(angle) * dist)
        y = int(center + math.sin(angle) * dist)
        particle_size = random.randint(1, 3)
        alpha = random.randint(100, 200)
        if 0 <= x < size and 0 <= y < size:
            draw.ellipse([x, y, x + particle_size, y + particle_size],
                        fill=(*COLORS['ocean_spray'], alpha))

    # Central bright spot
    draw.ellipse([center-2, center-2, center+2, center+2],
                fill=(*COLORS['ocean_spray'], 180))

    return img


def create_detailed_beach_sand(width=426, height=140):
    """Create detailed sandy beach texture"""
    img = Image.new('RGBA', (width, height), COLORS['sand_mid'])
    draw = ImageDraw.Draw(img)

    random.seed(333)

    # Base gradient - wet near water (top)
    for y in range(height):
        ratio = y / height
        if ratio < 0.15:
            # Very wet sand
            t = ratio / 0.15
            r = int(COLORS['sand_wet'][0] * (1-t) + COLORS['sand_dark'][0] * t)
            g = int(COLORS['sand_wet'][1] * (1-t) + COLORS['sand_dark'][1] * t)
            b = int(COLORS['sand_wet'][2] * (1-t) + COLORS['sand_dark'][2] * t)
        elif ratio < 0.35:
            # Damp sand
            t = (ratio - 0.15) / 0.2
            r = int(COLORS['sand_dark'][0] * (1-t) + COLORS['sand_mid'][0] * t)
            g = int(COLORS['sand_dark'][1] * (1-t) + COLORS['sand_mid'][1] * t)
            b = int(COLORS['sand_dark'][2] * (1-t) + COLORS['sand_mid'][2] * t)
        else:
            # Dry sand
            t = (ratio - 0.35) / 0.65
            r = int(COLORS['sand_mid'][0] * (1-t) + COLORS['sand_light'][0] * t)
            g = int(COLORS['sand_mid'][1] * (1-t) + COLORS['sand_light'][1] * t)
            b = int(COLORS['sand_mid'][2] * (1-t) + COLORS['sand_light'][2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Sand grain texture - many small dots
    for _ in range(2500):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        color = random.choice([
            COLORS['sand_grain_light'],
            COLORS['sand_grain_dark'],
            COLORS['sand_mid'],
            COLORS['sand_light'],
        ])
        size = random.choice([1, 1, 1, 2])
        if size == 1:
            draw.point((x, y), fill=color)
        else:
            draw.ellipse([x, y, x+size, y+size], fill=color)

    # Small pebbles scattered
    for _ in range(60):
        x = random.randint(0, width-5)
        y = random.randint(int(height * 0.3), height-5)
        size = random.randint(2, 4)
        color = COLORS['sand_pebble']
        draw.ellipse([x, y, x+size, y+size-1], fill=color)
        # Highlight
        draw.point((x+1, y), fill=COLORS['sand_light'])

    # Scattered shells
    shell_colors = [COLORS['shell_white'], COLORS['shell_pink'], COLORS['shell_tan']]
    for _ in range(20):
        x = random.randint(10, width-15)
        y = random.randint(int(height * 0.25), height-10)
        color = random.choice(shell_colors)
        size = random.randint(4, 8)
        # Shell shape
        draw.ellipse([x, y, x+size, y+size//2+1], fill=color)
        # Shell ridges
        if size > 5:
            draw.arc([x+1, y, x+size-1, y+size//2], 30, 150, fill=COLORS['sand_dark'])

    # Driftwood pieces
    for _ in range(3):
        x = random.randint(20, width-60)
        y = random.randint(int(height * 0.4), height-15)
        length = random.randint(30, 50)
        thickness = random.randint(4, 8)
        angle = random.uniform(-0.2, 0.2)

        # Draw wood with grain
        end_x = int(x + length * math.cos(angle))
        end_y = int(y + length * math.sin(angle))

        draw.line([(x, y), (end_x, end_y)], fill=COLORS['wood_mid'], width=thickness)
        draw.line([(x, y-1), (end_x, end_y-1)], fill=COLORS['wood_light'], width=thickness//2)
        draw.line([(x, y+thickness//2), (end_x, end_y+thickness//2)], fill=COLORS['wood_dark'], width=2)

    # Seaweed/debris at water line
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(5, int(height * 0.15))
        length = random.randint(8, 20)
        # Dark seaweed
        for i in range(length):
            px = x + random.randint(-2, 2)
            py = y + i // 3
            if 0 <= px < width and 0 <= py < height:
                draw.point((px, py), fill=(50, 70, 45, 200))

    return img


def create_large_raft(size=96):
    """Create detailed wooden raft with logs, rope, and box"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size // 96

    # Main raft logs (horizontal)
    log_positions = [25, 35, 45, 55, 65]
    for i, y in enumerate(log_positions):
        y *= s
        shade = COLORS['raft_log_mid'] if i % 2 == 0 else COLORS['raft_log_dark']
        highlight = COLORS['raft_log_light'] if i % 2 == 0 else COLORS['raft_log_mid']

        # Log body
        draw.rounded_rectangle([6*s, y, 90*s, y + 9*s], radius=3*s, fill=shade)
        # Top highlight
        draw.line([(8*s, y + 2*s), (88*s, y + 2*s)], fill=highlight, width=2*s)
        # Bottom shadow
        draw.line([(8*s, y + 7*s), (88*s, y + 7*s)], fill=COLORS['raft_log_dark'], width=s)

        # Wood grain lines
        for gx in range(12*s, 85*s, 12*s):
            draw.line([(gx, y + 3*s), (gx + 6*s, y + 6*s)], fill=highlight, width=s)

    # Cross beams (vertical)
    for bx in [18, 72]:
        bx *= s
        draw.rectangle([bx, 22*s, bx + 8*s, 72*s], fill=COLORS['raft_log_light'])
        draw.line([(bx + 2*s, 24*s), (bx + 2*s, 70*s)], fill=COLORS['raft_log_mid'], width=s)

    # Rope bindings
    rope_positions = [(22*s, 28*s), (22*s, 48*s), (22*s, 62*s),
                      (76*s, 28*s), (76*s, 48*s), (76*s, 62*s)]
    for rx, ry in rope_positions:
        # Rope coil
        draw.ellipse([rx - 3*s, ry, rx + 5*s, ry + 5*s], fill=COLORS['rope'])
        draw.arc([rx - 3*s, ry, rx + 5*s, ry + 5*s], 0, 180, fill=COLORS['rope_dark'], width=s)
        # Rope cross
        draw.line([(rx - 2*s, ry + 6*s), (rx + 4*s, ry - 2*s)], fill=COLORS['rope'], width=2*s)

    return img


# Generate all enhanced assets
print("Generating enhanced pixel art assets...")

print("  Creating epic storm sky...")
create_epic_storm_sky(426, 160).save("assets/sprites/environment/storm_sky.png")

print("  Creating epic storm ocean...")
create_epic_storm_ocean(426, 120).save("assets/sprites/environment/storm_ocean.png")

print("  Creating lightning bolt...")
create_lightning_bolt(80, 160).save("assets/sprites/effects/lightning.png")

print("  Creating rain sheet...")
create_rain_sheet(64, 64).save("assets/sprites/effects/rain.png")

print("  Creating wind streaks...")
create_wind_streaks(100, 16).save("assets/sprites/effects/wind_line.png")

print("  Creating ocean spray...")
create_ocean_spray(16).save("assets/sprites/effects/spray.png")

print("  Creating detailed beach sand...")
create_detailed_beach_sand(426, 140).save("assets/sprites/environment/beach_sand.png")

print("  Creating large raft...")
create_large_raft(96).save("assets/sprites/environment/raft_large.png")

print("\nEnhanced assets generated successfully!")
