from constants import TILE_SIZE

# Animated decor: the pack's frames, joined into strips by tools/make_strip.py
decor_texture_data = {
    "torch": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Objects/torch_strip.png",
    },
    "side_torch": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Objects/side_torch_strip.png",
    },
    "candlestick_1": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Objects/candlestick_1_strip.png",
    },
    "candlestick_2": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Objects/candlestick_2_strip.png",
    },
}
