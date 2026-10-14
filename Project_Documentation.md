# Dungeon Sprint: Project Documentation

## 1. What this document is

`README.md` covers what the game is, how to install it, and how to play it. This file explains how the code works: how the project is organized, what every module does, how one frame of gameplay runs, what shape the data takes, and how to add new content.

The code itself has no docstrings on purpose. Explanations live here so the source stays short and readable. Comments in the code are kept only where a line would be unclear on its own.

## 2. Design rules

These are the rules the project was refactored around. New code should follow them.

**One job per module.** Every file does one thing. `systems/roll.py` only knows about rolling, `systems/health.py` only knows about health, and so on. If a file starts doing two jobs, split it.

**Services are modules of functions.** Shared behaviour lives in `systems/` as plain functions. A system takes the data it works on as arguments and either changes it in place or returns a new value. For example, `take_damage(health, amount)` changes a health dict, and `steer(...)` returns a new velocity.

**Identity is plain data.** An entity's state is stored as simple dicts on the object, and the systems operate on those dicts:

| Dict | Created by | Used by |
| --- | --- | --- |
| `health` | `systems.health.new_health` | `health`, `combat`, `consumables`, `health_bar` |
| `roll` | inline in `Player.__init__` | `systems.roll` |
| `animation` | `systems.animation.new_animation` | `systems.animation` |
| `inventory` | `systems.inventory.new_inventory` | `inventory`, `interact`, `consumables`, `inventory_ui` |
| `stats` | `systems.stats.compute_stats` | `Player` movement and roll |
| `intent` | `systems.input.read_input` | `Player` and `Level` |

**Rules are separate from application.** Systems decide *what happens* (how fast you accelerate, whether a roll can start, what a chest drops). Entities and states decide *when* to apply them (the player calls `try_start_roll` when the roll intent is set). Content such as enemy stats, loot tables and texture layouts is kept in `*_data.py` files, separate from the logic that reads it.

**Code style.**
- Names are explicit and not abbreviated (`move_direction`, `game_state_manager`, `equipment_slot_x`). Short names are fine only for things like `pos`, `dt`, `x` and `y`.
- File and folder names are snake_case. Classes are PascalCase. Constants are UPPER_SNAKE_CASE.
- No type hints and no docstrings. Comments are fine when they are accurate, and section comments are plain `# Like this`.
- Module-private helpers and caches start with an underscore (`_IMAGE_CACHE`, `_get_icon`).
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

**`tools/line_counter.py`.** Counts lines in every `.py` file (skipping `venv`, `.venv`, `.git` and `__pycache__`) and rewrites the "Project Statistics" section at the end of `README.md`.

**`hooks/pre-commit`.** The repo's git config sets `core.hooksPath = hooks`, so this script runs before every commit. It runs `tools/line_counter.py` and stages `README.md`, so the statistics are always current. It has commented-out lines for running Black and Pylint, which are not active. A fresh clone needs `git config core.hooksPath hooks` to enable it.

## 4. Startup and the main loop

`main.py` defines `Game`. Its constructor runs in this order, and the order matters:

1. `pygame.init()`.
2. `settings.load_settings()` reads `settings.json`. It must run before the window is created, because the window needs the fullscreen setting.
3. `create_window(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen)` opens the window. It must exist before any image is loaded, because `load_image` calls `convert_alpha()`, which needs a display.
4. The system mouse is hidden and a `Cursor` is built from `Assets/Cursors/01.png` at half scale.
5. Sound: all sound effects and music are loaded, the saved volumes are applied, and the title music (`JuiceWrldChasingTheDragon`) starts. It plays once and does not loop.
6. The FPS label (`TextLabel` at the top right) and its timer are created.
7. A `GameStateManager` starting on `"start"` is created, then the three states (`Start`, `Options`, `Level`) are built and registered under the names `"start"`, `"options"` and `"level"`.

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

The window uses `pygame.SCALED`. The game always draws to a 1280x720 surface and pygame scales it to fit the real window or monitor, so all coordinates in the code are in that 1280x720 space.

## 5. State flow

A *state* is any object with `update(dt)` and `draw(screen)`. `GameStateManager` (`states/state_manager.py`) holds:
- `states`: a dict of name to state object.
- `current`: the name of the active state.
- `previous`: the name of the state before it.

`set_state(name)` moves `current` into `previous` and switches to `name`. An unknown name raises `ValueError`, so a typo fails loudly instead of silently. `go_back()` switches to `previous`.

```
            Start ──"Start"──▶ Level
              │                  │
          "Options"          ESC (plays "Pause")
              ▼                  ▼
           Options ◀─────────────┘
              │
   "Main Menu" ──▶ Start      "Back" ──▶ Level  (only shown when previous == "level")
```

- **Start** (`states/menus/start.py`): Start goes to the level, Options goes to the options menu, Exit posts a `pygame.QUIT` event so the main loop shuts down normally.
- **Level** (`states/map/level.py`): the dungeon. ESC switches to options and plays the `Pause` sound.
- **Options** (`states/menus/options.py`): music and SFX sliders, an FPS toggle and a fullscreen toggle. Main Menu returns to start. Back (`can_go_back()`) only appears when the previous state is `"level"`, so it acts as "resume". Both buttons save the settings file.

All three states are built once at startup and kept alive, so leaving and returning to the level resumes it where you left off. There is no reset or new game yet.

## 6. Folder-by-folder reference

### Root

- **`main.py`**: `Game`, the startup and main loop described above.
- **`globals.py`**: shared constants only. Screen size, `FRAME_RATE`, `TILE_SIZE` (16), `PLAYER_SPRITE_SIZE` (64), `UNLOCK_DOOR_DISTANCE`, `SMALL_HEALTH_POTION_VALUE` (70), the color palette (all colors are kept even when unused), and `DUNGEON_LEVEL_ONE` (the map path).

### `entities/`

- **`player/player.py`**: `Player`. Holds `pos`, `velocity`, `last_direction`, `walking`, `intent`, `base_stats`, and the `roll`, `animation`, `health`, `inventory` and `stats` dicts. `update(dt, walls)` runs the player's frame (section 7). Methods: `update_facing`, `update_movement`, `update_roll`, `handle_animation_state`, `draw`.
- **`player/load_player.py`**: `load_player(spawn_pos)` loads the player animations (cropped from 64x64 sheets down to 16x16) and returns a `Player`.
- **`player/player_texture_data.py`**: sprite sheet layout for idle, walk and roll in the up, down and right directions. Left is generated by flipping right.
- **`enemies/enemy.py`**: `Enemy(type_data, pos)`. Copies its stats from the type data, then `update(dt, walls, target_pos)` advances its animation and moves it with the behaviour named in `behavior`. `draw` shows a health bar above it once it has taken damage, and its hitbox when debug is on.
- **`enemies/enemy_type_data.py`**: `ENEMY_TYPES`, one entry per enemy kind (section 8).
- **`enemies/enemy_texture_data.py`**: enemy sprite sheet layouts. `skeleton_texture_data` is an empty placeholder until skeleton art exists.
- **`enemies/load_enemies.py`**: `load_enemies(enemy_spawns)` turns the map's spawn positions into `Enemy` objects. Spawn names with no matching `ENEMY_TYPES` entry are skipped.

### `items/`

- **`items.py`**:
  - `Item`: an item template or stack. It has `id`, `name`, `animations`, `description`, `quantity`, `max_stack`, `animation_speed`, `value_text` and `image` (first idle frame). `clone()` is a shallow copy, so a clone has its own `quantity` but shares the same images.
  - `EquipmentItem(Item)`: adds `slot` and `bonuses`, and always has `max_stack` 1.
  - `WorldItem`: a sprite for an item lying on the ground. It holds a clone of the item data and its own animation.
  - `Chest`: a sprite placed from the map.
- **`item_database.py`**: `initialize_item_database()` builds and returns the dict of item templates, keyed by item id: `gold_key`, `small_health_potion`, `speed_boots`.
- **`item_texture_data.py`**: sprite sheet layouts for each item.
- **`loot_table_data.py`**: `CHEST_LOOT`, what a chest can drop (section 8).

### `states/`

- **`state_manager.py`**: `GameStateManager` (section 5).
- **`map/level.py`**: `Level(game_state_manager, map_path)`. Loads the map, item database, player and enemies. Runs and draws gameplay. Helpers that systems call back into:
  - `unlock_door(door_id)` removes every door tile with that id.
  - `refresh_walls()` rebuilds `solid_tiles` (walls plus remaining doors).
  - `spawn_loot(drops, center)` creates `WorldItem`s scattered randomly around a point.
- **`map/map_loader.py`**: reads the TMX file with pytmx.
  - `load_level_data(map_path)` returns one dict with everything the level needs.
  - `build_map` draws the floor into a single surface and creates the tile and chest sprites.
  - `find_player_spawn` and `find_enemy_spawns` read spawn objects.
- **`map/tiles.py`**: `WallTile`, `DecorTile` and `Door` sprites. Each draws itself offset by the camera. Doors carry a `door_id`.
- **`menus/start.py`** and **`menus/options.py`**: the menus (section 5).

### `systems/`

| Module | Job | Main functions |
| --- | --- | --- |
| `input.py` | Turns keyboard and mouse into an intent dict | `read_input` |
| `movement.py` | Velocity steering and wall collision | `steer`, `move_and_collide` |
| `roll.py` | Roll start, duration and cooldown | `try_start_roll`, `advance_roll` |
| `enemy_ai.py` | Enemy behaviours and line of sight | `fly_velocity`, `wander_chase_velocity`, `trigger_flee`, `has_line_of_sight`, `random_idle_direction` |
| `collision.py` | Finds enemies touching the player | `find_player_contacts` |
| `combat.py` | What happens on contact | `resolve_contact` |
| `health.py` | Health dict rules | `new_health`, `take_damage`, `heal`, `is_dead`, `set_max_health` |
| `stats.py` | Base stats plus equipment bonuses | `compute_stats` |
| `inventory.py` | Inventory dict rules | `new_inventory`, `add_item`, `remove_item`, `has_item`, `count_item`, `can_equip` |
| `interact.py` | The F key: chests, doors, pickups | `interact`, `find_target`, `open_chest`, `unlock_door`, `pick_up_item` |
| `loot.py` | Rolls a loot table | `roll_loot` |
| `consumables.py` | Using items | `use_small_health_potion` |
| `animation.py` | Animation dict rules | `new_animation`, `set_animation`, `advance_animation` |
| `assets.py` | Loading and caching images and animations | `load_image`, `load_animations`, `slice_frames`, `crop_center`, `add_flipped_left` |
| `hitbox.py` | Pixel-perfect masks | `get_mask`, `sprites_overlap`, `draw_hitbox` |
| `camera.py` | The shared camera rect | `camera`, `center_camera`, `is_on_screen` |
| `display.py` | Creating the window | `create_window` |
| `debug.py` | Debug flags | `show_hitboxes`, `toggle_hitboxes` |
| `sound.py` | Loading and playing audio | `load_sfx`, `load_music`, `play_sfx`, `play_music`, `stop_music`, `set_sfx_volume`, `set_music_volume` |
| `settings.py` | Reading and saving `settings.json` | `load_settings`, `save_settings`, `get_setting`, `set_setting` |

Some systems hold module-level state that is shared by everyone who imports them: `camera.camera`, `debug.show_hitboxes`, `settings.SETTINGS`, `sound.SFX` and `sound.MUSIC`, and the caches in `assets` and `hitbox`. Read flags through the module (`debug.show_hitboxes`), not with `from systems.debug import show_hitboxes`. A `from` import copies the value once at import time and never sees later toggles.

### `ui_objects/`

- **`button.py`**: `Button(image, pos)`. Plays `Button_Hover` when the mouse enters and draws a white outline while hovered. On a left click it plays `Button_Click` and sets `clicked_this_frame`, which `is_clicked()` returns. `set_image` swaps the picture (used by the FPS toggle).
- **`slider.py`**: `Slider`, a draggable knob on a track between `min_value` and `max_value`. `get_current_value()` returns the value as an int.
- **`text_label.py`**: `TextLabel`, rendered text at a position. `update_text` re-renders it. Text is drawn without anti-aliasing for a pixel look.
- **`inventory_ui.py`**: `InventoryUI`, the inventory screen (section 7).
- **`health_bar.py`**: `draw_health_bar(screen, health, x, y, width, height)`. Gray background with a fill that is green, or red at 30% health or below.
- **`create_outline.py`**: `make_outline` builds a one-pixel outline surface from an image's mask. `draw_outline` blits it shifted one pixel in each direction to make a thicker outline.
- **`cursor.py`**: `Cursor`, the custom mouse cursor, drawn slightly down and right of the real mouse position.

### `tools/`

- **`line_counter.py`**: see section 3.

## 7. One gameplay frame, step by step

This is `Level.update(dt)` followed by `Level.draw(screen)`.

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
- `pause`: switch to options, play `Pause`, and stop this frame's update.
- `debug`: toggle hitbox drawing.
- `interact`: run `interact.interact(player, level)` (below).
- `inventory`: open the inventory. When closing, any held item goes back into the inventory first. If it doesn't fit, the inventory stays open.
- A mouse click while the inventory is open goes to `InventoryUI.handle_click`.

The game keeps running while the inventory is open. It is an overlay, not a pause.

**3. Player update** (`Player.update`):
1. Sets `walking` and updates `last_direction` from the move direction. Facing doesn't change mid-roll. Vertical input wins over horizontal for facing.
2. Recomputes `stats` from `base_stats` plus equipment bonuses, every frame, so equipping takes effect immediately. If the health stat changed, `set_max_health` updates the maximum and clamps current health.
3. `roll` intent → `try_start_roll`. A roll needs a move direction, can't start during another roll, and can't start during cooldown.
4. `heal` intent → `use_small_health_potion`. Heals 70 and removes one potion, unless health is already full or there is no potion.
5. `update_movement`: `steer` computes the new velocity, then `move_and_collide` moves the rect. Hitting a wall zeros velocity on that axis.
6. `update_roll`: while rolling, the player is also moved by `roll_speed` in the roll direction (on top of normal movement), then `advance_roll` counts down the roll timer and the cooldown.
7. Picks the animation `player_{idle|walk|roll}_{direction}` and advances it.
8. Copies `rect.topleft` into `pos`.

**How `steer` works.** With input, it adds `direction * acceleration * dt`. If the input points sharply against the current velocity (dot product below -0.5), it also brakes by `friction * 0.01 * dt` of the velocity, which makes turning around snappier. With no input, it removes `friction * 1.2 * dt` of speed, stopping exactly at zero rather than overshooting. Finally it caps speed at `max_speed`.

**How `move_and_collide` works.** It moves on X, pushes the rect out of the first wall it overlaps, then does the same on Y. Doing the axes separately lets you slide along walls. Walls whose center is more than 64 pixels away on that axis are skipped for speed. It returns `(hit_x, hit_y)`.

**4. Enemy update.** Each enemy gets the solid tiles and the player's position:
- **`fly`** (Skull): ignores walls. While `flee_timer` is running it moves away from the player, while `return_timer` is running it moves toward the player, within `CHASE_RANGE` (200) it chases, and otherwise it drifts slowly in a random diagonal that occasionally changes.
- **`wander_chase`** (Skeleton): collides with walls. If it has line of sight to the player (no wall rect crosses the line between them), it chases. Otherwise it wanders at half speed.

**5. Contact and combat.** `find_player_contacts` checks enemies within 100 pixels and keeps those whose masks actually overlap the player (pixel-perfect, not rectangle). For each contact, `resolve_contact`:
- deals the enemy's `attack_damage` to the player,
- deals 1 damage to the enemy,
- starts the enemy's flee (2 s) then return (3 s) timers.

Enemies at 0 health are removed. This currently happens every frame the sprites overlap (see section 11).

**6. Ground items and camera.** Ground items advance their animation, and the camera centers on the player.

**What `interact` does (F).** It looks in a box 15 pixels larger than the player and takes the first match in this priority order:
1. **A chest:** rolls `CHEST_LOOT`, spawns the drops around the chest, and removes the chest.
2. **A door, only if you have a `gold_key`:** removes every door tile with the same `door_id`, rebuilds the solid tiles, and uses up one key.
3. **A ground item:** adds it to the inventory. If only part of the stack fits, the rest stays on the ground with the reduced quantity.

**Drawing order** (`Level.draw`). Everything world-space is drawn at `position - camera`, and anything off screen (`is_on_screen`) is skipped:
1. The pre-rendered floor surface.
2. Decor, walls, then doors. Doors within `UNLOCK_DOOR_DISTANCE` (32) of the player get a white outline. This outline doesn't check for a key.
3. Ground items and chests.
4. The player and enemies, sorted by `rect.y` so whoever is lower on screen draws in front.
5. The player's health bar (screen space, top left).
6. The inventory overlay, if open.

**Inventory screen** (`InventoryUI`):
- A 10-column grid of 48-pixel slots (20 slots), plus a column of equipment slots: `head`, `chest`, `boots`, `ability_1`, `ability_2`.
- Clicking a grid slot swaps it with the item in your hand, which picks up, places or swaps.
- Clicking an equipment slot while holding an item equips it only if `item.slot` matches that slot name. Clicking it with an empty hand takes the equipped item off.
- Hovering an item with an empty hand shows a tooltip with name, description and `value_text` (if any). Stack counts show in the slot corner.

## 8. Data formats

**Player `base_stats`** (`player.py`). These are the values before equipment:

| Stat | Value | Used for |
| --- | --- | --- |
| `attack` | 5 | Not used yet |
| `defense` | 0 | Not used yet |
| `max_speed` | 70 | Speed cap in `steer` (pixels/second) |
| `health` | 500 | Max health |
| `roll_speed` | 200 | Extra speed during a roll |
| `acceleration` | 47 | Speed gained per second of input |
| `friction` | 3000 | Braking and stopping strength |

Roll timing is in `systems/roll.py`: `ROLL_DURATION` 0.4 s, `ROLL_COOLDOWN` 1.0 s (the cooldown starts when the roll starts).

**Equipment bonuses.** `compute_stats` copies `base_stats` and adds each equipped item's `bonuses` to stats with the same name. Bonus names that aren't in `base_stats` are ignored. Speed boots give `{"max_speed": 10, "acceleration": 20, "defense": 3, "health": 10}`.

**`ENEMY_TYPES`** (`enemy_type_data.py`). The key must match the map spawn name after `Enemy_`:

```python
"Skull": {
    "max_health": 100,
    "attack_damage": 5,        # damage dealt to the player on contact
    "behavior": "fly",         # "fly" or "wander_chase"
    "speed": 50,
    "texture_data": skull_enemy_texture_data,
    "start_animation": "skull_idle",
},
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

**Animation dict** (`systems/animation.py`). `{"frames", "current", "index", "timer", "speed"}`. `speed` is frames per second: 10 by default, and 4 for item animations. `set_animation` only restarts when the name actually changes and exists.

**Item database** (`item_database.py`). Keys are item ids, values are `Item` or `EquipmentItem` templates. Templates are never put in an inventory directly. Code always works with `clone()`s.

**`CHEST_LOOT`** (`loot_table_data.py`). Each entry is rolled independently, so one chest can drop several things:

```python
{"item_id": "small_health_potion", "chance": 0.9, "min_quantity": 1, "max_quantity": 3}
```

`chance` is 0.0 to 1.0, and the quantity is a random whole number between min and max inclusive.

**Settings file.** `settings.json` in the project root. It is ignored by git, so each machine has its own. It is created when you leave the options menu.

```json
{"fps_enabled": false, "full_screen_enabled": false, "music_volume": 0.5, "sfx_volume": 0.5}
```

Missing keys fall back to the defaults in `systems/settings.py`. A corrupted file prints a warning and uses the defaults.

**Sounds.** Every `.wav` or `.ogg` in `Assets/Sounds` and `Assets/Music` is loaded and named by its filename without the extension. Names currently used: `Button_Hover`, `Button_Click` and `Pause` (SFX), and `JuiceWrldChasingTheDragon` (music). A missing name prints a message instead of crashing.

**The map** (`Assets/Maps/Dungeon_Level_One.tmx`, made in Tiled, 16x16 tiles). The loader looks for these names:

| Layer | Type | What the loader does |
| --- | --- | --- |
| `Floor` | Tile layer | Drawn once into `map_surface` |
| `Walls` | Tile layer | One `WallTile` per tile. These block movement. |
| `Wall_Decor`, `Floor_Decor` | Tile layers | `DecorTile`s, drawn but not solid |
| `Door_Tiles` | Tile layer | One `Door` per tile. These block movement until unlocked. |
| `Logic_Layer` | Tile layer | Not drawn. Its tiles carry a `door_id` property, and each door tile reads the `door_id` at the same x and y. |
| `Chests` | Object layer | One `Chest` per object named `chest` (any capitalization) |
| `Entity_Spawns` | Object layer | `Player` is the player spawn. `Enemy_<Type>` objects (e.g. `Enemy_Skull`) are enemy spawns. |

Door tiles that share a `door_id` (e.g. `door_1`) unlock together as one door.

## 9. How to add things

**A new enemy type.**
1. Add its sheet layout to `entities/enemies/enemy_texture_data.py`.
2. Add an entry to `ENEMY_TYPES` with a key like `"Bat"`, its stats, a `behavior` (`"fly"` or `"wander_chase"`), its texture data and its starting animation name.
3. In Tiled, place objects named `Enemy_Bat` in `Entity_Spawns`.
4. For a new behaviour, write a `<behavior>_velocity` function in `systems/enemy_ai.py` and add a branch for it in `Enemy.update_movement`.

**A new item.**
1. Add its sheet layout to `items/item_texture_data.py`.
2. In `initialize_item_database`, load its animations and add an `Item` (or `EquipmentItem` with `slot` and `bonuses`) under a new id.
3. To make it drop, add an entry to `CHEST_LOOT`.
4. If it does something when used, add a function to `systems/consumables.py` and call it from the player on a new intent.

**New equipment.** Use `EquipmentItem` with `slot` set to one of `head`, `chest`, `boots`, `ability_1` or `ability_2`. Its `bonuses` keys must match names in `base_stats`. For a new slot, add the name to `EQUIPMENT_SLOT_NAMES` in `systems/inventory.py`. The inventory screen draws one equipment box per name.

**A new key binding.** Add a field to the dict returned by `read_input`, then react to it in `Level.update` (level-wide actions) or `Player.update` (player actions).

**A new state or menu.**
1. Create a class with `update(dt)` and `draw(screen)` that takes `game_state_manager`.
2. Build it in `Game.__init__` and register it with `add_state("name", state)`.
3. Switch to it from another state with `set_state("name")`.

**A new level.** Make a TMX map using the layer names in section 8, add its path to `globals.py`, and build a `Level` with that path. There is no level-to-level transition yet.

**A new sound or music track.** Drop a `.wav` or `.ogg` into `Assets/Sounds` or `Assets/Music` and play it by filename: `sound.play_sfx("Name")` or `sound.play_music("Name")`.

## 10. Debug tools

- **P**: toggles `debug.show_hitboxes`. While it's on, mask outlines are drawn for the player (green), enemies (red) and walls (blue). These are the same masks used for contact detection, so what you see is exactly what collides with enemies. Wall collision itself uses rectangles.
- **FPS counter**: turn it on in Options. It shows in the top right and refreshes twice a second. The setting is saved.

## 11. Known gaps and planned work

**Combat:**
- Contact damage is applied every frame the player and an enemy overlap, so at 240 FPS a short touch deals a lot of damage. It should be limited by invulnerability frames (i-frames) after a hit.
- The player can't die. `is_dead` is only checked for enemies, and nothing happens at 0 health.
- Healing has no cooldown.
- Damage based on dash or roll speed is planned.
- A per-enemy speed drain on contact (set in `ENEMY_TYPES`) is planned.
- `attack` and `defense` stats exist but aren't used yet.

**Movement:** tuning is planned. It may include a drift feel and a "grip" stat.

**Audio:** only the title track plays, once. Per-screen music (each state starting its own track on `enter()`) is planned.

**Content and map:**
- Skeletons reuse the skull sprite until `skeleton_texture_data` is filled in.
- The map has a `Keys` tile layer and an `Items` object layer (with placed `gold_key` and `small_health_potion` objects) that the loader doesn't read yet. Items currently only come from chests.
- Returning to the main menu doesn't reset the level. Pressing Start resumes the same run.
- There is only one level, with no win condition or exit.
