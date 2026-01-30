extends Node
## GameState - Autoload singleton for managing game data, stats, and saves

# Player Info
var player_name: String = "Player"
var island_name: String = "Paradise Island"
var player_appearance: Dictionary = {
	"hair_color": Color.GOLD,
	"outfit_color": Color.PINK
}

# Charlie Stats (0.0 to 1.0)
var bonding: float = 0.0  # Heart meter
var entertainment: float = 0.0  # Entertainment meter
var hunger: float = 1.0  # Hunger meter (1.0 = full, 0.0 = starving)

# Stat decay tracking (game hours since last decay)
var last_hunger_decay_hour: float = 8.0
var last_entertainment_decay_hour: float = 8.0
var last_bonding_decay_day: int = 1

# Decay rates
const HUNGER_DECAY_INTERVAL: float = 8.0  # Every 8 game hours
const HUNGER_DECAY_AMOUNT: float = 0.05  # 5% per interval
const ENTERTAINMENT_DECAY_INTERVAL: float = 8.0  # Every 8 game hours
const ENTERTAINMENT_DECAY_AMOUNT: float = 0.01  # 1% per interval
const BONDING_DECAY_INTERVAL: int = 1  # Every 24 game hours (1 day)
const BONDING_DECAY_AMOUNT: float = 0.02  # 2% per day

# Game Progress
var current_phase: int = 0  # 0=Intro, 1=House, 2=Outside
var intro_complete: bool = false
var charlie_found: bool = false
var charlie_coaxed: bool = false
var charlie_trusts_player: bool = false  # Unlocks outdoor exploration
var first_sleep_complete: bool = false
var first_overworld_complete: bool = false  # First time exploring outside

# Fetch game progress
var fetch_attempts: int = 0
var charlie_returns_ball: bool = false  # Learned after several successful fetches

# Interaction counts
var feed_count: int = 0
var pet_count: int = 0
var fetch_success_count: int = 0

# Day/Time (managed by TimeWeather but saved here)
var current_day: int = 1
var current_hour: float = 8.0  # 8 AM start

# Save file path
const SAVE_PATH = "user://savegame.save"

signal stats_changed
signal phase_changed(new_phase: int)
signal charlie_trust_unlocked

func _ready() -> void:
	print("GameState initialized")

# Stat modification functions
func add_bonding(amount: float) -> void:
	bonding = clampf(bonding + amount, 0.0, 1.0)
	emit_signal("stats_changed")
	_check_trust_unlock()

func add_entertainment(amount: float) -> void:
	entertainment = clampf(entertainment + amount, 0.0, 1.0)
	emit_signal("stats_changed")
	_check_trust_unlock()

func add_hunger(amount: float) -> void:
	hunger = clampf(hunger + amount, 0.0, 1.0)
	emit_signal("stats_changed")

func process_stat_decay(game_hour: float, game_day: int) -> void:
	# Calculate hours passed since last hunger decay
	var hours_since_hunger_decay = game_hour - last_hunger_decay_hour
	if hours_since_hunger_decay < 0:
		hours_since_hunger_decay += 24.0  # Wrapped to next day

	# Hunger decay every 8 hours
	while hours_since_hunger_decay >= HUNGER_DECAY_INTERVAL:
		hunger = clampf(hunger - HUNGER_DECAY_AMOUNT, 0.0, 1.0)
		last_hunger_decay_hour += HUNGER_DECAY_INTERVAL
		if last_hunger_decay_hour >= 24.0:
			last_hunger_decay_hour -= 24.0
		hours_since_hunger_decay -= HUNGER_DECAY_INTERVAL

	# Calculate hours passed since last entertainment decay
	var hours_since_ent_decay = game_hour - last_entertainment_decay_hour
	if hours_since_ent_decay < 0:
		hours_since_ent_decay += 24.0

	# Entertainment decay every 8 hours
	while hours_since_ent_decay >= ENTERTAINMENT_DECAY_INTERVAL:
		entertainment = clampf(entertainment - ENTERTAINMENT_DECAY_AMOUNT, 0.0, 1.0)
		last_entertainment_decay_hour += ENTERTAINMENT_DECAY_INTERVAL
		if last_entertainment_decay_hour >= 24.0:
			last_entertainment_decay_hour -= 24.0
		hours_since_ent_decay -= ENTERTAINMENT_DECAY_INTERVAL

	# Bonding decay every 24 hours (each new day)
	var days_since_bonding_decay = game_day - last_bonding_decay_day
	while days_since_bonding_decay >= BONDING_DECAY_INTERVAL:
		bonding = clampf(bonding - BONDING_DECAY_AMOUNT, 0.0, 1.0)
		last_bonding_decay_day += BONDING_DECAY_INTERVAL
		days_since_bonding_decay -= BONDING_DECAY_INTERVAL

	emit_signal("stats_changed")

func _check_trust_unlock() -> void:
	if not charlie_trusts_player and bonding >= 1.0 and entertainment >= 1.0:
		charlie_trusts_player = true
		emit_signal("charlie_trust_unlocked")
		print("Charlie now trusts you enough to explore outside!")

# Interaction functions (each gives 25% = 0.25)
func do_feed() -> void:
	feed_count += 1
	add_bonding(0.25)
	add_entertainment(0.125)
	add_hunger(0.25)  # Feeding restores 25% hunger
	print("Fed Charlie! Bonding: ", bonding, " Entertainment: ", entertainment, " Hunger: ", hunger)

func do_pet() -> void:
	pet_count += 1
	add_bonding(0.25)
	add_entertainment(0.125)
	print("Petted Charlie! Bonding: ", bonding, " Entertainment: ", entertainment)

func do_fetch_success() -> void:
	fetch_success_count += 1
	fetch_attempts += 1
	add_entertainment(0.25)
	add_bonding(0.125)

	# Charlie learns to return ball after 3 successful fetches
	if fetch_success_count >= 3 and not charlie_returns_ball:
		charlie_returns_ball = true
		print("Charlie learned to return the ball!")

	print("Fetch success! Entertainment: ", entertainment)

func set_phase(phase: int) -> void:
	current_phase = phase
	emit_signal("phase_changed", phase)

# Save/Load functions
func save_game() -> void:
	var save_data = {
		"player_name": player_name,
		"island_name": island_name,
		"player_appearance": player_appearance,
		"bonding": bonding,
		"entertainment": entertainment,
		"hunger": hunger,
		"last_hunger_decay_hour": last_hunger_decay_hour,
		"last_entertainment_decay_hour": last_entertainment_decay_hour,
		"last_bonding_decay_day": last_bonding_decay_day,
		"current_phase": current_phase,
		"intro_complete": intro_complete,
		"charlie_found": charlie_found,
		"charlie_coaxed": charlie_coaxed,
		"charlie_trusts_player": charlie_trusts_player,
		"first_sleep_complete": first_sleep_complete,
		"first_overworld_complete": first_overworld_complete,
		"fetch_attempts": fetch_attempts,
		"charlie_returns_ball": charlie_returns_ball,
		"feed_count": feed_count,
		"pet_count": pet_count,
		"fetch_success_count": fetch_success_count,
		"current_day": current_day,
		"current_hour": current_hour
	}

	var file = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_var(save_data)
		file.close()
		print("Game saved!")
	else:
		print("Error saving game!")

func load_game() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		print("No save file found")
		return false

	var file = FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file:
		var save_data = file.get_var()
		file.close()

		player_name = save_data.get("player_name", "Player")
		island_name = save_data.get("island_name", "Paradise Island")
		player_appearance = save_data.get("player_appearance", player_appearance)
		bonding = save_data.get("bonding", 0.0)
		entertainment = save_data.get("entertainment", 0.0)
		hunger = save_data.get("hunger", 1.0)
		last_hunger_decay_hour = save_data.get("last_hunger_decay_hour", 8.0)
		last_entertainment_decay_hour = save_data.get("last_entertainment_decay_hour", 8.0)
		last_bonding_decay_day = save_data.get("last_bonding_decay_day", 1)
		current_phase = save_data.get("current_phase", 0)
		intro_complete = save_data.get("intro_complete", false)
		charlie_found = save_data.get("charlie_found", false)
		charlie_coaxed = save_data.get("charlie_coaxed", false)
		charlie_trusts_player = save_data.get("charlie_trusts_player", false)
		first_sleep_complete = save_data.get("first_sleep_complete", false)
		first_overworld_complete = save_data.get("first_overworld_complete", false)
		fetch_attempts = save_data.get("fetch_attempts", 0)
		charlie_returns_ball = save_data.get("charlie_returns_ball", false)
		feed_count = save_data.get("feed_count", 0)
		pet_count = save_data.get("pet_count", 0)
		fetch_success_count = save_data.get("fetch_success_count", 0)

		if first_overworld_complete:
			current_day = save_data.get("current_day", 1)
			current_hour = save_data.get("current_hour", 8.0)
		else:
			current_day = 1
			current_hour = 8.0

		emit_signal("stats_changed")
		print("Game loaded!")
		return true

	return false

func reset_game() -> void:
	player_name = "Player"
	island_name = "Paradise Island"
	player_appearance = {"hair_color": Color.GOLD, "outfit_color": Color.PINK}
	bonding = 0.0
	entertainment = 0.0
	hunger = 1.0
	last_hunger_decay_hour = 8.0
	last_entertainment_decay_hour = 8.0
	last_bonding_decay_day = 1
	current_phase = 0
	intro_complete = false
	charlie_found = false
	charlie_coaxed = false
	charlie_trusts_player = false
	first_sleep_complete = false
	first_overworld_complete = false
	fetch_attempts = 0
	charlie_returns_ball = false
	feed_count = 0
	pet_count = 0
	fetch_success_count = 0
	current_day = 1
	current_hour = 8.0
	emit_signal("stats_changed")
