# Dungeon Sprint: Project Documentation

## 1. What this document is

`README.md` covers what the game is, how to install it, and how to play it. This file explains how the code works: how the project is organized, what every module does, how one frame of gameplay runs, what shape the data takes, and how to add new content.

The code itself has no docstrings on purpose. Explanations live here so the source stays short and readable. Comments in the code are kept only where a line would be unclear on its own.

## 2. Design rules

These are the rules the project was built around. New code should follow them.

**One job per module.** Every file does one thing. `systems/roll.py` only knows about rolling, `systems/health.py` only knows about health, and so on. If a file starts doing two jobs, split it.

**Folders by kind.** `states/` holds screens (the gameplay state and the menus), `world/` everything that makes up a floor (map loading, tiles, objects on the floor), `entities/` the player and enemies, `items/` item data (classes, database, sprite layouts, loot tables), `systems/` the rules, `ui_components/` reusable UI, and `tools/` developer scripts.

**Services are modules of functions.** Shared behaviour lives in `systems/` as plain functions. A system takes the data it works on as arguments and either changes it in place or returns a new value. For example, `take_damage(health, amount)` changes a health dict, and `steer(...)` returns a new velocity.

**Identity is plain data.** An entity's state is stored as simple dicts on the object, and the systems operate on those dicts:

| Dict | Created by | Used by |
| --- | --- | --- |
| `health` | `systems.health.new_health` | `health`, `combat`, `consumables`, `health_bar` |
| `roll` | inline in `Player.__init__` (holds `direction` and two timers from `new_timer`) | `systems.roll`, `combat`, `Player` |
| `invulnerability` | `systems.timer.new_timer` (Player and Enemy) | `timer`, `combat`, `Player.draw` |
| `heal_cooldown` | `systems.timer.new_timer` (Player) | `timer`, `consumables` |
| `death_timer` | `systems.timer.new_timer` (Run) | `timer`, `Run.update` |
| `animation` | `systems.animation.new_animation` | `systems.animation` |
| `inventory` | `systems.inventory.new_inventory` | `inventory`, `interact`, `consumables`, `inventory_ui` |
| `stats` | `systems.stats.compute_stats` | `Player` movement and roll |
| `intent` | `systems.input.read_input` | `Player` and `Run` |

**Rules are separate from application.** Systems decide *what happens* (how fast you accelerate, whether a roll can start, what a chest drops). Entities and states decide *when* to apply them (the player calls `try_start_roll` when the roll intent is set). Content such as enemy stats, loot tables and texture layouts is kept in `*_data.py` files, separate from the logic that reads it.

**Code style.**
- Names are explicit and not abbreviated (`move_direction`, `game_state_manager`, `equipment_slot_x`). Short names are fine only for things like `pos`, `dt`, `x` and `y`.
- File and folder names are snake_case. Classes are PascalCase. Constants are UPPER_SNAKE_CASE.
- No type hints and no docstrings. Comments are fine when they are accurate, and section comments are plain `# Like this`.
- Module-private **caches and state** start with an underscore (`_IMAGE_CACHE`, `_MASK_CACHE`, `_current_music_name`), meaning "don't touch this from outside". Functions and methods never do.
- **Layout standard** (every file follows it; `ui_components/hud.py` was the model):

  ```
  imports (isort groups)

  # Group label                     ← one comment line per group of constants
  CONSTANT = value  # unit or meaning, when it isn't obvious
  CONSTANT = value
                                    ← one blank line between groups, two after the last
  module helpers                    (only those used by this file)

  class:
      __init__: attributes in labelled groups (# Movement, # Health, ...)
      lifecycle first: enter, update, draw
      then the other methods top-down, in the order they're called
  ```

  Function modules (`systems/`, the tools) put their public functions first, in the order a caller uses them, then the helpers those call. Long modules split their functions with section comments (`ascii_to_tmx.py`: reading, solvability, tile layers, decor, objects, writing, grid helpers, entry point). Magic numbers become named constants with their unit (`INVENTORY_SLOT_COUNT`, `CURSOR_OFFSET`, the slider's `KNOB_WIDTH`), so every value has a name and lives in one place.
- Imports are named (never `import *`), unused imports are removed, and they are grouped as standard library, then third-party, then project, alphabetical within each group.
- Formatting is done by Black with its default 88-character line length.

## 3. Running and tooling

**Setup (Windows, from the project folder):**

```bash
python -m venv venv
```

```bash
venv/Scripts/python -m pip install -r requirements.txt
```

`requirements.txt` pins `pygame-ce==2.5.7` and `PyTMX==3.32`. Note that this is pygame-ce (community edition), not plain pygame. Features like `get_just_pressed` and `FRect` only exist in pygame-ce.

**Run the game:**

```bash
venv/Scripts/python main.py
```

Always run from the project root. Asset paths such as `Assets/Maps/Dungeon_Level_One.tmx` and the settings file `settings.json` are relative to the current folder.

**Formatting with Black.** Black is not in `requirements.txt`. Install it into the venv once with `venv/Scripts/python -m pip install black`, then:

```bash
venv/Scripts/python -m black .
```

Use `--check` to see whether anything needs formatting without changing files.

A trailing comma after the last item of a bracketed list tells Black to keep it exploded, one item per line (its *magic trailing comma*). So `for (dx, dy,) in ...` gets split over four lines; leave the comma out to keep a short list on one line.

**Sorting imports with isort.** `pyproject.toml` sets isort's `profile = "black"`, so the two tools agree. Imports are in groups separated by a blank line: the standard library, then third-party packages (`pygame`, `pytmx`), then the project's own modules. Within a group, plain `import x` lines come first, then the `from x import y` lines, each alphabetical:

```python
import os
import sys
from collections import deque

import pygame

from constants import TILE_SIZE
```

```bash
venv/Scripts/python -m isort .
```

As with Black, `--check` only reports.

**`tools/line_counter.py`.** Counts lines in every `.py` file (skipping the `IGNORED_FOLDERS`: `venv`, `.venv`, `.git` and `__pycache__`) and rewrites the "Project Statistics" section at the end of `README.md`.

**Running tools.** Tools that import project code such as `constants` are run as modules from the project root, with `-m` and a dotted name instead of a file path. `python tools/x.py` puts only the `tools/` folder on Python's import path, so `from constants import ...` fails with `ModuleNotFoundError`; `python -m tools.x` puts the current folder (the project root) on the path instead.

**`tools/make_sprite.py`.** Generates the game's own pixel art from text. Run it from the project root after editing any sprite; it regenerates every sprite, and an unchanged sprite comes out byte-identical:

```bash
venv/Scripts/python -m tools.make_sprite
```

Each sprite is an entry in `SPRITES`, keyed by name, holding three things:

```
SPRITES = {
    "panel_frame": {
        "path":   "Assets/UI/panel_frame.png",   where the PNG is saved
        "colors": {"o": PALETTE_SOOT, ...},       letter -> palette constant, for this sprite only
        "rows":   [".oooooooooo.", ...],         one string per pixel row, one letter per pixel
    },
    "speed_boots": {...},
}
```

`make_sprite(name, sprite)` draws one entry and `__main__` loops over them all. Letters only mean something inside their own sprite, so every sprite can use `o` for its outline, while `m` is the stone ring in the frame but mid leather in the boots. Colors come from the `PALETTE_*` constants in `constants.py`, so the art can only use the game's colors, and `.` is left transparent. The image size comes from the rows themselves (width from the first row, height from the row count), so editing the rows is all that's needed. The surface is created with `pygame.SRCALPHA`, which starts fully transparent, so skipped `.` pixels stay see-through; without it a new surface starts opaque black. Sprites are saved at 1× and scaled up by the game.

Typos in text art would otherwise fail silently (a short row leaves transparent pixels, an unknown letter would be skipped), so the tool stops with a `ValueError` naming the sprite and the spot instead: `speed_boots: row 4 is 15 wide, expected 16`, or `speed_boots: unknown letter 'z' at (3, 7)`.

The sprites:
- **`panel_frame`** (12×12, `Assets/UI/panel_frame.png`): the 9-slice frame used by the HUD and the inventory (section 6). `o` outline `PALETTE_SOOT`, `m` stone ring `PALETTE_WALL`, `l` light edge `PALETTE_LEATHER`, `s` shadow edge `PALETTE_SHADOW`, `f` fill `PALETTE_VOID`.
- **`speed_boots`** (16×16, `Assets/Items/speed_boots.png`): one boot in side view with a wing on the heel, filling the full width. `o` outline `PALETTE_VOID` (like the health potion), leather in three shades (`d` `PALETTE_CLAY`, `m` `PALETTE_LEATHER`, `l` `PALETTE_TAN`, lit from the top-left), `s` sole and buckle `PALETTE_STEEL`, and the wing in `w` `PALETTE_ICE` with `a` `PALETTE_AZURE` shading.
- **`padlock_silver`** and **`padlock_gold`** (7×10, `Assets/Objects/padlock_silver.png` and `padlock_gold.png`): the locks drawn on locked doors, so players can match a door to its key. Both entries use the same `PADLOCK_ROWS` constant, so the shape is defined once and only the colors differ: `o` outline and `k` keyhole in `PALETTE_VOID`, then light (`l`, top and left), mid (`m`) and dark (`d`, right side), in `PALETTE_ICE` / `PALETTE_STEEL` / `PALETTE_STONE` for silver and `PALETTE_CANDLE` / `PALETTE_GOLD` / `PALETTE_BRASS` for gold, lit from the top-left like the boots.

**`tools/preview_map.py`.** Renders a `.tmx` map to one PNG, the way the game sees it, with markers on top, so a floor can be checked without playing it. With no arguments it previews every map in `FLOOR_ORDER`; pass map paths to preview only those:

```bash
venv/Scripts/python -m tools.preview_map
venv/Scripts/python -m tools.preview_map Assets/Maps/Dungeon_Level_One.tmx
```

Images are saved to `map_previews/<map name>.png`, a folder listed in `.gitignore` because the images are generated.

- **It reuses the game's loader.** `preview_map(map_path, font)` calls `load_floor_data` from `map_loader.py`, the same function `Run` uses, so the preview always matches the game, and if map loading changes the preview follows; the tool only draws what it's given. The loader calls `.convert()` and `load_image`, which need a display, so `main()` first opens a hidden 1×1 window with `pygame.display.set_mode((1, 1), pygame.HIDDEN)`.
- **Drawing.** It draws on a `.copy()` of the map surface, so the loader's surface is never touched, then the walls, decor, doors, chests and crates in the game's order (decor after walls, since torches, banners and rings sit on wall tiles), each blitted at its `rect.topleft` with no camera (the whole map is the "screen"), then the placed items (keys) with their real images, centered on their positions. `main` builds the item database once with `initialize_item_database()` and passes it to `preview_map(map_path, font, item_database)`, so the images are the game's own. Then the markers:
  - **Door groups:** one `door_id` label per group. A door can be several tiles wide, so a `set` of already-labeled ids skips the rest; a set is a collection with fast "have I seen this?" checks.
  - **Enemy spawns:** a 1-pixel `PALETTE_BLOOD` box at each spawn, labeled with the first three letters of the type (`enemy_type[:3]`, a slice), so `Skull` and `Skeleton` show as `SKU` and `SKE`.
  - **Player spawn:** a `PALETTE_AZURE` dot with a `PALETTE_VOID` ring (a bigger circle drawn first). The two spawn kinds use different reference points, matching the game: the player spawn is the player's center, an enemy spawn is the enemy's top-left.
  - **The exit:** a 1-pixel `PALETTE_GOLD` outline around the exit *rect*, with the ladder tile visible inside it.
  - Labels come from `draw_label(surface, font, text, pos)`: Silkscreen at `LABEL_FONT_SIZE` 8, its native size, so it's perfectly crisp at 1× and scales up with the image, in `PALETTE_ICE` on a `PALETTE_VOID` box 1 pixel bigger on every side (`inflate(2, 2)`), so it reads over any tile.
- **Cropping and scaling.** Maps are usually bigger than the dungeon in them (Level One is 160×112 tiles), so the image is cropped to the walls and scaled up:

  ```
  bounds  = first wall rect .unionall(every other wall rect)     smallest rect containing all walls
  bounds  = bounds.inflate(2 × PREVIEW_MARGIN, 2 × PREVIEW_MARGIN)  PREVIEW_MARGIN = 2 tiles on each side
  bounds  = bounds.clip(whole image)                           stays inside the image if walls touch the edge
  cropped = preview.subsurface(bounds)                         a view of that area, not a copy
  image   = scale_by(cropped, PREVIEW_SCALE)                   PREVIEW_SCALE = 2
  ```

- **Arguments.** `sys.argv` is the list of words typed after the command (`sys.argv[0]` is the script), so `sys.argv[1:]` is the map paths, if any; when it's empty, the `or` falls back to `FLOOR_ORDER`. `dict.fromkeys(FLOOR_ORDER)` removes duplicates while keeping the order, because dict keys are unique, so a map listed twice is drawn once. `os.path.basename` and `os.path.splitext` turn `Assets/Maps/Dungeon_Level_One.tmx` into `Dungeon_Level_One` for the file name.
- A map with no walls would crash at `wall_rects[0]` (an `IndexError`), since the crop is based on the walls. Every real map has walls, so this only matters for a half-made map.

**`tools/ascii_to_tmx.py`.** Turns a floor sketched as text into a Tiled map that the game, the preview tool and Tiled all load. The file reads top to bottom like the pipeline: the legend and GID constants, then section comments for reading and checking, solvability, tile layers, decor, objects, writing the TMX, grid helpers, and the entry point. The text sources live in `Assets/Maps/Source/`, and the map is written next to the tilesets in `Assets/Maps/`, named after the source file, unless a second argument gives the output path:

```bash
venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/test_room.txt
venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/test_room.txt Assets/Maps/other_name.tmx
```

The legend:

| Char | Meaning |
|---|---|
| `#` | wall (autotiled) |
| `.` | floor |
| space | void, outside the dungeon |
| `@` | player spawn (exactly one) |
| `X` | exit, drawn as a ladder down; use one per floor (several cells would become one combined exit rect) |
| `C` | chest |
| `w` / `k` | Skull (drawn as a blue **w**isp) / Skeleton spawn (`ENEMY_TYPES`) |
| `B` | breakable crate (a **b**ox): blocks until the player rolls into it; it has floor under it, and the solvability check treats it as passable, since it can always be rolled through |
| `S` / `s` | **silver** door tile / silver key: the main path (`DOOR_KEYS`, `PLACED_ITEMS`) |
| `G` / `g` | **gold** door tile / gold key: treasure rooms |

A key's letter matches its door's letter. A door is two touching tiles of the same letter, in a row or column; the converter finds the groups itself and numbers them, so ids are never typed. Place one key of the right color per door group.

Everything except `#` and space has floor under it; `is_open(character)` is that rule, and the rest of the converter leans on it.

```
ASCII text file ──read_grid──▶ grid (list of equal-length strings) ──build──▶ .tmx file
                                  ▲
       a procedural generator ────┘  (produces the grid directly, skipping the text)
```

The **grid** is the shared format: hand-written and generated levels go through the same autotiling, so they get identical walls. Keeping the rules separate from the file writing also means the game could one day build a generated grid straight into a level in memory.

- **Reading.** `read_grid(path)` splits the file into rows (`splitlines()` also handles Windows `\r\n` line endings), drops blank lines at the end, and pads every row with spaces to the widest one (`ljust`), so trailing spaces never need typing. `cell_at(grid, x, y)` returns the character, or void outside the grid, so edges need no special cases.
- **Validation** (`validate_grid`, plus checks while building) stops with a `ValueError` naming the spot instead of writing a broken map: an unknown character; not exactly one `@`; no `X`; an open tile whose up, right, down or left neighbor is void (a gap in the wall the player could walk out through); a wall only 1 tile thick (floor on both sides, which no tile piece fits); a door tile with no partner next to it; and an exit that can't be reached (the solvability check below).
- **Autotiling walls** (`wall_gid(grid, x, y, rng)`). The rules were learned from the hand-built Level One, by grouping its wall tiles by which neighbors are open floor. They're checked in priority order and the first match wins (y grows downward, so `(0, 1)` is below):

  | The wall has open floor… | Piece | GIDs |
  |---|---|---|
  | below | top wall face | `TOP_WALL_GIDS` 2–5 |
  | above, and to the left | inner corner | `INNER_CORNER_WEST_GID` 51 |
  | above, and to the right | inner corner | `INNER_CORNER_EAST_GID` 54 |
  | above | bottom ledge | `BOTTOM_WALL_GIDS` 42–45 |
  | to its right | left side wall | `LEFT_WALL_GIDS` 11, 21, 31 |
  | to its left | right side wall | `RIGHT_WALL_GIDS` 16, 26, 36 |
  | only diagonally: se / sw / ne / nw | outer corner | `OUTER_CORNER_GIDS` 1 / 6 / 41 / 46 |
  | nowhere | solid | `VOID_GID` 79 |

  `open_at(dx, dy)` is a nested function: defined inside `wall_gid`, it can use `grid`, `x` and `y`, so each rule reads like the table. Where a piece has variants, `rng.choice` picks one so long walls don't repeat. Rooms are separated by walls at least 2 thick with doors in a short corridor, as in Level One; each room then gets its own corner pieces with solid 79 between them.
- **The exit's look** (`LADDER_GID` 40). Under each `X`, `build_tile_layers` puts the tileset's ladder (a ladder going down into a dark hole, with its rails sticking up out of it) on the `Floor_Decor` layer, over the normal floor. The exit's *logic* is still the `Exit` object (a rect); its *look* lives in the map data, so the game draws it as an ordinary decor tile with no exit-specific drawing code. Changing the exit art later means changing `LADDER_GID` and reconverting. The ladder is also what the interaction outline goes around when the player is at the exit.
- **Floors** (`FLOOR_PATTERN`). Floor tiles 12–15, 22–25 and 32–35 aren't interchangeable variants but one 4×3 slab picture cut into 12 pieces, and Level One lays it out as a repeating pattern (every floor tile in it follows the pattern). So the piece is chosen by position, not chance; `%` makes the pattern repeat, and the `- 1` starts a fresh slab at the first tile inside a room's top-left wall:

  ```
  floor GID = FLOOR_PATTERN[(y − 1) % 3][(x − 1) % 4]
  ```

  Walls and the void get `VOID_GID` on the Floor layer, as in the hand-made map.
- **Door tiles** (`door_gid`). A door is 2 tiles, and its partner (the same letter next to it) decides the half: partner below → top half (47), above → bottom half (57), right → left half (67), left → right half (68). Both colors use the same wooden door art; the color is data on the door (see the `Doors` objects below).
- **Door groups** (`find_door_groups(grid)`). `same_character_area(grid, start)` is a flood fill that only spreads into the **same character**, so from any door tile it finds its whole door. `find_door_groups` walks the door tiles in reading order (top to bottom, left to right) and returns `(key item id, set of cells)` pairs, for example `("gold_key", {(20, 4), (21, 4)})`. `seen |= cells` (union into) marks the group's cells so its second tile isn't counted again. A group that isn't exactly 2 tiles is a `ValueError` ("doors are 2 tiles"), where before a 3-tile door would silently have drawn the wrong pieces. Reading order keeps the numbering stable, so reconverting gives an identical file.
- **Layers** (`build_tile_layers(grid, rng)`) are 2D lists of GIDs (0 for empty), one per `TILE_LAYER_NAMES` entry, in the names and order `map_loader` expects. Each is built with `[[0] * width for _ in range(height)]`, which makes separate rows; `[[0] * width] * height` would list one row `height` times, so writing to one row would change them all. `Wall_Decor` and `Floor_Decor` only get the ladder here; `add_decor` fills them next (below).
- **Decor** (`add_decor(grid, layers, rng)`, called in `main` right after `build_tile_layers`). Decor is placed by rules, so floors need no extra legend characters. It runs **after** the walls, with the same seeded `rng`, so adding decor didn't change any existing wall tile, and a map converts the same way every time. Everything goes into the `Wall_Decor` and `Floor_Decor` layers, which the loader already turns into `DecorTile`s, so the game, the preview and Tiled all show it with no extra code. The rules, in the order they run (an earlier step claims a tile first):

  ```
  TOP WALLS   (a wall tile with floor below it)                         → Wall_Decor
    torch       evenly spaced per run of top wall, 1 per TORCH_SPACING (7),
                none on runs < TORCH_MIN_RUN (4), never above a door      TORCH_GID 91
    banner      between two neighbouring torches, BANNER_CHANCE (50%)     BANNER_GID 75
    wall ring   any other top-wall tile, WALL_RING_CHANCE (8%),
                never beside other decor or above a door                 WALL_RING_GIDS 76/77
  SIDE WALLS  (wall with floor beside it, none above or below)          → Wall_Decor
    side torch  on the FLOOR tile beside the wall, 1 per SIDE_TORCH_SPACING (8),
                runs ≥ SIDE_TORCH_MIN_RUN (6); mirrored on right walls    SIDE_TORCH_GID 92
  TREASURE    (floor only reachable through a gold door)                → Floor_Decor
    candlestick every corner                                              CANDLESTICK_GIDS 94/96
  FLOOR       ('.' tiles with no decor yet, not treasure)               → Floor_Decor
    big web     top-left corner (wall up + left), WEB_CHANCE (30%)        BIG_WEB_GID 65
    small web   top-right corner (wall up + right), 30%                   SMALL_WEB_GID 66
    rubble      any other tile beside a wall, RUBBLE_CHANCE (2.5%)        RUBBLE_GIDS 50/60
    bones       open floor (no wall beside it), BONES_CHANCE (1.5%)       BONE_GIDS 69/78
  ```

  Where each piece sits comes from how the hand-made Level One placed it: the side torch's art leans on the left edge of its tile, so it stands on the floor tile right of a left wall; the webs fill the corner their art points into.
  - **Runs.** `top_wall_runs(grid)` walks each row and collects unbroken stretches of "wall with floor below"; an opening in the wall ends a run, so torches are spaced per stretch of wall, not across a passage. `side_wall_runs(grid, side)` is the same walk turned on its side (columns, top to bottom), with `is_side_wall(grid, x, y, side)` as the test; `side` is both the direction from the wall to its floor (`+1` floor to the right, `-1` to the left) and where the torch goes (`x + side`). Its "not open above or below" checks keep corners out of the runs.
  - **Even spacing** (`evenly_spaced(run, spacing, min_length)`). The run is cut into `count` equal slices and a torch goes in the **middle** of each, so every torch stays away from the run's ends, and so from openings:

    ```
    count    = max(1, len(run) // spacing)
    position = int((index + 0.5) × len(run) / count)      for index in 0 … count − 1

    run of 22, spacing 7 → count 3, slice ≈ 7.33 → tiles 3, 11, 18
    ·  ·  ·  T  ·  ·  ·  ·  ·  ·  ·  T  ·  ·  ·  ·  ·  ·  T  ·  ·  ·
    ```

    `zip(torches, torches[1:])` pairs each torch with the next (`[a, b, c]` → `(a, b), (b, c)`): the gaps where banners can go. `above_door(grid, cell)` is true when a door tile is below the cell or diagonally below it; `has_decor_beside(decor, x, y)` checks the tiles to the left and right.
  - **Mirroring** (`FLIP_HORIZONTAL`, `0x80000000`). TMX marks a mirrored tile by setting the top bit of its GID, and `|` (bitwise OR) turns that bit on without touching the GID's own bits. pytmx reads the flag and returns an already-flipped image, so the loader needed no change:

    ```
    92                = 0b0000…0000 0101 1100
    92 | 0x80000000   = 0b1000…0000 0101 1100     same tile, "draw it flipped horizontally"
    ```

  - **Treasure** (`treasure_cells(grid)`). Worked out once in `add_decor` and passed to every step. It reuses the solvability flood fill: what the player can reach with **every** door open, minus what they can reach with only the **silver** doors open (`key_id == PLACED_ITEMS[SILVER_KEY]`). The set includes the gold door's tiles and the corridor behind it. Treasure areas get **only** candlesticks: top-wall decor drops wall tiles whose floor below is treasure (filtering the run **before** spacing, so a partly-treasure run is spaced over what's left), side torches skip a treasure floor tile, and clutter skips treasure tiles. So a treasure room is lit only by its candles and reads as special. `door_index(door_groups)` builds the `cell → door group index` lookup used by both this and `can_finish`.

    ```
    reach with EVERY door open     ████████████████████
    reach with only SILVER open    ██████████████
    treasure = first − second                    ██████      (set difference)
    ```

  - **Corners** (`is_corner(grid, x, y)`): a wall above **or** below, **and** a wall left **or** right. That's all four corners of a room, but no tile of a 2-wide corridor, whose ends touch a door or open floor. The candles loop over `sorted(treasure)`: `rng.choice` is called in loop order, and a set's order is an implementation detail, so sorting keeps the picks clearly stable.
  - **Clutter** (`add_floor_clutter`, `clutter_gid(walls, rng)`). `walls` is the set of directions (`UP`, `RIGHT`, `DOWN`, `LEFT`, unpacked from `DIRECTIONS`) with a `WALL` next to the tile; doors aren't walls. `{UP, LEFT} <= walls` is the subset check, "are both of these in `walls`?". Each tile uses **one** roll compared to its own chance, like a loot table, and uses it up even when nothing is placed, so results stay reproducible. Only `.` tiles get clutter, so it never lands under a chest, key, spawn, crate or the ladder.
  - **All values are first-pass**, to tune by playing.
- **Objects** (`build_objects(grid)`) are `(name, x, y, width, height)` tuples in pixels, with the names `map_loader` looks for, using the game's reference points: `Player` at the tile's center (the game sets `rect.center` to it); `Enemy_<type>` and `chest` at the tile's top-left; and one `Exit` rect covering every `X` cell, from the smallest x and y to the largest (`+ 1` to include the last cell). Placed items (`PLACED_ITEMS`: `s` → `silver_key`, `g` → `gold_key`) are point objects named by their item id, at the tile's center, because `GroundItem` places itself by `rect.center`. Chests go in a `Chests` object group, crates (`crate`, 16×16, placed by their top-left like chests) in `Crates`, placed items in `Items`, doors in `Doors`, and everything else in `Entity_Spawns`. The exit's and the doors' rects come from `cells_rect(cells)`, the bounding rect of a set of cells in pixels (shared, so the formula lives in one place).

  **Doors are objects** with **properties**: one `door` object per group, covering its two tiles, numbered `door_1`, `door_2` … (`enumerate(..., start=1)`), carrying which key opens it:

  ```xml
  <object id="8" name="door" x="320" y="64" width="32" height="16">
   <properties>
    <property name="door_id" value="door_1" />
    <property name="key" value="gold_key" />
   </properties>
  </object>
  ```

  This replaced the old `Logic_Layer`, a tile layer whose tiles came from `Logic_Tiles.tsx` (1 MB, of which only 3 tiles had ids). So there's no longer a limit on door groups, and the key a door needs is stored in the map data. A door object is a 6-item tuple, its properties dict last.
- **Writing** (`write_tmx`). A `.tmx` is XML, built with Python's `xml.etree.ElementTree` (`ET`). Objects are unpacked as `object_name, x, y, object_width, object_height, *extra`: `*extra` (star unpacking, the opposite of `*center` when building a tuple) collects whatever is left over into a list, `[]` for ordinary objects and `[properties]` for a door, which then gets a nested `<properties>` element with one `<property name=… value=…>` per entry, the shape Tiled itself writes. The rest: `ET.Element` makes the `<map>` root, `ET.SubElement` adds the tileset references (`TILESETS`: `Dungeon.tsx` at 1, `Logic_Tiles.tsx` at 101), one `<layer>` per tile layer with its GIDs as CSV text (`layer_csv`, the same format Tiled writes), and the object groups. Attribute values must be strings. Every layer and object group gets a unique id from `next_id` and every object one from `object_id`, and `nextlayerid` / `nextobjectid` tell Tiled which numbers to use next if the map is edited by hand. Spawn points have no size, so their width and height are left out. `ET.indent` adds line breaks and indentation, so the file and its diffs are readable.
- **Solvability check** (`can_finish`, run at the end of `validate_grid`). It answers: can a player starting at `@` reach the exit, picking up keys and opening doors along the way? It follows the game's rules: a door group opens with **its own color** of key (any silver key opens any silver door), and each group uses up one key. Keys are guaranteed by design (see the loot notes in section 8), and this is what checks it. Hard's generated floors will rely on the same check to reject unwinnable layouts.
  - **Flood fill** (`flood_fill(grid, start, door_at, opened)`): starting from `@`, it spreads to every open neighbor, then their neighbors, and so on, but never through a door that's still closed. What it covers is everywhere the player can walk right now. It's a breadth-first search: `queue` is a `deque` (a list built for removing from the front quickly), and `popleft()` takes the oldest cell, so the fill spreads outward in rings; `reachable` is a set, so "already seen?" is instant, and it's also the result. Three `continue`s skip a neighbor that was already seen, that's a wall or void, or that's a closed door: a cell in `door_at` (a dict from each door cell to its group number) whose group isn't in `opened`.

    ```
    @ . . . 1 . . X      reachable now: the 4 cells left of door 1
    ```

  - **Opening doors** (`can_finish(grid, start, door_groups, opened=frozenset())`): `opened` holds the numbers of the door groups opened so far. If the exit isn't reachable, it looks at each closed door group touching the reachable area and checks whether a key of **that door's color** is in hand, and if so calls itself with that group added. That's recursion; it ends because each call opens one more door. Different doors lead to different places, so it tries every choice, and returns `True` as soon as one works.

    ```
    keys in hand (per color) = keys of that color found in the reachable area
                               − doors of that color already opened

    test room: s . . S . X            silver door group 0, silver key s before it
    can_finish(opened = {})           exit not reached; group 0 is silver, 1 silver key found, 0 used → try it
    └─ can_finish(opened = {0})       reachable now includes X → True

    with g instead of s:              group 0 is silver, 0 silver keys found → nothing to try → False
    ```

    Counting every key in the reachable area is valid because that area only ever grows as doors open, so a player can always collect all of it before choosing the next door. `door_at` maps each door cell to its group number (a dict comprehension with two `for`s); `touching` is the set of group numbers next to the reachable area, and `touching - opened` the closed ones. `PLACED_ITEMS.get(character)` gives the item id of a key character and `None` for anything else, so only keys of the right color are counted. `opened | {index}` makes a **new** set for each try, so the tries don't affect each other. `any(...)` is true if at least one item is, and `sum(1 for ...)` counts matches.
  - **Why the default is `frozenset()`:** a default value is created once, when the function is defined, and shared by every call, so a mutable default like `set()` or `[]` can quietly carry changes from one call into the next, a classic Python trap. A `frozenset` can't be changed, so it's safe.
  - Helpers and constants: `find_cells(grid, characters)` lists the positions of the given characters (a comprehension with two `for`s, rows then cells); `SILVER_KEY` (`"s"`) and `GOLD_KEY` (`"g"`) name the key characters, and `DOOR_KEYS` maps each door letter to the key item that opens it; `DIRECTIONS` holds the 4 neighbor offsets (up, right, down, left), shared by the void check and the flood fill.
- **Reproducible output.** `random.Random(map_name)` is a generator seeded with the map's name: the same seed always gives the same "random" picks, so converting the same file twice writes an identical map and `git diff` only shows real changes, while each map still gets its own variety.
- **Two typos from building it, worth remembering** because both were valid Python that ran and quietly did the wrong thing: `{WALL < FLOOR, ...}` (a comparison, `False`, instead of two set items) and `cell_at(grid, x + dx, y=dx)` (a keyword argument setting `y` to `dx`). The cure is checking real output, not just that the code runs.
- **Doors can guard optional loot.** A door doesn't have to block the way to the exit: on Easy floor 1 the gold door locks a treasure room with a chest, so the gold key and the chest are a route choice, while the silver door is on the main path. The solvability check only proves the **exit** can be reached, so it can't tell a required door from an optional one; that's a design decision, checked by playing.
- **Enemies are never optional.** The exit stays shut until every enemy on the floor is defeated (see "What `interact` does"), so an enemy placed in a side room makes that room part of the required route. Keep optional rooms empty, or accept that they aren't optional. The solvability check doesn't know this either.
- **Limits:** doors exactly 2 tiles, walls at least 2 thick, only keys as placed items, and decor only by the rules above (no hand-placed decor). Converting overwrites the `.tmx`, so hand edits made in Tiled are lost on the next conversion.

**`tools/make_strip.py`.** Joins animation frames into one horizontal strip. The pack stores each animation as one file per frame (`keys_2_1.png` … `keys_2_4.png`), while the game's texture data expects one strip that `slice_frames` cuts into equal cells. The pack folder is git-ignored, so the game must never load from it: the tool **reads from the pack** and **writes into `Assets/`**, and only its output is committed. Running it needs the pack on your machine.

```bash
venv/Scripts/python -m tools.make_strip
```

It's built like `make_sprite`: `STRIPS` maps a name to `{"frames": [frame paths, in order], "path": output path}`, and `make_strip(name, strip)` handles any entry. The frame lists are list comprehensions over `range(1, 5)`, matching the pack's numbering. Every frame must be the same size, since `slice_frames` cuts equal cells, so it checks each frame against the first, using `zip(paths, frames)` to walk the two lists side by side and name the bad file in the `ValueError`. It then blits frame `index` at `index × frame width` on a transparent (`SRCALPHA`) surface and saves it. `PACK_FOLDER` and the per-folder constants (`KEYS_FOLDER`) keep the long pack paths in one place.

The strips so far:
- **`gold_key`** → `Assets/Items/gold_key_strip.png` (the pack's `keys_1`, 4 frames, a spinning gold key).
- **`silver_key`** → `Assets/Items/silver_key_strip.png` (the pack's `keys_2`, 4 frames, a spinning silver key).
- **`crate`** → `Assets/Objects/crate_strip.png` (the pack's `box_2`, a plain wooden box, 4 frames of squash and stretch: normal, tall, wide, flattened). The steel-banded `box_1` was skipped because it looks like the chest.

**`hooks/pre-commit`.** The repo's git config sets `core.hooksPath = hooks`, so this script runs before every commit. It runs `tools/line_counter.py` and stages `README.md`, so the statistics are always current. It has commented-out lines for running Black and Pylint, which are not active. A fresh clone needs `git config core.hooksPath hooks` to enable it.

## 4. Startup and the main loop

`main.py` defines `Game`. Its constructor runs in this order, and the order matters:

1. `pygame.init()`.
2. `settings.load_settings()` reads `settings.json`. It must run before the window is created, because the window needs the fullscreen setting.
3. `create_window(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen)` opens the window. It must exist before any image is loaded, because `load_image` calls `convert_alpha()`, which needs a display.
4. The system mouse is hidden and a `Cursor` is built from `Assets/Cursors/01.png` at half scale.
5. Sound: all sound effects and music are loaded and the saved volumes are applied. No music starts here.
6. The FPS counter (`FpsCounter`, see `ui_components/fps_counter.py`) is created. `Game.update` calls `fps_counter.update(dt, clock.get_fps())` every frame, and `Game.draw` draws it when the `fps_enabled` setting is on, so `Game` holds no FPS details itself.
7. A `GameStateManager` starting on `"main_menu"` is created, then the states are built and registered: `MainMenu` as `"main_menu"`, `OptionsMenu` as `"options"`, `Run` as `"run"`, and `RunEndScreen` twice, as `"game_over"` ("You Died!", red, `GAME_OVER_MUSIC`) and `"run_complete"` ("You Escaped!", green, no music of its own).
8. `self.game_state_manager.get_state().enter()` runs the first screen's `enter()`, which starts the menu music. The first state is set directly in `GameStateManager.__init__`, not through `set_state`, so its `enter()` has to be called by hand. It must come after the `add_state` calls, because `get_state()` looks the state up in the dict.

`run()` loops `update()` then `draw()` until `self.running` is false.

**`update()`:**
- Reads the event queue. A `pygame.QUIT` event (closing the window, or the Exit button) stops the loop.
- Computes `dt`, the seconds since the last frame, from `clock.tick(FRAME_RATE)`. `FRAME_RATE` is 240. Everything that moves or counts down is multiplied by `dt`, so the game runs at the same speed at any frame rate.
- Calls `update(dt)` on the current state, then updates the cursor.
- Every 0.5 seconds (`FPS_REFRESH_INTERVAL`), refreshes the FPS text. The timer subtracts the interval instead of resetting to zero, so the leftover time carries over.

**`draw()`:**
- Gets the screen with `pygame.display.get_surface()` and passes it to the current state's `draw(screen)`.
- Draws the FPS label if `fps_enabled` is on, then the cursor (last, so it is on top of everything).
- Calls `pygame.display.update()`.

After `run()` returns, `pygame.quit()` closes everything.

The window uses `pygame.SCALED`. The game always draws to a 1280x720 surface and pygame scales it to fit the real window or monitor, so all screen coordinates in the code are in that 1280x720 space.

Inside that, the run is drawn in two layers. The world is drawn at its true pixel size on a small canvas and scaled up by `GAME_SCALE` (3), so every art pixel becomes a crisp 3×3 block. The HUD is drawn afterwards at full resolution, so text stays sharp and the inventory's mouse positions stay in screen pixels:

```
1. the WORLD  →  drawn on a WORLD_WIDTH × WORLD_HEIGHT surface  →  scaled × GAME_SCALE  →  onto the screen
2. the HUD    →  drawn straight onto the screen afterwards, at full resolution
```

## 5. State flow

A *state* is any object with `update(dt)`, `draw(screen)` and `enter()`. `enter()` runs once each time the game switches to that state, and is where a state does its "on arrival" work, such as starting its music. A state with nothing to do on arrival still needs an `enter` whose body is `pass`, or the switch crashes with `AttributeError`. `GameStateManager` (`states/state_manager.py`) holds:
- `states`: a dict of name to state object.
- `current`: the name of the active state.
- `previous`: the name of the state before it.

`set_state(name)` moves `current` into `previous`, switches to `name`, then calls the new state's `enter()`. An unknown name raises `ValueError`, so a typo fails loudly instead of silently. `go_back()` switches to `previous` through `set_state`, so it calls `enter()` too.

```
         MainMenu ──"Start"──▶ Run ────player at 0 HP──▶ RunEndScreen "game_over"
              │                  │  └──exit of the last floor──▶ RunEndScreen "run_complete"
          "Options"          ESC (plays "pause")              │ (both)
              ▼                  ▼                  "Restart" ──▶ new Run
           Options ◀─────────────┘                  "Main Menu" ──▶ new Run, then MainMenu
              │
   "Main Menu" ──▶ MainMenu   "Back" ──▶ Run    (only shown when previous == "run")
```

- **MainMenu** (`states/menus/main_menu.py`): Start goes to the run, Options goes to the options menu, Exit posts a `pygame.QUIT` event so the main loop shuts down normally. `enter()` plays `MAIN_MENU_MUSIC` (`"menu_music"`).
- **Level** (`states/run.py`): the dungeon. ESC switches to options and plays the `pause` sound. When the player's health reaches 0 it plays `death`, stops the music, freezes for `DEATH_DELAY` (3.0) seconds, then switches to `"game_over"` (section 7, step 6). Climbing down the exit ladder (F) loads the next floor from `FLOOR_ORDER`, or switches to `"run_complete"` after the last one (step 7). `enter()` plays `LEVEL_MUSIC` (`"level_music"`). Unpausing calls it again, but the track keeps going instead of restarting (see `sound.py` in section 6).
- **Options** (`states/menus/options.py`): music and SFX sliders, an FPS toggle and a fullscreen toggle. Main Menu returns to the main menu. When the menu was opened from the run, it first calls `start_new_run()` so the abandoned run is thrown away. Back (`can_go_back()`) only appears when the previous state is `"run"`, so it acts as "resume". ESC does the same as Back, but only when the menu was opened from the run. In that case the menu is drawn over the dimmed, frozen run instead of a solid background. Both buttons save the settings file. `enter()` does nothing, so the pause menu keeps playing whatever music was already on.
- **RunEndScreen** (`states/menus/run_end.py`): the screen shown when a run ends, either way. It is one class created twice in `main.py` with different settings, `RunEndScreen(game_state_manager, title, title_color, music)`: the differences between the two screens are constructor arguments, not separate classes. It draws the title, the run's split times (one row per floor, then the total) and two text buttons over the frozen run. Restart and Main Menu both call `start_new_run()` (from `states/new_run.py`) first, then switch to `"run"` or `"main_menu"`. `enter()` reads the finished run's `splits`, `run_time` and `dying` from `game_state_manager.states["run"]` and renders the split table. If `music` is a track name, `enter()` stops the current music and plays it once, with `loops=0`. That's how the death screen plays `"game_over"`, and why Restart then starts the run's music again from the beginning. If `music` is `None`, as on the finish screen, the current track keeps playing.

All states are built once at startup and kept alive, so leaving and returning to the run normally resumes it where you left off. The exceptions are a death, and quitting to the main menu from the pause menu. `start_new_run(game_state_manager)` in `states/new_run.py` builds a brand new `Run(game_state_manager)`, which starts on the first floor, and registers it under `"run"` with `add_state`, which replaces the old one in the `states` dict. A rebuild resets everything the Run owns (player, enemies, chests, doors, ground items, the inventory screen) and recenters the camera, while the shared image, animation and mask caches are reused. Because the Run can be replaced, code that needs it should look it up through `game_state_manager.states["run"]` when it needs it, not keep a reference from startup. `Game.run_state` in `main.py` still points at the first Run and is not used after registration.

## 6. Folder-by-folder reference

### Root

- **`main.py`**: `Game`, the startup and main loop described above.
- **`constants.py`**: shared constants only (named `constants.py` rather than `globals.py`, which shared its name with Python's built-in `globals()` function and made `import globals` read like the built-in). `GAME_SCALE` (3) is how many screen pixels each world pixel becomes, and `WORLD_WIDTH` / `WORLD_HEIGHT` are the world canvas size, worked out from it so changing the one number switches the whole scale:

  ```
  WORLD_WIDTH  = ceil(SCREEN_WIDTH  ÷ GAME_SCALE)     3× → 427   (427 × 3 = 1281, 1 px falls off the edge)
  WORLD_HEIGHT = ceil(SCREEN_HEIGHT ÷ GAME_SCALE)     3× → 240
  ```

  `math.ceil` rounds up, so the scaled world always covers the whole screen. 2 gives 640×360 and 4 gives 320×180. Keep the scale a whole number: a screen pixel can't be split, so at 2.5× some art pixels come out 2 screen pixels wide and others 3, which looks lopsided and shimmers as the camera scrolls (smoothing instead makes it blurry).
  The rest of `constants.py`, in labelled groups: screen and timing (screen size, `FRAME_RATE`); the world canvas; art sizes (`TILE_SIZE` 16, `PLAYER_SPRITE_SIZE` 64); basic colors (`WHITE`, `RED` and so on, kept for debug drawing and later use; game art uses the palette), the tileset palette (all 34 colors in `Assets/Dungeon_Tileset.png` as `PALETTE_*` constants, grouped by family and ordered dark to light within each: darks and floors such as `PALETTE_VOID` (37, 19, 26) and `PALETTE_SHADOW` (84, 55, 64); walls, earth and wood such as `PALETTE_WALL` (110, 74, 72); reds `PALETTE_BLOOD` (188, 76, 81) and `PALETTE_ROSE`; fire and gold such as `PALETTE_TORCH` (191, 112, 77); moss and parchment; and stone, steel and ice such as `PALETTE_STONE` (144, 145, 158), `PALETTE_STEEL` (173, 193, 207) and `PALETTE_ICE` (202, 230, 245). UI and generated art use these names so everything stays on the tileset's colors. The UI color rules: steel is the normal text color, stone is secondary text such as item descriptions, and torch orange means "you can interact with this": hovered buttons and sliders, and the `Q` hotkey. In the world, the interaction outline is `PALETTE_CANDLE` when F will work and `PALETTE_STEEL` when it won't), `MENU_BACKGROUND_COLOR` (defined as `PALETTE_VOID`, the fill color of the Main Menu and Options screens; one name says which color, the other what it's for), `FLOOR_ORDER` (the map paths in play order; the run goes through them one after another, and the last one's exit ends the run. It lists the Easy floors, built with the ASCII converter from `Assets/Maps/Source/easy_floor_<n>.txt`; for now only `easy_floor_1.tmx`, which replaces the hand-built `Dungeon_Level_One.tmx`. That file stays in the repo as Tiled reference until all five Easy floors are in, and `test_room.tmx` stays as the converter's small test map), `FONT_PATH` (the menu font, `Assets/Fonts/Silkscreen-Regular.ttf`), `PANEL_FRAME_PATH` (`Assets/UI/panel_frame.png`, the frame art shared by the HUD and the inventory), `BUTTON_FONT_SIZE` (32, the button font size shared by every menu), and `OVERLAY_ALPHA` (160 of 255, how dark the overlay is when the game-over and paused options screens are drawn over the run).
- **`Assets/Fonts/`**: `Silkscreen-Regular.ttf`, a pixel font under the SIL Open Font License. Load it with `pygame.font.Font(FONT_PATH, size)`. Because it is a pixel font, render it without anti-aliasing (`False`) and use sizes that are multiples of 8, or the letters blur.

### `entities/`

- **`player/player.py`**: `Player`. Holds `pos`, `velocity`, `speed` (the actual speed last frame in pixels per second, measured as distance moved divided by `dt`), `facing`, `walking`, `intent`, `base_stats`, an `inventory` of `INVENTORY_SLOT_COUNT` (20) slots, and the `roll`, `invulnerability`, `heal_cooldown`, `animation`, `health`, `inventory` and `stats` dicts. `update(dt, walls)` runs the player's frame (section 7). Methods: `update_facing`, `update_movement`, `update_roll`, `update_animation`, `draw`. While invulnerable, `draw` skips the sprite while `is_blink_hidden(self.invulnerability, BLINK_INTERVAL)` is true, so the player blinks. `BLINK_INTERVAL` (0.1 s) is the player's own value, at the top of `player.py`. The debug hitbox is still drawn. `alpha` (starts at 255, fully visible) is how opaque the sprite is drawn, and the Run lowers it during death. When `alpha` is below 255, `draw` blits a faded **copy** of the frame instead of changing `self.image`. The animation frames are shared from the cache in `systems/assets.py`, so fading the frame itself would leave it faded for the next `Player` too, and a restarted player would be invisible.
- **`player/load_player.py`**: `load_player(spawn_pos)` loads the player animations (cropped from 64x64 sheets down to 16x16) and returns a `Player`.
- **`player/player_texture_data.py`**: sprite sheet layout for idle, walk and roll in the up, down and right directions. Left is generated by flipping right.
- **`enemies/enemy.py`**: `Enemy(type_data, pos)`. Copies its values from the type data with `type_data["..."]`: `attack`, `attack_damage`, `speed`, `knockback_multiplier`, `knockback_decay_rate`, `blink_interval`, `invulnerability_duration`, `loot_table`, `behavior`, `touch_damage` and `animation_prefix` (section 8). `knockback_velocity` (starts at zero) is the current shove in pixels per second.
  - **Body and art.** `rect` is the enemy's **body**, a `FRect` the size of the type's `"body"` box, and it's what moves, hits walls, gets separated and blocks the player. The art (`image`) can be bigger, and is drawn around the body: `art_topleft()` subtracts the body's offset inside the frame (`body_x`, `body_y`). Frames facing left are mirrored, so the offset is mirrored too (`image width − body_x − body width`), keeping the body under the same pixels whichever way it faces. `pos` is synced to `rect.topleft` at the end of every update. Pixel-perfect contact checks (`find_player_contacts`) use the art at `art_topleft()`.
  - **`update(dt, walls, target_pos)`.** A dying enemy only counts `death_time` up and finishes its knockback slide. Otherwise it either advances its swing (`update_attack`, standing still) or moves with its `behavior` (`update_movement`, which returns the velocity it chose) and then checks `try_start_attack`; then knockback, the `invulnerability` and `attack_cooldown` timers, and `moving` (whether the body's center changed this frame) and `facing` (from the sign of the chosen velocity's x; unchanged when it's 0). Last, `update_animation` picks the frame (section 7, step 4).
  - **Animation states.** For a type with an `animation_prefix`, `animation_name()` builds `<prefix>_<action>_<facing>`, with the action picked in priority order: `death` while dying, `hurt` for the first `HURT_DURATION` (0.5 s) of the invulnerability window, `move` while `moving`, else `idle`. A type with no prefix (the Skull) keeps its single animation. During a swing `update_animation` doesn't use the animation dict: it shows `attack_frames()[attack_step()]`, so the swing's own clock picks the frame.
  - **Dying.** `start_dying()` sets `dying`, resets `death_time` and ends any swing (`attacking = False`): a dying enemy never runs `update_attack`, so a swing left on would freeze on its attack frame instead of playing the death animation. `death_duration` is the death strip's frame count ÷ `DEFAULT_ANIMATION_SPEED`, worked out once in `__init__` (0 for a type without a death strip, so it's removed on the next frame). `is_done_dying()` tells the floor when to drop its loot and remove it. A dying enemy doesn't blink, has no health bar, isn't solid and is skipped by contacts and strikes.
  - **The swing** (types with an `"attack"`): `try_start_attack`, `update_attack`, `attack_frames`, `attack_step`, `is_striking`, `strike_rect` and `interrupt_attack`, explained in section 7, step 4.
  - **Bodies.** `is_solid()` is `not dying and behavior != "fly"`: walkers have solid bodies, fliers and the dying don't. `shove(displacement, walls)` moves the body by a displacement with `move_and_collide` (used by separation, section 7 step 5), so a shove can't push an enemy into a wall.
  - **`draw`.** Hides the sprite while `is_blink_hidden(self.invulnerability, self.blink_interval)` is true, unless `blink_interval` is `None` (the Skeleton shows its hurt animation instead) or it's dying. Its health bar (shown once it has taken damage, hidden while dying) and its debug boxes are always drawn, so its health stays readable while it blinks. The bar is `ENEMY_HEALTH_BAR_WIDTH` (16) × `ENEMY_HEALTH_BAR_HEIGHT` (2) art pixels plus the 1-pixel border, so 4 art pixels tall in total, and sits `ENEMY_HEALTH_BAR_GAP` (8) above the **body**.
- **`enemies/enemy_type_data.py`**: `ENEMY_TYPES`, one entry per enemy kind (section 8).
- **`enemies/enemy_texture_data.py`**: enemy sprite sheet layouts. `skull_texture_data` is the Skull's single 16×16 idle animation. `skeleton_texture_data` has one strip per action, all `SKELETON_FRAME_SIZE` (32×32) frames facing right: `skeleton_idle_right` (6 frames), `skeleton_move_right` (10), `skeleton_attack_right` (9), `skeleton_hurt_right` (5) and `skeleton_death_right` (17), from `Assets/Enemies/Skeleton/idle.png`, `move.png`, `attack.png`, `hurt.png` and `death.png` (the pack's sword skeleton sheets, copied into `Assets/`). `load_animations` adds the mirrored `_left` versions on load.
- **`enemies/load_enemies.py`**: `load_enemies(enemy_spawns)` turns the map's spawn positions into `Enemy` objects. Spawn names with no matching `ENEMY_TYPES` entry are skipped.

### `items/`

- **`items.py`**: item **data** only (the sprites that put items in the world are in `world/objects.py`):
  - `Item`: an item template or stack. It has `id`, `name`, `animations`, `description`, `quantity`, `max_stack`, `animation_speed`, `value_text` and `image` (first idle frame). `clone()` is a shallow copy, so a clone has its own `quantity` but shares the same images.
  - `EquipmentItem(Item)`: adds `slot` and `bonuses`, and always has `max_stack` 1.
- **`item_database.py`**: `initialize_item_database()` builds and returns the dict of item templates, keyed by item id: `gold_key` ("Opens treasure rooms"), `silver_key` ("Opens the way forward"), `small_health_potion`, `speed_boots`. The two keys use the pack's spinning key animations; on the ground they animate, while the HUD quick slots and the inventory show their first frame (`item.image`) as a still icon. It also defines `SMALL_HEALTH_POTION_VALUE` (10), how much HP a potion heals: it's the potion's own data, so it lives next to the potion's definition rather than in `constants.py` (which is for settings shared across the whole game). It's used for the tooltip's "Value: 10 HP" here, and imported by `systems/consumables.py` for the actual healing, so the two can never disagree.
- **`item_texture_data.py`**: sprite sheet layouts for each item, plus `crate_texture_data` for the crate strip. The keys' entries (`gold_key_texture_data`, `silver_key_texture_data`) point at the 4-frame strips made by `make_strip`; the old `animated_gold_key.png` and the unused static `gold_key.png` were removed.
- **`loot_table_data.py`**: the loot tables: `CHEST_LOOT`, what a chest can drop, `CRATE_LOOT`, what a broken crate can drop, and one table per enemy type (`SKULL_LOOT`, `SKELETON_LOOT`), what it can drop when it dies (section 8).

### `states/`

- **`state_manager.py`**: `GameStateManager` (section 5).
- **`new_run.py`**: `start_new_run(game_state_manager)` builds a fresh `Run`, starting on the first floor of `FLOOR_ORDER`, and registers it as `"run"`, replacing the old run. It's a plain function in its own module so any menu can start a new run without depending on another menu. Used by `RunEndScreen` (Restart and Main Menu) and `OptionsMenu` (Main Menu from a paused run).
- **`run.py`**: `Run(game_state_manager)`, **the run**: every floor in `FLOOR_ORDER`, one after another. It owns what lasts the whole run and the order of each frame; everything on the current map belongs to its `Floor` (`self.floor`, see `world/floor.py`).
  - **`__init__`** sets up what lasts the whole run: `run_time`, `splits`, the item database, the player, the HUD, the inventory screen, the death timer and the floor transition. It creates the player at `(0, 0)`, sets `floor_index` to 0 (which entry of `FLOOR_ORDER` is being played), then calls `load_floor` for the first floor, which places the player.
  - **`load_floor(map_path)`** builds a new `Floor(map_path, item_database)` and moves the **same** player object to the floor's `player_spawn`: it sets `rect.center`, syncs `pos` to the rect (enemy contact checks read `player.pos` before the player updates), zeroes `velocity` so the player doesn't slide in at full speed, centers the camera, and clears the interaction target. Because the player object is kept, health, inventory, gear and cooldowns carry over with no extra code, and because `run_time` lives on the `Run`, the timer keeps counting across floors. Because the floor is a **new object**, nothing from the old floor (ground items, particles, a pending exit, padlocks) can leak into the new one.

  ```
  Level (the run, built once)               Floor (one map, built by load_floor)
  ───────────────────────────               ────────────────────────────────────
  run_time, splits, floor_index             map surface, tiles, doors + padlocks
  item_database ──── shared with ─────────▶ chests, crates, ground items, particles
  player ──── placed at player_spawn ─────▶ enemies, solid_tiles, exit
  hud, inventory_ui, death, transition      update(dt, player), draw(surface, player, highlight)
  input + the order of each frame           unlock_door, spawn_loot, highlighted_sprites
  ```

  `world_surface` (`WORLD_WIDTH` × `WORLD_HEIGHT`) is the canvas the world is drawn on before it's scaled to the screen; `draw` fills it, hands it to `floor.draw`, then scales it up and draws the HUD, the inventory and the transition overlay on the screen.
  - `run_time` (starts at 0.0) holds the seconds spent in this run, across all floors, and is drawn by the HUD's timer panel.
  - `splits` (starts empty, run-wide like `run_time`) holds the `run_time` at the moment each exit was touched, one entry per finished floor, the last floor included. That's the speedrun meaning of a split: the clock reading at each checkpoint. Only these raw readings are stored; each floor's own time is worked out from them on the end screen (`floor_times`). Because the floor transition pauses the run timer, no transition time ends up in any floor's time.
  - **The floor transition** belongs to `floor_transition`, a `FloorTransition` (see `ui_components/floor_transition.py`). At the exit, the run calls `floor_transition.start()`. While `floor_transition.is_active()`, `update` only calls `update_transition(dt)`, which advances it and, on the one frame its `update` returns `True` (the screen has just gone fully black), raises `floor_index`, calls `load_floor` for the next map and `floor_transition.set_floor_number(floor_index + 1)` (players count from 1, the list from 0). `draw` ends with `floor_transition.draw(screen)`, over everything including the HUD.
  - `dying` (starts `False`) is the flag that says the death sequence has started, and `death_timer` (made with `new_timer()`) holds the seconds left before the game-over screen. `DEATH_DELAY` (3.0 s) is the whole freeze, and `DEATH_FADE_DURATION` (1.5 s) is how long the player's body takes to fade out. The fade must be no longer than the delay.
- **`menus/main_menu.py`**: `MainMenu(game_state_manager)`, the title screen (section 5).
  - `draw` fills the screen with `MENU_BACKGROUND_COLOR`, then draws the "DUNGEON SPRINT" title (`TITLE_FONT_SIZE` 96, at `TITLE_Y` 50, centered with `(SCREEN_WIDTH - width) // 2`) and the buttons.
  - Start, Options and Exit are `TextButton`s with a gray outline, centered and stacked at `START_BUTTON_Y` (300), `OPTIONS_BUTTON_Y` (380) and `EXIT_BUTTON_Y` (460).
- **`menus/options.py`**: `OptionsMenu(game_state_manager)`, the options menu (section 5).
  - It uses the same size of text title ("OPTIONS") as the Main Menu screen. All buttons are `TextButton`s with a gray outline.
  - The background depends on where the menu was opened from. When `can_go_back()` is true (opened from the run with ESC), `draw` first draws the paused Run, looked up from `game_state_manager.states["run"]`, then a full-screen black overlay at `OVERLAY_ALPHA` (160 of 255), the same way as the game-over screen. Otherwise it fills the screen with `MENU_BACKGROUND_COLOR`.
  - The FPS and Fullscreen toggles are centered at `FPS_BUTTON_Y` (220) and `FULL_SCREEN_BUTTON_Y` (300). Their text comes from `FPS_LABEL` and `FULL_SCREEN_LABEL` (`"FPS: {}"`, `"Fullscreen: {}"`) filled in by `on_off(enabled)`, which returns `"On"` or `"Off"`. When clicked, the setting flips and `set_text` shows the new state.
  - Main Menu and Back are created without a position, then placed in the bottom corners by setting `rect.bottomleft` and `rect.bottomright`, `NAVIGATION_BUTTON_MARGIN` (20) pixels from the screen edges.
  - The SFX and music sliders are centered at `SLIDER_X` (640) on `SFX_SLIDER_Y` (475) and `MUSIC_SLIDER_Y` (575), and are `SLIDER_WIDTH` x `SLIDER_HEIGHT` (300x20). Their labels use a separate Silkscreen font at `LABEL_FONT_SIZE` (24), so "Music Volume: 100" fits within the track width. Each label is left-aligned with its track's left edge (`SLIDER_LABEL_X`), and its y is the slider's y minus `SLIDER_LABEL_OFFSET_Y` (45), so a label moves with its slider.
- **`menus/run_end.py`**: `RunEndScreen(game_state_manager, title, title_color, music)`, the end-of-run screen used for both death and finishing (section 5).
  - The title is rendered from `FONT_PATH` at `TITLE_FONT_SIZE` (64) in `title_color` and centered horizontally with `(SCREEN_WIDTH - width) // 2` at `TITLE_Y` (120). Restart and Main Menu are `TextButton`s using the shared `BUTTON_FONT_SIZE`, placed by their midtop point `(SCREEN_WIDTH // 2, y)` at `RESTART_BUTTON_Y` (540) and `MAIN_MENU_BUTTON_Y` (610), turning `PALETTE_TORCH` on hover.
  - **The split table.** One row per floor with the time spent on that floor, a divider, then the total:

    ```
            You Escaped!                         SPLITS_TOP_Y (230), rows SPLIT_ROW_HEIGHT (42) apart

        Floor 1        00:45.12                  labels left-aligned at SPLIT_LABEL_X (center − 180)
        Floor 2        01:02.80                  times right-aligned at SPLIT_TIME_RIGHT (center + 180)
        ───────────────────────                  divider: SPLIT_DIVIDER_HEIGHT (3) px, PALETTE_SHADOW
        Total          01:47.92                  SPLIT_TOTAL_GAP (18) below the divider
    ```

    - `floor_times(splits, run_time)`, a plain function above the class, works out each floor's time from the stored clock readings. After a death, `run_time` is past the last split, so the floor the player died on gets a row too, with its time up to death. After a win, the last split equals `run_time`, so no extra row is added.

      ```
      splits  = [45.12, 107.92]       (run_time when each exit was touched)
      floor 1 = 45.12 − 0      = 45.12
      floor 2 = 107.92 − 45.12 = 62.80
      total   = run_time       = 107.92

      died on floor 3 at run_time 130.00:
      floor 3 = 130.00 − 107.92 (last split) = 22.08
      ```

      The subtracting is done in whole centiseconds (`to_centiseconds`, in `time_format.py`): each split is cut to whole hundredths first, and each floor time is the displayed split minus the previous displayed split. Integers are exact, so the floor times always add up to exactly the displayed Total. Subtracting raw floats instead would sometimes show a floor 0.01 too low (`2.33 − 0.01` is `2.3199999…`), and floors made of truncated parts wouldn't always sum to the truncated total.
    - `enter()` reads `splits`, `run_time` and `dying` from the run and calls `render_splits(splits, run_time, died)`. `dying` is `True` on the death screen and `False` on the win screen, which is how one class knows to show the floor the player died on in `PALETTE_BLOOD`; all other rows are `PALETTE_STEEL`.
    - `render_splits` builds `split_rows`, a list of `(image, pos)` pairs, once per screen visit, plus the `divider_rect`; `draw` only loops over them. `add_split_row(label, seconds, row_y, color)` renders one row's label and time, because the floor rows and the Total row are drawn the same way. The time's x is `SPLIT_TIME_RIGHT − its width`, which right-aligns it so the times line up. `__init__` starts with an empty list and an empty rect, so `draw` works even before the first `enter`.
    - It fits up to 5 floors between the title and the buttons.
  - `draw` first draws the current Run, looked up from `game_state_manager.states["run"]`, then a full-screen black overlay at `OVERLAY_ALPHA` (160 of 255), then the title, the split rows and divider, and the buttons. The run has to be redrawn every frame, because a translucent overlay drawn on its own would stack up to solid black.
  - Restart and Main Menu both call `start_new_run(self.game_state_manager)` from `states/new_run.py` before switching state.

### `systems/`

| Module | Job | Main functions |
| --- | --- | --- |
| `input.py` | Turns keyboard and mouse into an intent dict | `read_input` |
| `movement.py` | Velocity steering and wall collision | `steer`, `approach_fraction`, `decay_velocity`, `move_and_collide` |
| `blink.py` | When a blinking sprite is hidden | `is_blink_hidden(invulnerability, blink_interval)` |
| `roll.py` | Roll start, duration, cooldown and ease-out | `try_start_roll`, `advance_roll`, `is_rolling`, `roll_speed_multiplier` |
| `enemy_ai.py` | Enemy behaviours and line of sight | `fly_velocity`, `wander_chase_velocity`, `trigger_flee`, `has_line_of_sight`, `random_idle_direction` |
| `collision.py` | Finds enemies touching the player | `find_player_contacts` |
| `combat.py` | What happens on contact and when a swing lands. `resolve_contact` returns whether the enemy was hit, `resolve_strike` whether the player was. | `resolve_contact`, `resolve_strike` |
| `separation.py` | Keeps solid enemy bodies off each other and off the player | `separate_enemies`, `push_out` |
| `timer.py` | Countdown timers: a `{"time_left"}` dict counted down by `dt` | `new_timer`, `start_timer`, `advance_timer`, `is_running`, `time_left` |
| `health.py` | Health dict rules | `new_health`, `take_damage`, `heal`, `is_dead`, `set_max_health` |
| `stats.py` | Base stats plus equipment bonuses | `compute_stats` |
| `inventory.py` | Inventory dict rules | `new_inventory`, `add_item`, `remove_item`, `has_item`, `count_item`, `can_equip` |
| `interact.py` | The F key: chests, doors, pickups, and what F would act on | `interact`, `find_target`, `describe_target`, `open_chest`, `unlock_door`, `pick_up_item` |
| `loot.py` | Rolls a loot table | `roll_loot` |
| `consumables.py` | Using items and the heal cooldown | `use_small_health_potion` |
| `animation.py` | Animation dict rules | `new_animation`, `set_animation`, `advance_animation` |
| `assets.py` | Loading and caching images and animations | `load_image`, `load_animations`, `slice_frames`, `crop_center`, `add_flipped_left` |
| `masks.py` | Pixel-perfect masks and outlines. `images_overlap(first_image, first_pos, second_image, second_pos)` takes images and positions rather than sprites, since an enemy's art isn't at its `rect` | `get_mask`, `images_overlap`, `draw_hitbox`, `draw_highlight`, `grow_mask` |
| `particles.py` | Short-lived visual effects | `emit_burst`, `update_particles`, `draw_particles`, presets such as `CRATE_DEBRIS` |
| `camera.py` | The shared camera rect, the size of the world canvas (`WORLD_WIDTH` × `WORLD_HEIGHT`), not the screen, so a bigger `GAME_SCALE` means fewer tiles in view | `camera`, `center_camera`, `is_on_screen` |
| `display.py` | Creating the window | `create_window` |
| `debug.py` | Debug flags | `show_hitboxes`, `toggle_hitboxes` |
| `sound.py` | Loading and playing audio. `play_music(name, loops=-1)` loops forever by default and remembers the track in `_current_music_name`. Asking for the track that is already playing does nothing, so it doesn't restart. `stop_music` clears the remembered name. | `load_sfx`, `load_music`, `play_sfx`, `play_music`, `stop_music`, `set_sfx_volume`, `set_music_volume` |
| `settings.py` | Reading and saving `settings.json` | `load_settings`, `save_settings`, `get_setting`, `set_setting` |

Some systems hold module-level state that is shared by everyone who imports them: `camera.camera`, `debug.show_hitboxes`, `settings.SETTINGS`, `sound.SFX` and `sound.MUSIC`, and the caches in `assets` and `hitbox`. Read flags through the module (`debug.show_hitboxes`), not with `from systems.debug import show_hitboxes`. A `from` import copies the value once at import time and never sees later toggles.

### `ui_components/`

- **`button.py`**: `Button(image, pos, outline_color=PALETTE_STEEL, hover_image=None)`. `image` can be any surface, including text from `font.render`. Plays `button_hover` when the mouse enters. While hovered, it draws `hover_image` instead of `image` if it was given one; otherwise it draws an outline in `outline_color` around `image`. The outline is drawn first and the image on top of it, so only the ring just outside the shape shows. Drawn the other way round, the outline covers thin shapes such as letters. On a left click it plays `button_click` and sets `clicked_this_frame`, which `is_clicked()` returns. `set_image(image, hover_image=None)` swaps both pictures and rebuilds the outline. The new rect keeps the old `topleft`, so text that changes width would drift off center. `TextButton.set_text` corrects for that.
- **`text_button.py`**: `TextButton(text, font, midtop=(0, 0), text_color=PALETTE_STEEL, hover_color=PALETTE_TORCH)`, a `Button` subclass whose picture is rendered text.
  - On hover the text turns `hover_color` instead of being outlined: it renders a second copy of the text in `hover_color` and passes it to `Button` as `hover_image`. A thin 1 px outline was hard to see at the game's 3× pixel size, and a solid 3 px outline merged neighbouring letters together, while a recolor keeps every letter crisp.
  - The font is passed in rather than created here. Each state creates its fonts once in `__init__`, because building a `Font` reads the font file from disk.
  - It is placed by its `midtop` point (the middle of its top edge), so passing `(SCREEN_WIDTH // 2, y)` centers it. For any other placement, leave out `midtop` and set another anchor on `rect` afterwards, such as `rect.bottomleft`.
  - `set_text(text)` re-renders the text and its hover copy, then puts `midtop` back where it was, so a toggle like "FPS: On"/"FPS: Off" stays centered when its width changes.
- **`slider.py`**: `Slider`, a draggable knob on a track between `min_value` and `max_value`. `pos` is the **center** of the track, not its top-left, so the track's left edge is `pos[0] - size[0] // 2`. The part left of the knob is drawn in `track_color` and the rest in `PALETTE_SHADOW`. The knob is drawn in `knob_color`, or `PALETTE_TORCH` while hovered or dragged, the same hover color as the buttons. The options menu uses a `PALETTE_STEEL` fill and a `PALETTE_ICE` knob, so the knob stands out from the fill next to it. The track and knob have rounded corners (`TRACK_CORNER_RADIUS` 5, `KNOB_CORNER_RADIUS` 3). The knob is `KNOB_WIDTH` (20) pixels wide and sticks out `KNOB_OVERHANG` (5) pixels above and below the track. `get_current_value()` returns the value as an int.
- **`text_label.py`**: `TextLabel`, rendered text at a position (its top-left), at `DEFAULT_FONT_SIZE` (24) unless told otherwise; the four outline offsets are the `OUTLINE_OFFSETS` constant. `update_text` re-renders it, but does nothing if the text hasn't changed, so calling it every frame is cheap; `__init__` renders through `update_text` too, so there is one render path. With `outline_color` set (it defaults to `None`, so existing labels are unchanged), a copy of the text in that color is drawn one art pixel (`GAME_SCALE`) up, down, left and right first, then the text on top, giving it a dark rim that reads on any background:

  ```
     ░░░
    ░▓▓▓░      ▓ = the text
    ░▓░░░      ░ = the same text in the outline color, drawn 3 px up, down, left and right first
    ░▓▓▓░
     ░░░
  ```

  Text is drawn without anti-aliasing for a pixel look. With no `font` given, it builds Silkscreen from `FONT_PATH` at `font_size` (default 24, on the 3× grid), in `color` (default `PALETTE_STEEL`). Pass a ready-made `font` to share one font object between labels, in which case `font_size` is ignored. The menus, HUD and inventory pass their own fonts; the FPS counter uses the default.
- **`inventory_ui.py`**: `InventoryUI(inventory)`, the inventory screen (section 7). It reads the inventory only for its **shape**, the number of slots and the equipment slot names, so the layout follows the data: changing `new_inventory`'s slot count or `EQUIPMENT_SLOT_NAMES` resizes the window.
  - **Layout.** A centered, framed window titled "INVENTORY", with the equipment slots in a column on the left and the item grid, `GRID_COLUMNS` (5) wide, on the right. Every slot is a `SLOT_SIZE` (72) framed slot, `SLOT_GAP` (6) apart, the same as the HUD quick slots, with a 3× icon at `SLOT_ICON_OFFSET` (12). With 20 slots and 4 equipment slots, both columns are 4 slots tall, so they line up. The world behind is dimmed by a full-screen black overlay at `INVENTORY_DIM_ALPHA` (120 of 255), drawn first.

    ```
    grid rows      = ceil(slot count ÷ GRID_COLUMNS)
    grid width     = GRID_COLUMNS × SLOT_SIZE + (GRID_COLUMNS − 1) × SLOT_GAP      (gaps only between slots)
    grid height    = grid rows × SLOT_SIZE + (grid rows − 1) × SLOT_GAP
    window width   = WINDOW_PADDING + SLOT_SIZE + EQUIPMENT_GAP + grid width + WINDOW_PADDING
    window height  = WINDOW_PADDING + TITLE_HEIGHT + max(grid height, equipment height) + WINDOW_PADDING
    window x, y    = centered on the screen, snapped to the 3 px grid

    row, column    = divmod(slot index, GRID_COLUMNS)
    grid slot rect = (grid_x + column × (SLOT_SIZE + SLOT_GAP), slots_top + row × (SLOT_SIZE + SLOT_GAP), SLOT_SIZE, SLOT_SIZE)
    ```

  - **Slot rects.** Every slot's `pygame.Rect` is built once in `__init__`: `grid_slot_rects` is a list whose position matches the inventory slot index, and `equipment_slot_rects` is a dict keyed by slot name. Drawing loops over them, and clicking asks each one `rect.collidepoint(mouse_pos)` (`get_slot_at_mouse`, `get_equipment_slot_at_mouse`), so where the slots are is decided in exactly one place and gaps, columns and window position can't drift out of sync. `divmod(index, GRID_COLUMNS)` returns both `index // GRID_COLUMNS` (the row) and `index % GRID_COLUMNS` (the column) at once: slot 7 in 5 columns is row 1, column 2.
  - **`draw_slot(screen, rect, item)`** draws the slot frame, then, if there's an item, its icon (scaled by `GAME_SCALE` once and cached by item id in `get_icon`) and, for stacks of more than one, an outlined count placed by its visible ink one art pixel inside the bottom-right corner. One `count_label` is shared by every slot and re-positioned for each.
  - **Tooltips.** Hovering an item with an empty hand shows a framed tooltip next to the mouse: the name in `PALETTE_STEEL`, the description in `PALETTE_STONE`, and the value (if the item has one) in `PALETTE_TORCH`. Hovering an empty equipment slot shows just the slot's name (`"boots".title()` is "Boots"), so the empty slots can be told apart. An item's tooltip text never changes, so `build_tooltip(lines)` renders the whole tooltip, frame and text, into one surface the first time, and `get_tooltip(key, lines)` keeps it in `tooltip_cache` keyed by the item id (or `empty_<slot name>`, which can never clash with an item id); after that, hovering is a single blit. `draw_tooltip` places it `TOOLTIP_MOUSE_OFFSET` (18) down and right of the cursor, and flips it to the other side of the cursor if it would go off the screen.

    ```
    tooltip width  = widest line + 2 × TOOLTIP_PADDING                                       (rounded up to a multiple of 3)
    tooltip height = 2 × TOOLTIP_PADDING + (line count − 1) × TOOLTIP_LINE_HEIGHT + ink height  (rounded up to a multiple of 3)
    line y         = TOOLTIP_PADDING − ink top + line index × TOOLTIP_LINE_HEIGHT
    ```

    `TOOLTIP_PADDING` (18) is the 12 px frame border plus 6 px of room, and `TOOLTIP_LINE_HEIGHT` (27) is the visible text height (15) plus spacing. The size is rounded **up** so the text always fits. Subtracting the ink top (the empty space Silkscreen leaves above its letters, about 10 px) puts each line's visible top exactly at the padding.
  - **The held item** is drawn centered on the mouse, using the icon's own size.
- **`floor_transition.py`**: `FloorTransition`, the fade between floors: fade to black, a "Floor 2" card, fade back in. It runs inside the gameplay state rather than as its own game state, because it's part of playing a run and needs the world drawn underneath. It knows nothing about floors or `FLOOR_ORDER`: its owner starts it, asks whether it's running, and reacts to one signal. `phase` is `None` while playing, or the name of the current phase, and one `timer` is restarted for each phase:

  ```
  start() ─▶ "fade_out" ─▶ "card" ─▶ "fade_in" ─▶ None (playing)
              0.4 s        1.0 s      0.4 s
              overlay      the owner  overlay
              0 → 255      loads the  255 → 0
                           next floor
  ```

  - `start()` begins `"fade_out"`; `is_active()` is true while `phase` isn't `None`.
  - `update(dt)` advances the timer and, when it runs out, does what happens at the **end** of the current phase: the end of `"fade_out"` starts the card and **returns `True`**, the only frame it does; the end of `"card"` starts `"fade_in"`; the end of `"fade_in"` sets the phase back to `None`. Returning `True` once is how it tells its owner "the screen is black, load the next floor now" without knowing what a floor is, the same idea as a button's `is_clicked()`. The new floor loads while the screen is fully black, so the swap is never seen. `FADE_DURATION` (0.4 s) and `FLOOR_CARD_DURATION` (1.0 s) set the lengths.
  - Loading a floor takes real time, so the frame after loading gets a large `dt`. The timer advances by `min(dt, MAX_TRANSITION_DT)` (1/30 s), so a slow load can't skip the card; however long the load took, it counts as one short frame.
  - `set_floor_number(floor_number)` sets `floor_label` (a `TextLabel` at `FLOOR_CARD_FONT_SIZE`, Silkscreen 48) to `Floor {floor_number}` and centers it on the screen by its visible ink with `centered_text_x` / `centered_text_y`. It takes the number to show rather than reading the run's index, so the component stays independent.
  - `draw(screen)` does nothing while inactive; otherwise it blits `fade_overlay` (a screen-sized surface filled with `PALETTE_VOID`) at `overlay_alpha()`, over everything including the HUD so the whole screen fades together, and the card text on top during `"card"`.
  - `overlay_alpha()` says how dark the overlay is: `fade_left` goes from 1.0 to 0.0 as a fade runs, and the card is fully black.

    ```
    fade_left = time_left(timer) ÷ FADE_DURATION     (1.0 → 0.0)
    fade_out:  alpha = round(255 × (1 − fade_left))  (0 → 255, darkening)
    fade_in:   alpha = round(255 × fade_left)        (255 → 0, clearing)
    card:      alpha = 255
    ```

  Inside a class named `FloorTransition`, the old `transition_` prefixes (`transition_phase`, `transition_timer`, `transition_alpha`) only repeated the class name, so the attributes are just `phase`, `timer` and `overlay_alpha`.
- **`text_layout.py`**: shared helpers for placing text by its **visible ink** (`get_bounding_rect()`) rather than by its surface. A rendered surface is taller than its letters, because fonts reserve space above and below them (for Silkscreen at 24 the surface is 31 px tall but the digits only run from y 10 to 25), so lining up surfaces would leave text visibly off-center.

  ```
  snap_to_grid(value)                  = value // GAME_SCALE × GAME_SCALE
  centered_text_x(surface, center_x)   = snap(center_x − ink center x)
  centered_text_y(surface, center_y)   = snap(center_y − ink center y)
  bottom_right_text_pos(surface, right, bottom) = (right − ink right, bottom − ink bottom)
  ```

  Used by the HUD (the floor panel, the prompt, the quick-slot counts), the inventory (stack counts), the floor card in `floor_transition.py`, and the FPS counter. Each used to compute the ink rect and snap it by hand; one helper per kind of placement keeps the formula in one place.
- **`fps_counter.py`**: `FpsCounter`, the debug FPS readout: an outlined `TextLabel` in the default Silkscreen at 24, with no panel, because it's a debug readout rather than part of the game. `update(dt, fps)` refreshes the text every `FPS_REFRESH_INTERVAL` (0.5 s), since a number changing every frame is unreadable, and re-positions it by its ink: right-aligned `FPS_MARGIN` (12) from the screen's right edge, so a wider number grows to the left, and vertically centered on `FPS_CENTER_Y` (21). `draw(screen)` draws the label.

  ```
  x = SCREEN_WIDTH − FPS_MARGIN − ink right
  y = centered_text_y(label, FPS_CENTER_Y)
  ```
- **`time_format.py`**: run times as text, shared by the HUD timer and `RunEndScreen`.
  - `to_centiseconds(seconds)` turns seconds into a whole number of hundredths, truncating (rounding down) the way speedrun timers do, so a time is never shown before it's reached and 59.996 can't round up to `00:60.00`. Floats can't store most decimals exactly: `0.29` is really `0.28999999…`, so `0.29 * 100` is `28.999…` and a plain `int()` would give 28. Adding `FLOAT_NUDGE` (`1e-6`, a millionth of a centisecond) before truncating fixes values that are only a hair under a whole hundredth because of float noise, without changing real times.
  - `format_run_time(seconds)` turns seconds into `mm:ss.hh` text, e.g. 73.456 becomes `01:13.45`. All of its arithmetic is on the integer centiseconds, so nothing is lost to float noise:

    ```
    centiseconds  = to_centiseconds(seconds)        = int(seconds × 100 + FLOAT_NUDGE)
    minutes       = centiseconds // 6000            (6000 centiseconds in a minute)
    whole_seconds = centiseconds // 100 % 60        (seconds past the minute)
    hundredths    = centiseconds % 100
    ```

    `//` (floor division) drops the remainder and `%` keeps only the remainder. In the f-string, `02d` means a whole number padded to 2 digits.

  ```
  seconds           = int(seconds × 100) ÷ 100     (truncate to whole hundredths)
  minutes           = seconds // 60                (floor division)
  remaining_seconds = seconds % 60                 (remainder)
  text              = f"{minutes:02d}:{remaining_seconds:05.2f}"      73.456 → 01:13.45
  ```

- **`health_bar.py`**: `draw_health_bar(screen, health, x, y, width, height)`, used for enemy health bars (the player's health is drawn by the HUD). It draws, in order: a `PALETTE_VOID` border `HEALTH_BAR_BORDER` (1) pixel bigger on every side, so the bar reads over floors, walls and other enemies; the full-width empty bar in `PALETTE_SHADOW`; and the fill in `PALETTE_BLOOD`. The fill is always blood red, like the player's bar, so health has one color meaning throughout the game; the bar's length already shows how hurt the enemy is. A living enemy always shows at least 1 pixel of fill, because at 16 pixels for 100 HP each pixel is worth about 6 HP, and an enemy with 3 HP left would otherwise look dead:

  ```
  fill width = int(width × current ÷ max), at least 1 while current > 0
  ```

  Enemy bars are drawn on the world surface, so every value is in art pixels and lands on whole art pixels before the world is scaled up. Unlike the HUD, which draws straight onto the screen, they need no grid snapping.
- **`panel.py`**: `make_panel(frame_image, size)` builds a framed panel surface of any size from the small frame image, using **9-slice** scaling. `size` is in screen pixels. Build each panel once (for example in `__init__`) and blit it every frame.

  ```
  ┌────┬─────────┬────┐
  │ TL │   top   │ TR │   corners: drawn as they are, never stretched
  ├────┼─────────┼────┤
  │left│ center  │right│  edges: stretched along their length only
  ├────┼─────────┼────┤   center: stretched both ways (it's a solid fill)
  │ BL │ bottom  │ BR │
  └────┴─────────┴────┘
  ```

  The corner size `c` is `PANEL_CORNER_SIZE` (4 art pixels), which must match the border of the `panel_frame` sprite in `tools/make_sprite.py`. The art keeps all its detail in the outer 4 pixels, so each edge is the same color all the way along and is safe to stretch. Each of the 9 pieces is a (cut from the frame, drawn on the panel) pair of rects:

  | Piece | Cut from the frame (x, y, w, h) | Drawn on the panel (x, y, w, h) |
  | --- | --- | --- |
  | top-left | `0, 0, c, c` | `0, 0, c, c` |
  | top | `c, 0, frame middle w, c` | `c, 0, panel middle w, c` |
  | top-right | `frame_width − c, 0, c, c` | `width − c, 0, c, c` |
  | left | `0, c, c, frame middle h` | `0, c, c, panel middle h` |
  | center | `c, c, frame middle w, frame middle h` | `c, c, panel middle w, panel middle h` |
  | right | `frame_width − c, c, c, frame middle h` | `width − c, c, c, panel middle h` |
  | bottom-left | `0, frame_height − c, c, c` | `0, height − c, c, c` |
  | bottom | `c, frame_height − c, frame middle w, c` | `c, height − c, panel middle w, c` |
  | bottom-right | `frame_width − c, frame_height − c, c, c` | `width − c, height − c, c, c` |

  ```
  frame middle = frame size − 2 × c
  panel middle = panel size − 2 × c
  ```

  Every piece goes through the same loop: cut it with `subsurface` (a view into the image, no copy), resize it to its target with `pygame.transform.scale` (corners resize to their own size, so they're unchanged), and blit it. The panel is built at 1× (`size // GAME_SCALE`) and scaled up by `GAME_SCALE` at the end, so its pixels are the same 3×3 blocks as the world. A size that isn't a multiple of 3 is rounded down (100 becomes 99), and the smallest panel is `2 × c` art pixels (24 screen pixels) each way.
- **`hud.py`**: `HUD`, the in-game heads-up display. `Run` creates one and calls `hud.draw(screen, player, run_time, floor_number, prompt)` once per frame, passing `floor_index + 1` as the floor number and `interact_prompt` as the prompt; `draw` calls `draw_health`, `draw_timer`, `draw_floor`, `draw_quick_slots` and `draw_prompt`, so the Run never changes when the HUD gains parts. The HUD is given plain values rather than the `Run` itself, so it doesn't need to know about `FLOOR_ORDER` or `floor_index`, only the number to show. The font and the panels are created once in `__init__`.
  - **Pixel-grid rules.** The HUD uses Silkscreen only at 24 (its 8 px grid × 3) or 48, so font pixels are the same 3×3 blocks as the world and the frames. Every size and position is a multiple of 3, and anything calculated is snapped with `value // GAME_SCALE * GAME_SCALE`.
  - **Health** (`draw_health`): a `HEALTH_PANEL_SIZE` (312×54) panel at `HUD_MARGIN` (12), with a `HEALTH_BAR_SIZE` (186×24) bar at `HEALTH_BAR_OFFSET` (18, 15). The empty bar is `PALETTE_SHADOW`, the fill `PALETTE_BLOOD`, and the `current/max` text `PALETTE_STEEL`, `HEALTH_TEXT_GAP` (9) to the right of the bar. Gaps in `PALETTE_VOID` split the bar into segments, drawn after the fill so they cut through both parts. `segment_hp_for(max_health)` picks the segment size so there are at most `HEALTH_MAX_SEGMENTS` (5) blocks, each a round number of HP: 25 max gives 5-HP blocks, 35 gives 10, 100 gives 20.
  - **Centering text**: the HUD places its text with the shared ink-based helpers in `text_layout.py` (`centered_text_x`, `centered_text_y`, `bottom_right_text_pos`), since a text surface is taller than its letters.
  - **Timer** (`draw_timer`): a `TIMER_PANEL_SIZE` (162×54) panel centered at the top, showing `format_run_time(run_time)`. Centered text normally shifts sideways as the digits change, because a `1` is narrower than an `8` and the total width keeps changing. So the timer gives every digit a fixed-width cell, as wide as the widest digit, and centers each glyph in its cell; `:` and `.` keep their own width, since they never move. The total width is then the same for every time, so nothing re-centers. The 12 characters it needs are rendered once into `timer_glyphs` (a dict comprehension), and `timer_cell_width(character)` gives each one's cell.

    ```
    cells:  [ 0 ][ 1 ] : [ 0 ][ 8 ] . [ 8 ][ 8 ]
             └── each digit is centered in its own cell of the same width ──┘
    ```

  ```
  fill_width  = int(bar width × current ÷ max) // GAME_SCALE × GAME_SCALE      (snapped to the 3 px grid)
  segment HP  = first step in (5, 10, 20, 25, 50, 100) where max_health ÷ step ≤ 5
  gap offset  = int(bar width × gap HP ÷ max) // GAME_SCALE × GAME_SCALE
  text_y      = center_y − text_bounds.centery, snapped to the grid               (centered_text_y)
  panel_x     = (SCREEN_WIDTH − panel width) // 2, snapped                        (timer panel)
  cell width  = widest digit for 0–9, the glyph's own width for ":" and "."
  start x     = panel_x + (panel width − sum of all cell widths) // 2
  glyph x     = cell x + (cell width − glyph width) // 2
  ```
  - **Floor number** (`draw_floor`): a `FLOOR_PANEL_SIZE` (72×54) panel, the same height as the timer panel, `FLOOR_PANEL_GAP` (12) to its right, showing `F{floor_number}` in `PALETTE_STEEL`. Its x is worked out from the timer panel's x, so the timer stays exactly centered and moving it moves the floor panel too. The text is centered in the panel by its visible ink, the same way as the floor card. Its position is worked out on every draw, because the text width can change (`F9` → `F10`), while `update_text` only re-renders when the text actually changes, so it costs nothing until the floor changes.

    ```
    floor_panel_x = timer_panel_x + TIMER_PANEL_SIZE width + FLOOR_PANEL_GAP      (558 + 162 + 12 = 732)
    text_x        = centered_text_x(text, floor_panel_x + panel width // 2)
    text_y        = centered_text_y(text, HUD_MARGIN + panel height // 2)
    ```

  - **Quick slots** (`draw_quick_slots`, `draw_quick_slot`): three `QUICK_SLOT_SIZE` (72×72) slots at the bottom left, `QUICK_SLOT_GAP` (12) apart: potions, then silver keys, then gold keys. 72 is the 12 px frame border on each side plus a 48 px icon (16 art pixels × 3). One `draw_quick_slot(screen, slot_pos, icon, count, count_label, cooldown_fraction=0.0)` draws any slot in order: frame, icon, cooldown shade, count, each on top of the one before; `draw_quick_slots` calls it once per slot with that slot's values.
    - The key slots are data: `KEY_SLOT_ITEMS` (`("silver_key", "gold_key")`, left to right) is turned into `self.key_slots`, a list of dicts built in a loop in `__init__`, one per key, each with its `item_id`, `pos`, bright and faded `icon`, and its own `count_label` (each label remembers its own text and position). `draw_quick_slots` loops over them, so adding a key color is one more entry in the tuple. `enumerate(..., start=1)` numbers them after the potion slot (slot 0):

      ```
      slot x = HUD_MARGIN + index × (QUICK_SLOT_SIZE width + QUICK_SLOT_GAP)
      potion 12 (index 0),  silver key 96 (index 1),  gold key 180 (index 2)
      ```
    - The icons come from the item database: `HUD(item_database)` takes `Run`'s database and scales each item's `.image` by `GAME_SCALE` once. The database is the one source for item images, so the HUD, the inventory and ground items always match.
    - The counts (`x7`) are outlined `TextLabel`s, one per slot, placed by their visible ink (`get_bounding_rect()`) one art pixel inside the slot's bottom-right corner. The potion slot also shows an orange `Q` (`PALETTE_TORCH`) on its top-left corner, so the player knows which key heals.
    - A slot whose count is 0 shows a faded copy of its icon (`EMPTY_ICON_ALPHA`, 80 of 255). The faded copies are made once with `copy()` and `set_alpha`, so the bright originals stay bright.
    - While the heal cooldown runs, a dark see-through shade (`COOLDOWN_SHADE_ALPHA`, 160) covers the potion slot's inner window and shrinks upward as the cooldown runs out, so the icon "fills back up". It covers the whole inner window (`QUICK_SLOT_INNER_OFFSET` 9, `QUICK_SLOT_INNER_SIZE` 54×54), not just the icon, so it meets the frame's bevel on all four sides. Those two constants are tied to the panel art's border, the same as `PANEL_CORNER_SIZE`.

      ```
      cooldown just started     halfway          ready
      ┌────────┐              ┌────────┐       ┌────────┐
      │▓▓▓▓▓▓▓▓│              │▓▓▓▓▓▓▓▓│       │  icon  │
      │▓▓▓▓▓▓▓▓│              │  icon  │       │  icon  │
      └────────┘              └────────┘       └────────┘

      cooldown fraction = time_left(heal_cooldown) ÷ HEAL_COOLDOWN
      shade height      = inner window height × cooldown fraction      (snapped to the 3 px grid)
      ```

      One full-size shade is made once, and `screen.blit(shade, pos, area)` draws only its top `shade height` rows: `blit`'s third argument, `area`, is a rect inside the source, so only that part is drawn.
- **The interaction prompt** (`draw_prompt(screen, prompt)`): when `prompt` isn't `None`, it shows the `(text, available)` from `describe_target`, centered by its visible ink at the bottom of the screen, on `PROMPT_CENTER_Y` (`SCREEN_HEIGHT − HUD_MARGIN − 36`, level with the middle of the quick slots), snapped to the 3 px grid. Available actions use `prompt_label` (`PALETTE_STEEL`) and blocked ones `prompt_blocked_label` (`PALETTE_BLOOD`), both outlined in `PALETTE_VOID`; two labels means neither has to re-render when the color changes. Red text is the only thing that says *why* F won't work, while the outline just marks what you're near.
- **`button_outline.py`**: `make_outline` builds a one-pixel outline surface from an image's mask. It outlines each separate shape in the mask (`mask.connected_components()`), because `mask.outline()` alone only traces the first shape, which for text would be just the first letter. Holes inside a shape, like the inside of an "A", are not outlined. `draw_outline` blits it shifted one pixel in each direction to make a thicker outline.
- **`cursor.py`**: `Cursor`, the custom mouse cursor, centered `CURSOR_OFFSET` (5) pixels down and right of the real mouse position.

### `world/`

Everything that makes up a floor: how a map file is read, the tile sprites, and the objects placed on a floor. `states/` holds only screens, and `items/` only item data.

- **`map_loader.py`**: reads the TMX file with pytmx.
  - `load_floor_data(map_path)` returns one dict with everything the run needs.
  - `build_map` draws the floor into a single surface and creates the tile and chest sprites.
  - `assign_door_properties(tmx_data, door_tiles)` reads the `Doors` object group: for each door object it builds a `pygame.Rect` from its position and size, and gives every door tile inside it the object's `door_id` and `key` (pytmx reads an object's `<properties>` into the dict `map_object.properties`). `load_floor_data` calls it right after `build_map`. Maps no longer have a logic layer.
  - `build_map` also turns the `Crates` object group into `Crate` sprites (`floor_data["crates"]`), placed by each object's x and y like chests.
  - `find_player_spawn` and `find_enemy_spawns` read spawn objects.
  - `find_exit` returns a `pygame.Rect` for the object named `Exit`, or `None` if there isn't one.
  - `find_placed_items` returns `(item_id, center)` pairs for the objects in the `Items` object group, stored as `floor_data["placed_items"]`. Each object is named by its item id. It loops over `tmx_data.objectgroups` to find the group by name, so a map with no `Items` group just has no placed items (`get_layer_by_name` would crash instead). The center is worked out as `(x + width / 2, y + height / 2)`, which works for both kinds of object: Level One's 10×8 rectangles drawn in Tiled, and the converter's 0-sized points, whose center is just their x and y.
- **`tiles.py`**: `WallTile`, `DecorTile` and `Door` sprites. Each draws itself offset by the camera. Doors carry a `door_id` and a `key` (the item id that opens them, `silver_key` or `gold_key`), both set by `assign_door_properties`.
- **`floor.py`**: `Floor(map_path, item_database)`, everything on one map. `Run.load_floor` builds a new one for each floor, so its state starts clean by construction.
  - **What it holds**: the map data from `load_floor_data` (`map_surface`, `decor_tiles`, `wall_tiles`, `door_tiles`, `chests`, `crates`, `exit_rect`, `player_spawn`); `ground_items`, starting with the placed items from the map's `Items` layer (each a `GroundItem` of quantity 1, looked up in the item database, so an unknown id is a `KeyError` at load time, the right moment to find a typo); an empty `particles` list; the `enemies`; `exit_requested` (`False`); and the derived `solid_tiles` and `padlocks`.
  - **`update(dt, player)`** runs the floor's frame, after the player has moved: if the player is rolling, `break_touched_crates(player)`; every enemy moves (`enemy.update`); `resolve_enemy_contacts(player)` resolves touches between the player and living enemies (roll hits, touch damage, the `roll_hit` sound) and calls `start_dying()` on an enemy at 0 HP; `resolve_enemy_strikes(player)` checks every living enemy's swing; `separate_enemies(self.enemies, player, self.solid_tiles)` pushes overlapping bodies apart; `remove_dead_enemies()` rolls the `loot_table` of each enemy whose death animation has finished, spawns the drops at its body's center and removes it (looping over `list(self.enemies)`, a copy, so removing is safe); then the ground items animate, `update_crates` finishes breaking crates, and `update_particles` moves the debris.
  - **`player_walls(player)`** is what blocks the player this frame, passed by the run to `player.update`: while the player is rolling only `solid_tiles`, otherwise `solid_tiles` plus every solid enemy (`is_solid()`) that **isn't already overlapping** the player (section 7, step 5).
  - **`draw(surface, player, highlight=None)`** draws the world in order: the map surface, walls, then decor (on top of them, since torches, banners and rings sit on wall tiles), then doors, a padlock on each locked door group, crates, ground items and chests, the interaction outline (`highlight` is `None` or a `(sprites, color)` pair from the run; nothing is drawn for an empty list), the player and enemies sorted by `rect.y` so whoever is lower is drawn in front, then the particles on top. Off-camera sprites are skipped with `is_on_screen`.
  - **`highlighted_sprites(target)`** says what to outline for an interaction target: every door tile with the target door's `door_id` (unlocking works on the whole group, so the outline does too), the exit's ladder (the decor tiles inside `exit_rect`, since the exit has no sprite of its own), or just the chest or item. The run chooses the color; the floor knows its doors and ladder.
  - Helpers:
    - `unlock_door(door_id)` removes every door tile with that id.
    - `refresh_solid_tiles()` rebuilds `solid_tiles` (walls, remaining doors and unbroken crates).
    - `refresh_padlocks()` rebuilds `padlocks`, a list of `(key, center)` pairs, one per locked door group. It groups the door tiles by `door_id` with `doors_by_id.setdefault(door.door_id, []).append(door)` (`setdefault` returns the list stored under a key, creating an empty one the first time: the usual "group things by a key" pattern), then takes each group's center from `rects[0].unionall(rects[1:])`, the rect around its tiles: the seam of a double door, or the middle of a vertical one. The padlock art is loaded in `__init__` into `padlock_images` (cached by `load_image`, so each file is read from disk once) from `PADLOCK_IMAGE_PATHS`, keyed by key item id, the same value as `door.key`.
    - **Crates.** `refresh_solid_tiles()` adds every crate still in `crates` to `solid_tiles`, so crates block the player **and** enemies like walls. While the player is rolling, `update` calls `break_touched_crates(player)`: any crate touching the player's rect grown by `CRATE_TOUCH_MARGIN` (2 pixels) starts breaking, drops its `CRATE_LOOT` at its center, and, since a breaking crate isn't solid, `refresh_solid_tiles()` runs once if anything broke, so the roll carries straight through. The margin is needed because a solid crate pushes the player out, so the two never actually overlap; the grown rect catches "pressed right up against it". Walking into a crate just bumps it: rolling is the only way to break one, the same rule as damaging enemies. `update_crates(dt)` advances every crate and, for each one with `done_breaking`, emits a `CRATE_DEBRIS` burst at its center and kills it; it loops over `crates.sprites()`, a copy, so removing crates mid-loop is safe.
    - `solid_tiles` and `padlocks` are both derived from `door_tiles`, so both are rebuilt together, in `__init__` and in `unlock_door`, whenever the doors change. Forgetting the second call leaves a padlock floating where an opened door used to be.
    - `spawn_loot(drops, center)` creates `GroundItem`s scattered randomly around a point.
    - `enemies_left()` counts the enemies that aren't dying, with `sum(1 for ...)`. Dying ones already count as defeated, so the exit opens the moment the last one is hit, without waiting out its death animation.
    - `exit_rect` is the current floor's exit area, or `None` if the map has none. `exit_requested` (`False` on every new floor) is set when the player presses F at the exit, and acted on by the run at frame step 7.
- **`objects.py`**: the sprites placed on a floor, moved here from `items/items.py` so item **data** and world **sprites** live apart.
  - `GroundItem`: a sprite for an item lying on the ground (the `ground_items` group holds them). `item` is its own clone of the `Item` (so a stack on the ground has its own quantity), and it has its own animation.
  - `Chest`: a sprite placed from the map.
  - `Crate`: a breakable box placed from the map. It has three states:

    ```
    solid ──rolled into (start_breaking)──▶ breaking: shows impact frame 2 (wide), then 3 (flattened)
          ──impact over──▶ done_breaking = True ──▶ the run bursts debris and kills it
    ```

    `start_breaking()` shows the first impact frame **immediately**, so the hit lands on the same frame as the roll. `update(dt)` is a **one-shot** animation: the looping helper (`advance_animation`) wraps back to frame 0 with `%`, but a hit should play once, so it counts seconds since the hit and turns them into a step, `step = int(break_time × CRATE_IMPACT_SPEED)`. `CRATE_IMPACT_FRAMES` (`(2, 3)`) turns each step into a frame number in the strip, so changing which frames play is a one-line edit; at `CRATE_IMPACT_SPEED` 20 per second, the 2 frames take about a tenth of a second. When the steps run out it sets `done_breaking` instead of removing itself: the crate knows **when** its impact ends, but the particle list belongs to the floor, so the floor acts on the flag (the same "flag, then the owner acts" split as `exit_requested`). Its frames come from `load_animations(crate_texture_data)`, which is cached, so every crate shares the same 4 surfaces.

### `tools/`

- **`line_counter.py`**: see section 3.
- **`make_sprite.py`**: see section 3.
- **`preview_map.py`**: see section 3.
- **`ascii_to_tmx.py`**: see section 3.
- **`make_strip.py`**: see section 3.

## 7. One gameplay frame, step by step

This is `Run.update(dt)` followed by `Run.draw(screen)`.

Before step 1, `update` has two early exits. While the player is dying, it only advances the death freeze (step 6). Then, while `floor_transition.is_active()`, it only calls `update_transition(dt)` and returns. Both come before `read_input()` and `run_time += dt`, so input, ESC, the world and the run timer are all frozen; transition time doesn't count toward the run, since loading speed differs between computers.

**1. Read input.** `read_input()` returns a fresh intent dict and stores it on `player.intent`:

| Key | Field | Kind |
| --- | --- | --- |
| WASD | `move` | Held. A normalized `Vector2`, so diagonals aren't faster. |
| SPACE | `roll` | Pressed this frame |
| F | `interact` | Pressed this frame |
| Q | `heal` | Pressed this frame |
| E | `inventory` | Pressed this frame |
| ESC | `pause` | Pressed this frame |
| P | `debug` | Pressed this frame |
| Left mouse | `mouse_left_click` | Click position this frame, or `None` |

"Pressed this frame" uses pygame-ce's `get_just_pressed`, so holding a key triggers it only once.

**2. Level-wide intents.**
- `pause`: switch to options, play `pause`, and stop this frame's update.
- Right after the pause check, `run_time += dt`. Its position is the whole pause logic: while paused, `Run.update` isn't called at all; while dying, the dying block has already returned; and on the frame ESC is pressed, the pause check returns first. So the timer only counts frames of real play. Opening the inventory doesn't pause the game, so it doesn't pause the timer either.
- `debug`: toggle hitbox drawing.
- `interact`: run `interact.interact(player, floor)` (below).
- `inventory`: open the inventory. When closing, any held item goes back into the inventory first. If it doesn't fit, the inventory stays open.
- A mouse click while the inventory is open goes to `InventoryUI.handle_click`.

The game keeps running while the inventory is open. It is an overlay, not a pause, so managing items costs time and the world can still hurt you. `INVENTORY_PAUSES_GAME` (`False`, in `run.py`) makes this a one-word change: right after the inventory input (opening, closing and clicking), `Run.update` returns early when the inventory is open and the constant is `True`, which would stop the player, enemies, contacts and camera while the inventory stays usable. The check sits after `run_time += dt`, so the run timer would keep counting even while paused.

**3. Player update** (`Player.update`):
1. Sets `walking` and updates `facing` from the move direction. Facing doesn't change mid-roll. Vertical input wins over horizontal for facing.
2. Recomputes `stats` from `base_stats` plus equipment bonuses, every frame, so equipping takes effect immediately. If the health stat changed, `set_max_health` updates the maximum and clamps current health.
3. `roll` intent → `try_start_roll`. A roll needs a move direction, can't start during another roll (`is_rolling`), and can't start while `cooldown_timer` is running. Starting one starts both `active_timer` and `cooldown_timer`.
4. `heal` intent → `use_small_health_potion`. Heals `SMALL_HEALTH_POTION_VALUE` (10 of the 25 max), removes one potion and starts the heal cooldown, unless the cooldown is still running, health is already full or there is no potion. It returns whether a potion was used, and only then does the player play the `heal` sound. The sound is played here rather than in `systems/consumables.py` because it is feedback, not a rule.
5. `update_movement`: `steer` computes the new velocity from the move direction and the `max_speed`, `acceleration_rate`, `deceleration_rate` and `grip` stats, then `move_and_collide` moves the rect against the walls the run passed in, `floor.player_walls(player)`: the solid tiles, plus solid enemies while walking (step 5). Hitting a wall zeros velocity on that axis.
6. `update_roll`: while rolling, the player is also moved by `roll_speed` in the roll direction (on top of normal movement), scaled by `roll_speed_multiplier` so the push fades out at the end of the roll (see below), then `advance_roll` counts down `active_timer` and `cooldown_timer`.
   Then the player's `speed` is measured. At the very start of `update`, the player's center is copied into `start_pos`, before anything moves. After `update_movement` and `update_roll`, the distance from `start_pos` to the new center, divided by `dt`, gives the actual speed in pixels per second. Because it is measured rather than calculated, it includes walls: rolling into a wall gives a low speed.

   ```
   speed = distance moved this frame  ÷  dt
           └────── pixels ───────┘     └ seconds ┘   →  pixels per second
   ```

7. `advance_timer` counts down the invulnerability timer, then the heal cooldown.
8. Picks the animation `player_{idle|walk|roll}_{direction}` and advances it.
9. Copies `rect.topleft` into `pos`.

**How `steer` works.** `steer` is a kinematic controller, like Godot's: it doesn't push the player with forces, it moves the current velocity toward a *target velocity*, `direction * max_speed` (zero when there is no input). Each frame it closes a fraction of the gap between the two.

```
target velocity = direction × max_speed           (zero when there is no input)
new velocity    = velocity + (target velocity − velocity) × fraction
                             └────────── the gap ─────────┘
```

- **The fraction.** `approach_fraction(rate, dt)` returns `1 - exp(-rate * dt)`. Closing a fixed fraction of the gap per *frame* would feel snappier at higher frame rates, but this formula gives the same motion at any frame rate, because two frames of `dt` multiply out to exactly one frame of `2 * dt`. A higher `rate` is snappier. As a rule of thumb, the velocity is 95 % of the way to its target after about `3 / rate` seconds.

  ```
  fraction = 1 − e^(−rate × dt)              (approach_fraction)
  time to get 95 % of the way ≈ 3 ÷ rate seconds
  ```

- **Acceleration scales by itself.** Because a fraction of the *gap* is closed, the player gains a lot of speed when standing still (big gap) and very little near `max_speed` (small gap), easing in without overshooting. No speed cap is needed.
- **Grip.** With input, the velocity is split using the dot product: `along_speed = velocity.dot(direction)` is the speed in the input direction, `along_velocity` is that part as a vector, and `across_velocity` is everything left over (sideways motion from the previous heading). The along part approaches the target at `acceleration_rate`. The across part is removed at the `grip` rate, so turns don't drift. When `along_speed` is negative (the player is reversing), the along part uses `grip` too, so turning around is as snappy as turning sideways.

  ```
  along_speed     = velocity · direction        (dot product: speed in the input direction)
  along_velocity  = direction × along_speed
  across_velocity = velocity − along_velocity   (the sideways leftover)

  new along    = along_velocity  lerped toward target velocity
                 at acceleration_rate, or at grip when along_speed < 0 (reversing)
  new across   = across_velocity × (1 − approach_fraction(grip, dt))
  new velocity = new along + new across
  ```

  The split, with the input pointing up and the old velocity still heading right:

  ```
                direction (your input, length 1)
                ↑
                |   velocity
                |  ↗
    along part  | /
                |/____→ across part (sideways)
  ```

  The along part speeds up toward `max_speed`. The across part is the leftover from the previous heading, and grip removes it.
- **Stopping.** With no input, `steer` calls `decay_velocity(velocity, deceleration_rate, dt)`, which multiplies the velocity by `1 - approach_fraction(rate, dt)` and collapses it within a few frames. Below `STOP_SPEED` (1.0 px/s) it snaps to exactly 0, because closing a fraction of the gap never quite reaches zero. Enemy knockback fades with the same function. A velocity faded this way travels a total distance of about `speed / rate` before stopping, which is handy for tuning: 250 px/s at a rate of 12 slides about 21 px.

  ```
  new velocity = velocity × (1 − approach_fraction(rate, dt))      (decay_velocity)
                 then snapped to 0 below STOP_SPEED (1.0 px/s)

  total distance travelled ≈ starting speed ÷ rate
  ```

**How the roll eases out.** The roll push isn't constant. `roll_speed_multiplier(roll)` (`systems/roll.py`) scales it, holding at 1.0 for most of the roll and then fading to 0.0 just as the roll ends, so the player slides back into walking speed instead of dropping to it in one frame.

```
multiplier
1.0 ┤████████████████████▄
    │                     ▀▄
    │                       ▀▄
0.0 ┤                         ▀
    └──────────────────────────
    0 %      roll progress    100 %
                     ↑
           ROLL_EASE_OUT_START (0.7)
```

- **Progress.** `active_timer` counts down from `ROLL_DURATION` (0.4) to 0, so the fraction of the roll done is `1 - time_left(active_timer) / ROLL_DURATION`: 0.0 at the start, 1.0 at the end. `time_left` clamps at 0, because a timer that has counted below zero would otherwise give progress above 1.0 and a negative multiplier.

  ```
  progress = 1 − time_left(active_timer) ÷ ROLL_DURATION       (0.0 at the start → 1.0 at the end)
  ```

- **The fade.** Before `ROLL_EASE_OUT_START` the multiplier is 1.0. After it, it is `(1 - progress) / (1 - ROLL_EASE_OUT_START)`, a straight line from 1.0 at progress 0.7 to 0.0 at progress 1.0. With a 0.4 s roll, the fade covers the last 0.12 s.

  ```
  multiplier = 1.0                                          while progress < ROLL_EASE_OUT_START
             = (1 − progress) ÷ (1 − ROLL_EASE_OUT_START)    after it  (1.0 → 0.0)

  roll push  = roll direction × roll_speed × multiplier
  ```

- **Measured example.** Rolling from full walking speed, the player's `speed` sampled every 0.05 s is `270, 270, 270, 270, 270, 244, 160, 77`, then 70 on the first frame after the roll.

**How `move_and_collide` works.** It moves on X, pushes the rect out of the first wall it overlaps, then does the same on Y. Doing the axes separately lets you slide along walls. Walls whose center is more than 64 pixels away on that axis are skipped for speed. It returns `(hit_x, hit_y)`.

**Particles** (`systems/particles.py`). A particle is a tiny short-lived square that flies out, slows down and shrinks away. It's pure data, a dict with `pos`, `velocity`, `color`, `size`, `drag`, `lifetime` and `age`, and the functions are the rules; the list of live particles belongs to the `Floor` (`floor.particles`, a fresh list for every floor).

```
something happens ──▶ emit_burst(particles, center, PRESET)    adds `count` particles
every frame       ──▶ update_particles(particles, dt)          move, slow down, age, drop the dead
draw              ──▶ draw_particles(surface, particles, camera) one small square each, shrinking with age
```

- **Presets are recipes**: `CRATE_DEBRIS` is `{"count": 8, "colors": (leather, torch, clay), "speed": (40, 100), "lifetime": (0.25, 0.45), "size": (2, 3), "drag": 6}`, the crate's own colors so the debris reads as the same wood. Ranges are `(lowest, highest)`, picked at random per particle with `random.uniform(*range)` (`*` unpacks the pair into two arguments). A new effect (hits, deaths, roll dust) is a new preset, with no new code.
- **`emit_burst`** gives each particle a random direction at a random speed: `pygame.Vector2(speed, 0).rotate(direction)` is a vector pointing right with length `speed`, turned by a random 0 to 360 degrees.
- **`update_particles`** moves each particle by `velocity × dt` and slows it with drag, then keeps only the live ones. `particles[:] = [...]` replaces the list's **contents**, not the list: the floor holds a reference to the same list object, so a plain `particles = [...]` inside the function would only rebind a local name, and dead particles would never leave the run's list.
- **`draw_particles`** draws each one with `surface.fill(color, rect)`, the fastest way to draw a solid square, and makes it **shrink** in whole-pixel steps instead of fading: per-pixel alpha looks muddy at 3×, while hard steps (3, 2, 1 pixels, then gone) stay crisp pixel art. They're drawn on top of the world, after the actors.

```
speed after t seconds = start speed × e^(−drag × t)        (frame-rate independent, like movement steering;
                                                            drag 6 loses about 99.75% of the speed per second)
size on screen        = ceil(start size × (1 − age ÷ lifetime)), at least 1
```

**After `floor.update`, the interaction target** is worked out (see "The interaction target, outline and prompt" below), and drawn later with **`draw_highlight(screen, sprites, camera, color)`** from `systems/masks.py`. `draw_hitbox` (the debug outline) draws each sprite's `mask.outline()` on the sprite's own edge pixels, which went wrong for interaction in two ways: each door tile was outlined separately, so the shared edge between the halves showed as a line down the middle, and `outline()` only traces **one** connected shape, so the chest, whose art has a transparent row between lid and body, only got its lid outlined. `draw_highlight` instead builds one combined shape from all the sprites, seals 1-pixel gaps, and draws a ring just **outside** it, so the art isn't painted over:

  ```
  grow:   every set pixel also sets its 4 neighbors       (grow_mask; 1 px bigger all round)
  shrink: grow the OUTSIDE instead, then flip it back      (invert, grow_mask, invert)
  close:  grow, then shrink   → fills 1-pixel gaps (the chest's lid seam), keeps the outer edge
  ring:   grow(shape) − shape → the pixels just outside the shape
  ```

  - The work area is the union of the sprites' rects (converted to whole-pixel `pygame.Rect`s, since sprites use float rects and a mask needs whole sizes), grown by 2 pixels on every side (`inflate(4, 4)`) so the ring and the close step aren't cut off.
  - `mask.draw(other, offset)` copies another mask's set pixels in at an offset (used to combine the sprites, and 4 times by `grow_mask`); `invert()` flips every pixel; `erase(other, offset)` clears pixels; `to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))` turns the ring into an image with everything else transparent.
  - It's rebuilt each frame for at most a couple of 16-pixel sprites, which is cheap.

**4. The floor's frame: enemies.** Right after the player moves, `Run.update` calls `floor.update(dt, player)` (`world/floor.py`), which runs steps 4 and 5 and then finishes the floor's frame: crate breaking first if the player is rolling, then the enemies, then contacts, swing strikes, separation and removing finished deaths, then the ground items, breaking crates and particles. Each enemy gets the solid tiles and the player's position. An enemy that isn't swinging moves with its behaviour:
- **`fly`** (Skull): ignores walls. While its `flee_timer` is running it moves away from the player, then while its `return_timer` is running it moves toward the player (both are timers from `new_timer()`, started by `trigger_flee` after a contact), within `CHASE_RANGE` (200) it chases, and otherwise it drifts slowly in a random diagonal that occasionally changes.
- **`wander_chase`** (Skeleton): collides with walls. If it has line of sight to the player (no wall rect crosses the line between them), it chases. Otherwise it wanders at half speed.
- **The swing** (types with an `"attack"` dict, the Skeleton). After moving, `try_start_attack` starts a swing when the attack cooldown isn't running and the player's position is within `range` (20 px): it sets `attacking`, zeroes `attack_time`, clears `attack_landed` and turns to face the player. While `attacking`, the enemy doesn't move; `update_attack` counts `attack_time` up. The attack animation **is** the swing's clock: `attack_step()` is `int(attack_time × frame_rate)`, the frame shown and the swing's phase at once, so the hitbox can never drift out of sync with the art:

  ```
  attack_step = int(attack_time × frame_rate)            frame_rate 10 → one frame per 0.1 s

  step:   0  1  2  3  4  5 │ 6  7 │ 8
          └── wind-up ───┘ │strike│ recover               9 attack frames
          0.0 s ─────── 0.6 s ─ 0.8 s ─ 0.9 s → attacking = False, cooldown starts (1.0 s)
  ```

  `is_striking()` is true while the step is one of `strike_frames` (6 and 7, where the slash is drawn). `strike_rect()` is the hitbox in front of the body: `reach` (18 px) wide and as tall as the body, against the body's right edge when facing right and its left edge when facing left. When the step passes the last frame, the swing ends and `attack_cooldown` starts. The 0.6 s wind-up is the telegraph: long enough to walk out of the swing or roll through it.
- **Knockback**, after the behaviour's movement: `update_knockback` moves the enemy by `knockback_velocity * dt` with `move_and_collide`, sets the shove to 0 on any axis that hits a wall (so the enemy doesn't keep pressing into it), then fades it with `decay_velocity` at the enemy's `knockback_decay_rate`. Walls block knockback for every enemy, including flying Skulls that otherwise pass through walls. The AI keeps running during a shove, and since a hit also starts the flee, both push the enemy away.

**5. The floor's frame: contact and combat** (`floor.resolve_enemy_contacts`). `find_player_contacts` checks enemies within 100 pixels and keeps those whose masks actually overlap the player (pixel-perfect, not rectangle). For each contact, `resolve_contact`:
- **only while the player is rolling**, deals `round(player.speed * ROLL_DAMAGE_PER_SPEED)` to the enemy, shoves it, and starts the enemy's own invulnerability window for `enemy.invulnerability_duration`, unless the enemy is already invulnerable. Rolling is the player's only attack: walking into an enemy doesn't hurt it.
- **interrupts a swing**: a roll hit on an enemy with an `attack` calls `interrupt_attack()`, which cancels a swing still in its wind-up (not once it's striking or has landed) and starts the attack cooldown, so rolling into a winding-up Skeleton stops the blow,
- **only for types with `touch_damage`** (the Skull), deals the enemy's `attack_damage` to the player and starts the player's invulnerability window, unless the player is already invulnerable or is rolling. The Skeleton only hurts with its swing,
- always starts the enemy's flee (2 s) then return (3 s) timers, even when both hits were skipped, so an enemy can't stay on top of the player.

An enemy whose health reaches 0 calls `start_dying()`: it stops moving, attacking and blocking, and plays its death animation. Once `is_done_dying()`, `remove_dead_enemies` rolls its `loot_table` with `roll_loot`, spawns the drops at its center with `spawn_loot`, then removes it from `enemies`. The drops are spawned before the removal, while the enemy and its position still exist.

**Strikes** (`floor.resolve_enemy_strikes` → `resolve_strike(player, enemy)` in `systems/combat.py`). For every living enemy with an `attack`: if it `is_striking()`, hasn't landed this swing, and its `strike_rect()` touches the player's rect, the swing **lands**: `attack_landed` is set, so one swing can only hit once across both strike frames. If the player is invulnerable or rolling, the landed swing does nothing (dodged); otherwise it deals `attack_damage` and starts the player's invulnerability window. It returns whether the player was hit. The strike uses rectangles, not masks: the hitbox is a rule, not a picture.

**Bodies: separation and blocking.** Solid enemies (walkers, not fliers or the dying; `enemy.is_solid()`) can't stack on each other or stand on the player, and the player can't push them:

```
walking into an enemy   → blocked: solid enemies are in player_walls, so the player stops at its edge
rolling into an enemy   → player_walls drops the enemies: the roll passes through, hits and knocks it back
roll ends inside one    → that enemy is left out of player_walls (it overlaps), separation pushes it off
an enemy walks into you → it overlaps (combat sees it), then separation pushes the ENEMY out
two enemies overlap     → separation pushes each half the overlap apart
fliers (Skull)          → not solid: pass over everything, so their touch damage can always reach you
```

`separate_enemies(enemies, player, walls)` (`systems/separation.py`) runs **after** contacts and strikes, so combat has had its chance to see an overlap before it's undone. For each pair of solid enemies, `push_out(rect, other_rect)` returns the shortest way out of the overlap, or `None` if they don't overlap: it clips the two rects, and pushes along the **thinner** side of the overlap (the minimum translation), in the direction from the other's center to this one's. Each enemy is then `shove`d half of it, in opposite directions. Then, unless the player is rolling, an enemy overlapping the player is shoved the **whole** way out: the enemy always yields, because the player is blocked by solid enemies and can't be the one moving into them. While rolling there's no push, or the roll would carry the enemy along in front of it.

```
overlap = rect.clip(other_rect)                    the shared area (width or height 0 = no overlap)

overlap.width < overlap.height  → push x by ±overlap.width     (narrower sideways: slide apart sideways)
otherwise                       → push y by ±overlap.height
sign: + when this rect's center is right of / below the other's
```

`shove` moves with `move_and_collide`, so separation can't push an enemy into a wall. One pass a frame is enough: an overlap left over (three enemies in a cluster, or one pinned against a wall) is resolved over the next frames.

`floor.player_walls(player)` is the other half: the walls `Run.update` passes to `player.update`. It's chosen before the player moves, so on the single frame a roll starts the player is still blocked (1/240 s, not noticeable). An enemy already overlapping the player is left out, because `move_and_collide` against a rect you're already inside would snap the player to its edge.

**The shove.** The direction is from the player's center to the enemy's center, normalized, so a head-on hit pushes the enemy straight back and a glancing hit pushes it sideways. If the two centers are exactly the same point, that vector has zero length and can't be normalized, so the roll direction is used instead. The shove is `direction * player.speed * KNOCKBACK_PER_SPEED * enemy.knockback_multiplier`: the player's hit strength (roll speed times `KNOCKBACK_PER_SPEED`, 1.2) scaled by how easily this enemy is pushed. Speed now drives both damage and knockback, so a full-speed roll hits hardest and a hit as the roll fades barely shoves.

```
knockback speed    = player.speed  ×  KNOCKBACK_PER_SPEED  ×  enemy.knockback_multiplier
                     └──── the player's hit strength ────┘     └─ this enemy's weight ─┘

knockback velocity = direction (player → enemy, length 1) × knockback speed
slide distance     ≈ knockback speed ÷ enemy.knockback_decay_rate
```

The player's window lasts `PLAYER_INVULNERABILITY_DURATION` (1 s), and each enemy's lasts its own `invulnerability_duration`, so each side can be hit at most once per window however long the sprites overlap. If several enemies touch the player on the same frame, the first one's hit starts the window and the rest are skipped, because the contacts are resolved one at a time. A roll blocks damage for its 0.4 s but doesn't start a window. Enemies at 0 health start dying.

```
roll damage = round(player.speed  ×  ROLL_DAMAGE_PER_SPEED)
                    └ measured ─┘     └────── 0.15 ──────┘
                      roll speed
```

`ROLL_DAMAGE_PER_SPEED` is 0.15, so a roll at about 204 pixels per second deals 31, and a 100 health enemy takes about 3 rolls. Because damage comes from measured speed and the roll push fades out, a hit near the end of a roll does less damage than one early in it, which rewards rolling *into* enemies. Because an enemy's invulnerability (1 s) lasts longer than a roll (0.4 s), each enemy can be hit at most once per roll, but different enemies each have their own window, so rolling through a group hits them all. `resolve_contact` returns `True` when the enemy was hit, and `Run.update` then plays the `roll_hit` sound. The sound is played in the floor (`resolve_enemy_contacts`) rather than in `systems/combat.py` because it is feedback, not a rule.

**6. Player death.** After all contacts are resolved, the run checks `is_dead(player.health) and not self.dying`. The check is here rather than in `systems/health.py` because `is_dead` is the rule and what happens next is the run's decision.

`is_dead` is a condition that stays true on every frame once health is 0, but the death sequence must start only once, at the moment of death. The `dying` flag handles that: on the first dead frame the run sets `dying = True`, starts `death_timer` with `DEATH_DELAY`, stops the music, plays the `death` sound, and returns early so the ground items and camera don't update. On later frames `not self.dying` is false, so none of it repeats.

While `dying` is true, the very first thing `Run.update` does is count `death_timer` down by `dt`, update the fade, and return. Because that check comes before `read_input()`, input, movement, enemies and contacts are all skipped, so ESC can't pause and Q can't heal during the freeze. `Run.draw` still runs every frame, so the world stays on screen, frozen as it was. When the timer reaches 0 the run switches to `"game_over"`. Restart and Main Menu build a brand new `Run`, so `dying` and the timer reset on their own.

**The death fade.** Each dying frame, the Run works out how far the fade has gone and hands the result to the player, who only draws it:

```
elapsed       = DEATH_DELAY − time_left(death_timer)
fade_progress = min(1.0, elapsed ÷ DEATH_FADE_DURATION)    (0.0 → 1.0, then held)
player.alpha  = round(255 × (1 − fade_progress))           (255 visible → 0 invisible)
```

- `elapsed = DEATH_DELAY - time_left(death_timer)` is the seconds since death (the timer counts down, so time passed is the total minus what's left).
- `fade_progress = min(1.0, elapsed / DEATH_FADE_DURATION)` goes from 0.0 at death to 1.0 when the fade is done. The `min` holds it at 1.0 afterwards.
- `player.alpha = round(255 * (1 - fade_progress))` takes the body from fully visible to invisible.

So the body fades over 1.5 s, then the empty spot holds until the 3.0 s delay ends. The alpha is set in `update`, where the timer advances, so `draw` only draws. The player's blink doesn't interfere: the killing hit started the player's i-frames at 1.0 s, the freeze stops them counting down, and that frozen blink phase is a visible one.

**7. Leaving through the exit.** Climbing down takes **F**, and only once the floor is cleared: walking onto the ladder does nothing by itself, so nobody leaves a floor by accident, and F is refused while `floor.enemies_left()` is above 0. Pressing F at the exit only sets `exit_requested` (see "What `interact` does"); the leaving happens here, after the death check. If `exit_requested` is set, the run clears it, then records the split (`splits.append(run_time)`), for every floor including the last, then checks whether there is another floor (`floor_index + 1 < len(FLOOR_ORDER)`). If there is, it calls `floor_transition.start()`, which begins the fade; `floor_index` only goes up later, when the next floor actually loads at the end of the fade. Otherwise the run is over and the run switches to `"run_complete"`. Either way `update` returns.

```
FLOOR_ORDER = [floor 0, floor 1]

exit on floor 0:  0 + 1 < 2  →  floor_transition.start()  …  update returns True: floor_index 0 → 1, load_floor(FLOOR_ORDER[1])
exit on floor 1:  1 + 1 < 2 is false  →  "run_complete"
```

The check comes after the death check, so dying and pressing F at the exit on the same frame counts as a death. A map without an exit can never set the flag, because `find_target` checks `exit_rect is not None` first (and `and` stops at the first false part, so it never tries to collide with `None`). After the switch `Run.update` is no longer called, so `run_time` stays at the finishing time.

**8. Camera.** The camera centers on the player. (Ground items, breaking crates and particles were already updated at the end of `floor.update`, in step 4.)

**What `interact` does (F).** Everything about F comes from one question, `find_target(player, floor)`: "what would F act on right now?" All of `interact.py` takes the **floor**, since chests, ground items, doors, the exit and the enemy count all belong to it. It looks in a box `REACH` (15) pixels larger than the player and returns the first match, as `(kind, sprite)`, in this priority order:
1. **A chest.**
2. **A ground item.**
3. **The exit**, when the reach box touches `exit_rect`; the target is the rect itself, since the exit isn't a sprite. It comes after the ground items, so loot lying on the ladder is picked up first.
4. **A door tile**, even without a key. Doors are checked last because a locked door is now always a target: if they came first, a potion lying next to a locked door could never be picked up, since F would keep choosing the door. With doors last, things you can always act on win.

`describe_target(player, floor, found)` turns the target into the prompt text and whether F will work, `(text, available)`. It takes the floor for the exit, whose target is only `exit_rect`, a rect with no way back to the floor's enemies:

| Target | Text | Available |
|---|---|---|
| chest | `Press F to open chest` | yes |
| ground item | `Press F to pick up <item.name>` | yes |
| door, with its key (`door.key`) | `Press F to unlock door` | yes |
| silver door, no silver key | `Silver key required to unlock door` | no |
| gold door, no gold key | `Gold key required to unlock door` | no |
| exit, enemies left | `3 enemies left to defeat` (`1 enemy left to defeat` for one) | no |
| exit, floor cleared | `Press F to climb down` | yes |

`interact` asks the same question before acting and does nothing if the target isn't available, so the key check and the clear check each live in exactly one place, shared by the prompt, the outline color and the action. Then:
- **A chest:** rolls `CHEST_LOOT`, spawns the drops around the chest, and removes the chest.
- **A door:** removes every door tile with the same `door_id`, rebuilds the solid tiles, and uses up one key of the door's own color (`remove_item(inventory, door.key)`).

Every door tile knows which key opens it (`door.key`, `"silver_key"` or `"gold_key"`, from the map's `Doors` objects), so `describe_target` and `unlock_door` just ask the door; nothing in gameplay assumes a color. The "required" prompt builds the key's name from its id: `"silver_key".replace("_", " ")` is `"silver key"`, and `.capitalize()` uppercases only the first letter, giving `"Silver key"`. So a new key color later gets its prompt for free.
- **A ground item:** adds it to the inventory. If only part of the stack fits, the rest stays on the ground with the reduced quantity.
- **The exit:** sets `floor.exit_requested = True`, and nothing else. `interact` runs early in `Run.update`, before enemies move and before the death check; if it started the floor change right there, the rest of the frame would still run, and an enemy could hit (or kill) the player mid-transition. With a flag, the actual leaving happens at frame step 7, after the death check, so dying and exiting on the same frame still counts as a death, and the split and transition code stays in one place. Every new `Floor` starts with the flag `False`, so a new floor never starts with a pending exit.

**The interaction target, outline and prompt.** Right after `floor.update`, `Run.update` stores `interact_target` (from `find_target`) and `interact_prompt` (from `describe_target`, or `None`), so they match where the player is this frame; `draw` only uses them. Both are cleared in `__init__`, in `load_floor` (the target would otherwise point at a sprite from the old floor, and its outline would show during the fade-in, which skips `update`), and every frame of the death freeze (so no prompt shows while dying).

```
find_target(player, floor) ──▶ ("chest", …) / ("item", …) / ("exit", exit_rect) / ("door", …) / None
        ├──▶ describe_target ──▶ (text, available)
        ├──▶ outline: floor.highlighted_sprites(target) → the whole door group, the exit's ladder, or the one chest or item
        │             PALETTE_CANDLE if F will work, PALETTE_STEEL if it won't
        └──▶ HUD prompt: bottom center, steel text, or blood for "key required"
```

`floor.highlighted_sprites(target)` returns the sprites to outline (it lives on the floor because it needs the floor's doors and ladder; the run only picks the color and passes `(sprites, color)` to `floor.draw`): every door tile with the target's `door_id` (a door is 2 tiles, and unlocking works on the whole group, so the outline does too), the exit's ladder (the decor tiles inside `exit_rect`, since the exit has no sprite of its own), or just the chest or item. They're drawn with `draw_highlight` (see `masks.py`), but only if the list isn't empty: a map whose exit has no ladder tile (the old Level One) would give an empty list, and `draw_highlight` would crash on `rects[0]`. An empty list counts as false, so `if sprites:` reads "if there are any". The outline and the prompt come from the same answer as F itself, so they can never disagree with what F does.

**Drawing order** (`Run.draw`, then `Floor.draw`). Steps 1 to 5 draw onto `world_surface`, at `position - camera`, and anything outside the camera (`is_on_screen`) is skipped. Every world-drawing call already takes the surface to draw on as a parameter, so tiles, items and actors don't know or care that it's a small canvas. `Run.draw` does step 1, picks the interaction outline's color, and calls `floor.draw(world_surface, player, highlight)` for steps 2 to 5; then it does steps 6 to 9 itself:
1. Fill `world_surface` with `MENU_BACKGROUND_COLOR`, clearing last frame (the map doesn't cover the whole view, so old frames would otherwise smear around the edges).
2. The pre-rendered floor surface.
3. Walls, then decor (on top of the walls it hangs on), then doors, then a padlock centered on each locked door group, in the color of the key it needs (`padlock_images[key]`). `padlock_images.get(key)` returns `None` for a door with no key (only the old hand-made Level One has those), and that door is skipped instead of crashing.
4. Crates, ground items and chests (crates first, so loot dropped by a breaking crate is drawn on top of it), then the interaction outline around `highlighted_sprites` (candle or steel, from the `highlight` pair the run passed in), drawn after them so it isn't covered and before the actors so the player stays in front.
5. The player and enemies, sorted by `rect.y` so whoever is lower on screen draws in front. Enemy health bars and debug hitboxes are drawn by the entities onto the same surface, so they scale too. Then the particles, on top of the world.
6. Scale the world onto the screen: `pygame.transform.scale_by(world_surface, GAME_SCALE)` returns a new surface 3 times bigger, using nearest-neighbor scaling so pixels stay crisp instead of blurring, and it's blitted at (0, 0).
7. The HUD, `self.hud.draw(screen, player, run_time, floor_index + 1, interact_prompt)`: the health panel (top left), the run timer (top center), the floor number (right of the timer), the quick slots (bottom left) and the interaction prompt (bottom center), on the screen at full resolution. It comes after step 6, so it lands on top of the world.
8. The inventory overlay, if open.
9. `floor_transition.draw(screen)`: during a floor transition, the black overlay at `overlay_alpha()` over everything including the HUD, then the floor card text during `"card"`.

The pause menu and the end-of-run screens call `run.draw(screen)` to show the frozen run behind them, so they get the scaled view automatically.

**Inventory screen** (`InventoryUI`):
- A centered window with 4 equipment slots (`head`, `chest`, `boots`, `ability`) on the left and a 5 × 4 grid of the 20 inventory slots on the right, over the dimmed world (layout and formulas in section 6).
- Clicking a grid slot swaps it with the item in your hand, which picks up, places or swaps.
- Clicking an equipment slot while holding an item equips it only if `item.slot` matches that slot name. Clicking it with an empty hand takes the equipped item off.
- Hovering an item with an empty hand shows a framed tooltip with its name, description and `value_text` (if any); hovering an empty equipment slot shows the slot's name. Stack counts show, outlined, in the slot corner.

## 8. Data formats

**Player `base_stats`** (`player.py`). These are the values before equipment:

| Stat | Value | Used for |
| --- | --- | --- |
| `defense` | 0 | Not used yet |
| `max_speed` | 70 | Target speed in `steer` (pixels/second) |
| `health` | 25 | Max health (kept low for now while values are being worked out) |
| `roll_speed` | 200 | Extra speed during a roll |
| `acceleration_rate` | 20 | How fast the player reaches `max_speed` while holding a direction (95 % in about 0.15 s) |
| `deceleration_rate` | 60 | How fast the player stops with no input (to a full stop in about 0.07 s) |
| `grip` | 50 | How fast sideways and reversing velocity is removed (sideways drift gone in about 0.09 s) |

Roll timing is in `systems/roll.py`: `ROLL_DURATION` 0.4 s, `ROLL_COOLDOWN` 1.0 s (the cooldown starts when the roll starts), and `ROLL_EASE_OUT_START` 0.7 (the push starts fading after 70 % of the roll).

**`roll` dict** (player): `{"direction", "active_timer", "cooldown_timer"}`. `direction` is the move direction copied when the roll started. `active_timer` holds the seconds left in the current roll, and `cooldown_timer` the seconds before the next roll can start. Both are timers from `new_timer()`. There is no separate "active" flag: `is_rolling(roll)` is true while `active_timer` is running, and all code asks it that way.

**Timers** (`systems/timer.py`). Every countdown in the game is a `{"time_left": seconds}` dict made with `new_timer()`, including the enemies' flee and return countdowns. `start_timer(timer, duration)` sets it, `advance_timer(timer, dt)` subtracts `dt` each frame, and `is_running(timer)` is true while it is `> 0`. `time_left(timer)` returns the seconds left, never below 0, for code that needs the number itself, such as the roll ease-out and the player's blink. The value keeps counting below 0, which is harmless because every check goes through `is_running` or `time_left`. Only `timer.py` reads the `"time_left"` key directly, so the key could change again without touching anything else (it was renamed from `"timer"`, since a timer with a "timer" key read oddly and `time_left()` already returns it). The roll's `active_timer` and `cooldown_timer` are timers too. The one exception is animation, which is a different kind of timer that counts *up* to advance frames.

**`invulnerability` dict** (player and enemies): a timer holding the seconds of invulnerability left. The player's window is `PLAYER_INVULNERABILITY_DURATION` (1.0 s, `systems/combat.py`), and each enemy's is its own `invulnerability_duration` from `ENEMY_TYPES`. The player's `BLINK_INTERVAL` is 0.1 s (`player.py`), and `ROLL_DAMAGE_PER_SPEED` is 0.15 (`systems/combat.py`), so an enemy with 100 health dies after about 3 rolls.

**`heal_cooldown` dict** (player): a timer holding the seconds left before another potion can be used. `use_small_health_potion` refuses while `is_running(heal_cooldown)`. `HEAL_COOLDOWN` is 3.0 s (`systems/consumables.py`). The cooldown only starts when a potion is actually used, so a refused Q press (full health or no potion) doesn't start it.

**Equipment bonuses.** `compute_stats` copies `base_stats` and adds each equipped item's `bonuses` to stats with the same name. Bonus names that aren't in `base_stats` are ignored. Speed boots give `{"max_speed": 10, "acceleration_rate": 7, "defense": 3, "health": 10}`.

**`ENEMY_TYPES`** (`enemy_type_data.py`). The key must match the map spawn name after `Enemy_`:

```python
"Skull": {
    "max_health": 100,
    "attack_damage": 5,        # damage dealt to the player on contact
    "behavior": "fly",         # "fly" or "wander_chase"
    "speed": 50,
    "texture_data": skull_texture_data,
    "start_animation": "skull_idle",
    "knockback_multiplier": 1.2,   # how easily it is shoved by a roll hit
    "knockback_decay_rate": 10,    # how fast the shove fades (higher is shorter)
    "blink_interval": 0.1,         # seconds per blink on/off after a hit
    "invulnerability_duration": 1.0,  # seconds of i-frames after a hit
    "loot_table": SKULL_LOOT,     # what it can drop when it dies
    "body": (0, 0, 16, 16),        # x, y, width, height of the body inside the frame
    "touch_damage": True,          # hurts the player on contact
    "animation_prefix": None,      # one animation, no states
    "attack": None,                # no swing
},
"Skeleton": {
    "max_health": 100,
    "attack_damage": 6,            # damage of one landed swing
    "behavior": "wander_chase",
    "speed": 40,
    "texture_data": skeleton_texture_data,
    "start_animation": "skeleton_idle_right",
    "knockback_multiplier": 0.7,
    "knockback_decay_rate": 16,
    "blink_interval": None,        # no blink: it plays its hurt animation instead
    "invulnerability_duration": 1.0,
    "loot_table": SKELETON_LOOT,
    "body": (8, 13, 14, 16),       # the body inside its 32x32 frame
    "touch_damage": False,         # only its swing hurts
    "animation_prefix": "skeleton",  # animations named skeleton_<action>_<facing>
    "attack": {
        "range": 20,               # px: starts a swing when the player is this close
        "frame_rate": 10,          # attack frames per second: frames 0-5 wind up in 0.6 s
        "strike_frames": (6, 7),   # the frames that hurt: where the slash is drawn
        "reach": 18,               # px the strike hitbox extends in front of the body
        "cooldown": 1.0,           # s after a swing before the next one
    },
},
```

- **`attack_damage`** means what hurts: the touch for a `touch_damage` type, one landed swing for a type with an `attack`.
- **`body`** is the box that moves, collides, gets separated and blocks the player, given inside the art frame, so art can be bigger than the body (the Skeleton's 32×32 frame has a lot of empty space around a 14×16 body).
- **`animation_prefix`** turns on animation states: the texture data must then have `<prefix>_idle_right`, `_move_right`, `_hurt_right` and `_death_right` (and `_attack_right` for a type with an `attack`). `None` keeps the single `start_animation`.
- **`blink_interval`** `None` turns the hit blink off, for types whose hurt animation already shows the hit.
- **`attack`** `None` means no swing; a dict turns on the telegraphed swing (section 7, step 4).

Every key is required. `Enemy.__init__` reads them with `type_data["..."]`, so a missing key raises `KeyError` naming it when the floor loads, instead of silently using a default.

`knockback_multiplier` scales the player's hit strength: 1.0 is normal, above 1 is light (pushed further), below 1 is heavy, and 0 can't be moved at all. The Skull is 1.2 and the Skeleton 0.7, so the same roll slides a Skull about 38 px and a Skeleton about 14 px.

**Blink** (`systems/blink.py`). `is_blink_hidden(invulnerability, blink_interval)` is the shared rule: while the timer is running, `int(time_left / blink_interval)` counts up once per interval, and every odd count is hidden. The rule is shared, but each entity owns its interval: the player's `BLINK_INTERVAL` and each enemy's `blink_interval`.

```
blink_phase = int(time_left(invulnerability) ÷ blink_interval)    (counts up once per interval)
hidden      = timer is running  and  blink_phase is odd
```

**Texture data** (`*_texture_data.py`). One entry per animation:

```python
"player_walk_right": {
    "size": (64, 64),          # width and height of one frame
    "position": (0, 0),        # only the second number is used: the row on the sheet
    "frames": 6,               # how many frames, read left to right
    "file_path": "Assets/Player/Walk/Proto_Walk_Right.png",
},
```

`load_animations(texture_data, crop_size=None)` returns `{animation_name: [frames]}`:
- It slices each sheet into frames (`slice_frames`).
- If `crop_size` is given, it crops each frame from the center (`crop_center`).
- For every `*_right` animation it adds a mirrored `*_left` (`add_flipped_left`), unless a `*_left` already exists.

Results are cached by the set of animation names plus `crop_size`. Two texture dicts with identical names would share one cache entry, so give each animation a unique name. Images are cached by path in `load_image`.

**Health dict** (`systems/health.py`). `{"current": hp, "maximum": hp}`, made with `new_health(maximum)`, which starts full. `take_damage` and `heal` keep `current` between 0 and `maximum`; `set_max_health(health, new_max)` changes `maximum` and clamps `current` (used when gear changes the player's health stat). An enemy's health comes from its type's `"max_health"` stat in `ENEMY_TYPES`: that key names the stat, while the dict itself uses `"current"` and `"maximum"`.

**Animation dict** (`systems/animation.py`). `{"frames", "current", "index", "timer", "speed"}`. `speed` is frames per second: 10 by default, and 4 for item animations. `set_animation` only restarts when the name actually changes and exists.

**Item database** (`item_database.py`). Keys are item ids, values are `Item` or `EquipmentItem` templates. Templates are never put in an inventory directly. Code always works with `clone()`s.

**`CHEST_LOOT`** (`loot_table_data.py`). Each entry is rolled independently, so one chest can drop several things:

```python
{"item_id": "small_health_potion", "chance": 0.5, "min_quantity": 1, "max_quantity": 3}
{"item_id": "speed_boots", "chance": 0.08, "min_quantity": 1, "max_quantity": 1}
```

Keys are not chest loot: they're placed on the map (the `Items` layer), so every floor is guaranteed to have the keys its doors need, and routes don't depend on luck. Chests are for random extras: potions and gear.

**Crate loot.** `CRATE_LOOT` is a 15% chance of 1 to 2 small health potions per broken crate: crates are quick and plentiful, so each one is a small gamble, rolled at the moment of the hit.

**Enemy loot.** Each enemy type has its own table, the same shape as `CHEST_LOOT`, kept in `loot_table_data.py` and attached to the type as `ENEMY_TYPES[...]["loot_table"]`:

```python
SKULL_LOOT    = [{"item_id": "small_health_potion", "chance": 0.25, "min_quantity": 1, "max_quantity": 1}]
SKELETON_LOOT = [{"item_id": "small_health_potion", "chance": 0.35, "min_quantity": 1, "max_quantity": 1}]
```

Enemies drop single potions, smaller than a chest's 1 to 3, so chests stay the bigger prize and are worth a detour. A chest and an enemy go through the same pipeline; only the event and the table differ:

```
chest opened ──▶ roll_loot(CHEST_LOOT)        ──▶ floor.spawn_loot(drops, chest center)
enemy dies   ──▶ roll_loot(enemy.loot_table)  ──▶ floor.spawn_loot(drops, enemy center)
```

The table belongs to the enemy type, so a tougher enemy can be worth more, and because it's data, a difficulty mode can later scale every table (more potions on Easy) without touching code. With Level One's 2 Skulls and 2 Skeletons:

```
average potions per kill:  Skull 0.25, Skeleton 0.35
per full clear:            2 × 0.25 + 2 × 0.35 = 1.2 potions on average
chance of no drop at all:  0.75² × 0.65² ≈ 0.24   (about 1 clear in 4)
```

`chance` is 0.0 to 1.0, and the quantity is a random whole number between min and max inclusive.

**Settings file.** `settings.json` in the project root. It is ignored by git, so each machine has its own. It is created when you leave the options menu.

```json
{"fps_enabled": false, "full_screen_enabled": false, "music_volume": 0.5, "sfx_volume": 0.5}
```

Missing keys fall back to the defaults in `systems/settings.py`. A corrupted file prints a warning and uses the defaults.

**Sounds.** Every file ending in one of `AUDIO_EXTENSIONS` (`.wav`, `.ogg`) in `SFX_FOLDER` (`Assets/Sounds`) and `MUSIC_FOLDER` (`Assets/Music`) is loaded and named by its filename without the extension. Sound files are named in lowercase snake_case, so their keys are too. Names currently used: `button_hover`, `button_click`, `pause`, `heal`, `death` and `roll_hit` (SFX), and `menu_music`, `level_music` and `game_over` (music). Each state picks its own track in `enter()` (section 5). A missing name prints a message instead of crashing.

**The maps** (`Assets/Maps/*.tmx`, 16x16 tiles; the floors are written by the ASCII converter, and Tiled can open them). The loader looks for these names:

| Layer | Type | What the loader does |
| --- | --- | --- |
| `Floor` | Tile layer | Drawn once into `map_surface` |
| `Walls` | Tile layer | One `WallTile` per tile. These block movement. |
| `Wall_Decor`, `Floor_Decor` | Tile layers | `DecorTile`s, drawn but not solid |
| `Door_Tiles` | Tile layer | One `Door` per tile. These block movement until unlocked. |
| `Chests` | Object layer | One `Chest` per object named `chest` (any capitalization) |
| `Crates` | Object layer | One `Crate` per object |
| `Items` | Object layer | Placed items: each object is named by its item id (`silver_key`, `gold_key`) and spawned as a `GroundItem` at its center |
| `Doors` | Object layer | One `door` object per door group, with `door_id` and `key` properties; every door tile inside its rect gets both |
| `Entity_Spawns` | Object layer | `Player` is the player spawn. `Enemy_<Type>` objects (e.g. `Enemy_Skull`) are enemy spawns. A rectangle object named `Exit` is the floor's exit. A map without one can't be finished, but doesn't crash. |

Door tiles that share a `door_id` (e.g. `door_1`) unlock together as one door. The exit is drawn by the ladder tile on `Floor_Decor`.

## 9. How to add things

**A new enemy type.**
1. Add its sheet layout to `entities/enemies/enemy_texture_data.py`.
2. Add an entry to `ENEMY_TYPES` with a key like `"Bat"`, its stats, a `behavior` (`"fly"` or `"wander_chase"`), its texture data, its starting animation name, and its `knockback_multiplier`, `knockback_decay_rate`, `blink_interval` (or `None`), `invulnerability_duration`, `loot_table` (a table in `loot_table_data.py`; use `[]` for no drops), `body`, `touch_damage`, `animation_prefix` (or `None`) and `attack` (or `None`); section 8 explains each. Every key is required: a missing one crashes at floor load with a `KeyError` naming it.
3. In Tiled, place objects named `Enemy_Bat` in `Entity_Spawns`.
4. For a new behaviour, write a `<behavior>_velocity` function in `systems/enemy_ai.py` and add a branch for it in `Enemy.update_movement`.

**A new floor.**
1. Sketch it in `Assets/Maps/Source/<name>.txt` with the converter's legend (section 3): walls at least 2 thick, doors 2 tiles in a corridor through a wall, one key of the matching color per door group (`s` for an `S` door on the main path, `g` for a `G` treasure door), one `@`, one `X`, and crates (`B`) anywhere they should block the way or hide a little loot.
2. Convert it: `venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/<name>.txt`, which writes `Assets/Maps/<name>.tmx`. Fix any `ValueError` it reports. If it says the exit can't be reached, check that every door's key can be reached before that door.
3. Preview it: `venv/Scripts/python -m tools.preview_map Assets/Maps/<name>.tmx`, then check `map_previews/<name>.png`.
4. Add its path to `FLOOR_ORDER` in `constants.py`, where the order is the play order.
5. Optionally polish it in Tiled, but reconverting overwrites hand edits, so make changes in the text source where possible.

**A new item.**
1. Draw its art as a new entry in `SPRITES` in `tools/make_sprite.py` (16×16, saved to `Assets/Items/`) and run the tool, then add its sheet layout to `items/item_texture_data.py` pointing at that PNG.
2. In `initialize_item_database`, load its animations and add an `Item` (or `EquipmentItem` with `slot` and `bonuses`) under a new id.
3. To make it drop, add an entry to `CHEST_LOOT`.
4. If it does something when used, add a function to `systems/consumables.py` and call it from the player on a new intent.

**New equipment.** Use `EquipmentItem` with `slot` set to one of `head`, `chest`, `boots` or `ability`. Its `bonuses` keys must match names in `base_stats`. For a new slot, add the name to `EQUIPMENT_SLOT_NAMES` in `systems/inventory.py`. The inventory screen draws one equipment slot per name and resizes its window to fit.

**A new key binding.** Add a field to the dict returned by `read_input`, then react to it in `Run.update` (run-wide actions) or `Player.update` (player actions).

**A new state or menu.**
1. Create a class with `enter()`, `update(dt)` and `draw(screen)` that takes `game_state_manager`. Put its music in `enter()`, or use `pass` to keep whatever is playing.
2. Build it in `Game.__init__` and register it with `add_state("name", state)`.
3. Switch to it from another state with `set_state("name")`.
4. For a menu, follow the existing ones: fill the screen with `MENU_BACKGROUND_COLOR`, create the fonts once in `__init__` from `FONT_PATH`, and use `TextButton`s with `BUTTON_FONT_SIZE`.


**A new sound or music track.** Drop a `.wav` or `.ogg` into `Assets/Sounds` or `Assets/Music` and play it by filename: `sound.play_sfx("name")` or `sound.play_music("name")`. To give a screen its own track, call `play_music` in that state's `enter()`.

## 10. Debug tools

- **P**: toggles `debug.show_hitboxes`. While it's on, mask outlines are drawn for the player (green), enemies (red, around the art) and walls (blue). These are the same masks used for contact detection, so what you see is exactly what collides with enemies. Each enemy's **body** box is drawn in yellow (what moves, collides and blocks), and during the strike frames of a swing its **strike box** is drawn in red. Wall collision itself uses rectangles. The player's outline is still drawn while the sprite blinks during invulnerability.
- **FPS counter**: turn it on in Options. It shows in the top right and refreshes twice a second. The setting is saved.

## 11. Known gaps and planned work

**Combat:**
- Death fades the player's body out as a stand-in until real character art and a death animation exist.
- A per-enemy speed drain on contact (set in `ENEMY_TYPES`) is planned.
- A stagger (no AI movement while an enemy is being knocked back) is a possible follow-up if hits feel too floaty.
- `KNOCKBACK_PER_SPEED` could move into the player's `base_stats` if gear should ever boost knockback, so `compute_stats` picks up the bonus.
- The `defense` stat exists but isn't used yet.
- A Skeleton starts a swing by distance, but the strike box only reaches left or right, so a player standing straight above or below it can make it swing at nothing. Fine for now; a vertical strike (or only swinging when the player is level with it) is a possible follow-up.
- Skulls aren't solid, so several can overlap each other.
- Solid enemies can pin a walking player against a wall; rolling through them is the way out, and is on its cooldown sometimes. Part of the design, to judge in the tuning pass.
- Enemy hits have no particles yet (bone chips for Skeletons, sparks for Skulls; in the backlog).
- With the current stats, roll speed only varies between about 200 and 270 pixels per second, so roll damage varies only a little until movement tuning and gear change it.

**Movement:**
- All movement values are first-pass numbers. They will be tuned once the basic gameplay features are in and levels are being built, with feedback from playtesters.
- Speeds are in world pixels per second, so the player covers the same number of tiles per second at any `GAME_SCALE`. At 3× the screen shows a third as many tiles across, so movement looks about 3× faster on screen than it did at 1×. Something to judge in the tuning pass.

**Content and map:**
- Level One's `Keys` tile layer is unused and hidden: it was only a visual stand-in, and the `Items` object layer, which the loader reads, replaces it.
- `start_new_run()` reloads the map inside the update of whichever menu calls it (`RunEndScreen` or `OptionsMenu`), so the first frame of the new run gets a large `dt` covering the load time.
- If the inventory is open when the player touches an exit, it stays open underneath the floor transition (harmless; clicks are ignored until play resumes).
- Easy has 1 of its 5 floors so far, so a run currently ends at floor 1's exit, and the floor transition and split rows only show once floor 2 exists.
- The old hand-made `Dungeon_Level_One.tmx` still uses a `Logic_Layer`, which the loader no longer reads, so its doors load without ids. `Logic_Tile.tsx`, `Logic_Tiles.tsx` and their PNGs are only kept for it, and can go with it.
- The ASCII converter needs doors exactly 2 tiles long and walls at least 2 thick. Decor is automatic and first-pass (its values will need tuning), it places only keys, and several `X` cells become one bounding rect, so they should form a rectangle.
- There are no rules for room sizes yet. They'll be needed before more floors: hand-made floors and Hard's generated ones should follow the same size rules, so floors feel consistent.
- The old hand-made `Dungeon_Level_One.tmx` has no ladder tile, so its exit is invisible in-game now that the yellow outline is gone. It's only kept as Tiled reference.

**HUD:**
- The health panel has a fixed width, so health text wider than `25/25` (for example `100/100`) won't fit. Its width should be worked out from the text before max health goes above 99.
- The floor panel also has a fixed width, which fits up to `F9`.
- The end screen's split table fits up to 5 floors above the buttons.
- The menus and end screens use font sizes 32 and 64, which aren't on the 24/48 pixel grid the HUD follows; to be fixed in one menu pass.

**Menus and saving:**
- Choosing Main Menu from the pause menu throws the run away with no warning. A confirmation box that tells the player their progress won't be saved is planned. It would go in the Options Main Menu branch, before `start_new_run`.
- There is no saving system yet, so a run can't be saved and resumed later. Once saving exists, the confirmation box can change its wording, or save first.
