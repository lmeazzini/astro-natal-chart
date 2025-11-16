#!/usr/bin/env python3
"""
Remove white background from logo and save as PNG with transparency.

This script processes the logo.png file and creates a transparent version
by replacing white/near-white pixels with transparency.

Usage:
    python scripts/remove_bg.py
"""

from pathlib import Path

from PIL import Image


def remove_white_background(
    input_path: Path,
    output_path: Path,
    threshold: int = 240,
) -> None:
    """
    Remove white background from an image and save with transparency.

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        threshold: Pixel brightness threshold for white detection (0-255)
    """
    # Open the image
    img = Image.open(input_path)

    # Convert to RGBA if not already
    img = img.convert("RGBA")

    # Get pixel data
    data = img.getdata()

    # Create new pixel data with transparency
    new_data = []
    for item in data:
        # If pixel is white or near-white (all RGB values above threshold)
        if item[0] >= threshold and item[1] >= threshold and item[2] >= threshold:
            # Replace with transparent pixel
            new_data.append((255, 255, 255, 0))
        else:
            # Keep original pixel
            new_data.append(item)

    # Update image data
    img.putdata(new_data)

    # Save as PNG with transparency
    img.save(output_path, "PNG")
    print(f"✅ Created transparent logo: {output_path}")
    print(f"   Size: {img.size[0]}x{img.size[1]}px")


def main() -> None:
    """Main function to process logo."""
    # Define paths
    project_root = Path(__file__).parent.parent
    input_logo = project_root / "ux" / "figures" / "logo.png"
    output_logo = project_root / "ux" / "figures" / "logo-transparent.png"

    # Check if input exists
    if not input_logo.exists():
        print(f"❌ Error: Input logo not found at {input_logo}")
        return

    # Process image
    print(f"Processing logo: {input_logo}")
    remove_white_background(input_logo, output_logo, threshold=240)


if __name__ == "__main__":
    main()
