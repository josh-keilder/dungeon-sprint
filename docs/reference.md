# Reference

Every module, folder by folder. (This page still follows the old layout; it is being rewritten as `engine.md` and `game.md`.)

## Root

- **`main.py`**: `Game`, the startup and main loop described above.
- **`constants.py`**: shared constants only (named `constants.py` rather than `globals.py`, which shared its name with Python's built-in `globals()` function and made `import globals` read like the built-in). `GAME_SCALE` (3) is how many screen pixels each world pixel becomes, and `WORLD_WIDTH` / `WORLD_HEIGHT` are the world canvas size, worked out from it so changing the one number switches the whole scale:

  ```
  WORLD_WIDTH  = ceil(SCREEN_WIDTH  ÷ GAME_SCALE)     3× → 427   (427 × 3 = 1281, 1 px falls off the edge)
  WORLD_HEIGHT = ceil(SCREEN_HEIGHT ÷ GAME_SCALE)     3× → 240
  ```

  `math.ceil` rounds up, so the scaled world always covers the whole screen. 2 gives 640×360 and 4 gives 320×180. Keep the scale a whole number: a screen pixel can't be split, so at 2.5× some art pixels come out 2 screen pixels wide and others 3, which looks lopsided and shimmers as the camera scrolls (smoothing instead makes it blurry).
  The rest of `constants.py`, in labelled groups: screen and timing (screen size, `FRAME_RATE`); the world canvas; art sizes (`TILE_SIZE` 16, `PLAYER_SPRITE_SIZE` 64); basic colors (`WHITE`, `RED` and so on, kept for debug drawing and later use; game art uses the palette), the tileset palette (all 34 colors in `Assets/Dungeon_Tileset.png` as `PALETTE_*` constants, grouped by family and ordered dark to light within each: darks and floors such as `PALETTE_VOID` (37, 19, 26) and `PALETTE_SHADOW` (84, 55, 64); walls, earth and wood such as `PALETTE_WALL` (110, 74, 72); reds `PALETTE_BLOOD` (188, 76, 81) and `PALETTE_ROSE`; fire and gold such as `PALETTE_TORCH` (191, 112, 77); moss and parchment; and stone, steel and ice such as `PALETTE_STONE` (144, 145, 158), `PALETTE_STEEL` (173, 193, 207) and `PALETTE_ICE` (202, 230, 245). UI and generated art use these names so everything stays on the tileset's colors. The UI color rules: steel is the normal text color, stone is secondary text such as item descriptions, and torch orange means "you can interact with this": hovered buttons and sliders, and the `Q` hotkey. In the world, the interaction outline is `PALETTE_CANDLE` when F will work and `PALETTE_STEEL` when it won't), `MENU_BACKGROUND_COLOR` (defined as `PALETTE_VOID`, the fill color of the Main Menu and Options screens; one name says which color, the other what it's for), `FLOOR_ORDER` (the map paths in play order; the run goes through them one after another, and the last one's exit ends the run. It lists the Easy floors, built with the ASCII converter from `Assets/Maps/Source/easy_floor_<n>.txt`; for now only `easy_floor_1.tmx`, which replaces the hand-built `Dungeon_Level_One.tmx`. That file stays in the repo as Tiled reference until all five Easy floors are in, and `test_room.tmx` stays as the converter's small test map), `FONT_PATH` (the menu font, `Assets/Fonts/Silkscreen-Regular.ttf`), `PANEL_FRAME_PATH` (`Assets/UI/panel_frame.png`, the frame art shared by the HUD and the inventory), `BUTTON_FONT_SIZE` (32, the button font size shared by every menu), and `OVERLAY_ALPHA` (160 of 255, how dark the overlay is when the game-over and paused options screens are drawn over the run).
- **`Assets/Fonts/`**: `Silkscreen-Regular.ttf`, a pixel font under the SIL Open Font License. Load it with `pygame.font.Font(FONT_PATH, size)`. Because it is a pixel font, render it without anti-aliasing (`False`) and use sizes that are multiples of 8, or the letters blur.

## `entities/`

- **`player/player.py`**: `Player`. Holds `pos`, `velocity`, `speed` (the actual speed last frame in pixels per second, measured as distance moved divided by `dt`), `facing`, `walking`, `intent`, `base_stats`, an `inventory` of `INVENTORY_SLOT_COUNT` (20) slots, and the `roll`, `invulnerability`, `heal_cooldown`, `animation`, `health`, `inventory` and `stats` dicts. `update(dt, walls)` runs the player's frame ([One frame](frame.md)). Methods: `update_facing`, `update_movement`, `update_roll`, `update_animation`, `draw`. While invulnerable, `draw` skips the sprite while `is_blink_hidden(self.invulnerability, BLINK_INTERVAL)` is true, so the player blinks. `BLINK_INTERVAL` (0.1 s) is the player's own value, at the top of `player.py`. The debug hitbox is still drawn. `alpha` (starts at 255, fully visible) is how opaque the sprite is drawn, and the Run lowers it during death. When `alpha` is below 255, `draw` blits a faded **copy** of the frame instead of changing `self.image`. The animation frames are shared from the cache in `systems/assets.py`, so fading the frame itself would leave it faded for the next `Player` too, and a restarted player would be invisible.
- **`player/load_player.py`**: `load_player(spawn_pos)` loads the player animations (cropped from 64x64 sheets down to 16x16) and returns a `Player`.
- **`player/player_texture_data.py`**: sprite sheet layout for idle, walk and roll in the up, down and right directions. Left is generated by flipping right.
- **`enemies/enemy.py`**: `Enemy(type_data, pos)`. Copies its values from the type data with `type_data["..."]`: `attack`, `attack_damage`, `speed`, `knockback_multiplier`, `knockback_decay_rate`, `blink_interval`, `invulnerability_duration`, `loot_table`, `behavior`, `touch_damage` and `animation_prefix` ([Data formats](data-formats.md)). `knockback_velocity` (starts at zero) is the current shove in pixels per second.
  - **Body and art.** `rect` is the enemy's **body**, a `FRect` the size of the type's `"body"` box, and it's what moves, hits walls, gets separated and blocks the player. The art (`image`) can be bigger, and is drawn around the body: `art_topleft()` subtracts the body's offset inside the frame (`body_x`, `body_y`). Frames facing left are mirrored, so the offset is mirrored too (`image width − body_x − body width`), keeping the body under the same pixels whichever way it faces. `pos` is synced to `rect.topleft` at the end of every update. Pixel-perfect contact checks (`find_player_contacts`) use the art at `art_topleft()`.
  - **`update(dt, walls, target_pos)`.** A dying enemy only counts `death_time` up and finishes its knockback slide. Otherwise it either advances its swing (`update_attack`, standing still) or moves with its `behavior` (`update_movement`, which returns the velocity it chose) and then checks `try_start_attack`; then knockback, the `invulnerability` and `attack_cooldown` timers, and `moving` (whether the body's center changed this frame) and `facing` (from the sign of the chosen velocity's x; unchanged when it's 0). Last, `update_animation` picks the frame ([One frame](frame.md), step 4).
  - **Animation states.** For a type with an `animation_prefix`, `animation_name()` builds `<prefix>_<action>_<facing>`, with the action picked in priority order: `death` while dying, `hurt` for the first `HURT_DURATION` (0.5 s) of the invulnerability window, `move` while `moving`, else `idle`. A type with no prefix (the Skull) keeps its single animation. During a swing `update_animation` doesn't use the animation dict: it shows `attack_frames()[attack_step()]`, so the swing's own clock picks the frame.
  - **Dying.** `start_dying()` sets `dying`, resets `death_time` and ends any swing (`attacking = False`): a dying enemy never runs `update_attack`, so a swing left on would freeze on its attack frame instead of playing the death animation. `death_duration` is the death strip's frame count ÷ `DEFAULT_ANIMATION_SPEED`, worked out once in `__init__` (0 for a type without a death strip, so it's removed on the next frame). `is_done_dying()` tells the floor when to drop its loot and remove it. A dying enemy doesn't blink, has no health bar, isn't solid and is skipped by contacts and strikes.
  - **The swing** (types with an `"attack"`): `try_start_attack`, `update_attack`, `attack_frames`, `attack_step`, `is_striking`, `strike_rect` and `interrupt_attack`, explained in [One frame](frame.md), step 4.
  - **Bodies.** `is_solid()` is `not dying and behavior != "fly"`: walkers have solid bodies, fliers and the dying don't. `shove(displacement, walls)` moves the body by a displacement with `move_and_collide` (used by separation, [One frame](frame.md) step 5), so a shove can't push an enemy into a wall.
  - **`draw`.** Hides the sprite while `is_blink_hidden(self.invulnerability, self.blink_interval)` is true, unless `blink_interval` is `None` (the Skeleton shows its hurt animation instead) or it's dying. Its health bar (shown once it has taken damage, hidden while dying) and its debug boxes are always drawn, so its health stays readable while it blinks. The bar is `ENEMY_HEALTH_BAR_WIDTH` (16) × `ENEMY_HEALTH_BAR_HEIGHT` (2) art pixels plus the 1-pixel border, so 4 art pixels tall in total, and sits `ENEMY_HEALTH_BAR_GAP` (8) above the **body**.
- **`enemies/enemy_type_data.py`**: `ENEMY_TYPES`, one entry per enemy kind ([Data formats](data-formats.md)).
- **`enemies/enemy_texture_data.py`**: enemy sprite sheet layouts. `skull_texture_data` is the Skull's single 16×16 idle animation. `skeleton_texture_data` has one strip per action, all `SKELETON_FRAME_SIZE` (32×32) frames facing right: `skeleton_idle_right` (6 frames), `skeleton_move_right` (10), `skeleton_attack_right` (9), `skeleton_hurt_right` (5) and `skeleton_death_right` (17), from `Assets/Enemies/Skeleton/idle.png`, `move.png`, `attack.png`, `hurt.png` and `death.png` (the pack's sword skeleton sheets, copied into `Assets/`). `load_animations` adds the mirrored `_left` versions on load.
- **`enemies/load_enemies.py`**: `load_enemies(enemy_spawns)` turns the map's spawn positions into `Enemy` objects. Spawn names with no matching `ENEMY_TYPES` entry are skipped.

## `items/`

- **`items.py`**: item **data** only (the sprites that put items in the world are in `world/objects.py`):
  - `Item`: an item template or stack. It has `id`, `name`, `animations`, `description`, `quantity`, `max_stack`, `animation_speed`, `value_text` and `image` (first idle frame). `clone()` is a shallow copy, so a clone has its own `quantity` but shares the same images.
  - `EquipmentItem(Item)`: adds `slot` and `bonuses`, and always has `max_stack` 1.
- **`item_database.py`**: `initialize_item_database()` builds and returns the dict of item templates, keyed by item id: `gold_key` ("Opens treasure rooms"), `silver_key` ("Opens the way forward"), `small_health_potion`, `speed_boots`. The two keys use the pack's spinning key animations; on the ground they animate, while the HUD quick slots and the inventory show their first frame (`item.image`) as a still icon. It also defines `SMALL_HEALTH_POTION_VALUE` (10), how much HP a potion heals: it's the potion's own data, so it lives next to the potion's definition rather than in `constants.py` (which is for settings shared across the whole game). It's used for the tooltip's "Value: 10 HP" here, and imported by `systems/consumables.py` for the actual healing, so the two can never disagree.
- **`item_texture_data.py`**: sprite sheet layouts for each item, plus `crate_texture_data` for the crate strip. The keys' entries (`gold_key_texture_data`, `silver_key_texture_data`) point at the 4-frame strips made by `make_strip`; the old `animated_gold_key.png` and the unused static `gold_key.png` were removed.
- **`loot_table_data.py`**: the loot tables: `CHEST_LOOT`, what a chest can drop, `CRATE_LOOT`, what a broken crate can drop, and one table per enemy type (`SKULL_LOOT`, `SKELETON_LOOT`), what it can drop when it dies ([Data formats](data-formats.md)).

## `states/`

- **`state_manager.py`**: `GameStateManager` ([Architecture](architecture.md)).
- **`new_run.py`**: `start_new_run(game_state_manager)` builds a fresh `Run`, starting on the first floor of `FLOOR_ORDER`, and registers it as `"run"`, replacing the old run. It's a plain function in its own module so any menu can start a new run without depending on another menu. Used by `RunEndScreen` (Restart and Main Menu) and `OptionsMenu` (Main Menu from a paused run).
- **`run.py`**: `Run(game_state_manager)`, **the run**: every floor in `FLOOR_ORDER`, one after another. It owns what lasts the whole run and the order of each frame; everything on the current map belongs to its `Floor` (`self.floor`, see `world/floor.py`).
  - **`__init__`** sets up what lasts the whole run: `run_time`, `splits`, the item database, the player, the HUD, the inventory screen, the death timer and the floor transition. It creates the player at `(0, 0)`, sets `floor_index` to 0 (which entry of `FLOOR_ORDER` is being played), then calls `load_floor` for the first floor, which places the player.
  - **`load_floor(map_path)`** builds a new `Floor(map_path, item_database)` and moves the **same** player object to the floor's `player_spawn`: it sets `rect.center`, syncs `pos` to the rect (enemy contact checks read `player.pos` before the player updates), zeroes `velocity` so the player doesn't slide in at full speed, centers the camera, and clears the interaction target. Because the player object is kept, health, inventory, gear and cooldowns carry over with no extra code, and because `run_time` lives on the `Run`, the timer keeps counting across floors. Because the floor is a **new object**, nothing from the old floor (ground items, particles, a pending exit, padlocks) can leak into the new one.

  ```
  Level (the run, built once)               Floor (one map, built by load_floor)
  ───────────────────────────               ────────────────────────────────────
  run_time, splits, floor_index             map surface, tiles, doors + padlocks
  item_database ──── shared with ─────────▶ chests, crates, ground items, particles
  player ──── placed at player_spawn ─────▶ enemies, solid_rects, exit
  hud, inventory_ui, death, transition      update(dt, player), draw(surface, player, highlight)
  input + the order of each frame           unlock_door, spawn_loot, highlighted_sprites
  ```

  `world_surface` (`WORLD_WIDTH` × `WORLD_HEIGHT`) is the canvas the world is drawn on before it's scaled to the screen; `draw` fills it, hands it to `floor.draw`, then scales it up and draws the HUD, the inventory and the transition overlay on the screen.
  - `run_time` (starts at 0.0) holds the seconds spent in this run, across all floors, and is drawn by the HUD's timer panel.
  - `splits` (starts empty, run-wide like `run_time`) holds the `run_time` at the moment each exit was touched, one entry per finished floor, the last floor included. That's the speedrun meaning of a split: the clock reading at each checkpoint. Only these raw readings are stored; each floor's own time is worked out from them on the end screen (`floor_times`). Because the floor transition pauses the run timer, no transition time ends up in any floor's time.
  - **The floor transition** belongs to `floor_transition`, a `FloorTransition` (see `ui_components/floor_transition.py`). At the exit, the run calls `floor_transition.start()`. While `floor_transition.is_active()`, `update` only calls `update_transition(dt)`, which advances it and, on the one frame its `update` returns `True` (the screen has just gone fully black), raises `floor_index`, calls `load_floor` for the next map and `floor_transition.set_floor_number(floor_index + 1)` (players count from 1, the list from 0). `draw` ends with `floor_transition.draw(screen)`, over everything including the HUD.
  - `dying` (starts `False`) is the flag that says the death sequence has started, and `death_timer` (made with `new_timer()`) holds the seconds left before the game-over screen. `DEATH_DELAY` (3.0 s) is the whole freeze, and `DEATH_FADE_DURATION` (1.5 s) is how long the player's body takes to fade out. The fade must be no longer than the delay.
- **`menus/main_menu.py`**: `MainMenu(game_state_manager)`, the title screen ([Architecture](architecture.md)).
  - `draw` fills the screen with `MENU_BACKGROUND_COLOR`, then draws the "DUNGEON SPRINT" title (`TITLE_FONT_SIZE` 96, at `TITLE_Y` 50, centered with `(SCREEN_WIDTH - width) // 2`) and the buttons.
  - Start, Options and Exit are `TextButton`s with a gray outline, centered and stacked at `START_BUTTON_Y` (300), `OPTIONS_BUTTON_Y` (380) and `EXIT_BUTTON_Y` (460).
- **`menus/options.py`**: `OptionsMenu(game_state_manager)`, the options menu ([Architecture](architecture.md)).
  - It uses the same size of text title ("OPTIONS") as the Main Menu screen. All buttons are `TextButton`s with a gray outline.
  - The background depends on where the menu was opened from. When `can_go_back()` is true (opened from the run with ESC), `draw` first draws the paused Run, looked up from `game_state_manager.states["run"]`, then a full-screen black overlay at `OVERLAY_ALPHA` (160 of 255), the same way as the game-over screen. Otherwise it fills the screen with `MENU_BACKGROUND_COLOR`.
  - The FPS and Fullscreen toggles are centered at `FPS_BUTTON_Y` (220) and `FULL_SCREEN_BUTTON_Y` (300). Their text comes from `FPS_LABEL` and `FULL_SCREEN_LABEL` (`"FPS: {}"`, `"Fullscreen: {}"`) filled in by `on_off(enabled)`, which returns `"On"` or `"Off"`. When clicked, the setting flips and `set_text` shows the new state.
  - Main Menu and Back are created without a position, then placed in the bottom corners by setting `rect.bottomleft` and `rect.bottomright`, `NAVIGATION_BUTTON_MARGIN` (20) pixels from the screen edges.
  - The SFX and music sliders are centered at `SLIDER_X` (640) on `SFX_SLIDER_Y` (475) and `MUSIC_SLIDER_Y` (575), and are `SLIDER_WIDTH` x `SLIDER_HEIGHT` (300x20). Their labels use a separate Silkscreen font at `LABEL_FONT_SIZE` (24), so "Music Volume: 100" fits within the track width. Each label is left-aligned with its track's left edge (`SLIDER_LABEL_X`), and its y is the slider's y minus `SLIDER_LABEL_OFFSET_Y` (45), so a label moves with its slider.
- **`menus/run_end.py`**: `RunEndScreen(game_state_manager, title, title_color, music)`, the end-of-run screen used for both death and finishing ([Architecture](architecture.md)).
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

## `systems/`

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
| `display.py` | Creating the OpenGL window, letterboxing it, and mapping the mouse into game coordinates | `create_window`, `letterbox`, `get_mouse_pos` |
| `renderer.py` | Puts each frame in the window with ModernGL: the world layer (lit, GPU-scaled) and the UI layer ([Architecture](architecture.md)) | `Renderer` (`present`, `set_lights`, `set_blockers`), `submit_world`, `WORLD_SHADER` |
| `lighting.py` | The light look and light list: ambient, light types, flicker, which lights are near the view, the wall mask ([Architecture](architecture.md), "Lighting") | `LIGHT_TYPES`, `flame_position`, `flicker_wave`, `visible_lights`, `light_blockers` |
| `debug.py` | Debug flags | `show_hitboxes`, `toggle_hitboxes` |
| `sound.py` | Loading and playing audio. `play_music(name, loops=-1)` loops forever by default and remembers the track in `_current_music_name`. Asking for the track that is already playing does nothing, so it doesn't restart. `stop_music` clears the remembered name. | `load_sfx`, `load_music`, `play_sfx`, `play_music`, `stop_music`, `set_sfx_volume`, `set_music_volume` |
| `settings.py` | Reading and saving `settings.json` | `load_settings`, `save_settings`, `get_setting`, `set_setting` |

Some systems hold module-level state that is shared by everyone who imports them: `camera.camera`, `debug.show_hitboxes`, `settings.SETTINGS`, `sound.SFX` and `sound.MUSIC`, and the caches in `assets` and `hitbox`. Read flags through the module (`debug.show_hitboxes`), not with `from systems.debug import show_hitboxes`. A `from` import copies the value once at import time and never sees later toggles.

## `ui_components/`

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
- **`inventory_ui.py`**: `InventoryUI(inventory)`, the inventory screen ([One frame](frame.md)). It reads the inventory only for its **shape**, the number of slots and the equipment slot names, so the layout follows the data: changing `new_inventory`'s slot count or `EQUIPMENT_SLOT_NAMES` resizes the window.
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

## `world/`

Everything that makes up a floor: how a map file is read, the tile sprites, and the objects placed on a floor. `states/` holds only screens, and `items/` only item data.

- **`map_loader.py`**: reads the TMX file with pytmx.
  - `load_floor_data(map_path)` returns one dict with everything the run needs.
  - `build_map` draws the floor **and the walls** into a single surface (`map_surface`; walls never change and are always under everything else, so they're drawn once at load instead of every frame) and creates the tile and chest sprites. Its `elif` chain follows the map's layer order (Floor, Walls, decor, doors, then object groups); only the **first** matching branch of an `if`/`elif` chain runs, so a layer name must appear in it once.
  - **Decor** (`build_decor(tmx_data, layer, decor_tiles, lights)`, for `Wall_Decor` and `Floor_Decor`). Each tile's Tiled GID is looked up in `ANIMATED_DECOR_GIDS` (`{91: "torch", 92: "side_torch", 94: "candlestick_1", 96: "candlestick_2"}`). Anything else (banners, rings, webs, rubble, bones, the ladder) becomes a still `DecorTile`, as before. A light GID becomes an `AnimatedDecor` with that animation's frames from `decor_texture_data`, mirrored with `pygame.transform.flip` if the tile was flipped (new surfaces per torch, so the shared cache is never changed), starting on a random frame (`random.randrange`) so neighbouring torches don't flicker in sync, and its flame's position is added to `lights` as `(name, flame_position(name, tile_center, flipped))` (`floor_data["lights"]`, [Data formats](data-formats.md); the loader is the only place that knows whether a torch is mirrored, so it applies the offset). The map keeps the still tiles, so Tiled and `preview_map` show the decor with no special code; the swap only happens on load.
  - **pytmx renumbers tiles.** Each combination of a Tiled GID and its flip flags gets its own *internal* gid, which is what `layer.iter_data()` yields as `(x, y, gid)`. `tiled_gid_and_flip(tmx_data, gid)` translates back with two lookups:

    ```
    tmx_data.tiledgidmap[internal]  → the Tiled GID                (92 for both side torches)
    tmx_data.gidmap[tiled_gid]      → [(internal, flags), …]        one entry per flip variant

    floor 1:  internal 37 → 92, flags all off            left-wall side torch
              internal 38 → 92, flipped_horizontally     right-wall side torch
    ```

    `flipped` is true when the entry with this internal gid has `flags.flipped_horizontally` set. `tmx_data.get_tile_image_by_gid(gid)` gives a still tile's image, already flipped by pytmx.
  - `assign_door_properties(tmx_data, door_tiles)` reads the `Doors` object group: for each door object it builds a `pygame.Rect` from its position and size, and gives every door tile inside it the object's `door_id` and `key` (pytmx reads an object's `<properties>` into the dict `map_object.properties`). `load_floor_data` calls it right after `build_map`. Maps no longer have a logic layer.
  - `build_map` also turns the `Crates` object group into `Crate` sprites (`floor_data["crates"]`), placed by each object's x and y like chests.
  - `find_player_spawn` and `find_enemy_spawns` read spawn objects.
  - `find_exit` returns a `pygame.Rect` for the object named `Exit`, or `None` if there isn't one.
  - `find_placed_items` returns `(item_id, center)` pairs for the objects in the `Items` object group, stored as `floor_data["placed_items"]`. Each object is named by its item id. It loops over `tmx_data.objectgroups` to find the group by name, so a map with no `Items` group just has no placed items (`get_layer_by_name` would crash instead). The center is worked out as `(x + width / 2, y + height / 2)`, which works for both kinds of object: Level One's 10×8 rectangles drawn in Tiled, and the converter's 0-sized points, whose center is just their x and y.
- **`tiles.py`**: `WallTile`, `DecorTile`, `AnimatedDecor` and `Door` sprites. `AnimatedDecor(groups, frames, pos, start_index)` is a looping decor tile: its animation dict holds the one strip under the name `"loop"`, starts at `start_index`, and plays at `DECOR_ANIMATION_SPEED` (6 fps; at the default 10, a 4-frame flame loops 2.5 times a second and looks frantic). `update(dt)` advances it. Each draws itself offset by the camera. Doors carry a `door_id` and a `key` (the item id that opens them, `silver_key` or `gold_key`), both set by `assign_door_properties`.
- **`decor_texture_data.py`**: `decor_texture_data`, the four light strips (`torch`, `side_torch`, `candlestick_1`, `candlestick_2`), 16×16 frames, 4 each, from `Assets/Objects/<name>_strip.png`.
- **`floor.py`**: `Floor(map_path, item_database)`, everything on one map. `Run.load_floor` builds a new one for each floor, so its state starts clean by construction.
  - **What it holds**: the map data from `load_floor_data` (`map_surface`, `decor_tiles`, `wall_tiles`, `door_tiles`, `chests`, `crates`, `exit_rect`, `player_spawn`, `lights`); `ground_items`, starting with the placed items from the map's `Items` layer (each a `GroundItem` of quantity 1, looked up in the item database, so an unknown id is a `KeyError` at load time, the right moment to find a typo); an empty `particles` list; the `enemies`; `exit_requested` (`False`); `edge_walls`; and the derived `solid_rects`, `light_blockers` and `padlocks`.
  - **`edge_walls(wall_tiles)`** (a module function) keeps only the walls next to open space, including diagonally. Floor 1's walls fill the whole map, but only 614 of its 2570 touch a floor tile: anything moving hits one of those first, so the rest can never be touched and are left out of collision. Light still uses every wall (`light_blockers`), because the shader needs the full map.
  - **`update(dt, player)`** runs the floor's frame, after the player has moved: if the player is rolling, `break_touched_crates(player)`; every enemy moves (`enemy.update`); `resolve_enemy_contacts(player)` resolves touches between the player and living enemies (roll hits, touch damage, the `roll_hit` sound) and calls `start_dying()` on an enemy at 0 HP; `resolve_enemy_strikes(player)` checks every living enemy's swing; `separate_enemies(self.enemies, player, self.solid_rects)` pushes overlapping bodies apart; `remove_dead_enemies()` rolls the `loot_table` of each enemy whose death animation has finished, spawns the drops at its body's center and removes it (looping over `list(self.enemies)`, a copy, so removing is safe); then the decor animates (`decor_tiles.update(dt)`: `Group.update` calls `update(dt)` on every sprite, and a `DecorTile` inherits `Sprite.update`, which accepts any arguments and does nothing, so still and animated decor share one group with no checks), the ground items animate, `update_crates` finishes breaking crates, and `update_particles` moves the debris.
  - **`player_walls(player)`** is what blocks the player this frame, passed by the run to `player.update`: while the player is rolling only `solid_rects`, otherwise `solid_rects` plus the `rect` of every solid enemy (`is_solid()`) that **isn't already overlapping** the player ([One frame](frame.md), step 5). Like everything passed as `walls`, it's a list of plain rects.
  - **`draw(surface, player, highlight=None)`** draws the world in order: the map surface (floor and walls), then decor (on top of the walls, since torches, banners and rings sit on wall tiles), then doors, a padlock on each locked door group, crates, ground items and chests, the interaction outline (`highlight` is `None` or a `(sprites, color)` pair from the run; nothing is drawn for an empty list), the player and enemies sorted by `rect.y` so whoever is lower is drawn in front, then the particles on top. Off-camera sprites are skipped with `is_on_screen`.
  - **`highlighted_sprites(target)`** says what to outline for an interaction target: every door tile with the target door's `door_id` (unlocking works on the whole group, so the outline does too), the exit's ladder (the decor tiles inside `exit_rect`, since the exit has no sprite of its own), or just the chest or item. The run chooses the color; the floor knows its doors and ladder.
  - Helpers:
    - `unlock_door(door_id)` removes every door tile with that id.
    - `refresh_solid_rects()` rebuilds `solid_rects`: the `rect`s of the edge walls, remaining doors and unbroken crates.
    - `refresh_light_blockers()` rebuilds `light_blockers` from every wall and the remaining doors ([Architecture](architecture.md), "Lighting").
    - `refresh_padlocks()` rebuilds `padlocks`, a list of `(key, center)` pairs, one per locked door group. It groups the door tiles by `door_id` with `doors_by_id.setdefault(door.door_id, []).append(door)` (`setdefault` returns the list stored under a key, creating an empty one the first time: the usual "group things by a key" pattern), then takes each group's center from `rects[0].unionall(rects[1:])`, the rect around its tiles: the seam of a double door, or the middle of a vertical one. The padlock art is loaded in `__init__` into `padlock_images` (cached by `load_image`, so each file is read from disk once) from `PADLOCK_IMAGE_PATHS`, keyed by key item id, the same value as `door.key`.
    - **Crates.** `refresh_solid_rects()` adds every crate still in `crates` to `solid_rects`, so crates block the player **and** enemies like walls. While the player is rolling, `update` calls `break_touched_crates(player)`: any crate touching the player's rect grown by `CRATE_TOUCH_MARGIN` (2 pixels) starts breaking, drops its `CRATE_LOOT` at its center, and, since a breaking crate isn't solid, `refresh_solid_rects()` runs once if anything broke, so the roll carries straight through. The margin is needed because a solid crate pushes the player out, so the two never actually overlap; the grown rect catches "pressed right up against it". Walking into a crate just bumps it: rolling is the only way to break one, the same rule as damaging enemies. `update_crates(dt)` advances every crate and, for each one with `done_breaking`, emits a `CRATE_DEBRIS` burst at its center and kills it; it loops over `crates.sprites()`, a copy, so removing crates mid-loop is safe.
    - `solid_rects`, `light_blockers` and `padlocks` are all derived from `door_tiles`, so all three are rebuilt together, in `__init__` and in `unlock_door`, whenever the doors change. Forgetting one leaves a padlock floating where an opened door used to be, or a doorway that still blocks light.
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

## `tools/`

- **`line_counter.py`**: see [Tooling](tooling.md).
- **`make_sprite.py`**: see [Tooling](tooling.md).
- **`preview_map.py`**: see [Tooling](tooling.md).
- **`ascii_to_tmx.py`**: see [Tooling](tooling.md).
- **`make_strip.py`**: see [Tooling](tooling.md).
