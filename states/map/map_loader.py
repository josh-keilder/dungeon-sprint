import pygame
from pytmx.util_pygame import load_pygame
from globals import TILESIZE
from states.map.tiles import WallTile, DecorTile, Door
from items.items import Chest


def load_level_data(map_path):
    tmx_data = load_pygame(map_path)

    level_data = build_map(tmx_data)

    level_data["player_spawn"] = find_player_spawn(tmx_data)
    level_data["enemy_spawns"] = find_enemy_spawns(tmx_data)

    return level_data


def build_map(tmx_data):
    map_width = tmx_data.width * TILESIZE
    map_height = tmx_data.height * TILESIZE
    map_surface = pygame.Surface((map_width, map_height)).convert()

    decor_tiles = pygame.sprite.Group()
    wall_tiles = pygame.sprite.Group()
    door_tiles = pygame.sprite.Group()
    chests = pygame.sprite.Group()

    logic_layer = tmx_data.get_layer_by_name("Logic_Layer")

    for layer in tmx_data.visible_layers:

        if layer.name == "Floor":
            for x, y, surf in layer.tiles():
                map_surface.blit(surf, (x * TILESIZE, y * TILESIZE))

        elif layer.name == "Walls":
            for x, y, surf in layer.tiles():
                WallTile(
                    groups=wall_tiles,
                    image=surf,
                    pos=(x * TILESIZE, y * TILESIZE),
                )

        elif layer.name in ["Wall_Decor", "Floor_Decor"]:
            for x, y, surf in layer.tiles():
                DecorTile(
                    groups=decor_tiles,
                    image=surf,
                    pos=(x * TILESIZE, y * TILESIZE),
                )

        elif layer.name == "Door_Tiles":
            for x, y, surf in layer.tiles():
                door_tile = Door(
                    groups=door_tiles,
                    image=surf,
                    pos=(x * TILESIZE, y * TILESIZE),
                )
                # Extract door_id property from the logic layer at the same coordinate
                logic_props = tmx_data.get_tile_properties(
                    x, y, tmx_data.layers.index(logic_layer)
                )
                if logic_props:
                    door_tile.door_id = logic_props.get("door_id")

        elif layer.name == "Chests":
            for obj in layer:
                if obj.name.lower() == "chest":
                    Chest(pos=(obj.x, obj.y), groups=chests)

    return {
        "map_surface": map_surface,
        "decor_tiles": decor_tiles,
        "wall_tiles": wall_tiles,
        "door_tiles": door_tiles,
        "chests": chests,
    }


def find_player_spawn(tmx_data):

    for obj in tmx_data.objects:
        if obj.name == "Player":
            return (obj.x, obj.y)

    return (0, 0)


def find_enemy_spawns(tmx_data):
    enemy_positions = {}

    for obj in tmx_data.objects:
        if obj.name and obj.name.startswith("Enemy_"):
            # Split 'Enemy_Skeleton' into ['Enemy', 'Skeleton'] and take the latter
            enemy_type = obj.name.split("_", 1)[1]

            if enemy_type not in enemy_positions:
                enemy_positions[enemy_type] = []

            enemy_positions[enemy_type].append((obj.x, obj.y))

    return enemy_positions
