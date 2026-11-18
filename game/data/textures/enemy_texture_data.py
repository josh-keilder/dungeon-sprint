from game.data.constants import TILE_SIZE

# The art is bigger than the body; see "body" in ENEMY_TYPES
SKELETON_FRAME_SIZE = (32, 32)

# Skeleton: one strip per animation, all facing right (left is mirrored on load)
skeleton_texture_data = {
    "skeleton_idle_right": {
        "size": SKELETON_FRAME_SIZE,
        "position": (0, 0),
        "frames": 6,
        "file_path": "Assets/Enemies/Skeleton/idle.png",
    },
    "skeleton_move_right": {
        "size": SKELETON_FRAME_SIZE,
        "position": (0, 0),
        "frames": 10,
        "file_path": "Assets/Enemies/Skeleton/move.png",
    },
    "skeleton_attack_right": {
        "size": SKELETON_FRAME_SIZE,
        "position": (0, 0),
        "frames": 9,
        "file_path": "Assets/Enemies/Skeleton/attack.png",
    },
    "skeleton_hurt_right": {
        "size": SKELETON_FRAME_SIZE,
        "position": (0, 0),
        "frames": 5,
        "file_path": "Assets/Enemies/Skeleton/hurt.png",
    },
    "skeleton_death_right": {
        "size": SKELETON_FRAME_SIZE,
        "position": (0, 0),
        "frames": 17,
        "file_path": "Assets/Enemies/Skeleton/death.png",
    },
}

skull_texture_data = {
    # Idle
    "skull_idle": {
        "size": (TILE_SIZE, TILE_SIZE),
        "position": (0, 0),
        "frames": 4,
        "file_path": "Assets/Enemies/Skull/Idle/skull_idle.png",
    },
}
