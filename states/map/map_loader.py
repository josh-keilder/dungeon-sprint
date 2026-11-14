import pygame
from pytmx.util_pygame import load_pygame

from globals import TILE_SIZE
from items.items import Chest
from states.map.tiles import DecorTile, Door, WallTile


def load_level_data(map_path):
    tmx_data = load_pygame(map_path)

    level_data = build_map(tmx_data)
    assign_door_properties(tmx_data, level_data["door_tiles"])

    level_data["player_spawn"] = find_player_spawn(tmx_data)
    level_data["enemy_spawns"] = find_enemy_spawns(tmx_data)
    level_data["exit_rect"] = find_exit(tmx_data)
    level_data["placed_items"] = find_placed_items(tmx_data)

    return level_data


def build_map(tmx_data):
    map_width = tmx_data.width * TILE_SIZE
    map_height = tmx_data.height * TILE_SIZE
    map_surface = pygame.Surface((map_width, map_height)).convert()

    decor_tiles = pygame.sprite.Group()
    wall_tiles = pygame.sprite.Group()
    door_tiles = pygame.sprite.Group()
    chests = pygame.sprite.Group()

    for layer in tmx_data.visible_layers:
        if layer.name == "Floor":
            for x, y, tile_image in layer.tiles():
                map_surface.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))

        elif layer.name == "Walls":
            for x, y, tile_image in layer.tiles():
                WallTile(
                    groups=wall_tiles,
                    image=tile_image,
                    pos=(x * TILE_SIZE, y * TILE_SIZE),
                )

        elif layer.name in ["Wall_Decor", "Floor_Decor"]:
            for x, y, tile_image in layer.tiles():
                DecorTile(
                    groups=decor_tiles,
                    image=tile_image,
                    pos=(x * TILE_SIZE, y * TILE_SIZE),
                )

        elif layer.name == "Door_Tiles":
            for x, y, tile_image in layer.tiles():
                Door(
                    groups=door_tiles,
                    image=tile_image,
                    pos=(x * TILE_SIZE, y * TILE_SIZE),
                )

        elif layer.name == "Chests":
            for map_object in layer:
                if map_object.name.lower() == "chest":
                    Chest(pos=(map_object.x, map_object.y), groups=chests)

    return {
        "map_surface": map_surface,
        "decor_tiles": decor_tiles,
        "wall_tiles": wall_tiles,
        "door_tiles": door_tiles,
        "chests": chests,
    }


def find_player_spawn(tmx_data):
    for map_object in tmx_data.objects:
        if map_object.name == "Player":
            return (map_object.x, map_object.y)

    return (0, 0)


def find_enemy_spawns(tmx_data):
    enemy_positions = {}

    for map_object in tmx_data.objects:
        if map_object.name and map_object.name.startswith("Enemy_"):
            # Split 'Enemy_Skeleton' into ['Enemy', 'Skeleton'] and take the latter
            enemy_type = map_object.name.split("_", 1)[1]

            if enemy_type not in enemy_positions:
                enemy_positions[enemy_type] = []

            enemy_positions[enemy_type].append((map_object.x, map_object.y))

    return enemy_positions


def find_exit(tmx_data):
    for map_object in tmx_data.objects:
        if map_object.name == "Exit":
            return pygame.Rect(
                map_object.x, map_object.y, map_object.width, map_object.height
            )
    return None


def find_placed_items(tmx_data):
    placed_items = []

    for layer in tmx_data.objectgroups:
        if layer.name != "Items":
            continue

        for map_object in layer:
            center = (
                map_object.x + map_object.width / 2,
                map_object.y + map_object.height / 2,
            )
            placed_items.append((map_object.name, center))

    return placed_items


def assign_door_properties(tmx_data, door_tiles):
    for layer in tmx_data.objectgroups:
        if layer.name != "Doors":
            continue

        for map_object in layer:
            door_rect = pygame.Rect(
                map_object.x, map_object.y, map_object.width, map_object.height
            )
            for door in door_tiles:
                if door_rect.colliderect(door.rect):
                    door.door_id = map_object.properties["door_id"]
                    door.key = map_object.properties["key"]
