import os
import time
import subprocess
import requests
from PIL import Image
from google import genai
from google.genai import types

# Configuration
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

client = genai.Client(api_key=API_KEY)

MODEL_ID = "veo-3.1-generate-preview"
OUTPUT_DIR = "assets/sprites/veo_charlie"
TEMP_DIR = "assets/sprites/veo_charlie/temp"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

ACTIONS = {
    "idle_still": "stood still breathing, sticking his tongue out",
    "idle_bored": "looking bored",
    "idle_confused": "looking confused",
    "walk_left": "walking to the left",
    "walk_right": "walking to the right",
    "walk_up": "walking up",
    "walk_down": "walking down",
    "walk_ball_left": "walking with a red ball to the left",
    "walk_ball_right": "walking with a red ball to the right",
    "walk_ball_up": "walking with a red ball up",
    "walk_ball_down": "walking with a red ball down",
    "walk_bone_left": "walking with a bone to the left",
    "walk_bone_right": "walking with a bone to the right",
    "walk_bone_up": "walking with a bone up",
    "walk_bone_down": "walking with a bone down",
    "walk_chicken_left": "walking with a chicken drumstick to the left",
    "walk_chicken_right": "walking with a chicken drumstick to the right",
    "walk_chicken_up": "walking with a chicken drumstick up",
    "walk_chicken_down": "walking with a chicken drumstick down",
}

def remove_green_background(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # Simple chroma key: if green is dominant
        r, g, b, a = item
        # If green is much higher than red and blue
        # Using a slightly more robust check for "bright green"
        if g > 100 and g > r * 1.1 and g > b * 1.1:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(output_path)

def extract_frames(video_path, action_name):
    # Extract 8 frames, one every 0.5s (assuming 4s video)
    # ffmpeg -i input.mp4 -vf "fps=2" out_%d.png
    # But to be precise for exactly 8 frames from 4s:
    # We can use select filter or just fps.
    
    output_pattern = os.path.join(TEMP_DIR, f"{action_name}_%d.png")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", "fps=2",
        "-vframes", "8",
        output_pattern
    ]
    subprocess.run(cmd, check=True)
    
    # Process each frame
    for i in range(1, 9):
        raw_frame = os.path.join(TEMP_DIR, f"{action_name}_{i}.png")
        if os.path.exists(raw_frame):
            final_frame = os.path.join(OUTPUT_DIR, f"charlie_{action_name}_{i-1}.png")
            remove_green_background(raw_frame, final_frame)
            print(f"  Saved {final_frame}")
            os.remove(raw_frame)

def generate_animation(action_name, action_desc):
    # Check if already generated
    if all(os.path.exists(os.path.join(OUTPUT_DIR, f"charlie_{action_name}_{i}.png")) for i in range(8)):
        print(f"Skipping {action_name}, already exists.")
        return

    print(f"Generating animation for: {action_name}...")
    
    prompt = (
        f"Generate a high quality pixel art animation of Charlie, a shih-tzu, {action_desc}. "
        "Consistent Charlie design, 32-bit retro game aesthetic similar to Legend of Zelda: Link to the Past. "
        "Solid bright green background (#00FF00) for chroma keying. "
        "Charlie should be centered in the frame. The background must be purely solid green."
    )
    
    # Optional: Use reference image if desired. 
    # The prompt says "A reference sprite can be found in charlie-sprite.png"
    # and "Request a green screen background".
    
    try:
        # Using generate_videos
        # Note: some versions might require config=types.GenerateVideosConfig
        operation = client.models.generate_videos(
            model=MODEL_ID,
            prompt=prompt,
            # We can't easily pass the reference image to generate_videos in the same way as generate_content
            # but we can try to include it if the API supports it.
            # For now, let's stick to the prompt description.
        )
        
        print(f"  Operation {operation.name} started. Waiting...")
        
        # Poll for completion
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation.name)
            
        if operation.error:
            print(f"  Error: {operation.error}")
            if "quota" in str(operation.error).lower():
                print("  Rate limited. Pausing for 60 seconds...")
                time.sleep(60)
            return

        # Assuming the result has a video with a download URL or bytes
        # In some cases it might be a GCS path.
        video_obj = operation.result.generated_videos[0].video
        
        video_path = os.path.join(TEMP_DIR, f"{action_name}.mp4")
        
        # If it's a URI we might need to download it
        if hasattr(video_obj, 'uri') and video_obj.uri:
            # If URI starts with http, download it
            if video_obj.uri.startswith('http'):
                r = requests.get(video_obj.uri)
                with open(video_path, 'wb') as f:
                    f.write(r.content)
            else:
                # Might be a special URI or file path
                print(f"  Unsupported video URI: {video_obj.uri}")
                return
        elif hasattr(video_obj, 'bytes') and video_obj.bytes:
            with open(video_path, 'wb') as f:
                f.write(video_obj.bytes)
        else:
            print(f"  No video data found in result: {video_obj}")
            return

        print(f"  Video saved to {video_path}. Extracting frames...")
        extract_frames(video_path, action_name)
        os.remove(video_path)

    except Exception as e:
        print(f"  An error occurred: {e}")
        if "429" in str(e):
            print("  Rate limit hit. Pausing...")
            time.sleep(60)

if __name__ == "__main__":
    for name, desc in ACTIONS.items():
        generate_animation(name, desc)