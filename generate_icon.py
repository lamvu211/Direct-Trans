"""
generate_icon.py - Generate DirectTrans icon.ico programmatically using Pillow.
Run this script once to create src/assets/icon.ico
"""

import os
from PIL import Image, ImageDraw, ImageFont


def generate_icon():
    """Generate a DirectTrans icon with 'DT' text on a gradient-like blue background."""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Rounded rectangle background (Catppuccin blue)
        padding = max(1, size // 16)
        # Draw filled rounded rectangle
        bg_color = (137, 180, 250)  # #89b4fa - Catppuccin Mocha blue
        corner_radius = max(2, size // 6)

        # Draw background with rounded corners
        draw.rounded_rectangle(
            [padding, padding, size - padding - 1, size - padding - 1],
            radius=corner_radius,
            fill=bg_color
        )

        # Add slight gradient overlay at top for depth
        overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(size // 3):
            alpha = int(30 * (1 - y / (size // 3)))
            overlay_draw.line(
                [(padding + corner_radius, y + padding),
                 (size - padding - corner_radius - 1, y + padding)],
                fill=(255, 255, 255, alpha)
            )
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        # Draw "DT" text
        font_size = max(6, int(size * 0.45))
        try:
            font = ImageFont.truetype("segoeuib.ttf", font_size)  # Segoe UI Bold
        except Exception:
            try:
                font = ImageFont.truetype("arialbd.ttf", font_size)
            except Exception:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()

        text = "DT"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2 - bbox[1]  # Adjust for font baseline

        # Text shadow for depth
        shadow_offset = max(1, size // 32)
        draw.text((x + shadow_offset, y + shadow_offset), text,
                  fill=(30, 30, 46, 100), font=font)  # Dark shadow

        # Main text in white
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        images.append(img)

    # Save as .ico with multiple sizes
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'assets')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'icon.ico')

    # Use the largest image as base, save all sizes
    images[-1].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[:-1]
    )

    print(f"Icon generated: {output_path}")
    return output_path


if __name__ == '__main__':
    generate_icon()
