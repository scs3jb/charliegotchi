# Claude Code Prompt: Charlie's Island Adventure Sprite Creation

## The Prompt

```
I want to create high quality sprites for my game about a Shih Tzu Charlie.

Generate animated sprite frames for Charlie, a shih-tzu.
- A reference sprite can be found in charlie-sprite.png
- 8 frames showing Charlie stood still breathing, sticking his tongue out.
- 8 frames showing Charlie looking bored
- 8 frames showing Charlie looking confused
- 8 frames showing Charlie walking to the left
- 8 frames showing Charlie walking to the right
- 8 frames showing Charlie walking up
- 8 frames showing Charlie walking down
- 8 frames showing Charlie walking with a red ball to the left
- 8 frames showing Charlie walking with a red ball to the right
- 8 frames showing Charlie walking with a red ball up
- 8 frames showing Charlie walking with a red ball down
- 8 frames showing Charlie walking with a bone to the left
- 8 frames showing Charlie walking with a bone to the right
- 8 frames showing Charlie walking with a bone up
- 8 frames showing Charlie walking with a bone down
- 8 frames showing Charlie walking with a chicken drumstick to the left
- 8 frames showing Charlie walking with a chicken drumstick to the right
- 8 frames showing Charlie walking with a chicken drumstick up
- 8 frames showing Charlie walking with a chicken drumstick down
- Consistent Charlie design across all frames
- Transparent background for compositing
- Pixel art style, 32-bit retro game aesthetic, similar to Legend of Zelda: Link to the Past.

Use Google's Gemini API. My API key is in the GEMINI_API_KEY environment variable.

Approach:
1. Use Veo 3.1 video generation to create a 4-second video of each animation
2. Request a green screen background for chroma keying
3. Extract 8 frames from the video using ffmpeg
4. Remove the green background with PIL to create transparent PNGs
5. Save as charlie_action_0.png through charlie_action_7.png in a sprites/ directory, where action is the action above

After generating, show me the frames so I can verify the wing positions vary and the design is consistent.
```

---

## How It Works

When you give Claude Code this prompt, it will:

1. **Write a Python script** that calls Gemini Veo 3.1 to generate a video
2. **Generate a 4-second video** of charlie on green background
3. **Extract 8 frames** using ffmpeg (one every 0.5 seconds)
4. **Remove green pixels** and replace with transparency using PIL
5. **Show you the frames** so you can give feedback

### Giving Feedback

After seeing the results, tell Claude what to fix:

- "The green background wasn't fully removed" → Claude fixes the chroma key algorithm
- "Charlie's legs don't move enough between frames" → Claude adjusts the prompt
- "Charlie looks different in some frames" → Claude regenerates
- "I also need a Charlie sprite with transparent background" → Claude generates it

---

## Prerequisites

1. **Gemini API Key**: Get one from https://aistudio.google.com/
2. **Set environment variable**: `export GEMINI_API_KEY="your-key-here"`
3. **FFmpeg**: `sudo apt install ffmpeg` (Linux) or `brew install ffmpeg` (Mac)
4. **Python packages**: `pip install google-genai pillow`

---
