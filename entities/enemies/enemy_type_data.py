from entities.enemies.enemy_texture_data import skull_enemy_texture_data

ENEMY_TYPES = {
    "Skull": {
        "max_health": 100,
        "attack_damage": 5,
        "behavior": "fly",
        "speed": 50,
        "texture_data": skull_enemy_texture_data,
        "start_animation": "skull_idle",
        "knockback_multiplier": 1.2,
        "knockback_decay_rate": 10,
        "blink_interval": 0.1,
        "invulnerability_duration": 1.0,
    },
    "Skeleton": {
        "max_health": 100,
        "attack_damage": 3,
        "behavior": "wander_chase",
        "speed": 40,
        "texture_data": skull_enemy_texture_data,
        "start_animation": "skull_idle",
        "knockback_multiplier": 0.7,
        "knockback_decay_rate": 16,
        "blink_interval": 0.15,
        "invulnerability_duration": 1.0,
    },
}
