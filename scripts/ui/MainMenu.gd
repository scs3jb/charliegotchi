extends Control
## MainMenu - Title screen with New Game, Continue, and Quit options

@onready var continue_button: Button = $VBoxContainer/ContinueButton

func _ready() -> void:
	# Only show Continue if save exists
	if continue_button:
		continue_button.visible = FileAccess.file_exists(GameState.SAVE_PATH)

func _on_new_game_pressed() -> void:
	GameState.reset_game()
	get_tree().change_scene_to_file("res://scenes/Cutscene_Intro.tscn")

func _on_continue_pressed() -> void:
	if GameState.load_game():
		# Go to appropriate scene based on progress
		match GameState.current_phase:
			0:
				get_tree().change_scene_to_file("res://scenes/Cutscene_Intro.tscn")
			1:
				if GameState.charlie_found:
					get_tree().change_scene_to_file("res://scenes/House.tscn")
				else:
					get_tree().change_scene_to_file("res://scenes/Beach_Start.tscn")
			2:
				get_tree().change_scene_to_file("res://scenes/Overworld.tscn")
	else:
		print("No save file found!")

func _on_quit_pressed() -> void:
	get_tree().quit()
