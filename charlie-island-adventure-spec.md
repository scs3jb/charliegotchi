# Charlie's Island Adventure - Complete Game Specification

## Engine and Platforms
- **Godot 4.x** / **GDScript**
- **Android, Windows, Linux**

## Controls
- **W, A, S, D** movement
- **Arrow keys** (alternative movement)  
- **Mouse** for UI/interaction
- **Touch** for Android (virtual joystick + tap-to-move)

## High-Level Concept
2D top-down pet-care + exploration game starring baby Shih Tzu **Charlie**.  
Cozy/cute mood: *Tamagotchi* + *Harvest Moon* + *Animal Crossing* + *Zelda: Link to the Past*.

## Design
- Charlie is a shih tzu
- The player is a girl with blonde hair
- Style is similar to Legend of Zelda: Link to the Past

## 🎬 Phase 0: Intro Cutscene (Non-Interactive)
```

✅ NON-INTERACTIVE: Player only watches

- Charlie on raft in storm, hiding in cardboard box
- Storm ends → raft lands on beach → box on sand
- Auto-transition to Phase 1 beach scene

```

## 🏠 Phase 1: House and Bonding
```

1. Player customizes character (appearance, name) + island name
2. Beach: Find Charlie in box → food mini-game → coax him out
3. Pick up Charlie → go home (house interior scene)
4. House activities:
    - Feed Charlie
    - Pet Charlie
    - Play fetch (room-scale top-down)
5. FETCH RULES:
    - Initially: Charlie fetches ball but DOESN'T return it
    - Player walks to him → press button to take ball
    - After several rounds → Charlie learns to return ball
6. STATS (visible UI bars):
    - Heart (Bonding): +25% per interaction
    - Entertainment: +25% per interaction
    - 4 successful interactions = full meter
7. LEAD STATUS:
    - INSIDE HOUSE: Charlie NOT on lead, moves freely
    - Near house door → Charlie auto-follows player
    - Door interaction → equip lead/harness → load Phase 2
8. Unlock message when both stats full:
> "Charlie now trusts you enough to explore outside."
```

## 🌳 Phase 2: Outside with Lead
```

1. Door interaction auto-equips lead/harness on Charlie
2. OUTSIDE: Charlie ALWAYS on lead
3. LEAD BEHAVIOR:
    - Max wander distance from player
    - Opposite direction → leash pulls/stops player
    - High bonding → Charlie walks in sync with player
4. House door returns to Phase 1 interior
```

## 🌍 Overworld Features
```

- Zelda-style large top-down world
- Day/night cycle, 4 seasons, weather (rain/snow/lightning/wind)
- WALKING MECHANICS:
    - Long walks → boredom → Sniffari (reset boredom)
    - Charlie pees/poops → player picks up poop (mini-game)
    - Tutorial popups for each new mechanic

```

## 🐾 Wildlife Encounters
```

Animals: wolves, birds, dubious squirrel, rapping rat, manic mouse, grubby pigeon

FIRST ENCOUNTER: Pokémon-style tutorial screen

- Charlie actions: Bark, Bite, Lick, Whimper, Throw poo bag
- Teaches how to handle that animal type

LATER ENCOUNTERS: Direct overworld handling (no battle screen)

```

## 💤 Sleep System
```

1. FIRST sleep: Cutscene (player in bed, Charlie in basket)
2. Unlocks QUICK SLEEP:
    - Teleport home → sleep → pause all stats
    - Click "Wake" → next morning
```

## Godot Requirements
```

SCENES:
MainMenu.tscn | Cutscene_Intro.tscn | Beach_Start.tscn
House.tscn | Overworld.tscn | Battle_Tutorial.tscn | UI_HUD.tscn

AUTOLOAD SINGLETONS:
GameState.gd (stats/unlocks/save) | TimeWeather.gd

SAVE/LOAD:
Player data, Charlie stats, day/time/season, unlocks

```

## Expected Completion Flow
```

✅ Phase 0: Intro cutscene works
✅ Phase 1: Beach→House→4 interactions→door unlock
🎉 Phase 1 COMPLETE
✅ Phase 2: Lead system + overworld navigation
✅ Wildlife encounters (tutorial + repeat)
✅ Sleep system (first + quick sleep)
🎉 Phase 2 COMPLETE
🏆 GAME COMPLETE

