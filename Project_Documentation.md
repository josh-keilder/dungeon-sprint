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

**`hooks/pre-commit`.** The repo's git config sets `core.hooksPath = hooks`, so this script runs before every commit. It runs `tools/line_counter.py` and stages `README.md`, so the statistics are always current. It has commented-out lines for running Black and Pylint, which are not active. A fresh clone needs `git config core.hooksPath hooks` to enable it.

## 4. Startup and the main loop

`main.py` defines `Game`. Its constructor runs in this order, and the order matters:

1. `pygame.init()`.
2. `settings.load_settings()` reads `settings.json`. It must run before the window is created, because the window needs the fullscreen setting.
3. `create_window(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen)` opens the window. It must exist before any image is loaded, because `load_image` calls `convert_alpha()`, which needs a display.
4. The system mouse is hidden and a `Cursor` is built from `Assets/Cursors/01.png` at half scale.
5. Sound: all sound effects and music are loaded and the saved volumes are applied. No music starts here.
6. The FPS label (`TextLabel` at the top right) and its timer are created.
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

The window uses `pygame.SCALED`. The game always draws to a 1280x720 surface and pygame scales it to fit the real window or monitor, so all coordinates in the code are in that 1280x720 space.

## 5. State flow

A *state* is any object with `update(dt)`, `draw(screen)` and `enter()`. `enter()` runs once each time the game switches to that state, and is where a state does its "on arrival" work, such as starting its music. A state with nothing to do on arrival still needs an `enter` whose body is `pass`, or the switch crashes with `AttributeError`. `GameStateManager` (`states/state_manager.py`) holds:
- `states`: a dict of name to state object.
- `current`: the name of the active state.
- `previous`: the name of the state before it.

`set_state(name)` moves `current` into `previous`, switches to `name`, then calls the new state's `enter()`. An unknown name raises `ValueError`, so a typo fails loudly instead of silently. `go_back()` switches to `previous` through `set_state`, so it calls `enter()` too.

```
         MainMenu ──"Start"──▶ Level ──player at 0 HP──▶ RunEndScreen "game_over"
              │                  │  └──reach the exit──▶ RunEndScreen "level_complete"
          "Options"          ESC (plays "pause")              │ (both)
              ▼                  ▼                  "Restart" ──▶ new Level
           Options ◀─────────────┘                  "Main Menu" ──▶ new Level, then MainMenu
              │
   "Main Menu" ──▶ MainMenu   "Back" ──▶ Level  (only shown when previous == "level")
```

- **MainMenu** (`states/menus/main_menu.py`): Start goes to the level, Options goes to the options menu, Exit posts a `pygame.QUIT` event so the main loop shuts down normally. `enter()` plays `MAIN_MENU_MUSIC` (`"menu_music"`).
- **Level** (`states/map/level.py`): the dungeon. ESC switches to options and plays the `pause` sound. When the player's health reaches 0 it plays `death`, stops the music, freezes for `DEATH_DELAY` (3.0) seconds, then switches to `"game_over"` (section 7, step 6). Touching the exit switches to `"level_complete"` (step 7). `enter()` plays `LEVEL_MUSIC` (`"level_music"`). Unpausing calls it again, but the track keeps going instead of restarting (see `sound.py` in section 6).
- **Options** (`states/menus/options.py`): music and SFX sliders, an FPS toggle and a fullscreen toggle. Main Menu returns to the main menu. When the menu was opened from the level, it first calls `start_new_run()` so the abandoned run is thrown away. Back (`can_go_back()`) only appears when the previous state is `"level"`, so it acts as "resume". ESC does the same as Back, but only when the menu was opened from the level. In that case the menu is drawn over the dimmed, frozen level instead of a solid background. Both buttons save the settings file. `enter()` does nothing, so the pause menu keeps playing whatever music was already on.
- **RunEndScreen** (`states/menus/run_end.py`): the screen shown when a run ends, either way. It is one class created twice in `main.py` with different settings, `RunEndScreen(game_state_manager, title, title_color, music)`: the differences between the two screens are constructor arguments, not separate classes. It draws the title, the run time and two text buttons over the frozen level. Restart and Main Menu both call `start_new_run()` (from `states/new_run.py`) first, then switch to `"level"` or `"main_menu"`. `enter()` reads the finished run's `run_time` from `game_state_manager.states["level"]` and renders it. If `music` is a track name, `enter()` stops the current music and plays it once, with `loops=0`. That's how the death screen plays `"game_over"`, and why Restart then starts the level music again from the beginning. If `music` is `None`, as on the finish screen, the current track keeps playing.

All states are built once at startup and kept alive, so leaving and returning to the level normally resumes it where you left off. The exceptions are a death, and quitting to the main menu from the pause menu. `start_new_run(game_state_manager)` in `states/new_run.py` builds a brand new `Level(game_state_manager, DUNGEON_LEVEL_ONE)` and registers it under `"level"` with `add_state`, which replaces the old one in the `states` dict. A rebuild resets everything the Level owns (player, enemies, chests, doors, ground items, the inventory screen) and recenters the camera, while the shared image, animation and mask caches are reused. Because the Level can be replaced, code that needs it should look it up through `game_state_manager.states["level"]` when it needs it, not keep a reference from startup. `Game.level` in `main.py` still points at the first Level and is not used after registration.

## 6. Folder-by-folder reference

### Root

- **`main.py`**: `Game`, the startup and main loop described above.
- **`globals.py`**: shared constants only. Screen size, `FRAME_RATE`, `TILE_SIZE` (16), `PLAYER_SPRITE_SIZE` (64), `UNLOCK_DOOR_DISTANCE`, `SMALL_HEALTH_POTION_VALUE` (70), the color palette (all colors are kept even when unused), `MENU_BACKGROUND_COLOR` (`(37, 19, 26)`, the fill color of the Main Menu and Options screens), `DUNGEON_LEVEL_ONE` (the map path), `FONT_PATH` (the menu font, `Assets/Fonts/Silkscreen-Regular.ttf`), `BUTTON_FONT_SIZE` (32, the button font size shared by every menu), and `OVERLAY_ALPHA` (160 of 255, how dark the overlay is when the game-over and paused options screens are drawn over the level).
- **`Assets/Fonts/`**: `Silkscreen-Regular.ttf`, a pixel font under the SIL Open Font License. Load it with `pygame.font.Font(FONT_PATH, size)`. Because it is a pixel font, render it without anti-aliasing (`False`) and use sizes that are multiples of 8, or the letters blur.

### `entities/`

- **`player/player.py`**: `Player`. Holds `pos`, `velocity`, `speed` (the actual speed last frame in pixels per second, measured as distance moved divided by `dt`), `last_direction`, `walking`, `intent`, `base_stats`, and the `roll`, `invulnerability`, `heal_cooldown`, `animation`, `health`, `inventory` and `stats` dicts. `update(dt, walls)` runs the player's frame (section 7). Methods: `update_facing`, `update_movement`, `update_roll`, `handle_animation_state`, `draw`. While invulnerable, `draw` skips the sprite every other `BLINK_INTERVAL` (0.1 s) so the player blinks. The debug hitbox is still drawn. `alpha` (starts at 255, fully visible) is how opaque the sprite is drawn, and Level lowers it during death. When `alpha` is below 255, `draw` blits a faded **copy** of the frame instead of changing `self.image`. The animation frames are shared from the cache in `systems/assets.py`, so fading the frame itself would leave it faded for the next `Player` too, and a restarted player would be invisible.
- **`player/load_player.py`**: `load_player(spawn_pos)` loads the player animations (cropped from 64x64 sheets down to 16x16) and returns a `Player`.
- **`player/player_texture_data.py`**: sprite sheet layout for idle, walk and roll in the up, down and right directions. Left is generated by flipping right.
- **`enemies/enemy.py`**: `Enemy(type_data, pos)`. Copies its stats from the type data, then `update(dt, walls, target_pos)` advances its animation, moves it with the behaviour named in `behavior`, and counts down its `invulnerability` timer with `advance_timer`. `draw` shows a health bar above it once it has taken damage, and its hitbox when debug is on.
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
- **`new_run.py`**: `start_new_run(game_state_manager)` builds a fresh `Level` for `DUNGEON_LEVEL_ONE` and registers it as `"level"`, replacing the old run. It's a plain function in its own module so any menu can start a new run without depending on another menu. Used by `RunEndScreen` (Restart and Main Menu) and `Options` (Main Menu from a paused run).
- **`map/level.py`**: `Level(game_state_manager, map_path)`. Loads the map, item database, player and enemies. Runs and draws gameplay. Helpers that systems call back into:
  - `unlock_door(door_id)` removes every door tile with that id.
  - `refresh_walls()` rebuilds `solid_tiles` (walls plus remaining doors).
  - `spawn_loot(drops, center)` creates `WorldItem`s scattered randomly around a point.
  - `run_time` (starts at 0.0) holds the seconds spent in this run, shown by `run_timer_text`, a `TextLabel` at `RUN_TIMER_POS` (20, 40) in a Silkscreen font at `HUD_FONT_SIZE` (24). It's left-aligned because Silkscreen isn't fixed-width, so centered text would shift sideways as the digits change.
  - `exit_rect` is the map's exit area, or `None` if the map has none.
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
  - The title is rendered from `FONT_PATH` at `TITLE_FONT_SIZE` (64) in `title_color` and centered horizontally with `(SCREEN_WIDTH - width) // 2` at `TITLE_Y` (200). Restart and Main Menu are `TextButton`s using the shared `BUTTON_FONT_SIZE`, placed by their midtop point `(SCREEN_WIDTH // 2, y)`, with a gray outline.
  - `render_run_time(run_time)` renders `"Time: "` plus `format_run_time(run_time)`, centered at `RUN_TIME_Y` (290). It's called once in `__init__` with 0.0, so the image always exists before the first `draw`, and again in `enter()` with the real time.
  - `draw` first draws the current Level, looked up from `game_state_manager.states["level"]`, then a full-screen black overlay at `OVERLAY_ALPHA` (160 of 255), then the title and buttons. The level has to be redrawn every frame, because a translucent overlay drawn on its own would stack up to solid black.
  - Restart and Main Menu both call `start_new_run(self.game_state_manager)` from `states/new_run.py` before switching state.

### `systems/`

| Module | Job | Main functions |
| --- | --- | --- |
| `input.py` | Turns keyboard and mouse into an intent dict | `read_input` |
| `movement.py` | Velocity steering and wall collision | `steer`, `approach_fraction`, `move_and_collide` |
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
| `camera.py` | The shared camera rect | `camera`, `center_camera`, `is_on_screen` |
| `display.py` | Creating the window | `create_window` |
| `debug.py` | Debug flags | `show_hitboxes`, `toggle_hitboxes` |
| `sound.py` | Loading and playing audio. `play_music(name, loops=-1)` loops forever by default and remembers the track in `_current_music_name`. Asking for the track that is already playing does nothing, so it doesn't restart. `stop_music` clears the remembered name. | `load_sfx`, `load_music`, `play_sfx`, `play_music`, `stop_music`, `set_sfx_volume`, `set_music_volume` |
| `settings.py` | Reading and saving `settings.json` | `load_settings`, `save_settings`, `get_setting`, `set_setting` |

Some systems hold module-level state that is shared by everyone who imports them: `camera.camera`, `debug.show_hitboxes`, `settings.SETTINGS`, `sound.SFX` and `sound.MUSIC`, and the caches in `assets` and `hitbox`. Read flags through the module (`debug.show_hitboxes`), not with `from systems.debug import show_hitboxes`. A `from` import copies the value once at import time and never sees later toggles.

### `ui_objects/`

- **`button.py`**: `Button(image, pos, outline_color=WHITE)`. `image` can be any surface, including text from `font.render`. Plays `button_hover` when the mouse enters and draws an outline in `outline_color` while hovered. The outline is drawn first and the image on top of it, so only the ring just outside the shape shows. Drawn the other way round, the outline covers thin shapes such as letters. On a left click it plays `button_click` and sets `clicked_this_frame`, which `is_clicked()` returns. `set_image` swaps the picture and rebuilds the outline. The new rect keeps the old `topleft`, so text that changes width would drift off center. `TextButton.set_text` corrects for that.
- **`text_button.py`**: `TextButton(text, font, midtop=(0, 0), text_color=WHITE, outline_color=WHITE)`, a `Button` subclass whose picture is rendered text.
  - The font is passed in rather than created here. Each state creates its fonts once in `__init__`, because building a `Font` reads the font file from disk.
  - It is placed by its `midtop` point (the middle of its top edge), so passing `(SCREEN_WIDTH // 2, y)` centers it. For any other placement, leave out `midtop` and set another anchor on `rect` afterwards, such as `rect.bottomleft`.
  - `set_text(text)` re-renders the text, then puts `midtop` back where it was, so a toggle like "FPS: On"/"FPS: Off" stays centered when its width changes.
- **`slider.py`**: `Slider`, a draggable knob on a track between `min_value` and `max_value`. `pos` is the **center** of the track, not its top-left, so the track's left edge is `pos[0] - size[0] // 2`. The part left of the knob is drawn in `track_color` and the rest in gray. The knob is drawn in `knob_color`, or white while hovered or dragged. The track and knob have rounded corners. `get_current_value()` returns the value as an int.
- **`text_label.py`**: `TextLabel`, rendered text at a position (its top-left). `update_text` re-renders it. Text is drawn without anti-aliasing for a pixel look. By default it builds its font with `SysFont(font_name, font_size)`, which only finds installed system fonts and cannot load a `.ttf` path such as `FONT_PATH`. Pass a ready-made `font` (for example `pygame.font.Font(FONT_PATH, 24)`) to use that instead, in which case `font_name` and `font_size` are ignored. The options menu labels use this. The FPS counter and the inventory labels use the default.
- **`inventory_ui.py`**: `InventoryUI`, the inventory screen (section 7).
- **`time_format.py`**: `format_run_time(seconds)` turns seconds into `mm:ss.hh` text, e.g. 73.456 becomes `01:13.45`. It first truncates to whole hundredths (`int(seconds * 100) / 100`) instead of rounding, the way speedrun timers do, so it never shows a time that hasn't been reached and 59.996 can't round up to `00:60.00`. `//` (floor division) gives the minutes and `%` (remainder) the seconds left over. In the f-string, `02d` means a whole number padded to 2 digits, and `05.2f` a decimal with 2 places padded to 5 characters, the decimal point included. Shared by the level HUD and `RunEndScreen`.
- **`health_bar.py`**: `draw_health_bar(screen, health, x, y, width, height)`. Gray background with a fill that is green, or red at 30% health or below.
- **`create_outline.py`**: `make_outline` builds a one-pixel outline surface from an image's mask. It outlines each separate shape in the mask (`mask.connected_components()`), because `mask.outline()` alone only traces the first shape, which for text would be just the first letter. Holes inside a shape, like the inside of an "A", are not outlined. `draw_outline` blits it shifted one pixel in each direction to make a thicker outline.
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
- `pause`: switch to options, play `pause`, and stop this frame's update.
- Right after the pause check, `run_time += dt`. Its position is the whole pause logic: while paused, `Level.update` isn't called at all; while dying, the dying block has already returned; and on the frame ESC is pressed, the pause check returns first. So the timer only counts frames of real play. Opening the inventory doesn't pause the game, so it doesn't pause the timer either.
- `debug`: toggle hitbox drawing.
- `interact`: run `interact.interact(player, level)` (below).
- `inventory`: open the inventory. When closing, any held item goes back into the inventory first. If it doesn't fit, the inventory stays open.
- A mouse click while the inventory is open goes to `InventoryUI.handle_click`.

The game keeps running while the inventory is open. It is an overlay, not a pause.

**3. Player update** (`Player.update`):
1. Sets `walking` and updates `last_direction` from the move direction. Facing doesn't change mid-roll. Vertical input wins over horizontal for facing.
2. Recomputes `stats` from `base_stats` plus equipment bonuses, every frame, so equipping takes effect immediately. If the health stat changed, `set_max_health` updates the maximum and clamps current health.
3. `roll` intent → `try_start_roll`. A roll needs a move direction, can't start during another roll (`is_rolling`), and can't start while `cooldown_timer` is running. Starting one starts both `active_timer` and `cooldown_timer`.
4. `heal` intent → `use_small_health_potion`. Heals 70, removes one potion and starts the heal cooldown, unless the cooldown is still running, health is already full or there is no potion. It returns whether a potion was used, and only then does the player play the `heal` sound. The sound is played here rather than in `systems/consumables.py` because it is feedback, not a rule.
5. `update_movement`: `steer` computes the new velocity from the move direction and the `max_speed`, `acceleration_rate`, `deceleration_rate` and `grip` stats, then `move_and_collide` moves the rect. Hitting a wall zeros velocity on that axis.
6. `update_roll`: while rolling, the player is also moved by `roll_speed` in the roll direction (on top of normal movement), scaled by `roll_speed_multiplier` so the push fades out at the end of the roll (see below), then `advance_roll` counts down `active_timer` and `cooldown_timer`.
   Then the player's `speed` is measured. At the very start of `update`, the player's center is copied into `start_pos`, before anything moves. After `update_movement` and `update_roll`, the distance from `start_pos` to the new center, divided by `dt`, gives the actual speed in pixels per second. Because it is measured rather than calculated, it includes walls: rolling into a wall gives a low speed.
7. `advance_timer` counts down the invulnerability timer, then the heal cooldown.
8. Picks the animation `player_{idle|walk|roll}_{direction}` and advances it.
9. Copies `rect.topleft` into `pos`.

**How `steer` works.** `steer` is a kinematic controller, like Godot's: it doesn't push the player with forces, it moves the current velocity toward a *target velocity*, `direction * max_speed` (zero when there is no input). Each frame it closes a fraction of the gap between the two.

- **The fraction.** `approach_fraction(rate, dt)` returns `1 - exp(-rate * dt)`. Closing a fixed fraction of the gap per *frame* would feel snappier at higher frame rates, but this formula gives the same motion at any frame rate, because two frames of `dt` multiply out to exactly one frame of `2 * dt`. A higher `rate` is snappier. As a rule of thumb, the velocity is 95 % of the way to its target after about `3 / rate` seconds.
- **Acceleration scales by itself.** Because a fraction of the *gap* is closed, the player gains a lot of speed when standing still (big gap) and very little near `max_speed` (small gap), easing in without overshooting. No speed cap is needed.
- **Grip.** With input, the velocity is split using the dot product: `along_speed = velocity.dot(direction)` is the speed in the input direction, `along_velocity` is that part as a vector, and `across_velocity` is everything left over (sideways motion from the previous heading). The along part approaches the target at `acceleration_rate`. The across part is removed at the `grip` rate, so turns don't drift. When `along_speed` is negative (the player is reversing), the along part uses `grip` too, so turning around is as snappy as turning sideways.

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
- **Stopping.** With no input, the velocity is multiplied by `1 - approach_fraction(deceleration_rate, dt)`, which collapses it within a few frames. Below `STOP_SPEED` (1.0 px/s) it snaps to exactly 0, because closing a fraction of the gap never quite reaches zero.

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
- **The fade.** Before `ROLL_EASE_OUT_START` the multiplier is 1.0. After it, it is `(1 - progress) / (1 - ROLL_EASE_OUT_START)`, a straight line from 1.0 at progress 0.7 to 0.0 at progress 1.0. With a 0.4 s roll, the fade covers the last 0.12 s.
- **Measured example.** Rolling from full walking speed, the player's `speed` sampled every 0.05 s is `270, 270, 270, 270, 270, 244, 160, 77`, then 70 on the first frame after the roll.

**How `move_and_collide` works.** It moves on X, pushes the rect out of the first wall it overlaps, then does the same on Y. Doing the axes separately lets you slide along walls. Walls whose center is more than 64 pixels away on that axis are skipped for speed. It returns `(hit_x, hit_y)`.

**4. Enemy update.** Each enemy gets the solid tiles and the player's position:
- **`fly`** (Skull): ignores walls. While `flee_timer` is running it moves away from the player, while `return_timer` is running it moves toward the player, within `CHASE_RANGE` (200) it chases, and otherwise it drifts slowly in a random diagonal that occasionally changes.
- **`wander_chase`** (Skeleton): collides with walls. If it has line of sight to the player (no wall rect crosses the line between them), it chases. Otherwise it wanders at half speed.

**5. Contact and combat.** `find_player_contacts` checks enemies within 100 pixels and keeps those whose masks actually overlap the player (pixel-perfect, not rectangle). For each contact, `resolve_contact`:
- **only while the player is rolling**, deals `round(player.speed * ROLL_DAMAGE_PER_SPEED)` to the enemy and starts the enemy's own invulnerability window, unless the enemy is already invulnerable. Rolling is the player's only attack: walking into an enemy doesn't hurt it.
- deals the enemy's `attack_damage` to the player and starts the player's invulnerability window, unless the player is already invulnerable or is rolling,
- always starts the enemy's flee (2 s) then return (3 s) timers, even when both hits were skipped, so an enemy can't stay on top of the player.

The window lasts `INVULNERABILITY_DURATION` (1 s), so each side can be hit at most once per second however long the sprites overlap. If several enemies touch the player on the same frame, the first one's hit starts the window and the rest are skipped, because the contacts are resolved one at a time. A roll blocks damage for its 0.4 s but doesn't start a window. Enemies at 0 health are removed.

`ROLL_DAMAGE_PER_SPEED` is 0.15, so a roll at about 204 pixels per second deals 31, and a 100 health enemy takes about 3 rolls. Because damage comes from measured speed and the roll push fades out, a hit near the end of a roll does less damage than one early in it, which rewards rolling *into* enemies. Because an enemy's invulnerability (1 s) lasts longer than a roll (0.4 s), each enemy can be hit at most once per roll, but different enemies each have their own window, so rolling through a group hits them all. `resolve_contact` returns `True` when the enemy was hit, and `Level.update` then plays the `roll_hit` sound. The sound is played in the level rather than in `systems/combat.py` because it is feedback, not a rule.

**6. Player death.** After all contacts are resolved, the level checks `is_dead(player.health) and not self.dying`. The check is here rather than in `systems/health.py` because `is_dead` is the rule and what happens next is the level's decision.

`is_dead` is a condition that stays true on every frame once health is 0, but the death sequence must start only once, at the moment of death. The `dying` flag handles that: on the first dead frame the level sets `dying = True`, starts `death_timer` with `DEATH_DELAY`, stops the music, plays the `death` sound, and returns early so the ground items and camera don't update. On later frames `not self.dying` is false, so none of it repeats.

While `dying` is true, the very first thing `Level.update` does is count `death_timer` down by `dt`, update the fade, and return. Because that check comes before `read_input()`, input, movement, enemies and contacts are all skipped, so ESC can't pause and Q can't heal during the freeze. `Level.draw` still runs every frame, so the world stays on screen, frozen as it was. When the timer reaches 0 the level switches to `"game_over"`. Restart and Main Menu build a brand new `Level`, so `dying` and the timer reset on their own.

**The death fade.** Each dying frame, Level works out how far the fade has gone and hands the result to the player, who only draws it:

- `elapsed = DEATH_DELAY - time_left(death_timer)` is the seconds since death (the timer counts down, so time passed is the total minus what's left).
- `fade_progress = min(1.0, elapsed / DEATH_FADE_DURATION)` goes from 0.0 at death to 1.0 when the fade is done. The `min` holds it at 1.0 afterwards.
- `player.alpha = round(255 * (1 - fade_progress))` takes the body from fully visible to invisible.

So the body fades over 1.5 s, then the empty spot holds until the 3.0 s delay ends. The alpha is set in `update`, where the timer advances, so `draw` only draws. The player's blink doesn't interfere: the killing hit started the player's i-frames at 1.0 s, the freeze stops them counting down, and that frozen blink phase is a visible one.

**7. Reaching the exit.** After the death check, if `exit_rect` isn't `None` and the player's rect overlaps it, the level switches to `"level_complete"` and returns. The check comes after the death check, so dying and touching the exit on the same frame counts as a death. `exit_rect is not None` is checked first, and because `and` stops at the first false part, a map without an exit never tries to collide with `None`. After the switch `Level.update` is no longer called, so `run_time` stays at the finishing time.

**8. Ground items and camera.** Ground items advance their animation, and the camera centers on the player.

**What `interact` does (F).** It looks in a box 15 pixels larger than the player and takes the first match in this priority order:
1. **A chest:** rolls `CHEST_LOOT`, spawns the drops around the chest, and removes the chest.
2. **A door, only if you have a `gold_key`:** removes every door tile with the same `door_id`, rebuilds the solid tiles, and uses up one key.
3. **A ground item:** adds it to the inventory. If only part of the stack fits, the rest stays on the ground with the reduced quantity.

**Drawing order** (`Level.draw`). Everything world-space is drawn at `position - camera`, and anything off screen (`is_on_screen`) is skipped:
1. The pre-rendered floor surface.
2. Decor, walls, then doors. Doors within `UNLOCK_DOOR_DISTANCE` (32) of the player get a white outline. This outline doesn't check for a key.
3. The exit, as a 2-pixel `YELLOW` outline (`exit_rect.move(-camera.x, -camera.y)` returns a shifted copy, so the stored rect is unchanged).
4. Ground items and chests.
5. The player and enemies, sorted by `rect.y` so whoever is lower on screen draws in front.
6. The player's health bar and the run timer (screen space, top left).
7. The inventory overlay, if open.

**Inventory screen** (`InventoryUI`):
- A 10-column grid of 48-pixel slots (20 slots), plus a column of equipment slots: `head`, `chest`, `boots`, `ability_1`, `ability_2`.
- Clicking a grid slot swaps it with the item in your hand, which picks up, places or swaps.
- Clicking an equipment slot while holding an item equips it only if `item.slot` matches that slot name. Clicking it with an empty hand takes the equipped item off.
- Hovering an item with an empty hand shows a tooltip with name, description and `value_text` (if any). Stack counts show in the slot corner.

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

**`invulnerability` dict** (player and enemies): a timer holding the seconds of invulnerability left. `INVULNERABILITY_DURATION` is 1.0 s (`systems/combat.py`), `BLINK_INTERVAL` is 0.1 s (`player.py`), and `ROLL_DAMAGE_PER_SPEED` is 0.15 (`systems/combat.py`), so an enemy with 100 health dies after about 3 rolls.

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
- The `defense` stat exists but isn't used yet.
- With the current stats, roll speed only varies between about 200 and 270 pixels per second, so roll damage varies only a little until movement tuning and gear change it.

**Movement:**
- All movement values are first-pass numbers. They will be tuned once the basic gameplay features are in and levels are being built, with feedback from playtesters.

**Content and map:**
- Skeletons reuse the skull sprite until `skeleton_texture_data` is filled in.
- The map has a `Keys` tile layer and an `Items` object layer (with placed `gold_key` and `small_health_potion` objects) that the loader doesn't read yet. Items currently only come from chests.
- `start_new_run()` reloads the map inside the update of whichever menu calls it (`RunEndScreen` or `Options`), so the first frame of the new run gets a large `dt` covering the load time.
- There is only one level. Reaching the exit ends the run with the finish screen, but there is no next-level transition yet.
- The exit is drawn only as a yellow outline until there is art for it.

**Menus and saving:**
- Choosing Main Menu from the pause menu throws the run away with no warning. A confirmation box that tells the player their progress won't be saved is planned. It would go in the Options Main Menu branch, before `start_new_run`.
- There is no saving system yet, so a run can't be saved and resumed later. Once saving exists, the confirmation box can change its wording, or save first.
