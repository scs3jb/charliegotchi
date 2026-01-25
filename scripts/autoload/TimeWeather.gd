extends Node
## TimeWeather - Autoload singleton for day/night cycle, seasons, and weather

enum Season { SPRING, SUMMER, AUTUMN, WINTER }
enum Weather { CLEAR, RAIN, SNOW, STORM, WINDY }

# Time settings
var time_scale: float = 60.0  # 1 real second = 1 game minute
var is_time_paused: bool = false

# Current state
var current_season: Season = Season.SPRING
var current_weather: Weather = Weather.CLEAR
var days_per_season: int = 7

# Lighting
var day_color: Color = Color(1.0, 1.0, 0.95)
var night_color: Color = Color(0.2, 0.2, 0.4)
var current_ambient: Color = day_color

signal time_updated(hour: float)
signal day_changed(day: int)
signal season_changed(season: Season)
signal weather_changed(weather: Weather)

func _ready() -> void:
	print("TimeWeather initialized")
	_update_ambient_light()

func _process(delta: float) -> void:
	if is_time_paused:
		return

	# Advance time
	GameState.current_hour += (delta * time_scale) / 60.0

	# Handle day rollover
	if GameState.current_hour >= 24.0:
		GameState.current_hour -= 24.0
		_advance_day()

	_update_ambient_light()
	emit_signal("time_updated", GameState.current_hour)

func _advance_day() -> void:
	GameState.current_day += 1
	emit_signal("day_changed", GameState.current_day)

	# Check for season change
	var season_day = (GameState.current_day - 1) % (days_per_season * 4)
	var new_season = int(season_day / days_per_season) as Season

	if new_season != current_season:
		current_season = new_season
		emit_signal("season_changed", current_season)
		print("Season changed to: ", Season.keys()[current_season])

	# Random weather change each day
	_randomize_weather()

func _randomize_weather() -> void:
	var rand = randf()

	match current_season:
		Season.SPRING:
			if rand < 0.3:
				current_weather = Weather.RAIN
			elif rand < 0.5:
				current_weather = Weather.WINDY
			else:
				current_weather = Weather.CLEAR
		Season.SUMMER:
			if rand < 0.1:
				current_weather = Weather.STORM
			elif rand < 0.2:
				current_weather = Weather.RAIN
			else:
				current_weather = Weather.CLEAR
		Season.AUTUMN:
			if rand < 0.4:
				current_weather = Weather.RAIN
			elif rand < 0.6:
				current_weather = Weather.WINDY
			else:
				current_weather = Weather.CLEAR
		Season.WINTER:
			if rand < 0.4:
				current_weather = Weather.SNOW
			elif rand < 0.6:
				current_weather = Weather.STORM
			else:
				current_weather = Weather.CLEAR

	emit_signal("weather_changed", current_weather)

func _update_ambient_light() -> void:
	var hour = GameState.current_hour

	# Dawn: 6-8, Day: 8-18, Dusk: 18-20, Night: 20-6
	if hour >= 6.0 and hour < 8.0:
		# Dawn
		var t = (hour - 6.0) / 2.0
		current_ambient = night_color.lerp(day_color, t)
	elif hour >= 8.0 and hour < 18.0:
		# Day
		current_ambient = day_color
	elif hour >= 18.0 and hour < 20.0:
		# Dusk
		var t = (hour - 18.0) / 2.0
		current_ambient = day_color.lerp(night_color, t)
	else:
		# Night
		current_ambient = night_color

func pause_time() -> void:
	is_time_paused = true

func resume_time() -> void:
	is_time_paused = false

func set_time(hour: float) -> void:
	GameState.current_hour = clampf(hour, 0.0, 23.99)
	_update_ambient_light()
	emit_signal("time_updated", GameState.current_hour)

func skip_to_morning() -> void:
	GameState.current_hour = 8.0
	_advance_day()
	_update_ambient_light()

func get_time_string() -> String:
	var hour = int(GameState.current_hour)
	var minute = int((GameState.current_hour - hour) * 60)
	var am_pm = "AM" if hour < 12 else "PM"
	var display_hour = hour % 12
	if display_hour == 0:
		display_hour = 12
	return "%d:%02d %s" % [display_hour, minute, am_pm]

func get_season_string() -> String:
	return Season.keys()[current_season].capitalize()

func get_weather_string() -> String:
	return Weather.keys()[current_weather].capitalize()

func is_daytime() -> bool:
	return GameState.current_hour >= 6.0 and GameState.current_hour < 20.0

func is_raining() -> bool:
	return current_weather == Weather.RAIN or current_weather == Weather.STORM

func is_snowing() -> bool:
	return current_weather == Weather.SNOW
