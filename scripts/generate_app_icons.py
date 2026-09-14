#!/usr/bin/env python3
"""
generate_app_icons.py
Generates Android mipmap launcher icons (both standard square with subtle rounded corners and circular round icons)
from /home/prime3vil/Pictures/Ebb&Flow.jpg across all standard densities.
"""

import os
from PIL import Image, ImageDraw

SOURCE_IMAGE = "/home/prime3vil/Pictures/Ebb&Flow.jpg"
RES_DIR = "/home/prime3vil/Documents/Antigravity/App Dev/Ebb&Flow/app/src/main/res"

DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192
}

def crop_center_square(img):
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    return img.crop((left, top, left + min_dim, top + min_dim))

def make_round_icon(square_img, size):
    resized = square_img.resize((size, size), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    
    round_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    round_img.paste(resized, (0, 0), mask=mask)
    return round_img

def make_square_icon(square_img, size):
    resized = square_img.resize((size, size), Image.Resampling.LANCZOS).convert("RGBA")
    # Rounded rectangle with radius = size // 6
    radius = size // 6
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    
    out_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out_img.paste(resized, (0, 0), mask=mask)
    return out_img

def main():
    if not os.path.exists(SOURCE_IMAGE):
        print(f"Error: {SOURCE_IMAGE} does not exist!")
        return

    print(f"Loading {SOURCE_IMAGE}...")
    orig = Image.open(SOURCE_IMAGE)
    square_base = crop_center_square(orig)

    for folder, size in DENSITIES.items():
        target_folder = os.path.join(RES_DIR, folder)
        os.makedirs(target_folder, exist_ok=True)

        sq_icon = make_square_icon(square_base, size)
        sq_path = os.path.join(target_folder, "ic_launcher.png")
        sq_icon.save(sq_path, "PNG")

        round_icon = make_round_icon(square_base, size)
        round_path = os.path.join(target_folder, "ic_launcher_round.png")
        round_icon.save(round_path, "PNG")

        print(f"Generated {folder}: {size}x{size} (ic_launcher.png, ic_launcher_round.png)")

    print("✅ All Android app icons generated successfully!")

if __name__ == "__main__":
    main()
