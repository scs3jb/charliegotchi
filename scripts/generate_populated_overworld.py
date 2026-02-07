#!/usr/bin/env python3
"""
Generate a richly populated Overworld.tscn with content for each biome.
Uses smart placement algorithms for dense, natural-looking prop distribution.
"""

import random
import math

# Screen dimensions
SCREEN_W = 426
SCREEN_H = 240
GRID_COLS = 6
GRID_ROWS = 4

# Biome layout
# [Beach ] [Meadow] [Meadow] [Forest] [Forest] [Mountain]
# [Beach ] [Home  ] [Meadow] [Forest] [Lake  ] [Mountain]
# [Beach ] [Meadow] [Path  ] [Path  ] [Lake  ] [Mountain]
# [Cliffs] [Cliffs] [Bridge] [Path  ] [Forest] [Mountain]

BIOMES = [
    ["beach", "meadow", "meadow", "forest", "forest", "mountain"],
    ["beach", "home", "meadow", "forest", "lake", "mountain"],
    ["beach", "meadow", "path", "path", "lake", "mountain"],
    ["cliffs", "cliffs", "bridge", "path", "forest", "mountain"],
]

# House exclusion zone (house at 640,320 with 100x80 body + margin)
HOUSE_EXCLUSION = (580, 260, 700, 420)

# Minimum spacing per prop type
SPACING = {
    'trees': 40,
    'rocks': 28,
    'bushes': 30,
    'flowers': 10,
    'water': 58,
    'mountains': 0,  # Overlap intentional for solid walls
    'cliffs': 0,
    'fences': 0,
    'paths': 0,
    'bridges': 0,
    'signposts': 60,
}


def screen_bounds(col, row):
    """Get pixel bounds for a screen."""
    return (col * SCREEN_W, row * SCREEN_H, (col + 1) * SCREEN_W, (row + 1) * SCREEN_H)


def is_in_exclusion_zone(x, y):
    """Check if a point falls within the house exclusion zone."""
    ex1, ey1, ex2, ey2 = HOUSE_EXCLUSION
    return ex1 <= x <= ex2 and ey1 <= y <= ey2


def get_neighbor_biomes(col, row):
    """Get biome types for all adjacent screens."""
    neighbors = {}
    for name, dc, dr in [('left', -1, 0), ('right', 1, 0), ('top', 0, -1), ('bottom', 0, 1)]:
        nc, nr = col + dc, row + dr
        if 0 <= nc < GRID_COLS and 0 <= nr < GRID_ROWS:
            neighbors[name] = BIOMES[nr][nc]
    return neighbors


def place_with_spacing(existing, bounds, count, min_spacing, max_attempts=80):
    """Place items using rejection sampling to ensure minimum spacing.
    Returns list of (x, y) tuples that don't overlap with existing points."""
    x1, y1, x2, y2 = bounds
    placed = []
    for _ in range(count):
        for _ in range(max_attempts):
            x = random.randint(int(x1), int(x2))
            y = random.randint(int(y1), int(y2))
            if is_in_exclusion_zone(x, y):
                continue
            ok = True
            for ex, ey in existing + placed:
                if math.hypot(x - ex, y - ey) < min_spacing:
                    ok = False
                    break
            if ok:
                placed.append((x, y))
                break
    return placed


def place_cluster(center, count, spread, min_spacing, bounds=None):
    """Place items in a Gaussian cluster around a center point.
    Returns list of (x, y) tuples."""
    cx, cy = center
    placed = []
    for _ in range(count):
        for _ in range(60):
            x = cx + random.gauss(0, spread)
            y = cy + random.gauss(0, spread)
            if bounds:
                bx1, by1, bx2, by2 = bounds
                if not (bx1 <= x <= bx2 and by1 <= y <= by2):
                    continue
            if is_in_exclusion_zone(x, y):
                continue
            ok = True
            for ex, ey in placed:
                if math.hypot(x - ex, y - ey) < min_spacing:
                    ok = False
                    break
            if ok:
                placed.append((x, y))
                break
    return placed


def place_along_edge(bounds, edge, count, spacing):
    """Place items evenly along a specific edge of a bounding box.
    edge: 'top', 'bottom', 'left', 'right'
    Returns list of (x, y) tuples."""
    x1, y1, x2, y2 = bounds
    placed = []
    if edge == 'top':
        for i in range(count):
            x = x1 + (x2 - x1) * (i + 0.5) / count + random.randint(-8, 8)
            y = y1 + random.randint(5, 20)
            if not is_in_exclusion_zone(x, y):
                placed.append((x, y))
    elif edge == 'bottom':
        for i in range(count):
            x = x1 + (x2 - x1) * (i + 0.5) / count + random.randint(-8, 8)
            y = y2 - random.randint(5, 20)
            if not is_in_exclusion_zone(x, y):
                placed.append((x, y))
    elif edge == 'left':
        for i in range(count):
            y = y1 + (y2 - y1) * (i + 0.5) / count + random.randint(-8, 8)
            x = x1 + random.randint(5, 20)
            if not is_in_exclusion_zone(x, y):
                placed.append((x, y))
    elif edge == 'right':
        for i in range(count):
            y = y1 + (y2 - y1) * (i + 0.5) / count + random.randint(-8, 8)
            x = x2 - random.randint(5, 20)
            if not is_in_exclusion_zone(x, y):
                placed.append((x, y))
    return placed


def place_wall(bounds, direction, tile_spacing, depth_layers):
    """Place a solid wall formation with overlapping tiles.
    direction: 'horizontal' (wall runs left-right) or 'vertical' (wall runs top-bottom)
    Returns list of (x, y) tuples."""
    x1, y1, x2, y2 = bounds
    placed = []
    if direction == 'horizontal':
        for layer in range(depth_layers):
            y_off = y1 + layer * (tile_spacing * 0.75)
            for x in range(int(x1), int(x2) + 1, int(tile_spacing * 0.75)):
                # Stagger alternate layers
                x_adj = x + (tile_spacing * 0.375 if layer % 2 else 0)
                placed.append((x_adj, y_off + random.randint(-3, 3)))
    else:  # vertical
        for layer in range(depth_layers):
            x_off = x1 + layer * (tile_spacing * 0.75)
            for y in range(int(y1), int(y2) + 1, int(tile_spacing * 0.75)):
                y_adj = y + (tile_spacing * 0.375 if layer % 2 else 0)
                placed.append((x_off + random.randint(-3, 3), y_adj))
    return placed


def generate_props():
    """Generate all prop placements."""
    props = {
        'trees': [],
        'rocks': [],
        'bushes': [],
        'fences': [],
        'flowers': [],
        'water': [],
        'mountains': [],
        'cliffs': [],
        'paths': [],
        'bridges': [],
        'signposts': [],
    }

    random.seed(42)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            biome = BIOMES[row][col]
            x1, y1, x2, y2 = screen_bounds(col, row)

            # Add margin to keep props away from screen edges
            margin = 20
            mx1 = x1 + margin
            my1 = y1 + margin
            mx2 = x2 - margin
            my2 = y2 - margin

            if biome == "beach":
                generate_beach(props, mx1, my1, mx2, my2, col, row)
            elif biome == "meadow":
                generate_meadow(props, mx1, my1, mx2, my2, col, row)
            elif biome == "forest":
                generate_forest(props, mx1, my1, mx2, my2, col, row)
            elif biome == "lake":
                generate_lake(props, mx1, my1, mx2, my2)
            elif biome == "mountain":
                generate_mountain(props, mx1, my1, mx2, my2, col, row)
            elif biome == "cliffs":
                generate_cliffs(props, mx1, my1, mx2, my2, col, row)
            elif biome == "path":
                generate_path(props, mx1, my1, mx2, my2, col, row)
            elif biome == "bridge":
                generate_bridge(props, mx1, my1, mx2, my2)
            elif biome == "home":
                generate_home(props, mx1, my1, mx2, my2)

            # Add biome transitions
            add_biome_transitions(props, col, row)

    return props


def add_biome_transitions(props, col, row):
    """Add transitional props along edges shared with different biome types."""
    biome = BIOMES[row][col]
    neighbors = get_neighbor_biomes(col, row)
    x1, y1, x2, y2 = screen_bounds(col, row)

    # Transition depth into current biome
    depth = 50

    for edge, neighbor_biome in neighbors.items():
        if neighbor_biome == biome:
            continue

        if neighbor_biome == "forest":
            # Trees + bushes along edge shared with forest
            if edge == 'left':
                bounds = (x1 + 5, y1 + 20, x1 + depth, y2 - 20)
            elif edge == 'right':
                bounds = (x2 - depth, y1 + 20, x2 - 5, y2 - 20)
            elif edge == 'top':
                bounds = (x1 + 20, y1 + 5, x2 - 20, y1 + depth)
            elif edge == 'bottom':
                bounds = (x1 + 20, y2 - depth, x2 - 20, y2 - 5)
            else:
                continue
            new_trees = place_with_spacing(props['trees'], bounds, 3, SPACING['trees'])
            props['trees'].extend(new_trees)
            new_bushes = place_with_spacing(props['bushes'], bounds, 2, SPACING['bushes'])
            props['bushes'].extend(new_bushes)

        elif neighbor_biome in ("mountain", "cliffs"):
            # Rocks along edge shared with mountain/cliffs
            if edge == 'left':
                bounds = (x1 + 5, y1 + 20, x1 + depth, y2 - 20)
            elif edge == 'right':
                bounds = (x2 - depth, y1 + 20, x2 - 5, y2 - 20)
            elif edge == 'top':
                bounds = (x1 + 20, y1 + 5, x2 - 20, y1 + depth)
            elif edge == 'bottom':
                bounds = (x1 + 20, y2 - depth, x2 - 20, y2 - 5)
            else:
                continue
            new_rocks = place_with_spacing(props['rocks'], bounds, 3, SPACING['rocks'])
            props['rocks'].extend(new_rocks)

        elif neighbor_biome == "lake":
            # Flowers along edge shared with lake
            if edge == 'left':
                bounds = (x1 + 5, y1 + 15, x1 + depth, y2 - 15)
            elif edge == 'right':
                bounds = (x2 - depth, y1 + 15, x2 - 5, y2 - 15)
            elif edge == 'top':
                bounds = (x1 + 15, y1 + 5, x2 - 15, y1 + depth)
            elif edge == 'bottom':
                bounds = (x1 + 15, y2 - depth, x2 - 15, y2 - 5)
            else:
                continue
            new_flowers = place_with_spacing(props['flowers'], bounds, 4, SPACING['flowers'])
            props['flowers'].extend(new_flowers)


def generate_beach(props, x1, y1, x2, y2, col, row):
    """Beach biome: 2-3 columns of water on left, rocks near waterline, vegetation right."""
    # Water columns on left side (2-3 columns for solid coverage)
    water_zone_right = x1 + (x2 - x1) * 0.35
    for wx_offset in range(3):
        water_x = x1 - 10 + wx_offset * 55
        if water_x > water_zone_right:
            break
        for y in range(int(y1 - 20), int(y2 + 30), 55):
            props['water'].append((water_x, y))

    # Rock clusters near the waterline
    waterline_x = water_zone_right + 15
    rock_cluster = place_cluster(
        (waterline_x, (y1 + y2) / 2), count=5, spread=40,
        min_spacing=SPACING['rocks'], bounds=(x1, y1, water_zone_right + 60, y2)
    )
    props['rocks'].extend(rock_cluster)

    # Additional scattered rocks on sand
    sand_rocks = place_with_spacing(
        props['rocks'], (water_zone_right + 30, y1, x2, y2), 3, SPACING['rocks']
    )
    props['rocks'].extend(sand_rocks)

    # Trees on the grassy right portion
    grass_zone = (x1 + (x2 - x1) * 0.55, y1 + 15, x2 - 10, y2 - 15)
    new_trees = place_with_spacing(props['trees'], grass_zone, 5, SPACING['trees'])
    props['trees'].extend(new_trees)

    # Bushes on right side
    new_bushes = place_with_spacing(props['bushes'], grass_zone, 3, SPACING['bushes'])
    props['bushes'].extend(new_bushes)

    # Flowers scattered on the grassy part
    flower_pts = place_with_spacing(props['flowers'], grass_zone, 6, SPACING['flowers'])
    props['flowers'].extend(flower_pts)


def generate_meadow(props, x1, y1, x2, y2, col, row):
    """Meadow biome: 3-5 flower clusters, scattered trees, bushes."""
    bounds = (x1, y1, x2, y2)

    # 3-5 flower clusters of 8-12 flowers each
    num_clusters = random.randint(3, 5)
    cluster_centers = place_with_spacing([], bounds, num_clusters, 60)
    for cx, cy in cluster_centers:
        cluster_size = random.randint(8, 12)
        cluster_pts = place_cluster((cx, cy), cluster_size, spread=25,
                                    min_spacing=SPACING['flowers'], bounds=bounds)
        props['flowers'].extend(cluster_pts)

    # 6-8 trees with natural spacing
    new_trees = place_with_spacing(props['trees'],
                                   (x1 + 20, y1 + 20, x2 - 20, y2 - 20),
                                   random.randint(6, 8), SPACING['trees'])
    props['trees'].extend(new_trees)

    # 5-7 bushes
    new_bushes = place_with_spacing(props['bushes'],
                                    (x1 + 15, y1 + 15, x2 - 15, y2 - 15),
                                    random.randint(5, 7), SPACING['bushes'])
    props['bushes'].extend(new_bushes)

    # 1-2 rocks
    new_rocks = place_with_spacing(props['rocks'],
                                   (x1 + 25, y1 + 25, x2 - 25, y2 - 25),
                                   random.randint(1, 2), SPACING['rocks'])
    props['rocks'].extend(new_rocks)


def generate_forest(props, x1, y1, x2, y2, col, row):
    """Forest biome: dense trees in grove clusters with navigable corridor."""
    bounds = (x1, y1, x2, y2)
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    # Define a navigable corridor (60-80px wide through center)
    corridor_half = random.randint(30, 40)
    corridor_left = cx - corridor_half
    corridor_right = cx + corridor_half

    # Place trees in 2-3 grove clusters, avoiding the corridor
    num_groves = random.randint(2, 3)
    grove_positions = []
    # Left grove
    grove_positions.append((x1 + (corridor_left - x1) / 2, cy + random.randint(-30, 30)))
    # Right grove
    grove_positions.append((corridor_right + (x2 - corridor_right) / 2, cy + random.randint(-30, 30)))
    if num_groves == 3:
        # Top or bottom grove offset from center
        grove_positions.append((cx + random.choice([-60, 60]),
                                random.choice([y1 + 40, y2 - 40])))

    for gx, gy in grove_positions:
        grove_size = random.randint(6, 8)
        grove_trees = place_cluster((gx, gy), grove_size, spread=35,
                                    min_spacing=SPACING['trees'], bounds=bounds)
        # Filter out trees that land in corridor
        grove_trees = [(x, y) for x, y in grove_trees
                       if not (corridor_left - 10 < x < corridor_right + 10)]
        props['trees'].extend(grove_trees)

    # Dense bushes between and around trees
    new_bushes = place_with_spacing(props['bushes'], bounds,
                                    random.randint(10, 14), SPACING['bushes'])
    # Filter corridor
    new_bushes = [(x, y) for x, y in new_bushes
                  if not (corridor_left < x < corridor_right)]
    props['bushes'].extend(new_bushes)

    # Rocks scattered in forest floor
    new_rocks = place_with_spacing(props['rocks'], bounds,
                                   random.randint(4, 6), SPACING['rocks'])
    props['rocks'].extend(new_rocks)

    # Flowers in clearings (corridor and small gaps)
    corridor_flowers = place_with_spacing(
        props['flowers'],
        (corridor_left, y1 + 10, corridor_right, y2 - 10),
        random.randint(4, 6), SPACING['flowers']
    )
    props['flowers'].extend(corridor_flowers)


def generate_lake(props, x1, y1, x2, y2):
    """Lake biome: large oval water body, double tree ring, dense shore flowers."""
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    bounds = (x1, y1, x2, y2)

    # Oval water body (28-32 tiles) - larger than before
    water_rx = 100  # horizontal radius
    water_ry = 65   # vertical radius
    water_count = 0
    for dx_step in range(-3, 4):
        for dy_step in range(-2, 3):
            wx = cx + dx_step * 32
            wy = cy + dy_step * 32
            # Check if within oval
            if (wx - cx)**2 / water_rx**2 + (wy - cy)**2 / water_ry**2 <= 1.3:
                props['water'].append((wx, wy))
                water_count += 1

    # Fill gaps with additional water tiles
    for _ in range(10):
        angle = random.uniform(0, 2 * math.pi)
        dist_x = random.uniform(0, water_rx * 0.8)
        dist_y = random.uniform(0, water_ry * 0.8)
        wx = cx + math.cos(angle) * dist_x
        wy = cy + math.sin(angle) * dist_y
        props['water'].append((wx, wy))

    # Inner ring of trees (close to shore)
    for angle_deg in range(0, 360, 25):
        angle = math.radians(angle_deg + random.randint(-5, 5))
        dist = random.randint(90, 105)
        x = cx + math.cos(angle) * dist
        y = cy + math.sin(angle) * dist * 0.65
        if x1 + 15 < x < x2 - 15 and y1 + 15 < y < y2 - 15:
            if not is_in_exclusion_zone(x, y):
                props['trees'].append((x, y))

    # Outer ring of trees
    for angle_deg in range(0, 360, 35):
        angle = math.radians(angle_deg + random.randint(-8, 8))
        dist = random.randint(115, 135)
        x = cx + math.cos(angle) * dist
        y = cy + math.sin(angle) * dist * 0.65
        if x1 + 15 < x < x2 - 15 and y1 + 15 < y < y2 - 15:
            if not is_in_exclusion_zone(x, y):
                props['trees'].append((x, y))

    # Dense flowers near the shore
    for _ in range(16):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.randint(75, 95)
        x = cx + math.cos(angle) * dist
        y = cy + math.sin(angle) * dist * 0.65
        if x1 < x < x2 and y1 < y < y2:
            if not is_in_exclusion_zone(x, y):
                props['flowers'].append((x, y))

    # Bushes near shore
    new_bushes = place_with_spacing(props['bushes'], bounds, 5, SPACING['bushes'])
    props['bushes'].extend(new_bushes)


def generate_mountain(props, x1, y1, x2, y2, col, row):
    """Mountain biome: 4-5 deep wall layers with rocks and scrub at base."""
    # Mountain wall fills the right portion of the screen (mountains are on col 5)
    # Wall starts from right edge and extends inward
    wall_start_x = x1  # Left edge of mountain screen
    wall_end_x = x1 + (x2 - x1) * 0.65  # ~65% of screen is mountain wall

    # 4-5 deep wall layers
    wall_tiles = place_wall(
        (wall_start_x - 10, y1 - 10, wall_end_x, y2 + 10),
        direction='vertical',
        tile_spacing=50,
        depth_layers=random.randint(4, 5)
    )
    props['mountains'].extend(wall_tiles)

    # Rocks at the base of the mountains (in the navigable strip)
    base_zone = (wall_end_x + 5, y1 + 15, x2 - 10, y2 - 15)
    rock_cluster = place_with_spacing(props['rocks'], base_zone,
                                      random.randint(5, 7), SPACING['rocks'])
    props['rocks'].extend(rock_cluster)

    # Hardy scrub bushes at base
    base_bushes = place_with_spacing(props['bushes'], base_zone,
                                     random.randint(3, 4), SPACING['bushes'])
    props['bushes'].extend(base_bushes)

    # Sparse flowers at base
    base_flowers = place_with_spacing(props['flowers'], base_zone,
                                      random.randint(2, 4), SPACING['flowers'])
    props['flowers'].extend(base_flowers)


def generate_cliffs(props, x1, y1, x2, y2, col, row):
    """Cliffs biome: 3 deep horizontal layers with vegetation below face."""
    # Cliff wall across upper portion of screen
    cliff_bottom = y1 + (y2 - y1) * 0.5

    # 3 deep layers of cliff tiles
    cliff_tiles = place_wall(
        (x1 - 10, y1 - 10, x2 + 10, cliff_bottom),
        direction='horizontal',
        tile_spacing=55,
        depth_layers=3
    )
    props['cliffs'].extend(cliff_tiles)

    # Rocks at cliff base
    base_zone = (x1 + 10, cliff_bottom + 5, x2 - 10, y2 - 10)
    rock_cluster = place_with_spacing(props['rocks'], base_zone,
                                      random.randint(5, 7), SPACING['rocks'])
    props['rocks'].extend(rock_cluster)

    # Trees below the cliff face
    new_trees = place_with_spacing(props['trees'], base_zone,
                                   random.randint(4, 6), SPACING['trees'])
    props['trees'].extend(new_trees)

    # Bushes in the navigable area
    new_bushes = place_with_spacing(props['bushes'], base_zone,
                                    random.randint(3, 5), SPACING['bushes'])
    props['bushes'].extend(new_bushes)

    # Flowers scattered below
    new_flowers = place_with_spacing(props['flowers'], base_zone,
                                     random.randint(4, 6), SPACING['flowers'])
    props['flowers'].extend(new_flowers)


def generate_path(props, x1, y1, x2, y2, col, row):
    """Path biome: 3-wide path strip, trees + flowers lining both sides, fences."""
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    # 3-wide vertical path strip
    path_half_width = 22
    for y in range(int(y1 - 20), int(y2 + 20), 40):
        props['paths'].append((cx - path_half_width, y))
        props['paths'].append((cx, y))
        props['paths'].append((cx + path_half_width, y))

    # Horizontal connections at row 3
    if row == 3:
        for x in range(int(x1 - 20), int(x2 + 20), 40):
            props['paths'].append((x, cy - path_half_width))
            props['paths'].append((x, cy))
            props['paths'].append((x, cy + path_half_width))

    # Signpost at intersections
    if row == 2 and col == 2:
        props['signposts'].append((cx + 50, cy))
    elif row == 3 and col == 3:
        props['signposts'].append((cx + 50, cy - 50))

    # Trees lining both sides of the path
    left_tree_zone = (x1 + 10, y1 + 15, cx - 55, y2 - 15)
    right_tree_zone = (cx + 55, y1 + 15, x2 - 10, y2 - 15)

    left_trees = place_with_spacing(props['trees'], left_tree_zone,
                                    random.randint(4, 5), SPACING['trees'])
    props['trees'].extend(left_trees)
    right_trees = place_with_spacing(props['trees'], right_tree_zone,
                                     random.randint(4, 5), SPACING['trees'])
    props['trees'].extend(right_trees)

    # Flowers lining the path edges
    for side_offset in [-40, -30, 30, 40]:
        for _ in range(3):
            y = random.randint(int(y1 + 10), int(y2 - 10))
            fx = cx + side_offset + random.randint(-5, 5)
            if x1 < fx < x2 and not is_in_exclusion_zone(fx, y):
                props['flowers'].append((fx, y))

    # Bushes along sides
    new_bushes = place_with_spacing(
        props['bushes'],
        (x1 + 10, y1 + 10, x2 - 10, y2 - 10),
        random.randint(4, 6), SPACING['bushes']
    )
    # Filter out bushes on the path itself
    new_bushes = [(x, y) for x, y in new_bushes
                  if abs(x - cx) > path_half_width + 15]
    props['bushes'].extend(new_bushes)

    # Fences along path sections
    fence_y_start = y1 + 30
    for fy in range(int(fence_y_start), int(y2 - 20), 48):
        if random.random() < 0.7:
            props['fences'].append((cx - 55, fy))
        if random.random() < 0.7:
            props['fences'].append((cx + 55, fy))


def generate_bridge(props, x1, y1, x2, y2):
    """Bridge biome: full water coverage both sides, vegetation at corners."""
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    # Full water coverage on both sides of the bridge
    # Left water area
    for wx in range(int(x1 - 10), int(cx - 30), 52):
        for wy in range(int(y1 - 10), int(y2 + 20), 52):
            props['water'].append((wx, wy))
    # Right water area
    for wx in range(int(cx + 30), int(x2 + 20), 52):
        for wy in range(int(y1 - 10), int(y2 + 20), 52):
            props['water'].append((wx, wy))

    # Bridge tiles going north-south (wider bridge)
    for y in range(int(y1 - 10), int(y2 + 10), 38):
        props['bridges'].append((cx - 15, y))
        props['bridges'].append((cx + 15, y))

    # Path connecting to bridge from top and bottom
    props['paths'].append((cx, y1 - 20))
    props['paths'].append((cx, y2 + 20))

    # Vegetation clusters at corners
    corners = [
        (x1 + 25, y1 + 25), (x1 + 25, y2 - 25),
        (x2 - 25, y1 + 25), (x2 - 25, y2 - 25),
    ]
    for corner_x, corner_y in corners:
        if not is_in_exclusion_zone(corner_x, corner_y):
            props['flowers'].append((corner_x + random.randint(-8, 8),
                                     corner_y + random.randint(-8, 8)))
            props['flowers'].append((corner_x + random.randint(-12, 12),
                                     corner_y + random.randint(-12, 12)))
            if random.random() < 0.5:
                props['bushes'].append((corner_x, corner_y))


def generate_home(props, x1, y1, x2, y2):
    """Home biome: complete fence perimeter, garden flower clusters, hedge bushes."""
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    # Complete fence perimeter around the property
    fence_margin = 15
    fence_x1 = x1 + fence_margin
    fence_x2 = x2 - fence_margin
    fence_y1 = y1 + fence_margin
    fence_y2 = y2 - fence_margin

    # Top fence
    for x in range(int(fence_x1), int(fence_x2) + 1, 40):
        props['fences'].append((x, fence_y1))
    # Bottom fence (gap for gate where path passes through)
    gate_half_width = 35
    for x in range(int(fence_x1), int(fence_x2) + 1, 40):
        if abs(x - cx) > gate_half_width:
            props['fences'].append((x, fence_y2))
    # Left fence
    for y in range(int(fence_y1 + 40), int(fence_y2), 40):
        props['fences'].append((fence_x1, y))
    # Right fence
    for y in range(int(fence_y1 + 40), int(fence_y2), 40):
        props['fences'].append((fence_x2, y))

    # Garden flower clusters (below and around the house)
    garden_areas = [
        (cx - 100, cy + 50),   # Left garden
        (cx + 100, cy + 50),   # Right garden
        (cx, cy + 90),         # Front garden
    ]
    for gx, gy in garden_areas:
        garden_bounds = (x1 + 25, y1 + 25, x2 - 25, y2 - 25)
        cluster_pts = place_cluster((gx, gy), random.randint(6, 8), spread=20,
                                    min_spacing=SPACING['flowers'], bounds=garden_bounds)
        props['flowers'].extend(cluster_pts)

    # Trees around the property (outside house exclusion zone)
    tree_positions = [
        (cx - 160, cy - 60), (cx + 160, cy - 60),
        (cx - 170, cy + 60), (cx + 170, cy + 60),
        (cx - 100, cy - 90), (cx + 100, cy - 90),
        (cx - 130, cy + 80), (cx + 130, cy + 80),
    ]
    for tx, ty in tree_positions:
        if x1 + 10 < tx < x2 - 10 and y1 + 10 < ty < y2 - 10:
            if not is_in_exclusion_zone(tx, ty):
                props['trees'].append((tx, ty))

    # Hedge bushes lining the walkway and around house
    hedge_positions = [
        (cx - 60, cy + 65), (cx + 60, cy + 65),
        (cx - 80, cy + 80), (cx + 80, cy + 80),
        (cx - 40, cy + 90), (cx + 40, cy + 90),
        (cx - 100, cy + 40), (cx + 100, cy + 40),
    ]
    for bx, by in hedge_positions:
        if not is_in_exclusion_zone(bx, by):
            props['bushes'].append((bx, by))

    # Path leading to house (wider, from bottom)
    for y in range(int(cy + 80), int(y2 + 20), 40):
        props['paths'].append((cx - 15, y))
        props['paths'].append((cx, y))
        props['paths'].append((cx + 15, y))


def generate_scene(props):
    """Generate the complete Overworld.tscn content."""

    header = '''[gd_scene load_steps=70 format=3 uid="uid://overworld"]

[ext_resource type="Script" path="res://scripts/scenes/Overworld.gd" id="1_overworld"]
[ext_resource type="Script" path="res://scripts/player/Player.gd" id="2_player"]
[ext_resource type="Script" path="res://scripts/charlie/Charlie.gd" id="3_charlie"]
[ext_resource type="Script" path="res://scripts/ui/HUD.gd" id="4_hud"]
[ext_resource type="Script" path="res://scripts/wildlife/WildlifeSpawner.gd" id="9_wildlife_spawner"]
[ext_resource type="Texture2D" path="res://assets/sprites/characters/charlie_spritesheet.png" id="6_charlie_sprite"]
[ext_resource type="SpriteFrames" path="res://assets/sprites/characters/charlie_sprite_frames.tres" id="7_charlie_frames"]
[ext_resource type="SpriteFrames" path="res://resources/sprites/player_frames.tres" id="8_player_frames"]
[ext_resource type="PackedScene" path="res://scenes/props/Tree.tscn" id="10_tree"]
[ext_resource type="PackedScene" path="res://scenes/props/Rock.tscn" id="11_rock"]
[ext_resource type="PackedScene" path="res://scenes/props/Bush.tscn" id="12_bush"]
[ext_resource type="PackedScene" path="res://scenes/props/Fence.tscn" id="13_fence"]
[ext_resource type="PackedScene" path="res://scenes/props/FlowerPatch.tscn" id="14_flower"]
[ext_resource type="PackedScene" path="res://scenes/props/WaterBody.tscn" id="15_water"]
[ext_resource type="PackedScene" path="res://scenes/props/MountainWall.tscn" id="16_mountain"]
[ext_resource type="PackedScene" path="res://scenes/props/CliffWall.tscn" id="17_cliff"]
[ext_resource type="PackedScene" path="res://scenes/props/PathTile.tscn" id="18_path"]
[ext_resource type="PackedScene" path="res://scenes/props/BridgeTile.tscn" id="19_bridge"]
[ext_resource type="PackedScene" path="res://scenes/props/Signpost.tscn" id="20_signpost"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_player"]
size = Vector2(16, 12)

[sub_resource type="CircleShape2D" id="CircleShape2D_interaction"]
radius = 30.0

[sub_resource type="RectangleShape2D" id="RectangleShape2D_charlie"]
size = Vector2(18, 12)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_house"]
size = Vector2(100, 80)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_idle_down"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(0, 0, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_idle_left"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(0, 32, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_idle_right"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(0, 64, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_idle_up"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(0, 96, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_down_1"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(32, 0, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_down_2"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(64, 0, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_down_3"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(96, 0, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_left_1"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(32, 32, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_left_2"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(64, 32, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_left_3"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(96, 32, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_right_1"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(32, 64, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_right_2"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(64, 64, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_right_3"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(96, 64, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_up_1"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(32, 96, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_up_2"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(64, 96, 32, 32)

[sub_resource type="AtlasTexture" id="AtlasTexture_charlie_walk_up_3"]
atlas = ExtResource("6_charlie_sprite")
region = Rect2(96, 96, 32, 32)

[sub_resource type="SpriteFrames" id="SpriteFrames_charlie"]
animations = [{
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_down")
}],
"loop": true,
"name": &"idle_down",
"speed": 5.0
}, {
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_left")
}],
"loop": true,
"name": &"idle_left",
"speed": 5.0
}, {
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_right")
}],
"loop": true,
"name": &"idle_right",
"speed": 5.0
}, {
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_up")
}],
"loop": true,
"name": &"idle_up",
"speed": 5.0
}, {
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_1")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_2")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_3")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_2")
}],
"loop": true,
"name": &"walk_down",
"speed": 10.0
}, {
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_1")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_2")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_3")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_2")
}],
"loop": true,
"name": &"walk_left",
"speed": 10.0
}, {
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_1")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_2")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_3")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_2")
}],
"loop": true,
"name": &"walk_right",
"speed": 10.0
}, {
"frames": [{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_1")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_2")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_3")
}, {
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_2")
}],
"loop": true,
"name": &"walk_up",
"speed": 10.0
}]

[node name="Overworld" type="Node2D"]
y_sort_enabled = true
script = ExtResource("1_overworld")

[node name="Background" type="ColorRect" parent="."]
z_index = -10
offset_right = 2556.0
offset_bottom = 960.0
color = Color(0.3, 0.55, 0.25, 1)

'''

    content = header
    idx = 1

    # Add biome-specific background colors
    biome_colors = {
        'beach': 'Color(0.85, 0.78, 0.6, 1)',
        'lake': 'Color(0.3, 0.55, 0.25, 1)',
        'mountain': 'Color(0.4, 0.38, 0.35, 1)',
        'cliffs': 'Color(0.35, 0.5, 0.28, 1)',
    }

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            biome = BIOMES[row][col]
            if biome in biome_colors:
                x1, y1, x2, y2 = screen_bounds(col, row)
                content += f'''[node name="Biome_{col}_{row}" type="ColorRect" parent="."]
z_index = -9
offset_left = {x1}.0
offset_top = {y1}.0
offset_right = {x2}.0
offset_bottom = {y2}.0
color = {biome_colors[biome]}

'''

    # Add path tiles
    for i, (x, y) in enumerate(props['paths']):
        content += f'[node name="Path{i+1}" parent="." instance=ExtResource("18_path")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add bridge tiles
    for i, (x, y) in enumerate(props['bridges']):
        content += f'[node name="Bridge{i+1}" parent="." instance=ExtResource("19_bridge")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add water bodies
    for i, (x, y) in enumerate(props['water']):
        content += f'[node name="Water{i+1}" parent="." instance=ExtResource("15_water")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add mountains
    for i, (x, y) in enumerate(props['mountains']):
        content += f'[node name="Mountain{i+1}" parent="." instance=ExtResource("16_mountain")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add cliffs
    for i, (x, y) in enumerate(props['cliffs']):
        content += f'[node name="Cliff{i+1}" parent="." instance=ExtResource("17_cliff")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add flowers
    for i, (x, y) in enumerate(props['flowers']):
        content += f'[node name="Flower{i+1}" parent="." instance=ExtResource("14_flower")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add trees (these will be Y-sorted)
    for i, (x, y) in enumerate(props['trees']):
        content += f'[node name="Tree{i+1}" parent="." instance=ExtResource("10_tree")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add rocks
    for i, (x, y) in enumerate(props['rocks']):
        content += f'[node name="Rock{i+1}" parent="." instance=ExtResource("11_rock")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add bushes
    for i, (x, y) in enumerate(props['bushes']):
        content += f'[node name="Bush{i+1}" parent="." instance=ExtResource("12_bush")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add fences
    for i, (x, y) in enumerate(props['fences']):
        content += f'[node name="Fence{i+1}" parent="." instance=ExtResource("13_fence")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add signposts
    for i, (x, y) in enumerate(props['signposts']):
        content += f'[node name="Signpost{i+1}" parent="." instance=ExtResource("20_signpost")]\n'
        content += f'position = Vector2({int(x)}, {int(y)})\n\n'

    # Add House and core game objects
    content += '''[node name="House" type="Area2D" parent="." groups=["interactable"]]
z_index = 10
position = Vector2(640, 320)
collision_layer = 32

[node name="Sprite" type="ColorRect" parent="House"]
offset_left = -50.0
offset_top = -40.0
offset_right = 50.0
offset_bottom = 40.0
color = Color(0.6, 0.45, 0.35, 1)

[node name="Roof" type="ColorRect" parent="House"]
offset_left = -60.0
offset_top = -55.0
offset_right = 60.0
offset_bottom = -35.0
color = Color(0.5, 0.2, 0.2, 1)

[node name="Door" type="ColorRect" parent="House"]
offset_left = -12.0
offset_top = 15.0
offset_right = 12.0
offset_bottom = 40.0
color = Color(0.4, 0.3, 0.2, 1)

[node name="Window1" type="ColorRect" parent="House"]
offset_left = -40.0
offset_top = -20.0
offset_right = -24.0
offset_bottom = 0.0
color = Color(0.6, 0.8, 0.9, 1)

[node name="Window2" type="ColorRect" parent="House"]
offset_left = 24.0
offset_top = -20.0
offset_right = 40.0
offset_bottom = 0.0
color = Color(0.6, 0.8, 0.9, 1)

[node name="Chimney" type="ColorRect" parent="House"]
offset_left = 25.0
offset_top = -70.0
offset_right = 40.0
offset_bottom = -50.0
color = Color(0.45, 0.35, 0.3, 1)

[node name="Label" type="Label" parent="House"]
offset_left = -30.0
offset_top = 45.0
offset_right = 30.0
offset_bottom = 60.0
text = "Home"
horizontal_alignment = 1

[node name="CollisionShape2D" type="CollisionShape2D" parent="House"]
shape = SubResource("RectangleShape2D_house")

[node name="HouseCollision" type="StaticBody2D" parent="House"]
collision_layer = 1
collision_mask = 0

[node name="CollisionShape2D" type="CollisionShape2D" parent="House/HouseCollision"]
shape = SubResource("RectangleShape2D_house")

[node name="Player" type="CharacterBody2D" parent="."]
y_sort_enabled = true
position = Vector2(640, 400)
collision_layer = 2
collision_mask = 1
script = ExtResource("2_player")

[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="Player"]
texture_filter = 1
position = Vector2(0, -16)
sprite_frames = ExtResource("8_player_frames")
animation = &"idle_down"
autoplay = "idle_down"

[node name="CollisionShape2D" type="CollisionShape2D" parent="Player"]
position = Vector2(0, -6)
shape = SubResource("RectangleShape2D_player")

[node name="InteractionArea" type="Area2D" parent="Player"]
position = Vector2(0, -6)
collision_layer = 0
collision_mask = 32

[node name="CollisionShape2D" type="CollisionShape2D" parent="Player/InteractionArea"]
shape = SubResource("CircleShape2D_interaction")

[node name="Camera2D" type="Camera2D" parent="Player"]
limit_left = 0
limit_top = 0
limit_right = 426
limit_bottom = 240

[node name="Charlie" type="CharacterBody2D" parent="."]
y_sort_enabled = true
position = Vector2(670, 415)
collision_layer = 4
collision_mask = 1
script = ExtResource("3_charlie")

[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="Charlie"]
texture_filter = 1
position = Vector2(0, -16)
sprite_frames = ExtResource("7_charlie_frames")
animation = &"idle_down"
autoplay = "idle_down"

[node name="CollisionShape2D" type="CollisionShape2D" parent="Charlie"]
position = Vector2(0, -6)
shape = SubResource("RectangleShape2D_charlie")

[node name="LeashLine" type="Line2D" parent="."]
width = 2.0
default_color = Color(0.4, 0.3, 0.2, 1)

[node name="WildlifeSpawner" type="Node2D" parent="."]
y_sort_enabled = true
script = ExtResource("9_wildlife_spawner")

[node name="AmbientLight" type="CanvasModulate" parent="."]
color = Color(1, 1, 0.95, 1)

[node name="HUD" type="CanvasLayer" parent="."]
script = ExtResource("4_hud")

[node name="MarginContainer" type="MarginContainer" parent="HUD"]
offset_right = 120.0
offset_bottom = 95.0
theme_override_constants/margin_left = 8
theme_override_constants/margin_top = 8

[node name="VBoxContainer" type="VBoxContainer" parent="HUD/MarginContainer"]
layout_mode = 2
theme_override_constants/separation = 2

[node name="BondingLabel" type="Label" parent="HUD/MarginContainer/VBoxContainer"]
layout_mode = 2
theme_override_font_sizes/font_size = 10
text = "Bonding"

[node name="BondingBar" type="ProgressBar" parent="HUD/MarginContainer/VBoxContainer"]
custom_minimum_size = Vector2(100, 8)
layout_mode = 2
value = 0.0
show_percentage = false

[node name="EntertainmentLabel" type="Label" parent="HUD/MarginContainer/VBoxContainer"]
layout_mode = 2
theme_override_font_sizes/font_size = 10
text = "Entertainment"

[node name="EntertainmentBar" type="ProgressBar" parent="HUD/MarginContainer/VBoxContainer"]
custom_minimum_size = Vector2(100, 8)
layout_mode = 2
value = 0.0
show_percentage = false

[node name="TimeLabel" type="Label" parent="HUD/MarginContainer/VBoxContainer"]
layout_mode = 2
theme_override_font_sizes/font_size = 10
text = "8:00 AM"

[node name="WeatherLabel" type="Label" parent="HUD/MarginContainer/VBoxContainer"]
layout_mode = 2
theme_override_font_sizes/font_size = 10
text = "Clear - Spring"

[node name="InteractionPrompt" type="Label" parent="HUD"]
visible = false
anchors_preset = 7
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = -60.0
offset_top = -20.0
offset_right = 60.0
grow_horizontal = 2
grow_vertical = 0
theme_override_font_sizes/font_size = 12
text = "[E] Interact"
horizontal_alignment = 1

[node name="MessagePanel" type="Panel" parent="HUD"]
visible = false
anchors_preset = 5
anchor_left = 0.5
anchor_right = 0.5
offset_left = -100.0
offset_top = 30.0
offset_right = 100.0
offset_bottom = 60.0
grow_horizontal = 2

[node name="MessageLabel" type="Label" parent="HUD/MessagePanel"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
offset_left = 5.0
offset_top = 3.0
offset_right = -5.0
offset_bottom = -3.0
grow_horizontal = 2
grow_vertical = 2
theme_override_font_sizes/font_size = 10
text = "Message"
horizontal_alignment = 1
vertical_alignment = 1
autowrap_mode = 2

[node name="ScreenLabel" type="Label" parent="HUD"]
anchors_preset = 1
anchor_left = 1.0
anchor_right = 1.0
offset_left = -80.0
offset_top = 8.0
offset_right = -8.0
offset_bottom = 24.0
grow_horizontal = 0
theme_override_font_sizes/font_size = 10
text = "Home (1, 1)"
horizontal_alignment = 2
'''

    return content


def main():
    props = generate_props()

    # Count props
    total = sum(len(v) for v in props.values())
    print(f"Generated {total} props:")
    for name, items in props.items():
        if items:
            print(f"  {name}: {len(items)}")

    scene_content = generate_scene(props)

    with open('scenes/Overworld.tscn', 'w') as f:
        f.write(scene_content)

    print(f"\nSaved to scenes/Overworld.tscn")


if __name__ == "__main__":
    main()
