I want to create high quality sprites for my game about a Shih Tzu Charlie and a Player.

Generate animated sprite frames for the Player.
- A reference sprite can be found in player-sprite.png
- 4 frames showing Player stood still breathing, sticking his tongue out.
- 4 frames showing Player looking bored
- 4 frames showing Player looking confused
- 4 frames showing Player walking to the left
- 4 frames showing Player walking to the right
- 4 frames showing Player walking up
- 4 frames showing Player walking down
- 4 frames showing Player picking up Charlie
- 4 frames showing Player holding Charlie
- 4 frames showing Player holding Charlie walking to the left
- 4 frames showing Player holding Charlie walking to the right
- 4 frames showing Player holding Charlie walking up
- 4 frames showing Player holding Charlie walking down
- Consistent Player design across all frames
- Transparent background for compositing
- Pixel art style, 32-bit retro game aesthetic, similar to Legend of Zelda: Link to the Past.
- all 4 frames must be in a single row
- all rows should be in one file, stored in sprites/characters/player_spritesheet.png


Approach:
1. Generate a video to create a 4-second video of each animation
2. Request a green screen background for chroma keying
3. Extract 4 frames from the video using ffmpeg
4. Remove the green background with PIL to create transparent PNGs

After generating, show me the frames so I can verify the positions vary and the design is consistent.


## How It Works

When you give Claude Code this prompt, it will:

1. **Generate a 4-second video** of player on green background
2. **Extract 4 frames** using ffmpeg (one every 0.5 seconds)
3. **Remove green pixels** and replace with transparency using PIL
4. **Show you the frames** so you can give feedback
5. **Store each action on row** so you can see the action in a row
6. **Store all the rows in one file** called sprites/characters/player_spritesheet.png

### Giving Feedback

After seeing the results, tell Claude what to fix:

- "The green background wasn't fully removed" → Claude fixes the chroma key algorithm
- "Player's legs don't move enough between frames" → Claude adjusts the prompt
- "Player looks different in some frames" → Claude regenerates
- "I also need a Player sprite with transparent background" → Claude generates it