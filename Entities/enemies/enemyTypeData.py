from Entities.enemies.enemyTextureData import skull_enemy_texture_data

ENEMY_TYPES = {
    "Skull": {
        "max_health": 100,
        "attack_damage": 5,
        "behavior": "fly",
        "speed": 50,
        "texture_data": skull_enemy_texture_data,
        "start_animation": "skull_idle",
    },
    "Skeleton": {
        "max_health": 100,
        "attack_damage": 3,
        "behavior": "wander_chase",
        "speed": 40,
        "texture_data": skull_enemy_texture_data,
        "start_animation": "skull_idle",
    },
}
