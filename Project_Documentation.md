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
| `roll` | inline in `Player.__init__` (holds `direction` and two timers from `new_timer`) | `systems.roll`, `combat`, `Player` |
| `invulnerability` | `systems.timer.new_timer` (Player and Enemy) | `timer`, `combat`, `Player.draw` |
| `heal_cooldown` | `systems.timer.new_timer` (Player) | `timer`, `consumables` |
| `death_timer` | `systems.timer.new_timer` (Level) | `timer`, `Level.update` |
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

**Running tools.** Tools that import project code such as `globals` are run as modules from the project root, with `-m` and a dotted name instead of a file path. `python tools/x.py` puts only the `tools/` folder on Python's import path, so `from globals import ...` fails with `ModuleNotFoundError`; `python -m tools.x` puts the current folder (the project root) on the path instead.

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

`make_sprite(name, sprite)` draws one entry and `__main__` loops over them all. Letters only mean something inside their own sprite, so every sprite can use `o` for its outline, while `m` is the stone ring in the frame but mid leather in the boots. Colors come from the `PALETTE_*` constants in `globals.py`, so the art can only use the game's colors, and `.` is left transparent. The image size comes from the rows themselves (width from the first row, height from the row count), so editing the rows is all that's needed. The surface is created with `pygame.SRCALPHA`, which starts fully transparent, so skipped `.` pixels stay see-through; without it a new surface starts opaque black. Sprites are saved at 1× and scaled up by the game.

Typos in text art would otherwise fail silently (a short row leaves transparent pixels, an unknown letter would be skipped), so the tool stops with a `ValueError` naming the sprite and the spot instead: `speed_boots: row 4 is 15 wide, expected 16`, or `speed_boots: unknown letter 'z' at (3, 7)`.

The sprites:
- **`panel_frame`** (12×12, `Assets/UI/panel_frame.png`): the 9-slice frame used by the HUD and the inventory (section 6). `o` outline `PALETTE_SOOT`, `m` stone ring `PALETTE_WALL`, `l` light edge `PALETTE_LEATHER`, `s` shadow edge `PALETTE_SHADOW`, `f` fill `PALETTE_VOID`.
- **`speed_boots`** (16×16, `Assets/Items/speed_boots.png`): one boot in side view with a wing on the heel, filling the full width. `o` outline `PALETTE_VOID` (like the health potion), leather in three shades (`d` `PALETTE_CLAY`, `m` `PALETTE_LEATHER`, `l` `PALETTE_TAN`, lit from the top-left), `s` sole and buckle `PALETTE_STEEL`, and the wing in `w` `PALETTE_ICE` with `a` `PALETTE_AZURE` shading.
**`hooks/pre-commit`.** The repo's git config sets `core.hooksPath = hooks`, so this script runs before every commit. It runs `tools/line_counter.py` and stages `README.md`, so the statistics are always current. It has commented-out lines for running Black and Pylint, which are not active. A fresh clone needs `git config core.hooksPath hooks` to enable it.

## 4. Startup and the main loop

`main.py` defines `Game`. Its constructor runs in this order, and the order matters:

1. `pygame.init()`.
2. `settings.load_settings()` reads `settings.json`. It must run before the window is created, because the window needs the fullscreen setting.
3. `create_window(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen)` opens the window. It must exist before any image is loaded, because `load_image` calls `convert_alpha()`, which needs a display.
4. The system mouse is hidden and a `Cursor` is built from `Assets/Cursors/01.png` at half scale.
5. Sound: all sound effects and music are loaded and the saved volumes are applied. No music starts here.
6. The FPS label and its timer are created. It's an outlined `TextLabel` in the default Silkscreen at 24, with no panel, because it's a debug readout rather than part of the game. Each time its text refreshes, it's positioned by its visible ink: right-aligned `FPS_MARGIN` (12) from the screen's right edge, so a wider number grows to the left, and vertically centered on `FPS_CENTER_Y` (21), snapped to the grid:

   ```
   x = SCREEN_WIDTH − FPS_MARGIN − ink right
   y = (FPS_CENTER_Y − ink center y) // GAME_SCALE × GAME_SCALE
   ```
7. A `GameStateManager` starting on `"main_menu"` is created, then the states are built and registered: `MainMenu` as `"main_menu"`, `Options` as `"options"`, `Level` as `"level"`, and `RunEndScreen` twice, as `"game_over"` ("You Died!", red, `GAME_OVER_MUSIC`) and `"level_complete"` ("You Escaped!", green, no music of its own).
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

Inside that, the level is drawn in two layers. The world is drawn at its true pixel size on a small canvas and scaled up by `GAME_SCALE` (3), so every art pixel becomes a crisp 3×3 block. The HUD is drawn afterwards at full resolution, so text stays sharp and the inventory's mouse positions stay in screen pixels:

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
         MainMenu ──"Start"──▶ Level ──player at 0 HP──▶ RunEndScreen "game_over"
              │                  │  └──exit of the last floor──▶ RunEndScreen "level_complete"
          "Options"          ESC (plays "pause")              │ (both)
              ▼                  ▼                  "Restart" ──▶ new Level
           Options ◀─────────────┘                  "Main Menu" ──▶ new Level, then MainMenu
              │
   "Main Menu" ──▶ MainMenu   "Back" ──▶ Level  (only shown when previous == "level")
```

- **MainMenu** (`states/menus/main_menu.py`): Start goes to the level, Options goes to the options menu, Exit posts a `pygame.QUIT` event so the main loop shuts down normally. `enter()` plays `MAIN_MENU_MUSIC` (`"menu_music"`).
- **Level** (`states/map/level.py`): the dungeon. ESC switches to options and plays the `pause` sound. When the player's health reaches 0 it plays `death`, stops the music, freezes for `DEATH_DELAY` (3.0) seconds, then switches to `"game_over"` (section 7, step 6). Touching the exit loads the next floor from `LEVEL_ORDER`, or switches to `"level_complete"` after the last one (step 7). `enter()` plays `LEVEL_MUSIC` (`"level_music"`). Unpausing calls it again, but the track keeps going instead of restarting (see `sound.py` in section 6).
- **Options** (`states/menus/options.py`): music and SFX sliders, an FPS toggle and a fullscreen toggle. Main Menu returns to the main menu. When the menu was opened from the level, it first calls `start_new_run()` so the abandoned run is thrown away. Back (`can_go_back()`) only appears when the previous state is `"level"`, so it acts as "resume". ESC does the same as Back, but only when the menu was opened from the level. In that case the menu is drawn over the dimmed, frozen level instead of a solid background. Both buttons save the settings file. `enter()` does nothing, so the pause menu keeps playing whatever music was already on.
- **RunEndScreen** (`states/menus/run_end.py`): the screen shown when a run ends, either way. It is one class created twice in `main.py` with different settings, `RunEndScreen(game_state_manager, title, title_color, music)`: the differences between the two screens are constructor arguments, not separate classes. It draws the title, the run's split times (one row per floor, then the total) and two text buttons over the frozen level. Restart and Main Menu both call `start_new_run()` (from `states/new_run.py`) first, then switch to `"level"` or `"main_menu"`. `enter()` reads the finished run's `splits`, `run_time` and `dying` from `game_state_manager.states["level"]` and renders the split table. If `music` is a track name, `enter()` stops the current music and plays it once, with `loops=0`. That's how the death screen plays `"game_over"`, and why Restart then starts the level music again from the beginning. If `music` is `None`, as on the finish screen, the current track keeps playing.

All states are built once at startup and kept alive, so leaving and returning to the level normally resumes it where you left off. The exceptions are a death, and quitting to the main menu from the pause menu. `start_new_run(game_state_manager)` in `states/new_run.py` builds a brand new `Level(game_state_manager)`, which starts on the first floor, and registers it under `"level"` with `add_state`, which replaces the old one in the `states` dict. A rebuild resets everything the Level owns (player, enemies, chests, doors, ground items, the inventory screen) and recenters the camera, while the shared image, animation and mask caches are reused. Because the Level can be replaced, code that needs it should look it up through `game_state_manager.states["level"]` when it needs it, not keep a reference from startup. `Game.level` in `main.py` still points at the first Level and is not used after registration.

## 6. Folder-by-folder reference

### Root

- **`main.py`**: `Game`, the startup and main loop described above.
- **`globals.py`**: shared constants only. `GAME_SCALE` (3) is how many screen pixels each world pixel becomes, and `WORLD_WIDTH` / `WORLD_HEIGHT` are the world canvas size, worked out from it so changing the one number switches the whole scale:

  ```
  WORLD_WIDTH  = ceil(SCREEN_WIDTH  ÷ GAME_SCALE)     3× → 427   (427 × 3 = 1281, 1 px falls off the edge)
  WORLD_HEIGHT = ceil(SCREEN_HEIGHT ÷ GAME_SCALE)     3× → 240
  ```

  `math.ceil` rounds up, so the scaled world always covers the whole screen. 2 gives 640×360 and 4 gives 320×180. Keep the scale a whole number: a screen pixel can't be split, so at 2.5× some art pixels come out 2 screen pixels wide and others 3, which looks lopsided and shimmers as the camera scrolls (smoothing instead makes it blurry).
  The rest of `globals.py`: Screen size, `FRAME_RATE`, `TILE_SIZE` (16), `PLAYER_SPRITE_SIZE` (64), `UNLOCK_DOOR_DISTANCE`, `SMALL_HEALTH_POTION_VALUE` (70), the color palette (all colors are kept even when unused), the tileset palette (all 34 colors in `Assets/Dungeon_Tileset.png` as `PALETTE_*` constants, grouped by family and ordered dark to light within each: darks and floors such as `PALETTE_VOID` (37, 19, 26) and `PALETTE_SHADOW` (84, 55, 64); walls, earth and wood such as `PALETTE_WALL` (110, 74, 72); reds `PALETTE_BLOOD` (188, 76, 81) and `PALETTE_ROSE`; fire and gold such as `PALETTE_TORCH` (191, 112, 77); moss and parchment; and stone, steel and ice such as `PALETTE_STONE` (144, 145, 158), `PALETTE_STEEL` (173, 193, 207) and `PALETTE_ICE` (202, 230, 245). UI and generated art use these names so everything stays on the tileset's colors. The UI color rules: steel is the normal text color, stone is secondary text such as item descriptions, and torch orange means "you can interact with this": hovered buttons and sliders, and the `Q` hotkey), `OPTION_MENU_BUTTON_BACKGROUND` (defined as `PALETTE_WALL`, unused but kept), `MENU_BACKGROUND_COLOR` (defined as `PALETTE_VOID`, the fill color of the Main Menu and Options screens; one name says which color, the other what it's for), `LEVEL_ORDER` (the map paths in play order; the run goes through them one after another, and the last one's exit ends the run. For now it lists `Dungeon_Level_One.tmx` twice, to test the floor transition until level two exists), `FONT_PATH` (the menu font, `Assets/Fonts/Silkscreen-Regular.ttf`), `PANEL_FRAME_PATH` (`Assets/UI/panel_frame.png`, the frame art shared by the HUD and the inventory), `BUTTON_FONT_SIZE` (32, the button font size shared by every menu), and `OVERLAY_ALPHA` (160 of 255, how dark the overlay is when the game-over and paused options screens are drawn over the level).
- **`Assets/Fonts/`**: `Silkscreen-Regular.ttf`, a pixel font under the SIL Open Font License. Load it with `pygame.font.Font(FONT_PATH, size)`. Because it is a pixel font, render it without anti-aliasing (`False`) and use sizes that are multiples of 8, or the letters blur.

### `entities/`

- **`player/player.py`**: `Player`. Holds `pos`, `velocity`, `speed` (the actual speed last frame in pixels per second, measured as distance moved divided by `dt`), `last_direction`, `walking`, `intent`, `base_stats`, and the `roll`, `invulnerability`, `heal_cooldown`, `animation`, `health`, `inventory` and `stats` dicts. `update(dt, walls)` runs the player's frame (section 7). Methods: `update_facing`, `update_movement`, `update_roll`, `handle_animation_state`, `draw`. While invulnerable, `draw` skips the sprite while `is_blink_hidden(self.invulnerability, BLINK_INTERVAL)` is true, so the player blinks. `BLINK_INTERVAL` (0.1 s) is the player's own value, at the top of `player.py`. The debug hitbox is still drawn. `alpha` (starts at 255, fully visible) is how opaque the sprite is drawn, and Level lowers it during death. When `alpha` is below 255, `draw` blits a faded **copy** of the frame instead of changing `self.image`. The animation frames are shared from the cache in `systems/assets.py`, so fading the frame itself would leave it faded for the next `Player` too, and a restarted player would be invisible.
- **`player/load_player.py`**: `load_player(spawn_pos)` loads the player animations (cropped from 64x64 sheets down to 16x16) and returns a `Player`.
- **`player/player_texture_data.py`**: sprite sheet layout for idle, walk and roll in the up, down and right directions. Left is generated by flipping right.
- **`enemies/enemy.py`**: `Enemy(type_data, pos)`. Copies its stats from the type data with `type_data["..."]`: `attack_damage`, `speed`, `knockback_multiplier`, `knockback_decay_rate`, `blink_interval` and `invulnerability_duration` (section 8). `knockback_velocity` (starts at zero) is the current shove in pixels per second. `update(dt, walls, target_pos)` advances its animation, moves it with the behaviour named in `behavior`, applies the shove with `update_knockback`, and counts down its `invulnerability` timer with `advance_timer`. `draw` hides the sprite while `is_blink_hidden(self.invulnerability, self.blink_interval)` is true, so an enemy blinks after a roll hit. Its health bar (shown once it has taken damage) and its hitbox (when debug is on) are always drawn, so its health stays readable while it blinks. The bar is `ENEMY_HEALTH_BAR_WIDTH` (16) × `ENEMY_HEALTH_BAR_HEIGHT` (2) art pixels plus the 1-pixel border, so 4 art pixels tall in total, and sits `ENEMY_HEALTH_BAR_GAP` (8) above the sprite.
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
- **`new_run.py`**: `start_new_run(game_state_manager)` builds a fresh `Level`, starting on the first floor of `LEVEL_ORDER`, and registers it as `"level"`, replacing the old run. It's a plain function in its own module so any menu can start a new run without depending on another menu. Used by `RunEndScreen` (Restart and Main Menu) and `Options` (Main Menu from a paused run).
- **`map/level.py`**: `Level(game_state_manager)`, one whole run: every floor in `LEVEL_ORDER`, one after another. Runs and draws gameplay. Its setup is split by how long things live:
  - **`__init__`** sets up what lasts the whole run: `run_time`, the item database, the player, the HUD, the inventory screen and the death timer. It creates the player at `(0, 0)`, sets `level_index` to 0 (which entry of `LEVEL_ORDER` is being played), then calls `load_floor` for the first floor, which places the player.
  - **`load_floor(map_path)`** swaps in a floor: fresh `ground_items` (items left on the floor don't carry over), the map data from `load_level_data` (map surface, decor, walls, doors, chests, exit), the enemies, and `solid_tiles` through `refresh_walls()`. Then it moves the **same** player object to the floor's spawn: it sets `rect.center`, syncs `pos` to the rect (enemy contact checks read `player.pos` before the player updates), zeroes `velocity` so the player doesn't slide in at full speed, and centers the camera. Because the player object is kept, health, inventory, gear and cooldowns carry over with no extra code, and because `run_time` lives on the `Level`, the timer keeps counting across floors.

  ```
  Level.__init__ (once per run)          load_floor (once per floor)
  ─────────────────────────────          ───────────────────────────
  run_time, item_database                ground_items
  player  ──────── same object ────────▶ placed at this floor's spawn
  hud, inventory_ui, death_timer         map surface, tiles, doors, chests, exit
  level_index = 0 ──▶ load_floor(...)    enemies, solid_tiles, camera
  ```

  `world_surface` (`WORLD_WIDTH` × `WORLD_HEIGHT`) is the canvas the world is drawn on before it's scaled to the screen. Helpers that systems call back into:
  - `unlock_door(door_id)` removes every door tile with that id.
  - `refresh_walls()` rebuilds `solid_tiles` (walls plus remaining doors).
  - `spawn_loot(drops, center)` creates `WorldItem`s scattered randomly around a point.
  - `run_time` (starts at 0.0) holds the seconds spent in this run, across all floors, and is drawn by the HUD's timer panel.
  - `splits` (starts empty, run-wide like `run_time`) holds the `run_time` at the moment each exit was touched, one entry per finished floor, the last floor included. That's the speedrun meaning of a split: the clock reading at each checkpoint. Only these raw readings are stored; each floor's own time is worked out from them on the end screen (`floor_times`). Because the floor transition pauses the run timer, no transition time ends up in any floor's time.
  - `exit_rect` is the current floor's exit area, or `None` if the map has none.
  - **The floor transition.** Moving to the next floor fades the screen to black, shows a "Floor 2" card, and fades back in. It runs inside `Level` rather than as its own game state, because it's part of playing a run and needs the world drawn underneath. `transition_phase` is `None` while playing, or the name of the current phase, and one `transition_timer` is restarted for each phase:

    ```
    exit touched ─▶ "fade_out" ─▶ "card" ─▶ "fade_in" ─▶ None (playing)
                     0.4 s        1.0 s      0.4 s
                     overlay      load_floor overlay
                     0 → 255      at start   255 → 0
    ```

    - `update_transition(dt)` advances the timer and, when it runs out, does what happens at the **end** of the current phase: the end of `"fade_out"` raises `level_index`, calls `load_floor` and `show_floor_card`, and starts the card; the end of `"card"` starts `"fade_in"`; the end of `"fade_in"` sets the phase back to `None`. The new floor loads while the screen is fully black, so the swap is never seen. `FADE_DURATION` (0.4) and `FLOOR_CARD_DURATION` (1.0) set the lengths.
    - Loading a floor takes real time, so the frame after `load_floor` gets a large `dt`. The transition advances its timer by `min(dt, MAX_TRANSITION_DT)` (1/30 s), so a slow load can't skip the card; however long the load took, it counts as one short frame.
    - `show_floor_card()` sets `floor_label` (a `TextLabel` at Silkscreen 48) to `Floor {level_index + 1}` (players count from 1, the list from 0) and centers it on the screen by its visible ink, snapped to the 3 px grid, the same way as the FPS label.
    - `transition_alpha()` says how dark the overlay is: `fade_left` goes from 1.0 to 0.0 as a fade runs, and the card is fully black.

      ```
      fade_left = time_left(transition_timer) ÷ FADE_DURATION     (1.0 → 0.0)
      fade_out:  alpha = round(255 × (1 − fade_left))             (0 → 255, darkening)
      fade_in:   alpha = round(255 × fade_left)                   (255 → 0, clearing)
      card:      alpha = 255
      ```

    - `fade_overlay` is a screen-sized surface filled with `PALETTE_VOID`. It's drawn last, over the HUD too, so the whole screen fades together, with the card text on top during `"card"`.
  - `dying` (starts `False`) is the flag that says the death sequence has started, and `death_timer` (made with `new_timer()`) holds the seconds left before the game-over screen. `DEATH_DELAY` (3.0 s) is the whole freeze, and `DEATH_FADE_DURATION` (1.5 s) is how long the player's body takes to fade out. The fade must be no longer than the delay.
- **`map/map_loader.py`**: reads the TMX file with pytmx.
  - `load_level_data(map_path)` returns one dict with everything the level needs.
  - `build_map` draws the floor into a single surface and creates the tile and chest sprites.
  - `find_player_spawn` and `find_enemy_spawns` read spawn objects.
  - `find_exit` returns a `pygame.Rect` for the object named `Exit`, or `None` if there isn't one.
- **`map/tiles.py`**: `WallTile`, `DecorTile` and `Door` sprites. Each draws itself offset by the camera. Doors carry a `door_id`.
- **`menus/main_menu.py`**: `MainMenu(game_state_manager)`, the title screen (section 5).
  - `draw` fills the screen with `MENU_BACKGROUND_COLOR`, then draws the "DUNGEON SPRINT" title (`TITLE_FONT_SIZE` 96, at `TITLE_Y` 50, centered with `(SCREEN_WIDTH - width) // 2`) and the buttons.
  - Start, Options and Exit are `TextButton`s with a gray outline, centered and stacked at `START_BUTTON_Y` (300), `OPTIONS_BUTTON_Y` (380) and `EXIT_BUTTON_Y` (460).
- **`menus/options.py`**: `Options(game_state_manager)`, the options menu (section 5).
  - It uses the same size of text title ("OPTIONS") as the Main Menu screen. All buttons are `TextButton`s with a gray outline.
  - The background depends on where the menu was opened from. When `can_go_back()` is true (opened from the level with ESC), `draw` first draws the paused Level, looked up from `game_state_manager.states["level"]`, then a full-screen black overlay at `OVERLAY_ALPHA` (160 of 255), the same way as the game-over screen. Otherwise it fills the screen with `MENU_BACKGROUND_COLOR`.
  - The FPS and Fullscreen toggles are centered at `FPS_BUTTON_Y` (220) and `FULL_SCREEN_BUTTON_Y` (300). Their text comes from `FPS_LABEL` and `FULL_SCREEN_LABEL` (`"FPS: {}"`, `"Fullscreen: {}"`) filled in by `_on_off(enabled)`, which returns `"On"` or `"Off"`. When clicked, the setting flips and `set_text` shows the new state.
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
    - `enter()` reads `splits`, `run_time` and `dying` from the level and calls `render_splits(splits, run_time, died)`. `dying` is `True` on the death screen and `False` on the win screen, which is how one class knows to show the floor the player died on in `PALETTE_BLOOD`; all other rows are `PALETTE_STEEL`.
    - `render_splits` builds `split_rows`, a list of `(image, pos)` pairs, once per screen visit, plus the `divider_rect`; `draw` only loops over them. `add_split_row(label, seconds, row_y, color)` renders one row's label and time, because the floor rows and the Total row are drawn the same way. The time's x is `SPLIT_TIME_RIGHT − its width`, which right-aligns it so the times line up. `__init__` starts with an empty list and an empty rect, so `draw` works even before the first `enter`.
    - It fits up to 5 floors between the title and the buttons.
  - `draw` first draws the current Level, looked up from `game_state_manager.states["level"]`, then a full-screen black overlay at `OVERLAY_ALPHA` (160 of 255), then the title, the split rows and divider, and the buttons. The level has to be redrawn every frame, because a translucent overlay drawn on its own would stack up to solid black.
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
| `combat.py` | What happens on contact. `resolve_contact` returns whether the enemy was hit. | `resolve_contact` |
| `timer.py` | Countdown timers: a `{"timer"}` dict counted down by `dt` | `new_timer`, `start_timer`, `advance_timer`, `is_running`, `time_left` |
| `health.py` | Health dict rules | `new_health`, `take_damage`, `heal`, `is_dead`, `set_max_health` |
| `stats.py` | Base stats plus equipment bonuses | `compute_stats` |
| `inventory.py` | Inventory dict rules | `new_inventory`, `add_item`, `remove_item`, `has_item`, `count_item`, `can_equip` |
| `interact.py` | The F key: chests, doors, pickups | `interact`, `find_target`, `open_chest`, `unlock_door`, `pick_up_item` |
| `loot.py` | Rolls a loot table | `roll_loot` |
| `consumables.py` | Using items and the heal cooldown | `use_small_health_potion` |
| `animation.py` | Animation dict rules | `new_animation`, `set_animation`, `advance_animation` |
| `assets.py` | Loading and caching images and animations | `load_image`, `load_animations`, `slice_frames`, `crop_center`, `add_flipped_left` |
| `hitbox.py` | Pixel-perfect masks | `get_mask`, `sprites_overlap`, `draw_hitbox` |
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
- **`slider.py`**: `Slider`, a draggable knob on a track between `min_value` and `max_value`. `pos` is the **center** of the track, not its top-left, so the track's left edge is `pos[0] - size[0] // 2`. The part left of the knob is drawn in `track_color` and the rest in `PALETTE_SHADOW`. The knob is drawn in `knob_color`, or `PALETTE_TORCH` while hovered or dragged, the same hover color as the buttons. The options menu uses a `PALETTE_STEEL` fill and a `PALETTE_ICE` knob, so the knob stands out from the fill next to it. The track and knob have rounded corners. `get_current_value()` returns the value as an int.
- **`text_label.py`**: `TextLabel`, rendered text at a position (its top-left). `update_text` re-renders it, but does nothing if the text hasn't changed, so calling it every frame is cheap; `__init__` renders through `update_text` too, so there is one render path. With `outline_color` set (it defaults to `None`, so existing labels are unchanged), a copy of the text in that color is drawn one art pixel (`GAME_SCALE`) up, down, left and right first, then the text on top, giving it a dark rim that reads on any background:

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
  - **`draw_slot(screen, rect, item)`** draws the slot frame, then, if there's an item, its icon (scaled by `GAME_SCALE` once and cached by item id in `_get_icon`) and, for stacks of more than one, an outlined count placed by its visible ink one art pixel inside the bottom-right corner. One `count_label` is shared by every slot and re-positioned for each.
  - **Tooltips.** Hovering an item with an empty hand shows a framed tooltip next to the mouse: the name in `PALETTE_STEEL`, the description in `PALETTE_STONE`, and the value (if the item has one) in `PALETTE_TORCH`. Hovering an empty equipment slot shows just the slot's name (`"boots".title()` is "Boots"), so the empty slots can be told apart. An item's tooltip text never changes, so `build_tooltip(lines)` renders the whole tooltip, frame and text, into one surface the first time, and `get_tooltip(key, lines)` keeps it in `tooltip_cache` keyed by the item id (or `empty_<slot name>`, which can never clash with an item id); after that, hovering is a single blit. `draw_tooltip` places it `TOOLTIP_MOUSE_OFFSET` (18) down and right of the cursor, and flips it to the other side of the cursor if it would go off the screen.

    ```
    tooltip width  = widest line + 2 × TOOLTIP_PADDING                                       (rounded up to a multiple of 3)
    tooltip height = 2 × TOOLTIP_PADDING + (line count − 1) × TOOLTIP_LINE_HEIGHT + ink height  (rounded up to a multiple of 3)
    line y         = TOOLTIP_PADDING − ink top + line index × TOOLTIP_LINE_HEIGHT
    ```

    `TOOLTIP_PADDING` (18) is the 12 px frame border plus 6 px of room, and `TOOLTIP_LINE_HEIGHT` (27) is the visible text height (15) plus spacing. The size is rounded **up** so the text always fits. Subtracting the ink top (the empty space Silkscreen leaves above its letters, about 10 px) puts each line's visible top exactly at the padding.
  - **The held item** is drawn centered on the mouse, using the icon's own size.
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
- **`hud.py`**: `HUD`, the in-game heads-up display. `Level` creates one and calls `hud.draw(screen, player, run_time, floor_number)` once per frame, passing `level_index + 1` as the floor number; `draw` calls `draw_health`, `draw_timer`, `draw_floor` and `draw_quick_slots`, so Level never changes when the HUD gains parts. The HUD is given plain values rather than the `Level` itself, so it doesn't need to know about `LEVEL_ORDER` or `level_index`, only the number to show. The font and the panels are created once in `__init__`.
  - **Pixel-grid rules.** The HUD uses Silkscreen only at 24 (its 8 px grid × 3) or 48, so font pixels are the same 3×3 blocks as the world and the frames. Every size and position is a multiple of 3, and anything calculated is snapped with `value // GAME_SCALE * GAME_SCALE`.
  - **Health** (`draw_health`): a `HEALTH_PANEL_SIZE` (312×54) panel at `HUD_MARGIN` (12), with a `HEALTH_BAR_SIZE` (186×24) bar at `HEALTH_BAR_OFFSET` (18, 15). The empty bar is `PALETTE_SHADOW`, the fill `PALETTE_BLOOD`, and the `current/max` text `PALETTE_STEEL`, `HEALTH_TEXT_GAP` (9) to the right of the bar. Gaps in `PALETTE_VOID` split the bar into segments, drawn after the fill so they cut through both parts. `segment_hp_for(max_health)` picks the segment size so there are at most `HEALTH_MAX_SEGMENTS` (5) blocks, each a round number of HP: 25 max gives 5-HP blocks, 35 gives 10, 100 gives 20.
  - **Centering text** (`centered_text_y(text_surface, center_y)`): a rendered text surface is taller than its letters, because fonts reserve space above and below them (for Silkscreen at 24 the surface is 31 px tall but the digits only run from y 10 to 25). So text is centered by its visible pixels: `get_bounding_rect()` measures the ink, and its center is lined up with the target center.
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
    text_x        = (floor_panel_x + panel width // 2 − ink center x), snapped to the grid
    text_y        = centered_text_y(text, HUD_MARGIN + panel height // 2)
    ```

  - **Quick slots** (`draw_quick_slots`, `draw_quick_slot`): two `QUICK_SLOT_SIZE` (72×72) slots at the bottom left, `QUICK_SLOT_GAP` (12) apart, for potions and gold keys. 72 is the 12 px frame border on each side plus a 48 px icon (16 art pixels × 3). One `draw_quick_slot(screen, slot_pos, icon, count, count_label, cooldown_fraction=0.0)` draws any slot in order: frame, icon, cooldown shade, count, each on top of the one before; `draw_quick_slots` calls it once per slot with that slot's values.
    - The icons come from the item database: `HUD(item_database)` takes `Level`'s database and scales each item's `.image` by `GAME_SCALE` once. The database is the one source for item images, so the HUD, the inventory and ground items always match.
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
- **`create_outline.py`**: `make_outline` builds a one-pixel outline surface from an image's mask. It outlines each separate shape in the mask (`mask.connected_components()`), because `mask.outline()` alone only traces the first shape, which for text would be just the first letter. Holes inside a shape, like the inside of an "A", are not outlined. `draw_outline` blits it shifted one pixel in each direction to make a thicker outline.
- **`cursor.py`**: `Cursor`, the custom mouse cursor, drawn slightly down and right of the real mouse position.

### `tools/`

- **`line_counter.py`**: see section 3.
- **`make_sprite.py`**: see section 3.

## 7. One gameplay frame, step by step

This is `Level.update(dt)` followed by `Level.draw(screen)`.

Before step 1, `update` has two early exits. While the player is dying, it only advances the death freeze (step 6). Then, while a floor transition is running, it only calls `update_transition(dt)` and returns. Both come before `read_input()` and `run_time += dt`, so input, ESC, the world and the run timer are all frozen; transition time doesn't count toward the run, since loading speed differs between computers.

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
- Right after the pause check, `run_time += dt`. Its position is the whole pause logic: while paused, `Level.update` isn't called at all; while dying, the dying block has already returned; and on the frame ESC is pressed, the pause check returns first. So the timer only counts frames of real play. Opening the inventory doesn't pause the game, so it doesn't pause the timer either.
- `debug`: toggle hitbox drawing.
- `interact`: run `interact.interact(player, level)` (below).
- `inventory`: open the inventory. When closing, any held item goes back into the inventory first. If it doesn't fit, the inventory stays open.
- A mouse click while the inventory is open goes to `InventoryUI.handle_click`.

The game keeps running while the inventory is open. It is an overlay, not a pause, so managing items costs time and the world can still hurt you. `INVENTORY_PAUSES_GAME` (`False`, in `level.py`) makes this a one-word change: right after the inventory input (opening, closing and clicking), `Level.update` returns early when the inventory is open and the constant is `True`, which would stop the player, enemies, contacts and camera while the inventory stays usable. The check sits after `run_time += dt`, so the run timer would keep counting even while paused.

**3. Player update** (`Player.update`):
1. Sets `walking` and updates `last_direction` from the move direction. Facing doesn't change mid-roll. Vertical input wins over horizontal for facing.
2. Recomputes `stats` from `base_stats` plus equipment bonuses, every frame, so equipping takes effect immediately. If the health stat changed, `set_max_health` updates the maximum and clamps current health.
3. `roll` intent → `try_start_roll`. A roll needs a move direction, can't start during another roll (`is_rolling`), and can't start while `cooldown_timer` is running. Starting one starts both `active_timer` and `cooldown_timer`.
4. `heal` intent → `use_small_health_potion`. Heals 70, removes one potion and starts the heal cooldown, unless the cooldown is still running, health is already full or there is no potion. It returns whether a potion was used, and only then does the player play the `heal` sound. The sound is played here rather than in `systems/consumables.py` because it is feedback, not a rule.
5. `update_movement`: `steer` computes the new velocity from the move direction and the `max_speed`, `acceleration_rate`, `deceleration_rate` and `grip` stats, then `move_and_collide` moves the rect. Hitting a wall zeros velocity on that axis.
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

**4. Enemy update.** Each enemy gets the solid tiles and the player's position:
- **`fly`** (Skull): ignores walls. While `flee_timer` is running it moves away from the player, while `return_timer` is running it moves toward the player, within `CHASE_RANGE` (200) it chases, and otherwise it drifts slowly in a random diagonal that occasionally changes.
- **`wander_chase`** (Skeleton): collides with walls. If it has line of sight to the player (no wall rect crosses the line between them), it chases. Otherwise it wanders at half speed.
- **Knockback**, after the behaviour's movement: `update_knockback` moves the enemy by `knockback_velocity * dt` with `move_and_collide`, sets the shove to 0 on any axis that hits a wall (so the enemy doesn't keep pressing into it), then fades it with `decay_velocity` at the enemy's `knockback_decay_rate`. Walls block knockback for every enemy, including flying Skulls that otherwise pass through walls. The AI keeps running during a shove, and since a hit also starts the flee, both push the enemy away.

**5. Contact and combat.** `find_player_contacts` checks enemies within 100 pixels and keeps those whose masks actually overlap the player (pixel-perfect, not rectangle). For each contact, `resolve_contact`:
- **only while the player is rolling**, deals `round(player.speed * ROLL_DAMAGE_PER_SPEED)` to the enemy, shoves it, and starts the enemy's own invulnerability window for `enemy.invulnerability_duration`, unless the enemy is already invulnerable. Rolling is the player's only attack: walking into an enemy doesn't hurt it.
- deals the enemy's `attack_damage` to the player and starts the player's invulnerability window, unless the player is already invulnerable or is rolling,
- always starts the enemy's flee (2 s) then return (3 s) timers, even when both hits were skipped, so an enemy can't stay on top of the player.

**The shove.** The direction is from the player's center to the enemy's center, normalized, so a head-on hit pushes the enemy straight back and a glancing hit pushes it sideways. If the two centers are exactly the same point, that vector has zero length and can't be normalized, so the roll direction is used instead. The shove is `direction * player.speed * KNOCKBACK_PER_SPEED * enemy.knockback_multiplier`: the player's hit strength (roll speed times `KNOCKBACK_PER_SPEED`, 1.2) scaled by how easily this enemy is pushed. Speed now drives both damage and knockback, so a full-speed roll hits hardest and a hit as the roll fades barely shoves.

```
knockback speed    = player.speed  ×  KNOCKBACK_PER_SPEED  ×  enemy.knockback_multiplier
                     └──── the player's hit strength ────┘     └─ this enemy's weight ─┘

knockback velocity = direction (player → enemy, length 1) × knockback speed
slide distance     ≈ knockback speed ÷ enemy.knockback_decay_rate
```

The player's window lasts `PLAYER_INVULNERABILITY_DURATION` (1 s), and each enemy's lasts its own `invulnerability_duration`, so each side can be hit at most once per window however long the sprites overlap. If several enemies touch the player on the same frame, the first one's hit starts the window and the rest are skipped, because the contacts are resolved one at a time. A roll blocks damage for its 0.4 s but doesn't start a window. Enemies at 0 health are removed.

```
roll damage = round(player.speed  ×  ROLL_DAMAGE_PER_SPEED)
                    └ measured ─┘     └────── 0.15 ──────┘
                      roll speed
```

`ROLL_DAMAGE_PER_SPEED` is 0.15, so a roll at about 204 pixels per second deals 31, and a 100 health enemy takes about 3 rolls. Because damage comes from measured speed and the roll push fades out, a hit near the end of a roll does less damage than one early in it, which rewards rolling *into* enemies. Because an enemy's invulnerability (1 s) lasts longer than a roll (0.4 s), each enemy can be hit at most once per roll, but different enemies each have their own window, so rolling through a group hits them all. `resolve_contact` returns `True` when the enemy was hit, and `Level.update` then plays the `roll_hit` sound. The sound is played in the level rather than in `systems/combat.py` because it is feedback, not a rule.

**6. Player death.** After all contacts are resolved, the level checks `is_dead(player.health) and not self.dying`. The check is here rather than in `systems/health.py` because `is_dead` is the rule and what happens next is the level's decision.

`is_dead` is a condition that stays true on every frame once health is 0, but the death sequence must start only once, at the moment of death. The `dying` flag handles that: on the first dead frame the level sets `dying = True`, starts `death_timer` with `DEATH_DELAY`, stops the music, plays the `death` sound, and returns early so the ground items and camera don't update. On later frames `not self.dying` is false, so none of it repeats.

While `dying` is true, the very first thing `Level.update` does is count `death_timer` down by `dt`, update the fade, and return. Because that check comes before `read_input()`, input, movement, enemies and contacts are all skipped, so ESC can't pause and Q can't heal during the freeze. `Level.draw` still runs every frame, so the world stays on screen, frozen as it was. When the timer reaches 0 the level switches to `"game_over"`. Restart and Main Menu build a brand new `Level`, so `dying` and the timer reset on their own.

**The death fade.** Each dying frame, Level works out how far the fade has gone and hands the result to the player, who only draws it:

```
elapsed       = DEATH_DELAY − time_left(death_timer)
fade_progress = min(1.0, elapsed ÷ DEATH_FADE_DURATION)    (0.0 → 1.0, then held)
player.alpha  = round(255 × (1 − fade_progress))           (255 visible → 0 invisible)
```

- `elapsed = DEATH_DELAY - time_left(death_timer)` is the seconds since death (the timer counts down, so time passed is the total minus what's left).
- `fade_progress = min(1.0, elapsed / DEATH_FADE_DURATION)` goes from 0.0 at death to 1.0 when the fade is done. The `min` holds it at 1.0 afterwards.
- `player.alpha = round(255 * (1 - fade_progress))` takes the body from fully visible to invisible.

So the body fades over 1.5 s, then the empty spot holds until the 3.0 s delay ends. The alpha is set in `update`, where the timer advances, so `draw` only draws. The player's blink doesn't interfere: the killing hit started the player's i-frames at 1.0 s, the freeze stops them counting down, and that frozen blink phase is a visible one.

**7. Reaching the exit.** After the death check, if `exit_rect` isn't `None` and the player's rect overlaps it, the level first records the split (`splits.append(run_time)`), for every floor including the last, then checks whether there is another floor (`level_index + 1 < len(LEVEL_ORDER)`). If there is, it starts the `"fade_out"` phase of the floor transition; `level_index` only goes up later, when the next floor actually loads at the end of the fade. Otherwise the run is over and the level switches to `"level_complete"`. Either way `update` returns.

```
LEVEL_ORDER = [floor 0, floor 1]

exit on floor 0:  0 + 1 < 2  →  "fade_out"  …  end of fade: level_index 0 → 1, load_floor(LEVEL_ORDER[1])
exit on floor 1:  1 + 1 < 2 is false  →  "level_complete"
```

The check comes after the death check, so dying and touching the exit on the same frame counts as a death. `exit_rect is not None` is checked first, and because `and` stops at the first false part, a map without an exit never tries to collide with `None`. After the switch `Level.update` is no longer called, so `run_time` stays at the finishing time.

**8. Ground items and camera.** Ground items advance their animation, and the camera centers on the player.

**What `interact` does (F).** It looks in a box 15 pixels larger than the player and takes the first match in this priority order:
1. **A chest:** rolls `CHEST_LOOT`, spawns the drops around the chest, and removes the chest.
2. **A door, only if you have a `gold_key`:** removes every door tile with the same `door_id`, rebuilds the solid tiles, and uses up one key.
3. **A ground item:** adds it to the inventory. If only part of the stack fits, the rest stays on the ground with the reduced quantity.

**Drawing order** (`Level.draw`). Steps 1 to 6 draw onto `world_surface`, at `position - camera`, and anything outside the camera (`is_on_screen`) is skipped. Every world-drawing call already takes the surface to draw on as a parameter, so tiles, items and actors don't know or care that it's a small canvas:
1. Fill `world_surface` with `MENU_BACKGROUND_COLOR`, clearing last frame (the map doesn't cover the whole view, so old frames would otherwise smear around the edges).
2. The pre-rendered floor surface.
3. Decor, walls, then doors. Doors within `UNLOCK_DOOR_DISTANCE` (32) of the player get a `PALETTE_STEEL` outline. This outline doesn't check for a key.
4. The exit, as a 2-pixel `YELLOW` outline (`exit_rect.move(-camera.x, -camera.y)` returns a shifted copy, so the stored rect is unchanged).
5. Ground items and chests.
6. The player and enemies, sorted by `rect.y` so whoever is lower on screen draws in front. Enemy health bars and debug hitboxes are drawn by the entities onto the same surface, so they scale too.
7. Scale the world onto the screen: `pygame.transform.scale_by(world_surface, GAME_SCALE)` returns a new surface 3 times bigger, using nearest-neighbor scaling so pixels stay crisp instead of blurring, and it's blitted at (0, 0).
8. The HUD, `self.hud.draw(screen, player, run_time, level_index + 1)`: the health panel (top left), the run timer (top center), the floor number (right of the timer) and the quick slots (bottom left), on the screen at full resolution. It comes after step 7, so it lands on top of the world.
9. The inventory overlay, if open.
10. During a floor transition, `fade_overlay` at `transition_alpha()`, over everything including the HUD, then the floor card text during `"card"`.

The pause menu and the end-of-run screens call `level.draw(screen)` to show the frozen level behind them, so they get the scaled view automatically.

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

**Timers** (`systems/timer.py`). Every countdown in the game is a `{"timer": seconds_left}` dict made with `new_timer()`. `start_timer(timer, duration)` sets it, `advance_timer(timer, dt)` subtracts `dt` each frame, and `is_running(timer)` is true while it is `> 0`. `time_left(timer)` returns the seconds left, never below 0, for code that needs the number itself, such as the roll ease-out and the player's blink. The value keeps counting below 0, which is harmless because every check goes through `is_running` or `time_left`. Only `timer.py` reads the `"timer"` key directly. The roll's `active_timer` and `cooldown_timer` are timers too. The one exception is animation, which is a different kind of timer that counts *up* to advance frames.

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
    "texture_data": skull_enemy_texture_data,
    "start_animation": "skull_idle",
    "knockback_multiplier": 1.2,   # how easily it is shoved by a roll hit
    "knockback_decay_rate": 10,    # how fast the shove fades (higher is shorter)
    "blink_interval": 0.1,         # seconds per blink on/off after a hit
    "invulnerability_duration": 1.0,  # seconds of i-frames after a hit
},
```

Every key is required. `Enemy.__init__` reads them with `type_data["..."]`, so a missing key raises `KeyError` naming it when the level loads, instead of silently using a default.

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

**Sounds.** Every `.wav` or `.ogg` in `Assets/Sounds` and `Assets/Music` is loaded and named by its filename without the extension. Sound files are named in lowercase snake_case, so their keys are too. Names currently used: `button_hover`, `button_click`, `pause`, `heal`, `death` and `roll_hit` (SFX), and `menu_music`, `level_music` and `game_over` (music). Each state picks its own track in `enter()` (section 5). A missing name prints a message instead of crashing.

**The map** (`Assets/Maps/Dungeon_Level_One.tmx`, made in Tiled, 16x16 tiles). The loader looks for these names:

| Layer | Type | What the loader does |
| --- | --- | --- |
| `Floor` | Tile layer | Drawn once into `map_surface` |
| `Walls` | Tile layer | One `WallTile` per tile. These block movement. |
| `Wall_Decor`, `Floor_Decor` | Tile layers | `DecorTile`s, drawn but not solid |
| `Door_Tiles` | Tile layer | One `Door` per tile. These block movement until unlocked. |
| `Logic_Layer` | Tile layer | Not drawn. Its tiles carry a `door_id` property, and each door tile reads the `door_id` at the same x and y. |
| `Chests` | Object layer | One `Chest` per object named `chest` (any capitalization) |
| `Entity_Spawns` | Object layer | `Player` is the player spawn. `Enemy_<Type>` objects (e.g. `Enemy_Skull`) are enemy spawns. A rectangle object named `Exit` is the level exit. A map without one can't be finished, but doesn't crash. |

Door tiles that share a `door_id` (e.g. `door_1`) unlock together as one door.

## 9. How to add things

**A new enemy type.**
1. Add its sheet layout to `entities/enemies/enemy_texture_data.py`.
2. Add an entry to `ENEMY_TYPES` with a key like `"Bat"`, its stats, a `behavior` (`"fly"` or `"wander_chase"`), its texture data, its starting animation name, and its `knockback_multiplier`, `knockback_decay_rate`, `blink_interval` and `invulnerability_duration`. Every key is required: a missing one crashes at level load with a `KeyError` naming it.
3. In Tiled, place objects named `Enemy_Bat` in `Entity_Spawns`.
4. For a new behaviour, write a `<behavior>_velocity` function in `systems/enemy_ai.py` and add a branch for it in `Enemy.update_movement`.

**A new item.**
1. Draw its art as a new entry in `SPRITES` in `tools/make_sprite.py` (16×16, saved to `Assets/Items/`) and run the tool, then add its sheet layout to `items/item_texture_data.py` pointing at that PNG.
2. In `initialize_item_database`, load its animations and add an `Item` (or `EquipmentItem` with `slot` and `bonuses`) under a new id.
3. To make it drop, add an entry to `CHEST_LOOT`.
4. If it does something when used, add a function to `systems/consumables.py` and call it from the player on a new intent.

**New equipment.** Use `EquipmentItem` with `slot` set to one of `head`, `chest`, `boots` or `ability`. Its `bonuses` keys must match names in `base_stats`. For a new slot, add the name to `EQUIPMENT_SLOT_NAMES` in `systems/inventory.py`. The inventory screen draws one equipment slot per name and resizes its window to fit.

**A new key binding.** Add a field to the dict returned by `read_input`, then react to it in `Level.update` (level-wide actions) or `Player.update` (player actions).

**A new state or menu.**
1. Create a class with `enter()`, `update(dt)` and `draw(screen)` that takes `game_state_manager`. Put its music in `enter()`, or use `pass` to keep whatever is playing.
2. Build it in `Game.__init__` and register it with `add_state("name", state)`.
3. Switch to it from another state with `set_state("name")`.
4. For a menu, follow the existing ones: fill the screen with `MENU_BACKGROUND_COLOR`, create the fonts once in `__init__` from `FONT_PATH`, and use `TextButton`s with `BUTTON_FONT_SIZE`.

**A new level.** Make a TMX map using the layer names in section 8, including a `Player` spawn and an `Exit` rectangle in `Entity_Spawns`, add its path to `globals.py`, and build a `Level` with that path. There is no level-to-level transition yet.

**A new sound or music track.** Drop a `.wav` or `.ogg` into `Assets/Sounds` or `Assets/Music` and play it by filename: `sound.play_sfx("name")` or `sound.play_music("name")`. To give a screen its own track, call `play_music` in that state's `enter()`.

## 10. Debug tools

- **P**: toggles `debug.show_hitboxes`. While it's on, mask outlines are drawn for the player (green), enemies (red) and walls (blue). These are the same masks used for contact detection, so what you see is exactly what collides with enemies. Wall collision itself uses rectangles. The player's outline is still drawn while the sprite blinks during invulnerability.
- **FPS counter**: turn it on in Options. It shows in the top right and refreshes twice a second. The setting is saved.

## 11. Known gaps and planned work

**Combat:**
- Death fades the player's body out as a stand-in until real character art and a death animation exist.
- A per-enemy speed drain on contact (set in `ENEMY_TYPES`) is planned.
- A stagger (no AI movement while an enemy is being knocked back) is a possible follow-up if hits feel too floaty.
- `KNOCKBACK_PER_SPEED` could move into the player's `base_stats` if gear should ever boost knockback, so `compute_stats` picks up the bonus.
- The `defense` stat exists but isn't used yet.
- With the current stats, roll speed only varies between about 200 and 270 pixels per second, so roll damage varies only a little until movement tuning and gear change it.

**Movement:**
- All movement values are first-pass numbers. They will be tuned once the basic gameplay features are in and levels are being built, with feedback from playtesters.
- Speeds are in world pixels per second, so the player covers the same number of tiles per second at any `GAME_SCALE`. At 3× the screen shows a third as many tiles across, so movement looks about 3× faster on screen than it did at 1×. Something to judge in the tuning pass.

**Content and map:**
- Skeletons reuse the skull sprite until `skeleton_texture_data` is filled in.
- The map has a `Keys` tile layer and an `Items` object layer (with placed `gold_key` and `small_health_potion` objects) that the loader doesn't read yet. Items currently only come from chests.
- `start_new_run()` reloads the map inside the update of whichever menu calls it (`RunEndScreen` or `Options`), so the first frame of the new run gets a large `dt` covering the load time.
- If the inventory is open when the player touches an exit, it stays open underneath the floor transition (harmless; clicks are ignored until play resumes).
- `LEVEL_ORDER` lists level one twice, to test the floor transition, until level two exists.
- The exit is drawn only as a yellow outline until there is art for it.

**HUD:**
- The health panel has a fixed width, so health text wider than `25/25` (for example `100/100`) won't fit. Its width should be worked out from the text before max health goes above 99.
- The floor panel also has a fixed width, which fits up to `F9`.
- The end screen's split table fits up to 5 floors above the buttons.
- The menus and end screens use font sizes 32 and 64, which aren't on the 24/48 pixel grid the HUD follows; to be fixed in one menu pass.

**Menus and saving:**
- Choosing Main Menu from the pause menu throws the run away with no warning. A confirmation box that tells the player their progress won't be saved is planned. It would go in the Options Main Menu branch, before `start_new_run`.
- There is no saving system yet, so a run can't be saved and resumed later. Once saving exists, the confirmation box can change its wording, or save first.
