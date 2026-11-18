from entities.enemies.enemy_texture_data import (
    skeleton_texture_data,
    skull_texture_data,
)
from items.loot_table_data import SKELETON_LOOT, SKULL_LOOT
from world.particle_presets import BONE_CHIPS, SKULL_SPARKS

# Enemy types: the key must match the map's spawn name after "Enemy_".
# Every key is required; Enemy reads them with type_data["..."].
ENEMY_TYPES = {
    "Skull": {
        "max_health": 100,
        "attack_damage": 5,
        "behavior": "fly",
        "speed": 50,
        "texture_data": skull_texture_data,
        "start_animation": "skull_idle",
        "knockback_multiplier": 1.2,
        "knockback_decay_rate": 10,
        "blink_interval": 0.1,
        "invulnerability_duration": 1.0,
        "loot_table": SKULL_LOOT,
        # x, y, width, height inside the frame: the whole 16x16 skull
        "body": (0, 0, 16, 16),
        "touch_damage": True,  # hurts the player on contact
        "animation_prefix": None,  # Skull: one animation, no states
        "attack": None,  # Skull: hurts on touch instead
        "hit_particles": SKULL_SPARKS,
        "stagger_duration": 0.0,  # its knockback is long enough on its own
    },
    "Skeleton": {
        "max_health": 100,
        "attack_damage": 6,
        "behavior": "wander_chase",
        "speed": 40,
        "texture_data": skeleton_texture_data,
        "start_animation": "skeleton_idle_right",
        "knockback_multiplier": 0.7,
        "knockback_decay_rate": 16,
        "blink_interval": None,
        "invulnerability_duration": 1.0,
        "loot_table": SKELETON_LOOT,
        "body": (8, 13, 14, 16),  # the skeleton's body inside its 32x32 frame
        "touch_damage": False,  # only its swing hurts
        "animation_prefix": "skeleton",  # animations named skeleton_<action>_<facing>
        "attack": {
            "range": 20,  # pixels: starts a swing when the player is this close
            "frame_rate": 10,  # attack frames per second: frames 0-5 wind up in 0.6s
            "strike_frames": (6, 7),  # the frames that hurt: where the slash is drawn
            "reach": 18,  # pixels the strike hitbox extends in front of the body
            "cooldown": 1.0,  # seconds after a swing before the next one
            "line_up_gap": 16,  # pixels beside the player it walks to before swinging
            "level_tolerance": 6,  # pixels of height difference it still swings at
        },
        "hit_particles": BONE_CHIPS,
        "stagger_duration": 0.75,  # seconds without walking or swinging after a hit
    },
}
