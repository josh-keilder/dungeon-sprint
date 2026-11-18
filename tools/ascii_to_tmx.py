import os
import random
import sys
import xml.etree.ElementTree as ET
from collections import deque

from game.data.constants import TILE_SIZE

# Legend: one character per tile in the ASCII source
WALL = "#"
FLOOR = "."
VOID = " "  # outside the dungeon
PLAYER = "@"
EXIT = "X"  # drawn as a ladder down
CHEST = "C"
CRATE = "B"  # breakable box: blocks until rolled into
SILVER_KEY = "s"
GOLD_KEY = "g"
PLACED_ITEMS = {SILVER_KEY: "silver_key", GOLD_KEY: "gold_key"}
ENEMY_TYPES = {"w": "Skull", "k": "Skeleton"}

# Door tiles, and the key that opens them; a door is two touching tiles of the same letter
DOOR_KEYS = {"S": "silver_key", "G": "gold_key"}

KNOWN_CHARACTERS = (
    {WALL, FLOOR, VOID, PLAYER, EXIT, CHEST, CRATE}
    | set(ENEMY_TYPES)
    | set(DOOR_KEYS)
    | set(PLACED_ITEMS)
)

# Neighbors: up, right, down, left
DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))
UP, RIGHT, DOWN, LEFT = DIRECTIONS

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

# Decor GIDs
TORCH_GID = 91  # front-facing wall torch, on a top wall: a light source
BANNER_GID = 75
WALL_RING_GIDS = (76, 77)
SIDE_TORCH_GID = 92  # leans on the wall to its left: a light source
FLIP_HORIZONTAL = 0x80000000  # TMX flag bit on a GID: draw the tile mirrored
BIG_WEB_GID = 65  # fills a top-left corner
SMALL_WEB_GID = 66  # sits in a top-right corner
RUBBLE_GIDS = (50, 60)
BONE_GIDS = (69, 78)
CANDLESTICK_GIDS = (94, 96)  # lit, standing on the floor: light sources

# Decor rules
TORCH_SPACING = 7  # about one torch per this many tiles of top wall
TORCH_MIN_RUN = 4  # shorter top walls get no torch
BANNER_CHANCE = 0.5  # per gap between two torches
WALL_RING_CHANCE = 0.08  # per remaining top-wall tile
SIDE_TORCH_SPACING = 8  # about one side torch per this many tiles of side wall
SIDE_TORCH_MIN_RUN = 6  # shorter side walls get no torch
WEB_CHANCE = 0.3  # per top corner
RUBBLE_CHANCE = 0.025  # per floor tile against a wall
BONES_CHANCE = 0.015  # per open floor tile

# Output: the tile layers in the names and order map_loader expects
TILE_LAYER_NAMES = (
    "Floor",
    "Walls",
    "Wall_Decor",
    "Floor_Decor",
    "Door_Tiles",
)
MAPS_FOLDER = "Assets/Maps"
TILESETS = (("1", "Dungeon.tsx"),)


# Reading and checking the grid
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
    if not can_finish(grid, start, find_door_groups(grid)):
        raise ValueError(
            "the exit can't be reached from '@': check that every door has a "
            "matching key ('s' for 'S', 'g' for 'G') that can be reached before it"
        )


# Solvability: can the exit be reached, opening doors with matching keys?
def can_finish(grid, start, door_groups, opened=frozenset()):
    door_at = door_index(door_groups)
    reachable = flood_fill(grid, start, door_at, opened)

    if any(grid[y][x] == EXIT for x, y in reachable):
        return True

    touching = {
        door_at[(x + dx, y + dy)]
        for x, y in reachable
        for dx, dy in DIRECTIONS
        if (x + dx, y + dy) in door_at
    }

    for index in touching - opened:
        key_id = door_groups[index][0]
        keys_found = sum(
            1 for x, y in reachable if PLACED_ITEMS.get(grid[y][x]) == key_id
        )
        keys_used = sum(
            1 for opened_index in opened if door_groups[opened_index][0] == key_id
        )

        if keys_found - keys_used > 0 and can_finish(
            grid, start, door_groups, opened | {index}
        ):
            return True

    return False


def flood_fill(grid, start, door_at, opened):
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
            if neighbor in door_at and door_at[neighbor] not in opened:
                continue

            reachable.add(neighbor)
            queue.append(neighbor)

    return reachable


def find_door_groups(grid):
    door_groups = []
    seen = set()

    for cell in find_cells(grid, set(DOOR_KEYS)):
        if cell in seen:
            continue

        cells = same_character_area(grid, cell)
        seen |= cells
        if len(cells) != 2:
            raise ValueError(f"door at {cell} is {len(cells)} tiles; doors are 2 tiles")

        x, y = cell
        door_groups.append((DOOR_KEYS[grid[y][x]], cells))

    return door_groups


def same_character_area(grid, start):
    x, y = start
    character = grid[y][x]
    area = {start}
    queue = deque([start])

    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS:
            neighbor = (x + dx, y + dy)
            if neighbor not in area and cell_at(grid, *neighbor) == character:
                area.add(neighbor)
                queue.append(neighbor)

    return area


def door_index(door_groups):
    return {
        cell: index for index, (_, cells) in enumerate(door_groups) for cell in cells
    }


# Tile layers
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

            if character in DOOR_KEYS:
                layers["Door_Tiles"][y][x] = door_gid(grid, x, y)

            if character == EXIT:
                layers["Floor_Decor"][y][x] = LADDER_GID

    return layers


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


# Decor
def add_decor(grid, layers, rng):
    treasure = treasure_cells(grid)
    add_top_wall_decor(grid, layers["Wall_Decor"], treasure, rng)
    add_side_torches(grid, layers["Wall_Decor"], treasure)
    add_treasure_candles(grid, layers["Floor_Decor"], treasure, rng)
    add_floor_clutter(grid, layers, treasure, rng)


def add_top_wall_decor(grid, wall_decor, treasure, rng):
    for run in top_wall_runs(grid):
        run = [(x, y) for x, y in run if (x, y + 1) not in treasure]
        torches = evenly_spaced(run, TORCH_SPACING, TORCH_MIN_RUN)
        torches = [cell for cell in torches if not above_door(grid, cell)]
        for x, y in torches:
            wall_decor[y][x] = TORCH_GID

        for left, right in zip(torches, torches[1:]):
            if rng.random() < BANNER_CHANCE:
                x = (left[0] + right[0]) // 2
                wall_decor[left[1]][x] = BANNER_GID

        for x, y in run:
            if wall_decor[y][x] or has_decor_beside(wall_decor, x, y):
                continue
            if above_door(grid, (x, y)):
                continue
            if rng.random() < WALL_RING_CHANCE:
                wall_decor[y][x] = rng.choice(WALL_RING_GIDS)


def top_wall_runs(grid):
    runs = []
    for y, row in enumerate(grid):
        run = []
        for x, character in enumerate(row):
            if character == WALL and is_open(cell_at(grid, x, y + 1)):
                run.append((x, y))
            elif run:
                runs.append(run)
                run = []
        if run:
            runs.append(run)

    return runs


def add_side_torches(grid, wall_decor, treasure):
    for side, gid in ((1, SIDE_TORCH_GID), (-1, SIDE_TORCH_GID | FLIP_HORIZONTAL)):
        for run in side_wall_runs(grid, side):
            for x, y in evenly_spaced(run, SIDE_TORCH_SPACING, SIDE_TORCH_MIN_RUN):
                floor_x = x + side
                if (floor_x, y) in treasure:
                    continue
                if grid[y][floor_x] in DOOR_KEYS or wall_decor[y][floor_x]:
                    continue
                wall_decor[y][floor_x] = gid


def side_wall_runs(grid, side):
    runs = []
    for x in range(len(grid[0])):
        run = []
        for y in range(len(grid)):
            if is_side_wall(grid, x, y, side):
                run.append((x, y))
            elif run:
                runs.append(run)
                run = []
        if run:
            runs.append(run)

    return runs


def is_side_wall(grid, x, y, side):
    return (
        grid[y][x] == WALL
        and is_open(cell_at(grid, x + side, y))
        and not is_open(cell_at(grid, x, y - 1))
        and not is_open(cell_at(grid, x, y + 1))
    )


def add_treasure_candles(grid, floor_decor, treasure, rng):
    for x, y in sorted(treasure):
        if grid[y][x] == FLOOR and is_corner(grid, x, y):
            floor_decor[y][x] = rng.choice(CANDLESTICK_GIDS)


def treasure_cells(grid):
    start = find_cells(grid, {PLAYER})[0]
    door_groups = find_door_groups(grid)
    door_at = door_index(door_groups)

    every_door = set(range(len(door_groups)))
    silver_doors = {
        index
        for index, (key_id, _) in enumerate(door_groups)
        if key_id == PLACED_ITEMS[SILVER_KEY]
    }
    return flood_fill(grid, start, door_at, every_door) - flood_fill(
        grid, start, door_at, silver_doors
    )


def is_corner(grid, x, y):
    def wall_at(direction):
        return cell_at(grid, x + direction[0], y + direction[1]) == WALL

    return (wall_at(UP) or wall_at(DOWN)) and (wall_at(LEFT) or wall_at(RIGHT))


def add_floor_clutter(grid, layers, treasure, rng):
    wall_decor = layers["Wall_Decor"]
    floor_decor = layers["Floor_Decor"]

    for y, row in enumerate(grid):
        for x, character in enumerate(row):
            if character != FLOOR or wall_decor[y][x] or floor_decor[y][x]:
                continue
            if (x, y) in treasure:
                continue

            walls = {
                direction
                for direction in DIRECTIONS
                if cell_at(grid, x + direction[0], y + direction[1]) == WALL
            }
            gid = clutter_gid(walls, rng)
            if gid is not None:
                floor_decor[y][x] = gid


def clutter_gid(walls, rng):
    roll = rng.random()

    if {UP, LEFT} <= walls:
        return BIG_WEB_GID if roll < WEB_CHANCE else None
    if {UP, RIGHT} <= walls:
        return SMALL_WEB_GID if roll < WEB_CHANCE else None
    if walls:
        return rng.choice(RUBBLE_GIDS) if roll < RUBBLE_CHANCE else None

    return rng.choice(BONE_GIDS) if roll < BONES_CHANCE else None


def evenly_spaced(run, spacing, min_length):
    if len(run) < min_length:
        return []

    count = max(1, len(run) // spacing)
    return [run[int((index + 0.5) * len(run) / count)] for index in range(count)]


def above_door(grid, cell):
    x, y = cell
    return any(cell_at(grid, x + dx, y + 1) in DOOR_KEYS for dx in (-1, 0, 1))


def has_decor_beside(decor, x, y):
    return decor[y][x - 1] != 0 or decor[y][x + 1] != 0


# Objects
def build_objects(grid):
    objects = {
        "Chests": [],
        "Entity_Spawns": [],
        "Items": [],
        "Doors": [],
        "Crates": [],
    }
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
            elif character == CRATE:
                objects["Crates"].append(("crate", left, top, TILE_SIZE, TILE_SIZE))
            elif character in PLACED_ITEMS:
                center = (left + TILE_SIZE // 2, top + TILE_SIZE // 2)
                objects["Items"].append((PLACED_ITEMS[character], *center, 0, 0))
            elif character == EXIT:
                exit_cells.append((x, y))

    objects["Entity_Spawns"].append(("Exit", *cells_rect(exit_cells)))

    for index, (key_id, cells) in enumerate(find_door_groups(grid), start=1):
        properties = {"door_id": f"door_{index}", "key": key_id}
        objects["Doors"].append(("door", *cells_rect(cells), properties))

    return objects


def cells_rect(cells):
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    return (
        min(xs) * TILE_SIZE,
        min(ys) * TILE_SIZE,
        (max(xs) - min(xs) + 1) * TILE_SIZE,
        (max(ys) - min(ys) + 1) * TILE_SIZE,
    )


# Writing the TMX
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

        for object_name, x, y, object_width, object_height, *extra in group_objects:
            attributes = {
                "id": str(object_id),
                "name": object_name,
                "x": str(x),
                "y": str(y),
            }
            if object_width:
                attributes["width"] = str(object_width)
                attributes["height"] = str(object_height)
            object_element = ET.SubElement(group, "object", attributes)

            if extra:
                properties_element = ET.SubElement(object_element, "properties")
                for property_name, value in extra[0].items():
                    ET.SubElement(
                        properties_element,
                        "property",
                        {"name": property_name, "value": value},
                    )
            object_id += 1

    map_element.set("nextlayerid", str(next_id))
    map_element.set("nextobjectid", str(object_id))

    tree = ET.ElementTree(map_element)
    ET.indent(tree, space=" ")
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)


def layer_csv(rows):
    lines = [",".join(str(gid) for gid in row) for row in rows]
    return "\n" + ",\n".join(lines) + "\n"


# Grid helpers
def is_open(character):
    return character not in (WALL, VOID)


def cell_at(grid, x, y):
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        return grid[y][x]

    return VOID


def find_cells(grid, characters):
    return [
        (x, y)
        for y, row in enumerate(grid)
        for x, character in enumerate(row)
        if character in characters
    ]


# Entry point
def main():
    path = sys.argv[1]
    grid = read_grid(path)

    map_name = os.path.splitext(os.path.basename(path))[0]
    rng = random.Random(map_name)
    layers = build_tile_layers(grid, rng)
    add_decor(grid, layers, rng)
    objects = build_objects(grid)

    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = os.path.join(MAPS_FOLDER, f"{map_name}.tmx")

    write_tmx(output_path, layers, objects, len(grid[0]), len(grid))
    print(f"Saved {output_path} ({len(grid[0])}x{len(grid)} tiles)")


if __name__ == "__main__":
    main()
