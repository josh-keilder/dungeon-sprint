"""
Data: Item Database
-------------------
Defines the metadata for all collectable and interactable items in the game.
Each entry acts as a blueprint containing the item type, sprite dimensions,
animation frame counts, and file paths.
"""

from globals import *
import pygame

# --- Item Definitions ---

keys = {
    "gold_key": {
        "type": "key",
        "size": (TILESIZE, TILESIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Items/animated_gold_key.png",
    },
}

health_potions = {
    "health_potion": {
        "type": "potion",
        "size": (TILESIZE, TILESIZE),
        "position": (0, 0),
        "frames": 1,
        "file_path": "Assets/Items/health_potion.png",
    },
}

speed_boots = {
    "speed_boots": {
        "type": "equipment",
        "size": (TILESIZE, TILESIZE),
        "position": (0, 0),
        "frames": 1,
        "file_path": "Assets/Items/Speed_Boots_placeholder.png",
    },
}
