Implement a Candy Crush–style match‑3 feeding minigame for my Godot game “Charliegotchi” with the following requirements. Treat this as a full feature spec and ensure you cover UX, game design, integration with existing systems, and testing.

## Context and activation

- The minigame replaces the normal feeding interaction.
- It is activated by interacting with Charlie’s food bowl in the house scene (the same place where I currently feed him).
- When the player clicks/taps the bowl:
  - Transition smoothly from the house to the minigame scene (e.g., fade, slide, or zoom), without jarring audio cuts.
  - Pause or logically suspend normal Charliegotchi simulation while the minigame is active.
- When the minigame ends (success or failure), return cleanly to the house scene and resume Charliegotchi’s normal logic.

## Core game concept

- The board is a full screen grid filled with kibble pieces.
- The theme: Charlie is allergic to almost everything and especially to chicken; chicken in his food makes him itchy and makes him scratch.
- Gameplay:
  - Match‑3 (or more) by swapping adjacent tiles, similar to Candy Crush.
  - There are:
    - Multiple types of hypoallergenic kibble tiles (safe).
    - A distinct chicken tile type (the allergen).
  - The goal: match tiles to fill Charlie’s food bowl while clearing chicken from the board.
- Feedback:
  - Matching any kibble contributes to filling a “bowl fill” meter.
  - Matching chicken tiles:
    - Triggers a bark sound and a visible reaction from Charlie (e.g., bark animation, small shake).
    - Still contributes to clearing the board/meeting goals, but is clearly branded as “chicken” (bad).
- The board should continuously refill (falling tiles + new tiles from the top) as in standard match‑3.

## Win / fail conditions and stat effects

- Win condition:
  - The player reaches the target fill level for the bowl (e.g., a bowl meter reaches 100%) within either a move limit or a time limit (you can decide which is more fun and implement it, but make it configurable).
  - On success:
    - Charlie’s food bar is set to full.
    - Charlie’s happiness is set to full.
- Failure condition:
  - The player runs out of moves or time before filling the bowl sufficiently.
  - On failure:
    - Charlie loses bonding (reduce bonding stat by a configurable amount).
    - Charlie loses happiness (reduce happiness by a configurable amount).
- Make the amounts and thresholds configurable so I can tweak numbers without changing code.

## First‑time and tutorial behavior

- The first time this minigame is triggered:
  - Show a short, clear tutorial overlay before the board becomes interactive.
  - The text should explain:
    - Charlie is allergic to nearly everything, especially chicken.
    - Chicken makes him itch and scratch.
    - The goal is to “clean up” the kibble by matching pieces and removing chicken from his food.
    - Basic controls (swap adjacent pieces by click‑drag or tap‑drag).
  - Require the player to confirm (e.g., “OK, let’s feed Charlie!”) before the game starts.
- Store a persistent flag (e.g., `has_seen_feeding_minigame_tutorial`) so the tutorial only appears the first time, with the ability to re‑show it via an options/toggle if needed.

## Controls and input

- Input methods:
  - Mouse (desktop): click and drag to swap tiles, or click tile A then click tile B to swap (choose one scheme, but make it feel natural).
  - Touch (mobile/tablet): tap and drag between adjacent tiles to swap.
- Input rules:
  - Only allow swaps that result in at least one valid match (standard match‑3 behavior) unless we explicitly decide otherwise.
  - Provide visual feedback on selected tile and potential swap direction.
- Make sure the control handling is responsive and feels good with both mouse and touch, with no reliance on hover.

## UI, transitions, and flow

- Entry:
  - When tapped on the bowl, fade/transition into the minigame.
  - Show Charlie in some form on the minigame screen (e.g., side portrait) to maintain thematic connection.
- During play:
  - Display:
    - Bowl fill meter (clearly visible).
    - Remaining moves or remaining time (depending on chosen system).
    - Optional: a small icon or indicator for chicken tiles.
- Exit and results:
  - On win:
    - Show a results panel: “Charlie’s bowl is full! He’s very happy!” with a quick summary of performance (e.g., tiles matched, chicken cleared).
    - Apply stat changes (food and happiness to full).
    - Provide a clear “Return to house” / “Back” button.
  - On fail:
    - Show a results panel indicating failure gently (lighthearted, not harsh) and that Charlie has lost some bonding and happiness.
    - Apply the relevant stat decreases.
    - Provide a clear “Return to house” / “Try again” button (configurable whether retry is allowed immediately).
- Exiting early:
  - Include a visible but unobtrusive exit/quit button (e.g., a small “X” in a corner).
  - On early exit, define behavior:
    - Preferably treat it as a failed attempt (apply the same penalties) or as no effect—make this behavior configurable and clearly implemented.
  - Confirm before quitting mid‑run (simple “Are you sure?” dialog) to prevent accidental exits, especially on touch.

## Game feel and feedback

- Visual feedback:
  - Simple particle effects and small animations when matches happen.
  - Distinct effect when chicken tiles are removed (different color burst, bark reaction, or an overlay “No chicken!” text).
- Audio feedback:
  - Different sounds for:
    - Safe kibble matches (crunch).
    - Chicken matches (bark + special sound).
  - Short success and failure stings on result screens.
- Performance:
  - Ensure smooth animations and no noticeable frame drops on typical mid‑range hardware.

## Architecture and integration

- Implement the minigame as a separate scene or scene tree that can be instantiated from the house/food bowl interaction.
- Provide a clean interface (e.g., signals or callbacks) so the minigame reports:
  - `minigame_success` with relevant data (e.g., score, number of chicken tiles cleared).
  - `minigame_failure` with similar data.
  - Use this to update Charlie’s stats (food, happiness, bonding) in the main game.
- Make configuration values easily editable (via exported variables or a config resource), such as:
  - Board size.
  - Types and frequencies of tiles.
  - Move or time limits.
  - Stat changes on success/failure.
  - Sounds and visual effects references.

## Testing and quality

- Implement automated and/or scripted tests where feasible, and at least thorough manual testing:
  - Board logic:
    - Tile spawning respects defined frequencies.
    - Swaps only occur when valid (unless intentionally allowed invalid swaps).
    - Matches are detected correctly horizontally and vertically.
    - Cascades (new matches from falling tiles) resolve correctly without soft‑locks.
  - Win/fail logic:
    - The game ends correctly when the bowl meter is full.
    - The game ends correctly when moves/time run out.
  - Stat integration:
    - On success, Charlie’s food bar and happiness correctly go to full.
    - On failure, bonding and happiness are reduced as configured.
    - Early exit behaves according to the chosen rule.
  - UI flow:
    - First‑time tutorial appears once and is skipped on subsequent runs.
    - Results screens always show and buttons work correctly.
    - Transitions to and from the house scene are smooth and free of flicker or stuck states.
  - Input:
    - Mouse and touch controls both work and feel responsive.
- Add logging or debug options to help tune:
  - Difficulty parameters (tile distribution, move/time limits).
  - Stat changes on success/failure.

## Polish and extensibility

- Design the minigame so it can be iterated on later (e.g., adding power‑ups, obstacles, or special tiles) without rewriting the core architecture.
- Ensure the feature feels like a natural, seamless part of Charliegotchi, not a disconnected mini‑app: consistent art style, sound design, and UI language.
- Provide a short internal note or documentation file describing:
  - How to adjust configuration values.
  - How to hook into signals or outcomes.
  - Any caveats or known limitations.

Use this entire specification as the target behavior for implementing and iterating the feeding minigame.
