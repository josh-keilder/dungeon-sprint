import os

import pygame

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
    "o": (30, 22, 22),  # outline
    "m": (110, 74, 72),  # stone ring
    "l": (137, 90, 69),  # light edge (top and left)
    "s": (84, 55, 64),  # shadow edge (bottom and right)
    "f": (37, 19, 26),  # fill
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
