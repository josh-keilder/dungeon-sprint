import random

import pygame
from pytmx.util_pygame import load_pygame

from constants import TILE_SIZE
from engine.core.assets import load_animations
from systems.lighting import flame_position
from world.decor_texture_data import decor_texture_data
from world.objects import Chest, Crate
from world.tiles import AnimatedDecor, DecorTile, Door, WallTile

# Tileset GIDs swapped for an animated version on load; all of them are light sources
ANIMATED_DECOR_GIDS = {
    91: "torch",
    92: "side_torch",
    94: "candlestick_1",
    96: "candlestick_2",
}


def load_floor_data(map_path):
    tmx_data = load_pygame(map_path)

    floor_data = build_map(tmx_data)
    assign_door_properties(tmx_data, floor_data["door_tiles"])

    floor_data["player_spawn"] = find_player_spawn(tmx_data)
    floor_data["enemy_spawns"] = find_enemy_spawns(tmx_data)
    floor_data["exit_rect"] = find_exit(tmx_data)
    floor_data["placed_items"] = find_placed_items(tmx_data)

    return floor_data


def build_map(tmx_data):
    map_width = tmx_data.width * TILE_SIZE
    map_height = tmx_data.height * TILE_SIZE
    map_surface = pygame.Surface((map_width, map_height)).convert()

    decor_tiles = pygame.sprite.Group()
    wall_tiles = pygame.sprite.Group()
    door_tiles = pygame.sprite.Group()
    chests = pygame.sprite.Group()
    crates = pygame.sprite.Group()
    lights = []

    for layer in tmx_data.visible_layers:
        if layer.name == "Floor":
            for x, y, tile_image in layer.tiles():
                map_surface.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))

        elif layer.name == "Walls":
            for x, y, tile_image in layer.tiles():
                pos = (x * TILE_SIZE, y * TILE_SIZE)
                map_surface.blit(tile_image, pos)
                WallTile(groups=wall_tiles, image=tile_image, pos=pos)

        elif layer.name in ["Wall_Decor", "Floor_Decor"]:
            build_decor(tmx_data, layer, decor_tiles, lights)

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

        elif layer.name == "Crates":
            for map_object in layer:
                Crate(pos=(map_object.x, map_object.y), groups=crates)

    return {
        "map_surface": map_surface,
        "decor_tiles": decor_tiles,
        "wall_tiles": wall_tiles,
        "door_tiles": door_tiles,
        "chests": chests,
        "crates": crates,
        "lights": lights,
    }


def build_decor(tmx_data, layer, decor_tiles, lights):
    decor_animations = load_animations(decor_texture_data)

    for x, y, gid in layer.iter_data():
        if gid == 0:
            continue

        pos = (x * TILE_SIZE, y * TILE_SIZE)
        tiled_gid, flipped = tiled_gid_and_flip(tmx_data, gid)
        name = ANIMATED_DECOR_GIDS.get(tiled_gid)

        if name is None:
            DecorTile(
                groups=decor_tiles,
                image=tmx_data.get_tile_image_by_gid(gid),
                pos=pos,
            )
            continue

        frames = decor_animations[name]
        if flipped:
            frames = [pygame.transform.flip(frame, True, False) for frame in frames]

        AnimatedDecor(
            groups=decor_tiles,
            frames=frames,
            pos=pos,
            start_index=random.randrange(len(frames)),
        )
        tile_center = (pos[0] + TILE_SIZE / 2, pos[1] + TILE_SIZE / 2)
        lights.append((name, flame_position(name, tile_center, flipped)))


def tiled_gid_and_flip(tmx_data, gid):
    tiled_gid = tmx_data.tiledgidmap[gid]
    flipped = any(
        internal_gid == gid and flags.flipped_horizontally
        for internal_gid, flags in tmx_data.gidmap[tiled_gid]
    )
    return tiled_gid, flipped


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
