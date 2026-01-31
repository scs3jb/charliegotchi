extends StaticBody2D
class_name TreeProp

@onready var trunk_sprite = $TrunkSprite
@onready var canopy_sprite = $CanopySprite
@onready var interaction_area = $InteractionArea

var has_been_peed_on: bool = false
var last_peed_time: float = -999.0 # Total game hours
var squirrel_occupant: Node2D = null

func _ready() -> void:
	add_to_group("trees")
	if interaction_area:
		interaction_area.area_entered.connect(_on_area_entered)

func _on_area_entered(area: Area2D) -> void:
	# Potential for detecting things entering tree vicinity
	pass

func get_pee_position() -> Vector2:
	# Return a position slightly further to the side of the trunk to avoid collision
	return global_position + Vector2(18, 8)

func mark_as_peed_on() -> void:
	has_been_peed_on = true
	# We could change the sprite slightly or add a small effect
	print("Tree has been marked by Charlie!")

func set_squirrel_occupant(squirrel: Node2D) -> void:
	squirrel_occupant = squirrel

func is_occupied() -> bool:
	return is_instance_valid(squirrel_occupant)
