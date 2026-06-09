"""Generate a Radspion-branded QR code (center logo) and write a PNG."""

from __future__ import annotations

import argparse
import sys
from importlib.resources import files
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage

BOX_SIZE = 10
BORDER = 4


def asset_path(name: str) -> Path:
    return Path(files("radspion.tools.assets").joinpath(name))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a Radspion QR code PNG with the agency logo in the center.",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Path for the output PNG (parent directories are created if needed)",
    )
    parser.add_argument(
        "text",
        help="Payload to encode in the QR code",
    )
    return parser.parse_args(argv)


def make_qr_image(text: str) -> StyledPilImage:
    logo_path = asset_path("logo.png")
    if not logo_path.is_file():
        raise FileNotFoundError(f"Logo not found: {logo_path}")

    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(
        image_factory=StyledPilImage,
        embedded_image_path=str(logo_path),
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    output = args.output.expanduser().resolve()

    if output.suffix.lower() != ".png":
        print(f"Error: output must be a .png file, got: {output}", file=sys.stderr)
        raise SystemExit(1)

    try:
        img = make_qr_image(args.text)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output)
    print(output)
    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
