from game.data.constants import TILE_SIZE

# Sheet layouts: each entry is a one-row strip of square frames, sliced by load_animations

# Keys (4-frame spins from make_strip)
gold_key_texture_data = {
    "gold_key": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Items/gold_key_strip.png",
    },
}

silver_key_texture_data = {
    "silver_key": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Items/silver_key_strip.png",
    },
}

# Consumables
health_potion_texture_data = {
    "health_potion": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 1,
        "file_path": "Assets/Items/health_potion.png",
    },
}

# Equipment
speed_boots_texture_data = {
    "speed_boots": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 1,
        "file_path": "Assets/Items/speed_boots.png",
    },
}
