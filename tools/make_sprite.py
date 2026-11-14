import os

import pygame

from globals import (
    PALETTE_AZURE,
    PALETTE_BRASS,
    PALETTE_CANDLE,
    PALETTE_CLAY,
    PALETTE_GOLD,
    PALETTE_ICE,
    PALETTE_LEATHER,
    PALETTE_SHADOW,
    PALETTE_SOOT,
    PALETTE_STEEL,
    PALETTE_STONE,
    PALETTE_TAN,
    PALETTE_VOID,
    PALETTE_WALL,
)

PADLOCK_ROWS = [
    "..ooo..",
    ".ollmo.",
    "olo.odo",
    "olo.odo",
    "ooooooo",
    "ollllmo",
    "olmkmdo",
    "olmkmdo",
    "ommmmdo",
    "ooooooo",
]

SPRITES = {
    "panel_frame": {
        "path": "Assets/UI/panel_frame.png",
        "colors": {
            "o": PALETTE_SOOT,  # outline
            "m": PALETTE_WALL,  # stone ring
            "l": PALETTE_LEATHER,  # light edge (top and left)
            "s": PALETTE_SHADOW,  # shadow edge (bottom and right)
            "f": PALETTE_VOID,  # fill
        },
        "rows": [
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
        ],
    },
    "padlock_silver": {
        "path": "Assets/Objects/padlock_silver.png",
        "colors": {
            "o": PALETTE_VOID,  # outline
            "l": PALETTE_ICE,  # light (top and left)
            "m": PALETTE_STEEL,  # mid
            "d": PALETTE_STONE,  # dark (right side)
            "k": PALETTE_VOID,  # keyhole
        },
        "rows": PADLOCK_ROWS,
    },
    "padlock_gold": {
        "path": "Assets/Objects/padlock_gold.png",
        "colors": {
            "o": PALETTE_VOID,
            "l": PALETTE_CANDLE,
            "m": PALETTE_GOLD,
            "d": PALETTE_BRASS,
            "k": PALETTE_VOID,
        },
        "rows": PADLOCK_ROWS,
    },
    "speed_boots": {
        "path": "Assets/Items/speed_boots.png",
        "colors": {
            "o": PALETTE_VOID,  # outline
            "d": PALETTE_CLAY,  # leather, shadow
            "m": PALETTE_LEATHER,  # leather, mid
            "l": PALETTE_TAN,  # leather, highlight
            "s": PALETTE_STEEL,  # sole and buckle
            "w": PALETTE_ICE,  # wing
            "a": PALETTE_AZURE,  # wing shading
        },
        "rows": [
            "................",
            "................",
            "..o..ooooo......",
            ".owo.ollmoo.....",
            "owwaoolmmmo.....",
            "oawwollmmmo.....",
            ".oaaolmmmdo.....",
            "..ooolmmmmo.....",
            "....olmsmmdo....",
            "....ommmsmdooo..",
            "....ommmmmmdddo.",
            "....osmmmmmmdddo",
            "....osssssssssso",
            ".....oooooooooo.",
            "................",
            "................",
        ],  # 16 rows of 16 characters
    },
}


def make_sprite(name, sprite):
    width = len(sprite["rows"][0])
    height = len(sprite["rows"])

    frame_image = pygame.Surface((width, height), pygame.SRCALPHA)

    for y, row in enumerate(sprite["rows"]):
        if len(row) != width:
            raise ValueError(f"{name}: row {y} is {len(row)} wide, expected {width}")

        for x, letter in enumerate(row):
            # Transparent pixels
            if letter == ".":
                continue

            if letter not in sprite["colors"]:
                raise ValueError(f"{name}: unknown letter {letter!r} at ({x}, {y})")

            frame_image.set_at((x, y), sprite["colors"][letter])

    os.makedirs(os.path.dirname(sprite["path"]), exist_ok=True)

    pygame.image.save(frame_image, sprite["path"])

    print(f"Saved {name}: {sprite["path"]} ({width}x{height})")


if __name__ == "__main__":
    for name, sprite in SPRITES.items():
        make_sprite(name, sprite)
