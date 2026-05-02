#!/usr/bin/env python3
"""Regenerate workflow icon (256×256 PNG). Run from repo root: python3 scripts/generate_icon.py"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icon.png")
SIZE_HI = 512
OUT_SIZE = 256
PAD = 46
RADIUS = 100
# Diagonal gradient: sky → deep blue (reads well on light & dark Alfred chrome)
C0 = (56, 189, 248)   # sky-400
C1 = (29, 78, 216)    # blue-700
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def diagonal_gradient(w: int, h: int, a: tuple[int, int, int], b: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (w, h))
    px = []
    max_d = w + h - 2
    for y in range(h):
        for x in range(w):
            t = (x + y) / max(max_d, 1)
            r = int(a[0] + (b[0] - a[0]) * t)
            g = int(a[1] + (b[1] - a[1]) * t)
            bl = int(a[2] + (b[2] - a[2]) * t)
            px.append((r, g, bl))
    img.putdata(px)
    return img


def rounded_mask(w: int, h: int, pad: int, radius: int) -> Image.Image:
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((pad, pad, w - pad - 1, h - pad - 1), radius=radius, fill=255)
    return m


def pick_font() -> str:
    for p in FONT_CANDIDATES:
        if os.path.isfile(p):
            return p
    return FONT_CANDIDATES[-1]


def main() -> None:
    font_path = pick_font()
    try:
        font_zh = _font(font_path, 168)
        font_en = _font(font_path, 190)
    except OSError:
        print("No suitable font found; install Arial Unicode or similar.", file=sys.stderr)
        sys.exit(1)

    grad = diagonal_gradient(SIZE_HI, SIZE_HI, C0, C1)
    mask = rounded_mask(SIZE_HI, SIZE_HI, PAD, RADIUS)
    icon_hi = Image.new("RGBA", (SIZE_HI, SIZE_HI), (0, 0, 0, 0))
    icon_hi.paste(grad, (0, 0), mask)

    # Soft rim highlight (subtle, top edge)
    rim = Image.new("RGBA", (SIZE_HI, SIZE_HI), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.rounded_rectangle(
        (PAD, PAD, SIZE_HI - PAD - 1, SIZE_HI - PAD - 1),
        radius=RADIUS,
        outline=(255, 255, 255, 55),
        width=3,
    )
    icon_hi = Image.alpha_composite(icon_hi, rim)

    draw = ImageDraw.Draw(icon_hi)
    zh, en = "文", "A"
    cx, cy = SIZE_HI // 2, SIZE_HI // 2
    zb = draw.textbbox((0, 0), zh, font=font_zh)
    eb = draw.textbbox((0, 0), en, font=font_en)
    zw, ew = zb[2] - zb[0], eb[2] - eb[0]
    fill = (255, 255, 255, 255)
    dot_r = 5
    # Horizontal distance between glyph centers: half-widths + breathing room + dot
    center_dist = zw / 2.0 + dot_r * 2.5 + ew / 2.0 + 6.0
    draw.text((cx - center_dist, cy), zh, font=font_zh, fill=fill, anchor="mm")
    draw.text((cx + center_dist, cy), en, font=font_en, fill=fill, anchor="mm")
    draw.ellipse(
        (cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r),
        fill=(255, 255, 255, 255),
    )

    out = icon_hi.resize((OUT_SIZE, OUT_SIZE), Image.Resampling.LANCZOS)
    out.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
