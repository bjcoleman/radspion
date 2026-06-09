"""Compose the Radspion logo with centered text beneath it (e.g. clearance code)."""

from __future__ import annotations

import argparse
import sys
from importlib.resources import files
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Match `.landing__title` on radspion.com (DM Sans 600, letter-spacing 0.12em).
FONT_VARIATION_NAME = b"SemiBold"
LETTER_SPACING_EM = 0.12
REFERENCE_CODE = "RADSPION-CLEARANCE-TRAINING"
WIDTH_FILL_RATIO = 0.92
TEXT_GAP_RATIO = 0.04
TEXT_COLOR = "#000000"
WHITE_THRESHOLD = 240


def asset_path(name: str) -> Path:
    return Path(files("radspion.tools.assets").joinpath(name))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a PNG with the Radspion logo and centered text below it.",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Path for the output PNG (parent directories are created if needed)",
    )
    parser.add_argument(
        "text",
        help="Text to render below the logo (e.g. clearance code string)",
    )
    return parser.parse_args(argv)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    font_path = asset_path("fonts/DMSans.ttf")
    if not font_path.is_file():
        raise FileNotFoundError(f"Font not found: {font_path}")
    font = ImageFont.truetype(str(font_path), size=size)
    font.set_variation_by_name(FONT_VARIATION_NAME)
    return font


def letter_spacing_px(font_size: int) -> int:
    return round(font_size * LETTER_SPACING_EM)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    spacing = letter_spacing_px(font.size)
    if not text:
        return 0
    width = 0
    for index, char in enumerate(text):
        bbox = draw.textbbox((0, 0), char, font=font)
        width += bbox[2] - bbox[0]
        if index < len(text) - 1:
            width += spacing
    return width


def text_bbox(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int, int, int]:
    spacing = letter_spacing_px(font.size)
    if not text:
        return (0, 0, 0, 0)

    left = top = 0
    right = bottom = 0
    x = 0
    first = True
    for index, char in enumerate(text):
        bbox = draw.textbbox((x, 0), char, font=font)
        if first:
            left, top, right, bottom = bbox
            first = False
        else:
            left = min(left, bbox[0])
            top = min(top, bbox[1])
            right = max(right, bbox[2])
            bottom = max(bottom, bbox[3])
        x = bbox[2] + (spacing if index < len(text) - 1 else 0)
    return (left, top, right, bottom)


def graphic_content_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    """Bounding box of non-background pixels (transparent or near-white)."""
    pixels = image.load()
    width, height = image.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 10:
                continue
            if red >= WHITE_THRESHOLD and green >= WHITE_THRESHOLD and blue >= WHITE_THRESHOLD:
                continue
            xs.append(x)
            ys.append(y)
    if not xs:
        return 0, 0, width - 1, height - 1
    return min(xs), min(ys), max(xs), max(ys)


def whitespace_above_graphic(image: Image.Image) -> int:
    """Pixels between the top of the file and the graphic (matches logo.png padding)."""
    _left, top, _right, _bottom = graphic_content_bbox(image)
    return top


def calibrate_font_size(
    draw: ImageDraw.ImageDraw,
    logo_width: int,
) -> int:
    """Largest font size so REFERENCE_CODE fits within WIDTH_FILL_RATIO of logo width."""
    target_width = int(logo_width * WIDTH_FILL_RATIO)
    best = 8
    low, high = 8, 512
    while low <= high:
        size = (low + high) // 2
        font = load_font(size)
        width = text_width(draw, REFERENCE_CODE, font)
        if width <= target_width:
            best = size
            low = size + 1
        else:
            high = size - 1
    return best


def draw_spaced_text(
    draw: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    x, y = origin
    spacing = letter_spacing_px(font.size)
    for index, char in enumerate(text):
        draw.text((x, y), char, font=font, fill=fill)
        bbox = draw.textbbox((x, y), char, font=font)
        x = bbox[2] + (spacing if index < len(text) - 1 else 0)


def make_clearance_logo_image(text: str) -> Image.Image:
    logo_path = asset_path("logo.png")
    if not logo_path.is_file():
        raise FileNotFoundError(f"Logo not found: {logo_path}")

    logo = Image.open(logo_path).convert("RGBA")
    logo_width, logo_height = logo.size

    scratch = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(scratch)

    font_size = calibrate_font_size(draw, logo_width)
    font = load_font(font_size)

    measured_width = text_width(draw, text, font)
    if measured_width > logo_width:
        raise ValueError(
            f"text is wider than the logo ({measured_width}px > {logo_width}px): {text!r}",
        )

    bbox = text_bbox(draw, text, font)
    text_width_px = bbox[2] - bbox[0]
    text_height_px = bbox[3] - bbox[1]
    gap = max(12, round(logo_height * TEXT_GAP_RATIO))
    bottom_margin = whitespace_above_graphic(logo)
    canvas_height = logo_height + gap + text_height_px + bottom_margin

    image = Image.new("RGBA", (logo_width, canvas_height), (255, 255, 255, 255))
    image.paste(logo, (0, 0), logo)

    draw = ImageDraw.Draw(image)
    text_x = (logo_width - text_width_px) // 2 - bbox[0]
    text_y = logo_height + gap - bbox[1]
    draw_spaced_text(draw, (text_x, text_y), text, font, TEXT_COLOR)
    return image


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    output = args.output.expanduser().resolve()
    text = args.text.strip()
    if not text:
        print("Error: text must not be empty", file=sys.stderr)
        raise SystemExit(1)

    if output.suffix.lower() != ".png":
        print(f"Error: output must be a .png file, got: {output}", file=sys.stderr)
        raise SystemExit(1)

    try:
        image = make_clearance_logo_image(text)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(output)
    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
