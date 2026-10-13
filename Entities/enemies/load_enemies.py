from Entities.enemies.enemy import Enemy
from Entities.enemies.enemyTypeData import ENEMY_TYPES


def load_enemies(enemy_spawns) -> list:
    enemies = []

    for enemy_type, positions in enemy_spawns.items():
        type_data = ENEMY_TYPES.get(enemy_type)

        if type_data:
            for pos in positions:
                new_enemy = Enemy(type_data, pos)
                enemies.append(new_enemy)

    return enemies
