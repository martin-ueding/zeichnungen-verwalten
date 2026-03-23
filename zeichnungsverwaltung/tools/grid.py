import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def overlay_grid(image_path: Path) -> None:
    if not image_path.exists():
        print(f"Error: File not found: {image_path}", file=sys.stderr)
        return

    with Image.open(image_path) as img:
        img.load()
        width, height = img.size

        # A4 Dimensions
        A4_W, A4_H = 210, 297
        if width > height:
            target_ratio = A4_H / A4_W  # Landscape
        else:
            target_ratio = A4_W / A4_H  # Portrait

        current_ratio = width / height

        if abs(current_ratio - target_ratio) > 1e-4:
            if current_ratio > target_ratio:
                # Too wide, crop sides
                new_width = height * target_ratio
                offset = (width - new_width) / 2
                img = img.crop((offset, 0, width - offset, height))
            else:
                # Too tall, crop top/bottom
                new_height = width / target_ratio
                offset = (height - new_height) / 2
                img = img.crop((0, offset, width, height - offset))

            width, height = img.size

        is_portrait = height > width

        # Create copies for processing
        grid_img = img.copy()
        gray_img = img.convert("L")

    # A4 Dimensions in mm
    A4_WIDTH_MM = 210
    A4_HEIGHT_MM = 297

    # Calculate pixels per cm
    if is_portrait:
        pixels_per_cm = width / (A4_WIDTH_MM / 10)
    else:
        pixels_per_cm = width / (A4_HEIGHT_MM / 10)

    spacing_px = pixels_per_cm * 2

    # --- Create Grid Version ---
    draw = ImageDraw.Draw(grid_img)

    # Prepare font
    font_size = max(10, int(spacing_px / 6))
    try:
        font = ImageFont.load_default(size=font_size)
    except TypeError, OSError:
        font = ImageFont.load_default()

    # Draw Vertical lines and Column Numbers
    x = 0.0
    col = 1
    while x < width:
        draw.line([(x, 0), (x, height)], fill="white", width=1)
        draw.text((x + 5, 5), str(col), fill="white", font=font)
        x += spacing_px
        col += 1

    # Draw Horizontal lines and Row Numbers
    y = 0.0
    row = 1
    while y < height:
        draw.line([(0, y), (width, y)], fill="white", width=1)
        # Skip row number 1 to avoid duplication with column number 1
        if row > 1:
            draw.text((5, y + 5), str(row), fill="white", font=font)
        y += spacing_px
        row += 1

    # Save Grid Image
    grid_path = image_path.with_stem(f"{image_path.stem} (Gitter)")
    grid_img.save(grid_path)
    print(f"Created: {grid_path}")

    # --- Save Grayscale Version ---
    gray_path = image_path.with_stem(f"{image_path.stem} (grau)")
    gray_img.save(gray_path)
    print(f"Created: {gray_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Overlay a 2cm grid on an image (assuming A4 aspect ratio)."
    )
    parser.add_argument("image_path", type=Path, help="Path to the input image.")
    args = parser.parse_args()

    overlay_grid(args.image_path)
