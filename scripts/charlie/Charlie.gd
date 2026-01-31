extends CharacterBody2D
class_name Charlie
## Charlie - The baby Shih Tzu companion

@export var speed: float = 60.0
@export var follow_distance: float = 30.0  # How close to stay to player
@export var leash_max_distance: float = 96.0  # Max distance when on leash (3 Charlie lengths)

# References
var animated_sprite: AnimatedSprite2D = null

# State
enum State { IDLE, FOLLOWING, WANDERING, FETCHING, KEEP_AWAY, ON_LEASH, HELD, PEEING, SNIFFARI }
var current_state: State = State.IDLE

# Tree interest
var target_tree: Node2D = null
var pee_timer: float = 0.0
var bored_timer: float = 0.0
var pee_particles: CPUParticles2D = null

# Sniffari behavior
var sniffari_timer: float = 0.0
var sniffari_reward_timer: float = 0.0
var sniffari_interest_timer: float = 0.0
var sniffari_target_node: Node2D = null
var is_in_sniffari: bool = false # Internal flag to track Sniffari session

var is_on_leash: bool = false
var target_position: Vector2 = Vector2.ZERO
var player_ref: Node2D = null

# Fetch game
var ball_ref: Node2D = null
var has_ball: bool = false
var returning_ball: bool = false

# Keep-away behavior
var keep_away_timer: float = 0.0
var flee_direction: Vector2 = Vector2.ZERO

# Wander behavior
var wander_timer: float = 0.0
var wander_direction: Vector2 = Vector2.ZERO

# Leash resistance (for slowing player)
var is_resisting: bool = false
var resistance_amount: float = 0.0  # 0.0 to 1.0, how much Charlie is resisting
var leash_wander_timer: float = 0.0
var leash_wander_direction: Vector2 = Vector2.ZERO

# Wildlife attraction
var attracted_to_wildlife: Node2D = null
var wildlife_excitement: float = 0.0  # 0.0 to 1.0
var wildlife_attraction_radius: float = 120.0
var wildlife_spawner_ref: Node = null

# Animation
var facing_direction: String = "down"

# Obstacle avoidance
var stuck_timer: float = 0.0
var last_position: Vector2 = Vector2.ZERO
var avoidance_direction: Vector2 = Vector2.ZERO
var is_avoiding: bool = false

# Furniture collision rects for pathfinding
var furniture_rects: Array = [
	Rect2(5, 0, 115, 55),     # Kitchen counter area
	Rect2(128, 130, 24, 20),  # Chair1
	Rect2(248, 130, 24, 20),  # Chair2
	Rect2(188, 90, 24, 20),   # Chair3
	Rect2(188, 170, 24, 20),  # Chair4
	Rect2(155, 115, 90, 50),  # Table
	Rect2(350, 115, 60, 70),  # Sofa
]

signal reached_player
signal picked_up_ball
signal charlie_interacted
signal sniffari_finished

func _ready() -> void:
	add_to_group("charlie")
	add_to_group("interactable")
	_setup_animated_sprite()
	_setup_pee_particles()

func _setup_pee_particles() -> void:
	pee_particles = CPUParticles2D.new()
	pee_particles.name = "PeeParticles"
	pee_particles.emitting = false
	pee_particles.amount = 5
	pee_particles.lifetime = 0.4
	pee_particles.one_shot = false
	pee_particles.explosiveness = 0.0
	pee_particles.randomness = 0.2
	pee_particles.direction = Vector2(1, 0.2)
	pee_particles.spread = 8.0
	pee_particles.gravity = Vector2(0, 160)
	pee_particles.initial_velocity_min = 25.0
	pee_particles.initial_velocity_max = 40.0
	pee_particles.scale_amount_min = 0.8
	pee_particles.scale_amount_max = 1.2
	pee_particles.color = Color(1.0, 1.0, 0.0, 0.7)
	add_child(pee_particles)
	pee_particles.position = Vector2(0, -2)

func _setup_animated_sprite() -> void:
	animated_sprite = get_node_or_null("AnimatedSprite2D")
	if animated_sprite == null:
		animated_sprite = AnimatedSprite2D.new()
		animated_sprite.name = "AnimatedSprite2D"
		animated_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		animated_sprite.scale = Vector2(0.25, 0.25)
		add_child(animated_sprite)
		for child in get_children():
			if child is ColorRect: child.queue_free()
	else:
		animated_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	
	if animated_sprite.sprite_frames == null:
		push_warning("Charlie: AnimatedSprite2D has no SpriteFrames assigned!")
	else:
		animated_sprite.play("idle_down")

func _physics_process(delta: float) -> void:
	# Always process Sniffari timers if active, even if in PEEING sub-state
	if is_in_sniffari:
		_update_sniffari_timers(delta)

	match current_state:
		State.IDLE: _process_idle(delta)
		State.FOLLOWING: _process_following(delta)
		State.WANDERING: _process_wandering(delta)
		State.FETCHING: _process_fetching(delta)
		State.KEEP_AWAY: _process_keep_away(delta)
		State.ON_LEASH: _process_on_leash(delta)
		State.HELD: _process_held(delta)
		State.PEEING: _process_peeing(delta)
		State.SNIFFARI: _process_sniffari(delta)

	move_and_slide()
	_update_animation()

func _process_idle(delta: float) -> void:
	velocity = Vector2.ZERO
	_check_for_boredom(delta)

func _check_for_boredom(delta: float) -> void:
	bored_timer += delta
	if bored_timer > 5.0:
		if is_on_leash and GameState.bonding > 0.7:
			if randf() > 0.2:
				bored_timer = 0.0
				return
		_find_interesting_tree()

func _find_interesting_tree() -> void:
	var trees = get_tree().get_nodes_in_group("trees")
	if trees.size() == 0: return
	
	var current_total_hours = GameState.current_day * 24.0 + GameState.current_hour
	var nearest_tree = null
	var min_dist = 120.0
	if is_on_leash: min_dist = leash_max_distance * 1.2
	
	for tree in trees:
		if tree.get("last_peed_time") != null:
			if current_total_hours - tree.last_peed_time < 4.0:
				continue
		var dist = global_position.distance_to(tree.global_position)
		if dist < min_dist:
			min_dist = dist
			nearest_tree = tree
	
	if nearest_tree:
		target_tree = nearest_tree
		target_position = target_tree.get_pee_position() if target_tree.has_method("get_pee_position") else target_tree.global_position
		bored_timer = 0.0

func _process_peeing(delta: float) -> void:
	velocity = Vector2.ZERO
	pee_timer -= delta
	is_resisting = true
	resistance_amount = 1.0
	
	if pee_timer <= 0:
		_finish_peeing()

func _start_peeing() -> void:
	current_state = State.PEEING
	pee_timer = randf_range(6.0, 8.0)
	is_resisting = true
	resistance_amount = 1.0
	
	var dir_to_tree = Vector2.LEFT
	if target_tree and is_instance_valid(target_tree):
		dir_to_tree = (target_tree.global_position - global_position).normalized()
	
	if abs(dir_to_tree.x) > abs(dir_to_tree.y):
		facing_direction = "right" if dir_to_tree.x > 0 else "left"
	else:
		facing_direction = "down" if dir_to_tree.y > 0 else "up"
	
	if animated_sprite: animated_sprite.play("idle_" + facing_direction)
	
	if pee_particles: 
		pee_particles.direction = dir_to_tree + Vector2(0, -0.1)
		# Origin: ~10px up from feet (body center) 
		# and offset BACKWARDS from the tree direction to come from his rear
		pee_particles.position = Vector2(0, -10) - (dir_to_tree * 4.0)
		pee_particles.emitting = true

func _cancel_peeing() -> void:
	if current_state != State.PEEING: return
	if pee_particles: pee_particles.emitting = false
	
	var puddle_script = load("res://scripts/props/Puddle.gd")
	if puddle_script:
		var puddle = Node2D.new()
		puddle.set_script(puddle_script)
		get_parent().add_child(puddle)
		puddle.global_position = global_position + Vector2(0, 2)
		puddle.scale = Vector2(0.6, 0.6)
	
	target_tree = null
	target_position = Vector2.ZERO

func _finish_peeing() -> void:
	if pee_particles: pee_particles.emitting = false
	var puddle_script = load("res://scripts/props/Puddle.gd")
	if puddle_script:
		var puddle = Node2D.new()
		puddle.set_script(puddle_script)
		get_parent().add_child(puddle)
		puddle.global_position = global_position + Vector2(0, 2)
	
	if target_tree and is_instance_valid(target_tree):
		if target_tree.has_method("mark_as_peed_on"):
			target_tree.mark_as_peed_on()
		target_tree.set("last_peed_time", GameState.current_day * 24.0 + GameState.current_hour)
	
	target_tree = null
	target_position = Vector2.ZERO
	
	# Transition back correctly: check if we are in Sniffari
	if is_in_sniffari:
		current_state = State.SNIFFARI
	else:
		current_state = State.ON_LEASH if is_on_leash else State.IDLE
		if current_state == State.IDLE: bored_timer = 0.0

func _process_on_leash(delta: float) -> void:
	if not player_ref: return
	var distance_to_player = global_position.distance_to(player_ref.global_position)
	var direction_to_player = (player_ref.global_position - global_position).normalized()
	var leash_tension = distance_to_player / leash_max_distance
	var player_velocity = Vector2.ZERO
	if player_ref is CharacterBody2D: player_velocity = player_ref.velocity

	is_resisting = false
	resistance_amount = 0.0
	_check_for_boredom(delta)

	var distraction_factor = wildlife_excitement * (1.0 - GameState.bonding * 0.7)
	var tree_dir = Vector2.ZERO
	if target_tree and is_instance_valid(target_tree):
		tree_dir = (target_position - global_position).normalized()
		distraction_factor = max(distraction_factor, 0.8 * (1.0 - GameState.bonding * 0.5))

	if GameState.bonding >= 0.5:
		var target = player_ref.global_position + Vector2(20, 20)
		var target_dir = (target - global_position).normalized()
		if distraction_factor > 0.2:
			var interest_dir = tree_dir if tree_dir != Vector2.ZERO else (attracted_to_wildlife.global_position - global_position).normalized() if attracted_to_wildlife else Vector2.ZERO
			if interest_dir != Vector2.ZERO:
				var blended_dir = (target_dir * (1.0 - distraction_factor) + interest_dir * distraction_factor).normalized()
				velocity = blended_dir * speed * (1.0 + distraction_factor * 0.5)
			else: velocity = target_dir * speed
		else:
			if global_position.distance_to(target) > 5: velocity = target_dir * speed
			else: velocity = Vector2.ZERO
	else:
		var interest_dir = tree_dir if tree_dir != Vector2.ZERO else (attracted_to_wildlife.global_position - global_position).normalized() if attracted_to_wildlife else Vector2.ZERO
		if interest_dir != Vector2.ZERO and distraction_factor > 0.1:
			var chase_speed = speed * (1.0 + distraction_factor * 0.5)
			if distance_to_player >= leash_max_distance:
				var chase_factor = 0.4 * distraction_factor
				velocity = (interest_dir * chase_factor + direction_to_player * (1.0 - chase_factor)).normalized() * speed * 0.4
			elif leash_tension > 0.7:
				var tension_blend = (leash_tension - 0.7) / 0.3
				velocity = (interest_dir * chase_speed).lerp(direction_to_player * speed * 0.3, tension_blend * 0.6)
			else: velocity = interest_dir * chase_speed
		else:
			leash_wander_timer -= delta
			if leash_wander_timer <= 0:
				leash_wander_direction = Vector2.ZERO if randf() < 0.3 else Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
				leash_wander_timer = randf_range(1.0, 3.0)
			if distance_to_player >= leash_max_distance: velocity = direction_to_player * speed * 0.5
			elif leash_tension > 0.7:
				var wander_factor = 1.0 - ((leash_tension - 0.7) / 0.3)
				velocity = leash_wander_direction * speed * 0.4 * wander_factor + direction_to_player * speed * 0.3 * (1.0 - wander_factor)
			else: velocity = leash_wander_direction * speed * 0.5

	if target_tree and is_instance_valid(target_tree):
		var dist_to_target = global_position.distance_to(target_position)
		if dist_to_target < 15.0 or (leash_tension > 0.9 and dist_to_target < 30.0):
			_start_peeing()

	if leash_tension >= 0.7 and player_velocity.length() > 5:
		var moving_away_factor = player_velocity.normalized().dot(direction_to_player)
		if moving_away_factor > 0.2:
			var tension_factor = clampf((leash_tension - 0.7) / 0.3, 0.0, 1.0)
			resistance_amount = tension_factor * moving_away_factor
			if distraction_factor > 0.1:
				var wildlife_resistance = distraction_factor * 0.5
				if GameState.bonding < 0.5: wildlife_resistance *= (1.5 - GameState.bonding)
				resistance_amount += wildlife_resistance
			resistance_amount = clampf(resistance_amount, 0.0, 1.0)
			is_resisting = resistance_amount > 0.1
			if distance_to_player >= leash_max_distance * 0.95:
				velocity = direction_to_player * speed * 0.3 * tension_factor
				resistance_amount = 1.0
				is_resisting = true

func start_sniffari() -> void:
	if current_state == State.PEEING: _cancel_peeing()
	current_state = State.SNIFFARI
	is_in_sniffari = true
	sniffari_timer = 50.0
	sniffari_reward_timer = 10.0
	sniffari_interest_timer = 0.0
	sniffari_target_node = null
	target_position = Vector2.ZERO
	print("Sniffari started!")

func _update_sniffari_timers(delta: float) -> void:
	sniffari_timer -= delta
	sniffari_reward_timer -= delta
	
	if sniffari_reward_timer <= 0:
		GameState.add_bonding(0.2)
		sniffari_reward_timer = 10.0
		print("Sniffari bonding reward +20%")
		
	if sniffari_timer <= 0:
		_finish_sniffari()

func _process_sniffari(delta: float) -> void:
	# Timers now updated in _physics_process via _update_sniffari_timers
	if not is_in_sniffari: return
		
	sniffari_interest_timer -= delta
	if sniffari_interest_timer <= 0:
		_pick_sniffari_interest()
		
	if target_position != Vector2.ZERO:
		var dist = global_position.distance_to(target_position)
		if dist > 15.0:
			velocity = (target_position - global_position).normalized() * speed * 0.8
		else:
			velocity = Vector2.ZERO
			if sniffari_target_node and is_instance_valid(sniffari_target_node):
				if sniffari_target_node.is_in_group("trees") and randf() < 0.4:
					target_tree = sniffari_target_node
					_start_peeing()
					return
			if animated_sprite: animated_sprite.play("idle_down")
	else:
		velocity = Vector2.ZERO

func _pick_sniffari_interest() -> void:
	var roll = randf()
	if roll < 0.5: # Go to tree
		var trees = get_tree().get_nodes_in_group("trees")
		if trees.size() > 0:
			sniffari_target_node = trees[randi() % trees.size()]
			target_position = sniffari_target_node.get_pee_position() if sniffari_target_node.has_method("get_pee_position") else sniffari_target_node.global_position
	elif roll < 0.8: # Chase wildlife
		if wildlife_spawner_ref:
			sniffari_target_node = wildlife_spawner_ref.get_nearest_wildlife_to(global_position)
			if sniffari_target_node:
				target_position = sniffari_target_node.global_position
	else: # Just sniff grass nearby
		target_position = global_position + Vector2(randf_range(-80, 80), randf_range(-80, 80))
		sniffari_target_node = null
		
	sniffari_interest_timer = randf_range(4.0, 10.0)

func _finish_sniffari() -> void:
	is_in_sniffari = false
	if current_state == State.SNIFFARI:
		current_state = State.ON_LEASH if is_on_leash else State.IDLE
	emit_signal("sniffari_finished")
	print("Sniffari finished!")

func _process_held(delta: float) -> void:
	velocity = Vector2.ZERO
	if GameState.bonding >= 0.5: return
	if not wildlife_spawner_ref or not wildlife_spawner_ref.has_method("get_nearest_wildlife_to"): return
	if not player_ref: return
	var nearest = wildlife_spawner_ref.get_nearest_wildlife_to(player_ref.global_position)
	if not nearest or not is_instance_valid(nearest): return
	var dist = player_ref.global_position.distance_to(nearest.global_position)
	if dist < wildlife_attraction_radius:
		var escape_chance = (0.5 - GameState.bonding) * 0.06
		if randf() < escape_chance: _jump_out_and_chase(nearest)

func _process_following(delta: float) -> void:
	if not player_ref: return
	var target = target_position if target_position != Vector2.ZERO else player_ref.global_position
	var distance_to_target = global_position.distance_to(target)
	if distance_to_target > follow_distance:
		var direction = (target - global_position).normalized()
		if global_position.distance_to(last_position) < 1.0: stuck_timer += delta
		else:
			stuck_timer = 0.0
			is_avoiding = false
		last_position = global_position
		if stuck_timer > 0.3:
			direction = _get_avoidance_direction(target, delta)
			is_avoiding = true
		if not is_avoiding: direction = _steer_around_obstacles(direction, delta)
		velocity = direction * speed
	else:
		velocity = Vector2.ZERO
		target_position = Vector2.ZERO
		stuck_timer = 0.0
		is_avoiding = false
		emit_signal("reached_player")

func _get_avoidance_direction(target: Vector2, delta: float) -> Vector2:
	var direct = (target - global_position).normalized()
	var perp_left = Vector2(-direct.y, direct.x)
	var perp_right = Vector2(direct.y, -direct.x)
	var left_clear = _is_direction_clear(perp_left, 40.0)
	var right_clear = _is_direction_clear(perp_right, 40.0)
	if left_clear and not right_clear: avoidance_direction = perp_left
	elif right_clear and not left_clear: avoidance_direction = perp_right
	elif left_clear and right_clear:
		var left_pos = global_position + perp_left * 40
		var right_pos = global_position + perp_right * 40
		avoidance_direction = perp_left if left_pos.distance_to(target) < right_pos.distance_to(target) else perp_right
	else: avoidance_direction = -direct
	return (avoidance_direction * 0.8 + direct * 0.2).normalized()

func _steer_around_obstacles(direction: Vector2, delta: float) -> Vector2:
	var look_ahead = 30.0
	var future_pos = global_position + direction * look_ahead
	var charlie_rect = Rect2(future_pos.x - 10, future_pos.y - 6, 20, 12)
	for furn_rect in furniture_rects:
		if charlie_rect.intersects(furn_rect):
			var center = furn_rect.get_center()
			var to_obstacle = center - global_position
			var perp = Vector2(-to_obstacle.y, to_obstacle.x).normalized()
			if perp.dot(direction) < 0: perp = -perp
			return (direction * 0.4 + perp * 0.6).normalized()
	return direction

func _is_direction_clear(direction: Vector2, distance: float) -> bool:
	var future_pos = global_position + direction * distance
	var charlie_rect = Rect2(future_pos.x - 10, future_pos.y - 6, 20, 12)
	for furn_rect in furniture_rects:
		if charlie_rect.intersects(furn_rect): return false
	return true

func _process_wandering(delta: float) -> void:
	if target_tree and target_position != Vector2.ZERO:
		var dist = global_position.distance_to(target_position)
		if dist < 15.0:
			_start_peeing()
			return
		else:
			velocity = (target_position - global_position).normalized() * speed * 0.7
			_update_animation()
			return
	wander_timer -= delta
	if wander_timer <= 0:
		wander_direction = Vector2.ZERO if randf() < 0.3 else Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
		wander_timer = randf_range(1.0, 3.0)
	if is_on_leash and player_ref:
		var distance_to_player = global_position.distance_to(player_ref.global_position)
		if distance_to_player > leash_max_distance * 0.8:
			wander_direction = (player_ref.global_position - global_position).normalized()
	velocity = wander_direction * speed * 0.5
	_check_for_boredom(delta)

func _process_fetching(delta: float) -> void:
	if not ball_ref:
		current_state = State.IDLE
		return
	if not has_ball:
		var distance_to_ball = global_position.distance_to(ball_ref.global_position)
		if distance_to_ball > 10:
			var direction = (ball_ref.global_position - global_position).normalized()
			if global_position.distance_to(last_position) < 1.0: stuck_timer += delta
			else:
				stuck_timer = 0.0
				is_avoiding = false
			last_position = global_position
			if stuck_timer > 0.3:
				direction = _get_avoidance_direction(ball_ref.global_position, delta)
				is_avoiding = true
			elif not is_avoiding: direction = _steer_around_obstacles(direction, delta)
			velocity = direction * speed * 1.2
		else:
			has_ball = true
			ball_ref.visible = false
			stuck_timer = 0.0
			is_avoiding = false
			emit_signal("picked_up_ball")
			if GameState.charlie_returns_ball: returning_ball = true
			else:
				current_state = State.KEEP_AWAY
				keep_away_timer = randf_range(5.0, 10.0)
				velocity = Vector2.ZERO
	elif returning_ball and player_ref:
		var distance_to_player = global_position.distance_to(player_ref.global_position)
		if distance_to_player > follow_distance:
			var direction = (player_ref.global_position - global_position).normalized()
			if global_position.distance_to(last_position) < 1.0: stuck_timer += delta
			else:
				stuck_timer = 0.0
				is_avoiding = false
			last_position = global_position
			if stuck_timer > 0.3:
				direction = _get_avoidance_direction(player_ref.global_position, delta)
				is_avoiding = true
			elif not is_avoiding: direction = _steer_around_obstacles(direction, delta)
			velocity = direction * speed
		else:
			velocity = Vector2.ZERO
			current_state = State.IDLE
			returning_ball = false
			stuck_timer = 0.0
			is_avoiding = false
	else: velocity = Vector2.ZERO

func _process_keep_away(delta: float) -> void:
	if not player_ref or not has_ball:
		current_state = State.WANDERING
		return
	keep_away_timer -= delta
	var distance_to_player = global_position.distance_to(player_ref.global_position)
	var player_velocity = Vector2.ZERO
	if player_ref is CharacterBody2D: player_velocity = player_ref.velocity
	var player_predicted_pos = player_ref.global_position + player_velocity * 0.5
	if distance_to_player < 70:
		flee_direction = (global_position - player_predicted_pos).normalized()
		var zigzag = sin(Time.get_ticks_msec() * 0.008) * 0.6
		flee_direction = flee_direction.rotated(zigzag)
		var speed_mult = 1.6
		if randf() < 0.05: speed_mult = 2.2
		velocity = flee_direction * speed * speed_mult
		var new_pos = global_position + velocity * delta
		var wall_avoid = Vector2.ZERO
		if new_pos.x < 45: wall_avoid.x = 1.0
		elif new_pos.x > 380: wall_avoid.x = -1.0
		if new_pos.y < 45: wall_avoid.y = 1.0
		elif new_pos.y > 200: wall_avoid.y = -1.0
		if wall_avoid != Vector2.ZERO:
			var perpendicular = Vector2(-flee_direction.y, flee_direction.x)
			if randf() > 0.5: perpendicular = -perpendicular
			flee_direction = (flee_direction + perpendicular).normalized()
		velocity = flee_direction * speed * speed_mult
	elif distance_to_player < 120:
		flee_direction = (global_position - player_ref.global_position).normalized()
		if randf() < 0.1:
			var perpendicular = Vector2(-flee_direction.y, flee_direction.x)
			flee_direction = (flee_direction * 0.3 + perpendicular * 0.7).normalized()
		velocity = flee_direction * speed * 1.0
	else:
		if keep_away_timer < 2.0:
			velocity = velocity.lerp(Vector2.ZERO, 0.2)
			if randf() < 0.03:
				flee_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
				velocity = flee_direction * speed * 0.5
		else:
			if randf() < 0.03: flee_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
			velocity = flee_direction * speed * 0.35
	if keep_away_timer <= 0: keep_away_timer = randf_range(2.5, 5.0)

func _check_wildlife_attraction(delta: float) -> void:
	attracted_to_wildlife = null
	if wildlife_spawner_ref and wildlife_spawner_ref.has_method("get_nearest_wildlife_to"):
		var nearest = wildlife_spawner_ref.get_nearest_wildlife_to(global_position)
		if nearest and is_instance_valid(nearest):
			var dist = global_position.distance_to(nearest.global_position)
			if dist < wildlife_attraction_radius: attracted_to_wildlife = nearest
	if attracted_to_wildlife:
		var distance = global_position.distance_to(attracted_to_wildlife.global_position)
		var closeness = 1.0 - (distance / wildlife_attraction_radius)
		wildlife_excitement = lerpf(wildlife_excitement, closeness, delta * 3.0)
	else: wildlife_excitement = lerpf(wildlife_excitement, 0.0, delta * 2.0)

func set_wildlife_spawner(spawner: Node) -> void: wildlife_spawner_ref = spawner
func get_wildlife_excitement() -> float: return wildlife_excitement

func _update_animation() -> void:
	if not animated_sprite or not animated_sprite.sprite_frames: return
	var anim_name: String = ""
	var is_moving: bool = velocity.length() >= 5
	if is_moving:
		if abs(velocity.x) > abs(velocity.y): facing_direction = "right" if velocity.x > 0 else "left"
		else: facing_direction = "down" if velocity.y > 0 else "up"
	var action: String = "walk" if is_moving else "idle"
	anim_name = action + "_" + facing_direction
	if has_ball:
		var ball_anim: String = anim_name + "_ball"
		if animated_sprite.sprite_frames.has_animation(ball_anim): anim_name = ball_anim
		elif facing_direction == "up": anim_name = action + "_down_ball"
	if animated_sprite.sprite_frames.has_animation(anim_name):
		if animated_sprite.animation != anim_name: animated_sprite.play(anim_name)
	else:
		if animated_sprite.animation != "idle_down": animated_sprite.play("idle_down")

func set_player(player: Node2D) -> void: player_ref = player
func start_following() -> void: current_state = State.FOLLOWING
func start_wandering() -> void: current_state = State.WANDERING; wander_timer = 0.0
func stop_moving() -> void: current_state = State.IDLE; velocity = Vector2.ZERO
func fetch_ball(ball: Node2D) -> void: 
	if current_state == State.PEEING: _cancel_peeing()
	ball_ref = ball; has_ball = false; returning_ball = false; current_state = State.FETCHING
func equip_leash() -> void: is_on_leash = true; current_state = State.ON_LEASH
func remove_leash() -> void: is_on_leash = false; is_resisting = false; resistance_amount = 0.0; current_state = State.FOLLOWING
func is_leash_resisting() -> bool: return is_on_leash and is_resisting
func get_leash_resistance() -> float: return resistance_amount if is_on_leash else 0.0
func take_ball_from_charlie() -> bool: 
	if has_ball: has_ball = false; return true
	return false
func interact(player: Node2D) -> void:
	emit_signal("charlie_interacted")
	if has_ball: take_ball_from_charlie(); GameState.do_fetch_success()
	elif player.has_method("pickup") and player.held_object == null: player.pickup(self)
func _get_pet() -> void:
	var bonding_increase = 0.05
	GameState.bonding = clampf(GameState.bonding + bonding_increase, 0.0, 1.0)
	GameState.emit_signal("stats_changed")
	velocity = Vector2.ZERO
func get_picked_up() -> void:
	if current_state == State.PEEING: _cancel_peeing()
	var was_on_leash = is_on_leash
	if is_on_leash: is_on_leash = false; is_resisting = false; resistance_amount = 0.0
	current_state = State.HELD; visible = false; $CollisionShape2D.set_deferred("disabled", true)
	emit_signal("charlie_interacted"); set_meta("was_on_leash", was_on_leash)
func get_dropped(drop_pos: Vector2) -> void:
	global_position = drop_pos; visible = true; $CollisionShape2D.set_deferred("disabled", false)
	if has_meta("was_on_leash") and get_meta("was_on_leash"): equip_leash()
	else: current_state = State.IDLE
func _jump_out_and_chase(wildlife: Node2D) -> void:
	if current_state == State.PEEING: _cancel_peeing()
	if not player_ref: return
	if player_ref.has_method("drop"):
		global_position = player_ref.global_position + Vector2(randf_range(-15, 15), randf_range(-15, 15))
		visible = true; $CollisionShape2D.set_deferred("disabled", false); player_ref.held_object = null
	attracted_to_wildlife = wildlife; wildlife_excitement = 1.0
	if has_meta("was_on_leash") and get_meta("was_on_leash"): equip_leash()
	else: current_state = State.IDLE
