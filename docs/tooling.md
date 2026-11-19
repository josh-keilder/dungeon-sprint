# Tooling

## Running and tooling

**Setup (Windows, from the project folder):**

```bash
python -m venv .venv
```

```bash
.venv/Scripts/python -m pip install -r requirements.txt
```

The project uses **one** virtual environment, `.venv` (the one VS Code picks up; Python 3.14). Every command in this document and the README runs through `.venv/Scripts/python`. `requirements.txt` pins the direct dependencies: `pygame-ce==2.5.8`, `PyTMX==3.32`, `moderngl==5.13.0` and its `glcontext==3.1.0` (the OpenGL renderer, [Architecture](architecture.md)), plus the formatters `black==26.10.1` and `isort==9.0.2`. Note that this is pygame-ce (community edition), not plain pygame. Features like `get_just_pressed` and `FRect` only exist in pygame-ce. To update later: `.venv/Scripts/python -m pip list --outdated`, upgrade what's listed, then update the pins and check that `black --check` and `isort --check-only` still pass (a new formatter version can change its style). Save `requirements.txt` as UTF-8: `pip freeze > requirements.txt` in Windows PowerShell 5.1 writes UTF-16, which pip reads badly.

**Run the game:**

```bash
.venv/Scripts/python main.py
```

Always run from the project root. Asset paths such as `Assets/Maps/Dungeon_Level_One.tmx` and the settings file `settings.json` are relative to the current folder.

**Formatting with Black** (installed by `requirements.txt`):

```bash
.venv/Scripts/python -m black .
```

Use `--check` to see whether anything needs formatting without changing files.

A trailing comma after the last item of a bracketed list tells Black to keep it exploded, one item per line (its *magic trailing comma*). So `for (dx, dy,) in ...` gets split over four lines; leave the comma out to keep a short list on one line.

**Sorting imports with isort.** `pyproject.toml` sets isort's `profile = "black"`, so the two tools agree. Imports are in groups separated by a blank line: the standard library, then third-party packages (`pygame`, `pytmx`), then the project's own modules. Within a group, plain `import x` lines come first, then the `from x import y` lines, each alphabetical:

```python
import os
import sys
from collections import deque

import pygame

from game.data.constants import TILE_SIZE
```

```bash
.venv/Scripts/python -m isort .
```

As with Black, `--check` only reports.

**`tools/line_counter.py`.** Counts lines in every `.py` file (skipping the `IGNORED_FOLDERS`: `venv`, `.venv`, `.git`, `__pycache__` and `.claude`, where Claude Code keeps worktree copies of the project) and rewrites the "Project Statistics" section at the end of `README.md`.

**Running tools.** Tools that import project code such as `game.data.constants` are run as modules from the project root, with `-m` and a dotted name instead of a file path. `python tools/x.py` puts only the `tools/` folder on Python's import path, so `from game.data.constants import ...` fails with `ModuleNotFoundError`; `python -m tools.x` puts the current folder (the project root) on the path instead.

**`tools/make_sprite.py`.** Generates the game's own pixel art from text. Run it from the project root after editing any sprite; it regenerates every sprite, and an unchanged sprite comes out byte-identical:

```bash
.venv/Scripts/python -m tools.make_sprite
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

`make_sprite(name, sprite)` draws one entry and `__main__` loops over them all. Letters only mean something inside their own sprite, so every sprite can use `o` for its outline, while `m` is the stone ring in the frame but mid leather in the boots. Colors come from the `PALETTE_*` constants in `game/data/palette.py`, so the art can only use the game's colors, and `.` is left transparent. The image size comes from the rows themselves (width from the first row, height from the row count), so editing the rows is all that's needed. The surface is created with `pygame.SRCALPHA`, which starts fully transparent, so skipped `.` pixels stay see-through; without it a new surface starts opaque black. Sprites are saved at 1× and scaled up by the game.

Typos in text art would otherwise fail silently (a short row leaves transparent pixels, an unknown letter would be skipped), so the tool stops with a `ValueError` naming the sprite and the spot instead: `speed_boots: row 4 is 15 wide, expected 16`, or `speed_boots: unknown letter 'z' at (3, 7)`.

The sprites:
- **`panel_frame`** (12×12, `Assets/UI/panel_frame.png`): the 9-slice frame used by the HUD and the inventory ([Game reference](game.md)). `o` outline `PALETTE_SOOT`, `m` stone ring `PALETTE_WALL`, `l` light edge `PALETTE_LEATHER`, `s` shadow edge `PALETTE_SHADOW`, `f` fill `PALETTE_VOID`.
- **`speed_boots`** (16×16, `Assets/Items/speed_boots.png`): one boot in side view with a wing on the heel, filling the full width. `o` outline `PALETTE_VOID` (like the health potion), leather in three shades (`d` `PALETTE_CLAY`, `m` `PALETTE_LEATHER`, `l` `PALETTE_TAN`, lit from the top-left), `s` sole and buckle `PALETTE_STEEL`, and the wing in `w` `PALETTE_ICE` with `a` `PALETTE_AZURE` shading.
- **`padlock_silver`** and **`padlock_gold`** (7×10, `Assets/Objects/padlock_silver.png` and `padlock_gold.png`): the locks drawn on locked doors, so players can match a door to its key. Both entries use the same `PADLOCK_ROWS` constant, so the shape is defined once and only the colors differ: `o` outline and `k` keyhole in `PALETTE_VOID`, then light (`l`, top and left), mid (`m`) and dark (`d`, right side), in `PALETTE_ICE` / `PALETTE_STEEL` / `PALETTE_STONE` for silver and `PALETTE_CANDLE` / `PALETTE_GOLD` / `PALETTE_BRASS` for gold, lit from the top-left like the boots.

**`tools/preview_map.py`.** Renders a `.tmx` map to one PNG, the way the game sees it, with markers on top, so a floor can be checked without playing it. With no arguments it previews every map in `FLOOR_ORDER`; pass map paths to preview only those:

```bash
.venv/Scripts/python -m tools.preview_map
.venv/Scripts/python -m tools.preview_map Assets/Maps/Dungeon_Level_One.tmx
```

Images are saved to `map_previews/<map name>.png`, a folder listed in `.gitignore` because the images are generated.

- **It reuses the game's loader.** `preview_map(map_path, font)` calls `load_floor_data` from `game/world/map_loader.py`, the same function `Run` uses, so the preview always matches the game, and if map loading changes the preview follows; the tool only draws what it's given. The loader calls `.convert()` and `load_image`, which need a display, so `main()` first opens a hidden 1×1 window with `pygame.display.set_mode((1, 1), pygame.HIDDEN)`.
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
.venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/test_room.txt
.venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/test_room.txt Assets/Maps/other_name.tmx
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
- **Solvability check** (`can_finish`, run at the end of `validate_grid`). It answers: can a player starting at `@` reach the exit, picking up keys and opening doors along the way? It follows the game's rules: a door group opens with **its own color** of key (any silver key opens any silver door), and each group uses up one key. Keys are guaranteed by design (see the loot notes in [Data formats](data-formats.md)), and this is what checks it. Hard's generated floors will rely on the same check to reject unwinnable layouts.
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
.venv/Scripts/python -m tools.make_strip
```

It's built like `make_sprite`: `STRIPS` maps a name to `{"frames": [frame paths, in order], "path": output path}`, and `make_strip(name, strip)` handles any entry. The frame lists are list comprehensions over `range(1, 5)`, matching the pack's numbering. Every frame must be the same size, since `slice_frames` cuts equal cells, so it checks each frame against the first, using `zip(paths, frames)` to walk the two lists side by side and name the bad file in the `ValueError`. It then blits frame `index` at `index × frame width` on a transparent (`SRCALPHA`) surface and saves it. `PACK_FOLDER` and the per-folder constants (`KEYS_FOLDER`) keep the long pack paths in one place.

The strips so far:
- **`gold_key`** → `Assets/Items/gold_key_strip.png` (the pack's `keys_1`, 4 frames, a spinning gold key).
- **`silver_key`** → `Assets/Items/silver_key_strip.png` (the pack's `keys_2`, 4 frames, a spinning silver key).
- **`crate`** → `Assets/Objects/crate_strip.png` (the pack's `box_2`, a plain wooden box, 4 frames of squash and stretch: normal, tall, wide, flattened). The steel-banded `box_1` was skipped because it looks like the chest.
- **`torch`**, **`side_torch`**, **`candlestick_1`**, **`candlestick_2`** → `Assets/Objects/<name>_strip.png` (the pack's `torch` folder, 4 frames each): the animated versions of the tileset's still light tiles 91, 92, 94 and 96, swapped in by the map loader ([Game reference](game.md), `map_loader.py`). The torch frames line up exactly with the still tiles; the candlestick frames sit 1 pixel further left, too small to notice.

**`tools/check_engine_imports.py`.** Parses every `.py` file under `engine/` with Python's own parser (`ast`) and lists any import of the game's top-level modules (`GAME_MODULES`: `game`, `main`, `tools`), inside functions too, in both spellings (`import game.x` and `from game.x import y`). Relative imports (`node.level > 0`) are skipped, since they can only reach other engine files. It exits with an error when it finds one, which is what makes the hook block the commit:

```bash
.venv/Scripts/python tools/check_engine_imports.py
```

```
engine\core\timer.py:33: imports game.data.constants
The engine imports the game; pass the game's data in instead.
```

**`hooks/pre-commit`.** The repo's git config sets `core.hooksPath = hooks`, so this script runs before every commit (a fresh clone needs `git config core.hooksPath hooks` to enable it). It uses the project's `.venv` Python (`.venv/Scripts/python` on Windows, `.venv/bin/python` elsewhere, the system `python` as a last resort), because black and isort are only installed there. In order:

```
1. format     every staged .py file: isort, then black, then git add it again
              (re-adding stages the whole file, so a file staged only in part is committed in full)
2. check      tools/check_engine_imports.py: stop the commit if engine/ imports the game
3. count      tools/line_counter.py rewrites README.md's statistics, then git add README.md
```

Any step that fails stops the commit with `❌ Error: <what failed>. Fix before committing.` A commented-out Pylint step is kept for later.

## Debug tools

- **P**: toggles `debug.show_hitboxes`. While it's on, mask outlines are drawn for the player (green), enemies (red, around the art) and the walls next to open space (blue, drawn by `Floor.draw`, since the walls themselves are part of `map_surface`). These are the same masks used for contact detection, so what you see is exactly what collides with enemies. Each enemy's **body** box is drawn in yellow (what moves, collides and blocks), and during the strike frames of a swing its **strike box** is drawn in red. Wall collision itself uses rectangles. The player's outline is still drawn while the sprite blinks during invulnerability.
- **FPS counter**: turn it on in Options. It shows in the top right and refreshes twice a second. The setting is saved.
