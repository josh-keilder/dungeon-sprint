from constants import TILE_SIZE

# Sheet layouts: each entry is a one-row strip of square frames, sliced by load_animations

# World objects, used by game/world/objects.py

# The crate: frame 0 at rest, then the impact frames played when it breaks
crate_texture_data = {
    "crate": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Objects/crate_strip.png",
    },
}
