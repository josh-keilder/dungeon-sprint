from Entities.enemies.enemy import Enemy
from Entities.enemies.enemyTypeData import ENEMY_TYPES
from pytmx.util_pygame import load_pygame


def load_enemies(file_path=None) -> list:
    """
    Spawns enemies based on coordinates retrieved from the map file.

    Args:
        player: Reference to the player object for AI targeting.
        file_path: Path to the .tmx level file.

    Returns:
        list: A collection of instantiated enemy sprites.
    """
    enemies = []
    enemy_data = get_enemy_pos(file_path=file_path)

    for enemy_type, positions in enemy_data.items():
        type_data = ENEMY_TYPES.get(enemy_type)

        if type_data:
            for pos in positions:
                new_enemy = Enemy(type_data, pos)
                enemies.append(new_enemy)

    return enemies


def get_enemy_pos(file_path) -> dict:
    """
    Parses the map for object markers and categorizes them by enemy type.
    Example: An object named 'Enemy_Skull' will be stored under the 'Skull' key.
    """
    tmx_data = load_pygame(file_path)
    enemy_positions = {}

    for obj in tmx_data.objects:
        if obj.name and obj.name.startswith("Enemy_"):
            # Split 'Enemy_Skeleton' into ['Enemy', 'Skeleton'] and take the latter
            enemy_type = obj.name.split("_", 1)[1]

            if enemy_type not in enemy_positions:
                enemy_positions[enemy_type] = []

            enemy_positions[enemy_type].append((obj.x, obj.y))

    return enemy_positions
