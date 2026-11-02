#!/usr/bin/env python3
"""Draws each extension's 256 x 256 store icon in Samo's dot-matrix style: lit dots for the glyph, dim dots
around it, on a dark rounded square. Standard library only.

    python3 scripts/make-icons.py            # writes extensions/<id>/icon.png
"""

import math
import struct
import zlib
from pathlib import Path

SIZE = 256
RADIUS = 56  # corner radius of the square
GRID = 12  # dots per side
PITCH = 16  # pixels from one dot to the next
DOT = 5.5  # dot radius

BG = (18, 20, 26)
EDGE = (44, 48, 60)
DIM = (38, 42, 54)
LIT = (154, 165, 245)

GLYPHS = {
    # A terminal with a prompt: Claude Code sessions.
    "claude-sessions": [
        "............",
        ".##########.",
        ".#........#.",
        ".#.#......#.",
        ".#..#.....#.",
        ".#...#....#.",
        ".#..#.....#.",
        ".#.#..###.#.",
        ".#........#.",
        ".##########.",
        "............",
        "............",
    ],
    # A viewfinder: Shots.
    "shots": [
        "............",
        ".###....###.",
        ".#........#.",
        ".#........#.",
        "............",
        ".....##.....",
        ".....##.....",
        "............",
        ".#........#.",
        ".#........#.",
        ".###....###.",
        "............",
    ],
    # A clipboard: Clips.
    "clips": [
        "............",
        "....####....",
        "..##.##.##..",
        "..#......#..",
        "..#.####.#..",
        "..#......#..",
        "..#.###..#..",
        "..#......#..",
        "..#.####.#..",
        "..#......#..",
        "..########..",
        "............",
    ],
    # "Hi".
    "hello": [
        "............",
        "............",
        "..#..#..#...",
        "..#..#......",
        "..#..#..#...",
        "..####..#...",
        "..#..#..#...",
        "..#..#..#...",
        "..#..#..#...",
        "............",
        "............",
        "............",
    ],
}


def clamp(v):
    return max(0.0, min(1.0, v))


def rounded_square(x, y):
    """Coverage of the rounded square at pixel centre (x, y), anti-aliased, and whether it is on the edge."""
    cx = min(max(x, RADIUS), SIZE - RADIUS)
    cy = min(max(y, RADIUS), SIZE - RADIUS)
    d = math.hypot(x - cx, y - cy)
    return clamp(RADIUS + 0.5 - d), clamp(1.5 - abs(RADIUS - 1.0 - d)) if d > 0 else 0.0


def draw(glyph):
    offset = (SIZE - PITCH * (GRID - 1)) / 2
    rows = []
    for py in range(SIZE):
        row = bytearray([0])  # PNG filter: none
        for px in range(SIZE):
            x, y = px + 0.5, py + 0.5
            cover, edge = rounded_square(x, y)
            r, g, b = BG
            # Mix in the edge line.
            r, g, b = (c + (e - c) * edge for c, e in zip((r, g, b), EDGE))
            # The nearest dot.
            gx = round((x - offset) / PITCH)
            gy = round((y - offset) / PITCH)
            if 0 <= gx < GRID and 0 <= gy < GRID:
                d = math.hypot(x - (offset + gx * PITCH), y - (offset + gy * PITCH))
                a = clamp(DOT + 0.5 - d)
                colour = LIT if glyph[gy][gx] == "#" else DIM
                r, g, b = (c + (k - c) * a for c, k in zip((r, g, b), colour))
            row += bytes((round(r), round(g), round(b), round(255 * cover)))
        rows.append(bytes(row))
    return b"".join(rows)


def png(pixels):
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(pixels, 9))
        + chunk(b"IEND", b"")
    )


def main():
    root = Path(__file__).resolve().parent.parent
    for ext_id, glyph in GLYPHS.items():
        out = root / "extensions" / ext_id / "icon.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png(draw(glyph)))
        print(f"wrote {out.relative_to(root)}")


if __name__ == "__main__":
    main()
