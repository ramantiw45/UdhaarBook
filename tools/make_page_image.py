"""Render a sample khata page to an image, so the OCR layer can be tested
without a camera.

This is a *test fixture generator*, not a demo: the output is a clean digital
render, not a photograph. It exists because "the page is read on this machine"
is a claim that should be reproducible on any machine, including one with no
shopkeeper and no phone.

    python tools/make_page_image.py                # -> data/page_render.png
    python tools/make_page_image.py out.png --font "C:/Windows/Fonts/Inkfree.ttf"

Needs Pillow (installed with the optional OCR layer: requirements-ocr.txt).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FONT_CANDIDATES = (
    r"C:\Windows\Fonts\Nirmala.ttf",  # Latin + Devanagari
    r"C:\Windows\Fonts\mangal.ttf",
    r"C:\Windows\Fonts\Inkfree.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


def pick_font(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise SystemExit(
        "No usable font found. Pass one with --font, e.g. "
        r'--font "C:/Windows/Fonts/Nirmala.ttf"'
    )


def render(text: str, out: Path, font_path: str, size: int = 30) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(font_path, size)
    lines = text.splitlines() or [""]

    # Measure with a throwaway canvas, then draw on the real one.
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    widths, heights = [], []
    for line in lines:
        box = probe.textbbox((0, 0), line or " ", font=font)
        widths.append(box[2] - box[0])
        heights.append(box[3] - box[1])

    margin, leading = 48, int(size * 0.9)
    line_h = max(heights + [size]) + leading
    width = max(widths + [600]) + margin * 2
    height = line_h * len(lines) + margin * 2

    page = Image.new("RGB", (width, height), "#f7f4ec")  # paper, not pure white
    draw = ImageDraw.Draw(page)
    y = margin
    for line in lines:
        draw.text((margin, y), line, font=font, fill="#1b1a18")
        y += line_h

    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", nargs="?", default=str(ROOT / "data" / "page_render.png"))
    parser.add_argument("--source", default=str(ROOT / "samples" / "sample_ledger.txt"))
    parser.add_argument("--font", default=None)
    parser.add_argument("--size", type=int, default=30)
    args = parser.parse_args()

    text = Path(args.source).read_text(encoding="utf-8")
    path = render(text, Path(args.out), pick_font(args.font), args.size)
    print(f"wrote {path} ({path.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
