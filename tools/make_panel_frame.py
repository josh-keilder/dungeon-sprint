import os

import pygame

from globals import (
    PALETTE_LEATHER,
    PALETTE_SHADOW,
    PALETTE_SOOT,
    PALETTE_VOID,
    PALETTE_WALL,
)

FRAME_ROWS = [
    ".oooooooooo.",
    "ommmmmmmmmmo",
    "omllllllllmo",
    "omlffffffsmo",
    "omlffffffsmo",
    "omlffffffsmo",
    "omlffffffsmo",
    "omlffffffsmo",
    "omlffffffsmo",
    "omssssssssmo",
    "ommmmmmmmmmo",
    ".oooooooooo.",
]
FRAME_COLORS = {
    "o": PALETTE_SOOT,  # outline
    "m": PALETTE_WALL,  # stone ring
    "l": PALETTE_LEATHER,  # light edge (top and left)
    "s": PALETTE_SHADOW,  # shadow edge (bottom and right)
    "f": PALETTE_VOID,  # fill
}
OUTPUT_PATH = "Assets/UI/panel_frame.png"


def make_panel_frame():
    width = len(FRAME_ROWS[0])
    height = len(FRAME_ROWS)

    frame_image = pygame.Surface((width, height), pygame.SRCALPHA)

    for y, row in enumerate(FRAME_ROWS):
        for x, letter in enumerate(row):
            if letter in FRAME_COLORS:
                frame_image.set_at((x, y), FRAME_COLORS[letter])

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    pygame.image.save(frame_image, OUTPUT_PATH)

    print(f"Saved {OUTPUT_PATH} ({width}x{height})")


if __name__ == "__main__":
    make_panel_frame()
