extends Control
## IntroCutscene - Phase 0: Epic storm scene with Charlie on raft

@onready var scene_content: Node2D = $SceneContent
@onready var sky: ColorRect = $SceneContent/Sky
@onready var lightning_flash: ColorRect = $SceneContent/LightningFlash
@onready var cloud_layer: Node2D = $SceneContent/CloudLayer
@onready var ocean: Node2D = $SceneContent/Ocean
@onready var raft: Node2D = $SceneContent/Raft
@onready var charlie: Node2D = $SceneContent/Raft/Box/Charlie
@onready var rain_heavy: CPUParticles2D = $SceneContent/RainHeavy
@onready var rain_light: CPUParticles2D = $SceneContent/RainLight
@onready var spray_particles: CPUParticles2D = $SceneContent/SprayParticles
@onready var wind_lines: Node2D = $SceneContent/WindLines
@onready var narration_label: Label = $NarrationPanel/NarrationLabel
@onready var shake_timer: Timer = $ShakeTimer
@onready var lightning_timer: Timer = $LightningTimer
@onready var wave_timer: Timer = $WaveTimer

var cutscene_phase: int = 0
var phase_timer: float = 0.0
var total_time: float = 0.0

# Animation variables
var raft_base_y: float = 145.0
var wave_offset: float = 0.0
var shake_intensity: float = 3.0
var wind_speed: float = 200.0
var storm_intensity: float = 1.0

# Narration texts
var narrations = [
	"In the midst of a terrible storm...",
	"A tiny raft is tossed by the raging waves.",
	"Inside a cardboard box, a small puppy shivers in fear...",
	"This is Charlie. He doesn't know how he got here.",
	"Hours pass. The wind begins to calm...",
	"As dawn breaks, the storm fades away.",
	"The raft drifts toward a mysterious island...",
	"A new adventure awaits."
]

var phase_durations = [4.0, 4.0, 4.0, 3.0, 4.0, 4.0, 4.0, 3.0]

func _ready() -> void:
	raft_base_y = raft.position.y
	_advance_narration(0)

func _process(delta: float) -> void:
	phase_timer += delta
	total_time += delta

	# Animate raft bobbing
	_animate_raft(delta)

	# Animate wind lines
	_animate_wind(delta)

	# Animate clouds
	_animate_clouds(delta)

	# Charlie shivering effect
	_animate_charlie_shiver(delta)

	# Phase progression
	if cutscene_phase < narrations.size():
		if phase_timer >= phase_durations[cutscene_phase]:
			_next_phase()

	# Storm calming transition (phases 4-7)
	if cutscene_phase >= 4:
		_transition_to_calm(delta)

func _animate_raft(delta: float) -> void:
	wave_offset += delta * 3.0

	# Dramatic bobbing during storm
	var bob_intensity = 12.0 * storm_intensity
	var bob_speed = 2.5
	raft.position.y = raft_base_y + sin(wave_offset * bob_speed) * bob_intensity

	# Tilt with waves
	var tilt_intensity = 0.15 * storm_intensity
	raft.rotation = sin(wave_offset * 1.8) * tilt_intensity

func _animate_wind(delta: float) -> void:
	for child in wind_lines.get_children():
		child.position.x += wind_speed * delta * storm_intensity
		if child.position.x > 450:
			child.position.x = -100
			child.position.y = randf_range(40, 160)

func _animate_clouds(delta: float) -> void:
	cloud_layer.position.x += 15.0 * delta * storm_intensity
	if cloud_layer.position.x > 300:
		cloud_layer.position.x = 100

func _animate_charlie_shiver(delta: float) -> void:
	if storm_intensity > 0.3:
		charlie.position.x = sin(total_time * 20) * 1.5 * storm_intensity
	else:
		charlie.position.x = lerp(charlie.position.x, 0.0, delta * 2.0)

func _next_phase() -> void:
	cutscene_phase += 1
	phase_timer = 0.0

	if cutscene_phase < narrations.size():
		_advance_narration(cutscene_phase)
	else:
		_end_cutscene()

func _advance_narration(index: int) -> void:
	if narration_label and index < narrations.size():
		narration_label.text = narrations[index]

func _transition_to_calm(delta: float) -> void:
	# Gradually reduce storm intensity
	storm_intensity = lerp(storm_intensity, 0.0, delta * 0.3)

	# Reduce rain
	if rain_heavy:
		rain_heavy.amount = int(300 * storm_intensity)
		if storm_intensity < 0.1:
			rain_heavy.emitting = false

	if rain_light:
		rain_light.amount = int(150 * storm_intensity)
		if storm_intensity < 0.2:
			rain_light.emitting = false

	if spray_particles:
		spray_particles.amount = int(50 * storm_intensity)
		if storm_intensity < 0.15:
			spray_particles.emitting = false

	# Lighten sky
	if sky:
		var target_color = Color(0.5, 0.55, 0.7, 1.0)  # Dawn colors
		sky.color = sky.color.lerp(target_color, delta * 0.2)

	# Reduce shake
	shake_intensity = 3.0 * storm_intensity

	# Slow wind
	wind_speed = 200.0 * storm_intensity

	# Move raft toward "shore" in final phases
	if cutscene_phase >= 6:
		raft_base_y = lerp(raft_base_y, 170.0, delta * 0.3)

func _on_shake_timer_timeout() -> void:
	if storm_intensity > 0.1:
		scene_content.position = Vector2(
			randf_range(-shake_intensity, shake_intensity),
			randf_range(-shake_intensity, shake_intensity)
		)
	else:
		scene_content.position = Vector2.ZERO

func _on_lightning_timer_timeout() -> void:
	if storm_intensity > 0.3:
		_do_lightning()
		lightning_timer.wait_time = randf_range(1.5, 4.0)

func _do_lightning() -> void:
	lightning_flash.visible = true

	# Flash sequence
	var tween = create_tween()
	tween.tween_property(lightning_flash, "modulate:a", 1.0, 0.05)
	tween.tween_property(lightning_flash, "modulate:a", 0.3, 0.1)
	tween.tween_property(lightning_flash, "modulate:a", 0.8, 0.05)
	tween.tween_property(lightning_flash, "modulate:a", 0.0, 0.2)
	tween.tween_callback(func(): lightning_flash.visible = false)

func _on_wave_timer_timeout() -> void:
	# Animate wave positions
	for i in range(1, 4):
		var wave = ocean.get_node_or_null("Wave" + str(i))
		if wave:
			var offset = sin(total_time * 2.0 + i * 0.5) * 3.0 * storm_intensity
			wave.position.y = offset

	# Animate foam
	for i in range(1, 4):
		var foam = ocean.get_node_or_null("Foam" + str(i))
		if foam:
			foam.position.x += 20.0 * storm_intensity
			if foam.position.x > 450:
				foam.position.x = -80
				foam.position.y = randf_range(-8, 55)

func _end_cutscene() -> void:
	GameState.intro_complete = true
	GameState.set_phase(1)
	GameState.save_game()
	get_tree().change_scene_to_file("res://scenes/Beach_Start.tscn")

func _on_skip_pressed() -> void:
	_end_cutscene()
