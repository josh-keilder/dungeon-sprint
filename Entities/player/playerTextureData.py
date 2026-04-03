"""
Data: Player Texture Metadata
-----------------------------
Defines the spritesheet configurations for the player character. Each entry
specifies the frame dimensions, counts, and file paths for animations across
different states (Idle, Walk, Roll) and cardinal directions.

Note: 'Left' animations are typically handled via code-side flipping of 'Right'
assets to optimize storage and memory.
"""

from globals import *

player_texture_data = {
    # --- Idle Animations ---
    "player_idle_down": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 6,
        "file_path": "Assets/Player/Idle/Proto_Idle_Down.png",
    },
    "player_idle_up": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 6,
        "file_path": "Assets/Player/Idle/Proto_Idle_Up.png",
    },
    "player_idle_right": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 6,
        "file_path": "Assets/Player/Idle/Proto_Idle_Right.png",
    },
    # --- Walking Animations ---
    "player_walk_down": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 6,
        "file_path": "Assets/Player/Walk/Proto_Walk_Down.png",
    },
    "player_walk_up": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 6,
        "file_path": "Assets/Player/Walk/Proto_Walk_Up.png",
    },
    "player_walk_right": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 6,
        "file_path": "Assets/Player/Walk/Proto_Walk_Right.png",
    },
    # --- Rolling Animations ---
    "player_roll_down": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 5,
        "file_path": "Assets/Player/Roll/Proto_Roll_Down.png",
    },
    "player_roll_up": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 5,
        "file_path": "Assets/Player/Roll/Proto_Roll_Up.png",
    },
    "player_roll_right": {
        "type": "player",
        "size": (PLAYER_SPRITESIZE, PLAYER_SPRITESIZE),
        "position": (0, 0),
        "frames": 5,
        "file_path": "Assets/Player/Roll/Proto_Roll_Right.png",
    },
}
