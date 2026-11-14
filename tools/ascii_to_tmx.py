import os
import random
import sys
import xml.etree.ElementTree as ET
from collections import deque

from globals import TILE_SIZE

# Tile GIDs in Dungeon.tsx (firstgid 1), learned from Level One
# The floor is one 4x3 slab picture, repeated: pick the piece by position
FLOOR_PATTERN = (
    (12, 13, 14, 15),
    (22, 23, 24, 25),
    (32, 33, 34, 35),
)
VOID_GID = 79
TOP_WALL_GIDS = (2, 3, 4, 5)  # open floor below
BOTTOM_WALL_GIDS = (42, 43, 44, 45)  # open floor above
LEFT_WALL_GIDS = (11, 21, 31)  # open floor to the right
RIGHT_WALL_GIDS = (16, 26, 36)  # open floor to the left
INNER_CORNER_WEST_GID = 51  # open floor above and to the left
INNER_CORNER_EAST_GID = 54  # open floor above and to the right
OUTER_CORNER_GIDS = {"se": 1, "sw": 6, "ne": 41, "nw": 46}  # only a diagonal is open
DOOR_GIDS = {"top": 47, "bottom": 57, "left": 67, "right": 68}
LADDER_GID = 40  # the exit: a ladder down into a hole

# Logic_Tiles.tsx starts at GID 101; its tile 0 is door_1, tile 1 door_2, tile 2 door_3
LOGIC_FIRST_GID = 101

TILE_LAYER_NAMES = (
    "Floor",
    "Walls",
    "Wall_Decor",
    "Floor_Decor",
    "Door_Tiles",
    "Logic_Layer",
)

MAPS_FOLDER = "Assets/Maps"
TILESETS = (("1", "Dungeon.tsx"), (str(LOGIC_FIRST_GID), "Logic_Tiles.tsx"))

WALL = "#"
FLOOR = "."
VOID = " "
PLAYER = "@"
EXIT = "X"
CHEST = "C"
KEY = "g"
PLACED_ITEMS = {KEY: "gold_key"}
ENEMY_TYPES = {"s": "Skull", "k": "Skeleton"}
DOOR_IDS = {"1": "door_1", "2": "door_2", "3": "door_3"}

DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))

KNOWN_CHARACTERS = (
    {WALL, FLOOR, VOID, PLAYER, EXIT, CHEST}
    | set(ENEMY_TYPES)
    | set(DOOR_IDS)
    | set(PLACED_ITEMS)
)


def is_open(character):
    return character not in (WALL, VOID)


def read_grid(path):
    with open(path, encoding="utf-8") as file:
        rows = file.read().splitlines()

    while rows and not rows[-1].strip():
        rows.pop()

    width = max(len(row) for row in rows)
    grid = [row.ljust(width) for row in rows]

    validate_grid(grid)
    return grid


def validate_grid(grid):
    player_count = 0
    exit_count = 0

    for y, row in enumerate(grid):
        for x, character in enumerate(row):
            if character not in KNOWN_CHARACTERS:
                raise ValueError(f"unknown character {character!r} at ({x}, {y})")

            if character == PLAYER:
                player_count += 1
            if character == EXIT:
                exit_count += 1

            if is_open(character):
                for dx, dy in DIRECTIONS:
                    if cell_at(grid, x + dx, y + dy) == VOID:
                        raise ValueError(f"open tile at ({x}, {y}) touches the void")

    if player_count != 1:
        raise ValueError(f"expected 1 player spawn '@', found {player_count}")
    if exit_count == 0:
        raise ValueError("no exit 'X'")

    start = find_cells(grid, {PLAYER})[0]
    if not can_finish(grid, start):
        raise ValueError(
            "the exit can't be reached from '@': check that every door has "
            "a key 'g' that can be reached before it"
        )


def cell_at(grid, x, y):
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        return grid[y][x]

    return VOID


def wall_gid(grid, x, y, rng):
    def open_at(dx, dy):
        return is_open(cell_at(grid, x + dx, y + dy))

    if (open_at(-1, 0) and open_at(1, 0)) or (open_at(0, -1) and open_at(0, 1)):
        raise ValueError(f"wall at ({x}, {y}) is only 1 tile thick, walls need 2")

    if open_at(0, 1):
        return rng.choice(TOP_WALL_GIDS)

    if open_at(0, -1):
        if open_at(-1, 0):
            return INNER_CORNER_WEST_GID
        if open_at(1, 0):
            return INNER_CORNER_EAST_GID

        return rng.choice(BOTTOM_WALL_GIDS)

    if open_at(1, 0):
        return rng.choice(LEFT_WALL_GIDS)

    if open_at(-1, 0):
        return rng.choice(RIGHT_WALL_GIDS)

    for corner, (dx, dy) in (
        ("se", (1, 1)),
        ("sw", (-1, 1)),
        ("ne", (1, -1)),
        ("nw", (-1, -1)),
    ):
        if open_at(dx, dy):
            return OUTER_CORNER_GIDS[corner]

    return VOID_GID


def door_gid(grid, x, y):
    character = grid[y][x]

    if cell_at(grid, x, y + 1) == character:
        return DOOR_GIDS["top"]
    if cell_at(grid, x, y - 1) == character:
        return DOOR_GIDS["bottom"]
    if cell_at(grid, x + 1, y) == character:
        return DOOR_GIDS["left"]
    if cell_at(grid, x - 1, y) == character:
        return DOOR_GIDS["right"]

    raise ValueError(f"door at ({x}, {y}) needs a second tile next to it")


def build_tile_layers(grid, rng):
    width = len(grid[0])
    height = len(grid)
    layers = {name: [[0] * width for _ in range(height)] for name in TILE_LAYER_NAMES}

    for y, row in enumerate(grid):
        for x, character in enumerate(row):
            if is_open(character):
                layers["Floor"][y][x] = FLOOR_PATTERN[(y - 1) % 3][(x - 1) % 4]
            else:
                layers["Floor"][y][x] = VOID_GID

            if character == WALL:
                layers["Walls"][y][x] = wall_gid(grid, x, y, rng)

            if character in DOOR_IDS:
                layers["Door_Tiles"][y][x] = door_gid(grid, x, y)
                layers["Logic_Layer"][y][x] = LOGIC_FIRST_GID + int(character) - 1

            if character == EXIT:
                layers["Floor_Decor"][y][x] = LADDER_GID

    return layers


def build_objects(grid):
    objects = {"Chests": [], "Entity_Spawns": [], "Items": []}
    exit_cells = []

    for y, row in enumerate(grid):
        for x, character in enumerate(row):
            left = x * TILE_SIZE
            top = y * TILE_SIZE

            if character == PLAYER:
                center = (left + TILE_SIZE // 2, top + TILE_SIZE // 2)
                objects["Entity_Spawns"].append(("Player", *center, 0, 0))
            elif character in ENEMY_TYPES:
                enemy_name = f"Enemy_{ENEMY_TYPES[character]}"
                objects["Entity_Spawns"].append((enemy_name, left, top, 0, 0))
            elif character == CHEST:
                objects["Chests"].append(("chest", left, top, TILE_SIZE, TILE_SIZE))
            elif character in PLACED_ITEMS:
                center = (left + TILE_SIZE // 2, top + TILE_SIZE // 2)
                objects["Items"].append((PLACED_ITEMS[character], *center, 0, 0))
            elif character == EXIT:
                exit_cells.append((x, y))

    exit_xs = [x for x, _ in exit_cells]
    exit_ys = [y for _, y in exit_cells]
    objects["Entity_Spawns"].append(
        (
            "Exit",
            min(exit_xs) * TILE_SIZE,
            min(exit_ys) * TILE_SIZE,
            (max(exit_xs) - min(exit_xs) + 1) * TILE_SIZE,
            (max(exit_ys) - min(exit_ys) + 1) * TILE_SIZE,
        )
    )

    return objects


def layer_csv(rows):
    lines = [",".join(str(gid) for gid in row) for row in rows]
    return "\n" + ",\n".join(lines) + "\n"


def write_tmx(output_path, layers, objects, width, height):
    map_element = ET.Element(
        "map",
        {
            "version": "1.10",
            "orientation": "orthogonal",
            "renderorder": "right-down",
            "width": str(width),
            "height": str(height),
            "tilewidth": str(TILE_SIZE),
            "tileheight": str(TILE_SIZE),
            "infinite": "0",
        },
    )

    for first_gid, source in TILESETS:
        ET.SubElement(map_element, "tileset", {"firstgid": first_gid, "source": source})

    next_id = 1
    for name in TILE_LAYER_NAMES:
        layer = ET.SubElement(
            map_element,
            "layer",
            {
                "id": str(next_id),
                "name": name,
                "width": str(width),
                "height": str(height),
            },
        )
        data = ET.SubElement(layer, "data", {"encoding": "csv"})
        data.text = layer_csv(layers[name])
        next_id += 1

    object_id = 1
    for group_name, group_objects in objects.items():
        group = ET.SubElement(
            map_element, "objectgroup", {"id": str(next_id), "name": group_name}
        )
        next_id += 1

        for object_name, x, y, object_width, object_height in group_objects:
            attributes = {
                "id": str(object_id),
                "name": object_name,
                "x": str(x),
                "y": str(y),
            }
            if object_width:
                attributes["width"] = str(object_width)
                attributes["height"] = str(object_height)
            ET.SubElement(group, "object", attributes)
            object_id += 1

    map_element.set("nextlayerid", str(next_id))
    map_element.set("nextobjectid", str(object_id))

    tree = ET.ElementTree(map_element)
    ET.indent(tree, space=" ")
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)


def find_cells(grid, characters):
    return [
        (x, y)
        for y, row in enumerate(grid)
        for x, character in enumerate(row)
        if character in characters
    ]


def flood_fill(grid, start, opened_doors):
    reachable = {start}
    queue = deque([start])

    while queue:
        x, y = queue.popleft()

        for dx, dy in DIRECTIONS:
            neighbor = (x + dx, y + dy)
            if neighbor in reachable:
                continue

            character = cell_at(grid, *neighbor)
            if not is_open(character):
                continue
            if character in DOOR_IDS and character not in opened_doors:
                continue

            reachable.add(neighbor)
            queue.append(neighbor)

    return reachable


def can_finish(grid, start, opened_doors=frozenset()):
    reachable = flood_fill(grid, start, opened_doors)

    if any(grid[y][x] == EXIT for x, y in reachable):
        return True

    keys_found = sum(1 for x, y in reachable if grid[y][x] == KEY)
    keys_in_hand = keys_found - len(opened_doors)
    if keys_in_hand <= 0:
        return False

    touching = {
        cell_at(grid, x + dx, y + dy) for x, y in reachable for dx, dy in DIRECTIONS
    }
    closed_doors = (touching & set(DOOR_IDS)) - opened_doors

    for door in closed_doors:
        if can_finish(grid, start, opened_doors | {door}):
            return True

    return False


def main():
    path = sys.argv[1]
    grid = read_grid(path)

    map_name = os.path.splitext(os.path.basename(path))[0]
    rng = random.Random(map_name)
    layers = build_tile_layers(grid, rng)
    objects = build_objects(grid)

    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = os.path.join(MAPS_FOLDER, f"{map_name}.tmx")

    write_tmx(output_path, layers, objects, len(grid[0]), len(grid))
    print(f"Saved {output_path} ({len(grid[0])}x{len(grid)} tiles)")


if __name__ == "__main__":
    main()
