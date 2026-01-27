I want to create high quality sprites for my game about a Shih Tzu Charlie.

Generate animated sprite frames for Charlie, a shih-tzu.
- A reference sprite can be found in charlie-sprite.png
- 4 frames showing Charlie stood still breathing, sticking his tongue out.
- 4 frames showing Charlie looking bored
- 4 frames showing Charlie looking confused
- 4 frames showing Charlie walking to the left
- 4 frames showing Charlie walking to the right
- 4 frames showing Charlie walking up
- 4 frames showing Charlie walking down
- 4 frames showing Charlie walking with a red ball to the left
- 4 frames showing Charlie walking with a red ball to the right
- 4 frames showing Charlie walking with a red ball up
- 4 frames showing Charlie walking with a red ball down
- 4 frames showing Charlie walking with a bone to the left
- 4 frames showing Charlie walking with a bone to the right
- 4 frames showing Charlie walking with a bone up
- 4 frames showing Charlie walking with a bone down
- 4 frames showing Charlie walking with a chicken drumstick to the left
- 4 frames showing Charlie walking with a chicken drumstick to the right
- 4 frames showing Charlie walking with a chicken drumstick up
- 4 frames showing Charlie walking with a chicken drumstick down
- Consistent Charlie design across all frames
- Transparent background for compositing
- Pixel art style, 32-bit retro game aesthetic, similar to Legend of Zelda: Link to the Past.
- all 4 frames must be in a single row
- all rows should be in one file, stored in sprites/characters/charlie_spritesheet.png


Approach:
1. Generate a video to create a 4-second video of each animation
2. Request a green screen background for chroma keying
3. Extract 4 frames from the video using ffmpeg
4. Remove the green background with PIL to create transparent PNGs

After generating, show me the frames so I can verify the positions vary and the design is consistent.


## How It Works

When you give Claude Code this prompt, it will:

1. **Generate a 4-second video** of charlie on green background
2. **Extract 4 frames** using ffmpeg (one every 0.5 seconds)
3. **Remove green pixels** and replace with transparency using PIL
4. **Show you the frames** so you can give feedback
5. **Store each action on row** so you can see the action in a row
6. **Store all the rows in one file** called sprites/characters/charlie_spritesheet.png

### Giving Feedback

After seeing the results, tell Claude what to fix:

- "The green background wasn't fully removed" → Claude fixes the chroma key algorithm
- "Charlie's legs don't move enough between frames" → Claude adjusts the prompt
- "Charlie looks different in some frames" → Claude regenerates
- "I also need a Charlie sprite with transparent background" → Claude generates it