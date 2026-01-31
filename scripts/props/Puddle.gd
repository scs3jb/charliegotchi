extends Node2D
## Puddle - A temporary puddle left by Charlie

var lifetime: float = 0.0
var max_lifetime: float = 0.0

func _ready() -> void:
	max_lifetime = randf_range(3.0, 4.0)
	# Draw a small yellow ellipse
	var sprite = ColorRect.new()
	sprite.size = Vector2(12, 6)
	sprite.position = Vector2(-6, -3)
	sprite.color = Color(1.0, 0.9, 0.2, 0.7) # Transparent yellow
	# Add a bit of rounding style if possible, but ColorRect is simple
	add_child(sprite)
	
	# Ensure it's behind characters
	z_index = -1

func _process(delta: float) -> void:
	lifetime += delta
	if lifetime > max_lifetime * 0.7:
		# Fade out in the last 30% of lifetime
		var alpha = 1.0 - ((lifetime - max_lifetime * 0.7) / (max_lifetime * 0.3))
		modulate.a = clampf(alpha, 0.0, 1.0)
	
	if lifetime >= max_lifetime:
		queue_free()
