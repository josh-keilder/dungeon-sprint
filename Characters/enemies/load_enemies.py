from globals import *
from Characters.enemies.enemy import Skeleton, Skull_Enemy
from pytmx.util_pygame import load_pygame

def load_enemies(groups) -> list:
    # Spawns in enemies at enemy locations on the map
    enemies = []
    enemy_positions = get_enemy_pos(file_path = DUNGEON_LEVEL_ONE)
    print(enemy_positions)
    for pos in enemy_positions.get("Skull", []):
        new_skull_enemy = Skull_Enemy(groups, pos=pos)
        enemies.append(new_skull_enemy)
    for pos in enemy_positions.get("Skeleton", []):
        new_skull_enemy = Skeleton(groups, pos=pos)
        enemies.append(new_skull_enemy)

    return enemies

def get_enemy_pos(file_path) -> dict:
    tmx_data = load_pygame(file_path)
    enemy_positions = {}

    for obj in tmx_data.objects:
        if obj.name.startswith('Enemy_'):
            enemy_type = obj.name.split("_", 1)[1] 
            pos_x, pos_y = obj.x, obj.y
            if enemy_type not in enemy_positions:
                enemy_positions[enemy_type] = []
            enemy_positions[enemy_type].append((pos_x, pos_y))
        
    return enemy_positions