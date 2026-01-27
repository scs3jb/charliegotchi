from PIL import Image
import os
import glob

def remove_background(image, tolerance=30):
    # Convert manually to RGBA
    img = image.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    # Green screen color (usually bright green)
    # We'll detect primarily green pixels
    for item in datas:
        # Simple heuristic: if Green is significantly higher than Red and Blue
        if item[1] > 150 and item[0] < 100 and item[2] < 100:
             # Transparent
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
            
    img.putdata(newData)
    return img

def create_spritesheet(output_path, input_pattern, sprite_width=64, sprite_height=64):
    files = sorted(glob.glob(input_pattern))
    if not files:
        print(f"No files found for pattern: {input_pattern}")
        return

    # We have 13 animations, each with 4 frames.
    # We'll assume the generated images are rows of 4 frames.
    # Total height = 13 * sprite_height
    # Total width = 4 * sprite_width
    
    # Actually, let's just stack them vertically.
    # Expectation: Each input file corresponds to one animation row.
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    sheet_width = sprite_width * 4
    sheet_height = sprite_height * len(files)
    
    spritesheet = Image.new("RGBA", (sheet_width, sheet_height))
    
    for index, file_path in enumerate(files):
        print(f"Processing {file_path}...")
        try:
            row_img = Image.open(file_path)
            
            # Remove background if needed (optional if generation already did it, but plan says remove green)
            # row_img = remove_background(row_img) # Better to do this per frame if needed or on whole row
            # Let's assume the generation creates a green background for better segmentation
            row_img = remove_background(row_img)

            # Resize if necessary to match expected row width
            if row_img.width != sheet_width or row_img.height != sprite_height:
                row_img = row_img.resize((sheet_width, sprite_height), Image.Resampling.NEAREST)
            
            spritesheet.paste(row_img, (0, index * sprite_height))
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    spritesheet.save(output_path)
    print(f"Saved spritesheet to {output_path}")

if __name__ == "__main__":
    # Define the mapping of rows expected
    # This acts as a manifest of what we expect to generate
    # We will look for files named 01_idle.png, 02_bored.png, etc.
    
    # For now, just generic pattern matching in 'raw_sprites' directory
    base_dir = "/home/jbriggs/src/charliegotchi"
    raw_dir = os.path.join(base_dir, "raw_sprites")
    output_file = os.path.join(base_dir, "sprites/characters/player_spritesheet.png")
    
    create_spritesheet(output_file, os.path.join(raw_dir, "*.png"), sprite_width=64, sprite_height=64)
