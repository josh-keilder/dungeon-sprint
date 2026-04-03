"""
Data: Enemy Texture Metadata
-----------------------------
Defines the spritesheet configurations for the enemies. Each entry
specifies the frame dimensions, counts, and file paths for animations across
different states and cardinal directions.

Note: 'Left' animations are typically handled via code-side flipping of 'Right'
assets to optimize storage and memory.
"""

from globals import *

skeleton_texture_data = {}

skull_enemy_texture_data = {
    # Idle
    "skull_idle": {
        "type": "enemy",
        "size": (TILESIZE, TILESIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Enemies/Skull/Idle/skull_idle.png",
    },
}
