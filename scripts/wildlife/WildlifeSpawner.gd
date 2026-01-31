extends Node2D
class_name WildlifeSpawner
## WildlifeSpawner - Manages spawning of wildlife in the Overworld

const Butterfly = preload("res://scripts/wildlife/Butterfly.gd")
const Bird = preload("res://scripts/wildlife/Bird.gd")
const Squirrel = preload("res://scripts/wildlife/Squirrel.gd")

@export var max_wildlife: int = 4
@export var spawn_interval_min: float = 8.0
@export var spawn_interval_max: float = 15.0

# Spawn weights (higher = more likely)
var spawn_weights = {
	"butterfly": 5,
	"bird": 3,
	"squirrel": 2
}

# Spawn area bounds
var spawn_min: Vector2 = Vector2(50, 150)
var spawn_max: Vector2 = Vector2(800, 430)

# References
var charlie_ref: Node2D = null
var player_ref: Node2D = null

# State
var spawn_timer: float = 5.0  # Initial delay before first spawn
var active_wildlife: Array = []

func _ready() -> void:
	add_to_group("wildlife_spawner")

func _process(delta: float) -> void:
	spawn_timer -= delta

	if spawn_timer <= 0:
		_try_spawn_wildlife()
		spawn_timer = randf_range(spawn_interval_min, spawn_interval_max)

		# Adjust spawn rate based on weather/time
		spawn_timer *= _get_spawn_modifier()

func _try_spawn_wildlife() -> void:
	# Clean up dead references
	active_wildlife = active_wildlife.filter(func(w): return is_instance_valid(w))

	# Check max wildlife limit
	if active_wildlife.size() >= max_wildlife:
		return

	# Check weather/time conditions
	if not _should_spawn():
		return

	# Pick random wildlife type based on weights
	var wildlife_type = _pick_weighted_type()

	# Pick spawn position away from player
	var spawn_pos = _get_spawn_position(wildlife_type)
	if spawn_pos == Vector2.ZERO:
		return

	# Spawn the wildlife
	var wildlife = _create_wildlife(wildlife_type)
	if wildlife:
		wildlife.global_position = spawn_pos
		wildlife.set_charlie(charlie_ref)
		wildlife.wildlife_fled.connect(_on_wildlife_fled)
		wildlife.wildlife_despawned.connect(_on_wildlife_despawned)
		add_child(wildlife)
		active_wildlife.append(wildlife)

func _should_spawn() -> bool:
	# Less wildlife at night
	if not TimeWeather.is_daytime():
		if randf() > 0.3:  # 70% chance to skip spawn at night
			return false

	# Less wildlife in rain/storm
	if TimeWeather.is_raining():
		if randf() > 0.4:  # 60% chance to skip spawn in rain
			return false

	# No wildlife in snow
	if TimeWeather.is_snowing():
		if randf() > 0.2:  # 80% chance to skip spawn in snow
			return false

	return true

func _get_spawn_modifier() -> float:
	var modifier = 1.0

	# Slower spawns at night
	if not TimeWeather.is_daytime():
		modifier *= 1.5

	# Slower spawns in bad weather
	if TimeWeather.is_raining():
		modifier *= 1.3

	if TimeWeather.is_snowing():
		modifier *= 2.0

	return modifier

func _pick_weighted_type() -> String:
	var total_weight = 0
	for weight in spawn_weights.values():
		total_weight += weight

	var roll = randi() % total_weight
	var current = 0

	for type in spawn_weights:
		current += spawn_weights[type]
		if roll < current:
			return type

	return "butterfly"  # Fallback

func _get_spawn_position(type: String = "") -> Vector2:
	# If it's a squirrel, try to spawn near a tree
	if type == "squirrel":
		var trees = get_tree().get_nodes_in_group("trees")
		if trees.size() > 0:
			var tree = trees[randi() % trees.size()]
			# Spawn in a small radius around the tree
			var angle = randf() * PI * 2
			var dist = randf_range(20, 50)
			var pos = tree.global_position + Vector2(cos(angle), sin(angle)) * dist
			
			# Ensure it's within bounds
			pos.x = clampf(pos.x, spawn_min.x, spawn_max.x)
			pos.y = clampf(pos.y, spawn_min.y, spawn_max.y)
			return pos

	# Try to find a valid spawn position away from player
	for _attempt in range(10):
		var pos = Vector2(
			randf_range(spawn_min.x, spawn_max.x),
			randf_range(spawn_min.y, spawn_max.y)
		)

		# Check distance from player
		if player_ref:
			var dist_to_player = pos.distance_to(player_ref.global_position)
			if dist_to_player < 150:  # Too close to player
				continue

		# Check distance from Charlie
		if charlie_ref:
			var dist_to_charlie = pos.distance_to(charlie_ref.global_position)
			if dist_to_charlie < 100:  # Too close to Charlie
				continue

		return pos

	return Vector2.ZERO  # Failed to find valid position

func _create_wildlife(wildlife_type: String) -> Node2D:
	var wildlife: CharacterBody2D = null

	match wildlife_type:
		"butterfly":
			wildlife = CharacterBody2D.new()
			wildlife.set_script(Butterfly)
		"bird":
			wildlife = CharacterBody2D.new()
			wildlife.set_script(Bird)
		"squirrel":
			wildlife = CharacterBody2D.new()
			wildlife.set_script(Squirrel)

	return wildlife

func _on_wildlife_fled(wildlife: Wildlife) -> void:
	pass  # Entertainment already added in Wildlife.gd

func _on_wildlife_despawned(wildlife: Wildlife) -> void:
	active_wildlife.erase(wildlife)

func set_charlie(charlie: Node2D) -> void:
	charlie_ref = charlie

func set_player(player: Node2D) -> void:
	player_ref = player

func get_active_wildlife_count() -> int:
	active_wildlife = active_wildlife.filter(func(w): return is_instance_valid(w))
	return active_wildlife.size()

func get_nearest_wildlife_to(pos: Vector2) -> Node2D:
	active_wildlife = active_wildlife.filter(func(w): return is_instance_valid(w))

	var nearest: Node2D = null
	var nearest_dist: float = INF

	for wildlife in active_wildlife:
		if not is_instance_valid(wildlife):
			continue
		if wildlife.current_state == Wildlife.State.FLEEING:
			continue
		if wildlife.current_state == Wildlife.State.DESPAWNING:
			continue

		var dist = pos.distance_to(wildlife.global_position)
		if dist < nearest_dist:
			nearest = wildlife
			nearest_dist = dist

	return nearest
