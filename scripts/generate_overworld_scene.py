#!/usr/bin/env python3
"""
Generate Overworld.tscn with painted TileMap data for Charlie's Island Adventure.
Creates a 6x4 grid of screens with different biomes.
"""

import os
import random

# World dimensions
SCREEN_WIDTH = 426
SCREEN_HEIGHT = 240
GRID_COLS = 6
GRID_ROWS = 4
WORLD_WIDTH = SCREEN_WIDTH * GRID_COLS  # 2556
WORLD_HEIGHT = SCREEN_HEIGHT * GRID_ROWS  # 960
TILE_SIZE = 16

# Tile indices from our tileset
TILE_GRASS = 0
TILE_GRASS_LIGHT = 1
TILE_GRASS_DARK = 2
TILE_GRASS_FLOWER_RED = 3
TILE_GRASS_FLOWER_YELLOW = 4
TILE_GRASS_FLOWER_BLUE = 5
TILE_GRASS_FLOWER_WHITE = 6
TILE_DIRT = 16
TILE_DIRT_TOP = 17
TILE_DIRT_BOTTOM = 18
TILE_DIRT_LEFT = 19
TILE_DIRT_RIGHT = 20
TILE_SAND = 32
TILE_SAND_TOP = 33
TILE_WATER = 48
TILE_WATER_DEEP = 52
TILE_WATER_TOP = 56
TILE_WATER_BOTTOM = 57
TILE_WATER_LEFT = 58
TILE_WATER_RIGHT = 59
TILE_CLIFF = 80
TILE_CLIFF_TOP = 81
TILE_BRIDGE_H = 96
TILE_BRIDGE_V = 97

# Biome definitions (row, col) -> biome type
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


def get_biome(screen_x, screen_y):
    """Get biome type for a screen coordinate."""
    if 0 <= screen_y < GRID_ROWS and 0 <= screen_x < GRID_COLS:
        return BIOMES[screen_y][screen_x]
    return "grass"


def generate_tile_layer_data():
    """Generate the tile data for the ground layer."""
    tiles_x = WORLD_WIDTH // TILE_SIZE
    tiles_y = WORLD_HEIGHT // TILE_SIZE

    # Initialize with grass
    tile_data = [[TILE_GRASS for _ in range(tiles_x)] for _ in range(tiles_y)]

    random.seed(42)  # Consistent generation

    for screen_y in range(GRID_ROWS):
        for screen_x in range(GRID_COLS):
            biome = get_biome(screen_x, screen_y)

            # Screen bounds in tiles
            start_tx = (screen_x * SCREEN_WIDTH) // TILE_SIZE
            start_ty = (screen_y * SCREEN_HEIGHT) // TILE_SIZE
            end_tx = ((screen_x + 1) * SCREEN_WIDTH) // TILE_SIZE
            end_ty = ((screen_y + 1) * SCREEN_HEIGHT) // TILE_SIZE

            for ty in range(start_ty, end_ty):
                for tx in range(start_tx, end_tx):
                    tile_data[ty][tx] = get_tile_for_biome(biome, tx, ty, start_tx, start_ty, end_tx, end_ty)

    return tile_data


def get_tile_for_biome(biome, tx, ty, start_tx, start_ty, end_tx, end_ty):
    """Get appropriate tile for a position in a biome."""
    rel_x = tx - start_tx
    rel_y = ty - start_ty
    width = end_tx - start_tx
    height = end_ty - start_ty

    if biome == "beach":
        # Beach: sand on left, grass on right with water edge
        if rel_x < width * 0.4:
            # Water area
            if rel_x < width * 0.2:
                return TILE_WATER_DEEP
            return TILE_WATER
        elif rel_x < width * 0.5:
            return TILE_SAND
        else:
            # Grass with occasional flowers
            if random.random() < 0.05:
                return random.choice([TILE_GRASS_FLOWER_RED, TILE_GRASS_FLOWER_YELLOW])
            return TILE_GRASS

    elif biome == "meadow":
        # Meadow: lots of grass with flowers
        r = random.random()
        if r < 0.08:
            return random.choice([TILE_GRASS_FLOWER_RED, TILE_GRASS_FLOWER_YELLOW,
                                 TILE_GRASS_FLOWER_BLUE, TILE_GRASS_FLOWER_WHITE])
        elif r < 0.15:
            return TILE_GRASS_LIGHT
        elif r < 0.22:
            return TILE_GRASS_DARK
        return TILE_GRASS

    elif biome == "home":
        # Home screen: grass with a path leading to house
        center_x = width // 2
        # Vertical path
        if abs(rel_x - center_x) < 2:
            return TILE_DIRT
        # Some grass variation
        if random.random() < 0.1:
            return random.choice([TILE_GRASS_LIGHT, TILE_GRASS_DARK])
        return TILE_GRASS

    elif biome == "forest":
        # Forest: darker grass
        r = random.random()
        if r < 0.3:
            return TILE_GRASS_DARK
        elif r < 0.4:
            return TILE_GRASS
        elif r < 0.45:
            return TILE_GRASS_LIGHT
        return TILE_GRASS_DARK

    elif biome == "lake":
        # Lake: water in center, grass edges
        center_x = width // 2
        center_y = height // 2
        dist_x = abs(rel_x - center_x) / (width / 2)
        dist_y = abs(rel_y - center_y) / (height / 2)
        dist = (dist_x ** 2 + dist_y ** 2) ** 0.5

        if dist < 0.5:
            return TILE_WATER_DEEP
        elif dist < 0.7:
            return TILE_WATER
        elif dist < 0.85:
            return TILE_SAND
        return TILE_GRASS

    elif biome == "mountain":
        # Mountain: cliff tiles
        return TILE_CLIFF

    elif biome == "cliffs":
        # Cliffs: mix of cliff and grass
        if rel_y < height * 0.6:
            return TILE_CLIFF
        return TILE_GRASS_DARK

    elif biome == "path":
        # Path screen: dirt path through grass
        center_x = width // 2
        if abs(rel_x - center_x) < 3:
            return TILE_DIRT
        if random.random() < 0.1:
            return TILE_GRASS_LIGHT
        return TILE_GRASS

    elif biome == "bridge":
        # Bridge over water
        center_x = width // 2
        if rel_y < height * 0.3 or rel_y > height * 0.7:
            # Water areas
            return TILE_WATER
        elif abs(rel_x - center_x) < 3:
            return TILE_BRIDGE_V
        else:
            return TILE_WATER

    return TILE_GRASS


def tile_data_to_godot_format(tile_data):
    """Convert 2D tile array to Godot TileMap layer_0/tile_data format."""
    # Godot 4 uses PackedInt32Array with encoded coordinates and atlas coords
    # Format: each tile is 3 ints: (encoded_position, source_id, atlas_coords)
    # encoded_position = x + (y * 0x10000) for positive, uses two's complement for negative

    tiles = []
    for y, row in enumerate(tile_data):
        for x, tile_id in enumerate(row):
            if tile_id is not None and tile_id >= 0:
                # Position encoding for TileMap
                # Tile atlas coords: tile_id % 16, tile_id // 16
                atlas_x = tile_id % 16
                atlas_y = tile_id // 16

                # Add tile entry
                tiles.append((x, y, atlas_x, atlas_y))

    return tiles


def generate_collision_layer_data(tile_data):
    """Generate collision data for impassable tiles (water, cliffs)."""
    collision_tiles = []
    impassable = {TILE_WATER, TILE_WATER_DEEP, TILE_CLIFF, TILE_WATER_TOP,
                  TILE_WATER_BOTTOM, TILE_WATER_LEFT, TILE_WATER_RIGHT}

    for y, row in enumerate(tile_data):
        for x, tile_id in enumerate(row):
            if tile_id in impassable:
                collision_tiles.append((x, y))

    return collision_tiles


def generate_scene_file(tile_data):
    """Generate the Overworld.tscn file content."""

    # Tree positions - spread across the world
    tree_positions = [
        # Home screen (1,1)
        (540, 330), (680, 280), (500, 400),
        # Meadow screens
        (500, 100), (600, 150), (700, 80),
        (900, 200), (1000, 150), (1100, 250),
        # Forest screens
        (1400, 100), (1500, 180), (1600, 120), (1700, 200),
        (1450, 300), (1550, 350), (1650, 280), (1750, 380),
        (1400, 500), (1500, 550), (1600, 480),
        (1700, 800), (1750, 850), (1650, 880),
        # Meadow bottom
        (500, 600), (600, 650), (700, 550),
        (550, 750), (650, 800),
    ]

    scene = '''[gd_scene load_steps=56 format=3 uid="uid://overworld"]

[ext_resource type="Script" path="res://scripts/scenes/Overworld.gd" id="1_overworld"]
[ext_resource type="Script" path="res://scripts/player/Player.gd" id="2_player"]
[ext_resource type="Script" path="res://scripts/charlie/Charlie.gd" id="3_charlie"]
[ext_resource type="Script" path="res://scripts/ui/HUD.gd" id="4_hud"]
[ext_resource type="Script" path="res://scripts/wildlife/WildlifeSpawner.gd" id="9_wildlife_spawner"]
[ext_resource type="Texture2D" path="res://assets/sprites/characters/player_spritesheet.png" id="5_player_sprite"]
[ext_resource type="Texture2D" path="res://assets/sprites/characters/charlie_spritesheet.png" id="6_charlie_sprite"]
[ext_resource type="SpriteFrames" path="res://assets/sprites/characters/charlie_sprite_frames.tres" id="7_charlie_frames"]
[ext_resource type="SpriteFrames" path="res://resources/sprites/player_frames.tres" id="8_player_frames"]
[ext_resource type="PackedScene" path="res://scenes/props/Tree.tscn" id="10_tree"]
[ext_resource type="Texture2D" path="res://assets/sprites/tiles/terrain_atlas.png" id="11_terrain"]

[sub_resource type="TileSet" id="TileSet_terrain"]
tile_size = Vector2i(16, 16)
physics_layer_0/collision_layer = 1
physics_layer_0/collision_mask = 0

[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_terrain"]
texture = ExtResource("11_terrain")
texture_region_size = Vector2i(16, 16)

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
animations = [{{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_down")
}}],
"loop": true,
"name": &"idle_down",
"speed": 5.0
}}, {{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_left")
}}],
"loop": true,
"name": &"idle_left",
"speed": 5.0
}}, {{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_right")
}}],
"loop": true,
"name": &"idle_right",
"speed": 5.0
}}, {{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_idle_up")
}}],
"loop": true,
"name": &"idle_up",
"speed": 5.0
}}, {{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_1")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_2")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_3")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_down_2")
}}],
"loop": true,
"name": &"walk_down",
"speed": 10.0
}}, {{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_1")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_2")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_3")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_left_2")
}}],
"loop": true,
"name": &"walk_left",
"speed": 10.0
}}, {{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_1")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_2")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_3")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_right_2")
}}],
"loop": true,
"name": &"walk_right",
"speed": 10.0
}}, {{
"frames": [{{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_1")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_2")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_3")
}}, {{
"duration": 1.0,
"texture": SubResource("AtlasTexture_charlie_walk_up_2")
}}],
"loop": true,
"name": &"walk_up",
"speed": 10.0
}}]

[node name="Overworld" type="Node2D"]
y_sort_enabled = true
script = ExtResource("1_overworld")

[node name="TerrainTileMap" type="TileMap" parent="."]
z_index = -1
tile_set = SubResource("TileSet_terrain")
format = 2

'''

    # Add tree instances
    for i, (x, y) in enumerate(tree_positions):
        scene += f'''
[node name="Tree{i+1}" parent="." instance=ExtResource("10_tree")]
position = Vector2({x}, {y})
'''

    # Add House and rest of scene
    scene += '''
[node name="House" type="Area2D" parent="." groups=["interactable"]]
y_sort_enabled = true
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

[node name="Label" type="Label" parent="House"]
offset_left = -30.0
offset_top = 45.0
offset_right = 30.0
offset_bottom = 60.0
text = "House"
horizontal_alignment = 1

[node name="CollisionShape2D" type="CollisionShape2D" parent="House"]
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
text = "Screen: (1, 1)"
horizontal_alignment = 2
'''

    return scene


def main():
    tile_data = generate_tile_layer_data()
    scene_content = generate_scene_file(tile_data)

    output_path = "scenes/Overworld.tscn"
    with open(output_path, 'w') as f:
        f.write(scene_content)

    print(f"Generated: {output_path}")
    print(f"World size: {WORLD_WIDTH}x{WORLD_HEIGHT} pixels")
    print(f"Grid: {GRID_COLS}x{GRID_ROWS} screens")


if __name__ == "__main__":
    main()
