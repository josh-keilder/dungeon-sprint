import os

import pygame

PACK_FOLDER = "Assets/Dungeon Asset Pack"
KEYS_FOLDER = f"{PACK_FOLDER}/items and trap_animation/keys"

STRIPS = {
    "gold_key": {
        "frames": [f"{KEYS_FOLDER}/keys_1_{number}.png" for number in range(1, 5)],
        "path": "Assets/Items/gold_key_strip.png",
    },
    "silver_key": {
        "frames": [f"{KEYS_FOLDER}/keys_2_{number}.png" for number in range(1, 5)],
        "path": "Assets/Items/silver_key_strip.png",
    },
}


def make_strip(name, strip):
    frames = [pygame.image.load(path) for path in strip["frames"]]

    frame_size = frames[0].get_size()
    for path, frame in zip(strip["frames"], frames):
        if frame.get_size() != frame_size:
            raise ValueError(
                f"{name}: {path} is {frame.get_size()}, expected {frame_size}"
            )

    width, height = frame_size
    strip_image = pygame.Surface((width * len(frames), height), pygame.SRCALPHA)
    for index, frame in enumerate(frames):
        strip_image.blit(frame, (index * width, 0))

    os.makedirs(os.path.dirname(strip["path"]), exist_ok=True)
    pygame.image.save(strip_image, strip["path"])
    print(f"Saved {name}: {strip['path']} ({len(frames)} frames of {width}x{height})")


if __name__ == "__main__":
    for name, strip in STRIPS.items():
        make_strip(name, strip)
