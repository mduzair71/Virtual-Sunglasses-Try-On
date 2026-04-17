import os
from PIL import Image

def remove_white_background(image_path):
    if not os.path.exists(image_path):
        print(f"Skipping {image_path}, not found.")
        return
        
    print(f"Processing {image_path}...")
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    # threshold for 'white' - adjust if needed
    threshold = 240 
    
    for item in datas:
        # If r, g, b are all above threshold, make it transparent
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(image_path, "PNG")
    print(f"Successfully processed {image_path}")

# Paths to the assets in frontend/public
assets = [
    "frontend/public/aviator.png",
    "frontend/public/wayfarer.png",
    "frontend/public/round.png"
]

if __name__ == "__main__":
    for asset in assets:
        remove_white_background(asset)
