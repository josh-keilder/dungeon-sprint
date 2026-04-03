"""
Module: Enemy Loader
--------------------
Handles the discovery and instantiation of enemy entities from map data.
Parses the Tiled (.tmx) Object Layer for markers prefixed with 'Enemy_',
extracts the specific type (e.g., 'Skull', 'Skeleton'), and returns a
list of initialized enemy objects ready for the scene.
"""

import pygame
from globals import *
from Entities.enemies.enemy import Skeleton, Skull_Enemy
from pytmx.util_pygame import load_pygame

ENEMY_FACTORY = {"Skull": Skull_Enemy, "Skeleton": Skeleton}


def load_enemies(player=None, file_path=None) -> list:
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
        enemy_class = ENEMY_FACTORY.get(enemy_type)

        if enemy_class:
            for pos in positions:
                new_enemy = enemy_class(pos=pos, player=player)
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
