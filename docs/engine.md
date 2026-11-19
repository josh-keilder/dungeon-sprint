# Engine reference

Every module under `engine/`, by folder. Nothing here imports the game: anything game-specific is passed in (see [Design rules](design-rules.md)). The game's side is in [Game reference](game.md).

## `core/`

- **`game_loop.py`**: `GameLoop(renderer, screen_size, state_manager, frame_rate, cursor_image=None, fps_setting=None)`, the frame loop: events, `dt`, the current screen, the cursor and FPS counter on top, then `renderer.present` and `flip`. `run()` enters the first screen and loops until the window closes. Described in [Architecture](architecture.md).
- **`state_manager.py`**: `GameStateManager(start_state)`, the screens by name and which one is current: `add_state`, `get_state`, `set_state` (calls the new state's `enter()`; an unknown name raises `ValueError`), `get_previous_state`, `go_back`. See [Architecture](architecture.md), state flow.
- **`timer.py`**: countdown timers as `{"time_left", "duration"}` dicts counted down by `dt`. `new_timer`, `start_timer(timer, duration)` (remembers the duration), `advance_timer`, `is_running`, `time_left`, and the two fade helpers: `time_elapsed(timer)` (seconds since it started) and `fraction_left(timer)` (1.0 just started, 0.0 finished or never started).
  ```
  fraction_left = time_left ÷ duration          (0.0 when duration is 0: a timer that never started)
  time_elapsed  = duration − time_left
  fade alpha    = round(255 × fraction_left)    (the hurt vignette, the floor transition)
  ```
- **`settings.py`**: `SETTINGS`, the current settings. `load_settings(defaults, file_path)` starts from the game's defaults and merges the saved values over them, keeping only keys that exist in the defaults, so a setting removed from the game is dropped from the file on the next save. `get_setting`, `set_setting` (in memory only) and `save_settings` (writes the file; Options calls it on leaving the menu). The file is the game's `settings.json`.
- **`assets.py`**: loading and caching images and animations. `load_image`, `load_animations`, `slice_frames`, `crop_center`, `add_flipped_left`.
- **`debug.py`**: debug flags. `show_hitboxes`, `toggle_hitboxes`.

## `graphics/`

- **`animation.py`**: animation dict rules. `new_animation`, `set_animation`, `advance_animation`.
- **`blink.py`**: when a blinking sprite is hidden. `is_blink_hidden(invulnerability, blink_interval)`.
- **`camera.py`**: a camera is a `Rect` the size of the world canvas, not the screen, so a bigger `GAME_SCALE` means fewer tiles in view. The run owns its camera; the functions take it: `new_camera(view_size)`, `center_camera(camera, pos)`, `is_on_screen(camera, target_rect)`, and the two drawing helpers every world sprite uses, `world_to_screen(camera, pos)` and `rect_to_screen(camera, rect)` (a world position or rect minus the camera's top-left).
- **`display.py`**: `create_window(screen_size, fullscreen, title)` opens the OpenGL window and remembers the game's drawing size; `letterbox(window_size)`; `get_mouse_pos()`. See [Architecture](architecture.md).
- **`lighting.py`**: `MAX_LIGHTS` (32), `FLICKER_SPEEDS`, `flame_position(light_type, tile_center, flipped)`, `visible_lights(lights, light_types, camera, time)`, `light_blockers(map_size, tiles, tile_size)` and their helper `flicker_wave`. The light **look** (`LIGHT_TYPES`, ambient, bands) is game data in `game/data/light_types.py`. See [Architecture](architecture.md), "Lighting".
- **`masks.py`**: pixel-perfect masks and outlines. `images_overlap(first_image, first_pos, second_image, second_pos)` takes images and positions rather than sprites, since an enemy's art isn't at its `rect`. `get_mask`, `images_overlap`, `draw_hitbox`, `draw_highlight`, `grow_mask`.
- **`overlay.py`**: `new_overlay(size, color, alpha=255)`, a screen-sized `SRCALPHA` sheet of one color, for dimming or fading the screen: the pause menu, the end screens, the inventory and the floor transition use it.
- **`particles.py`**: short-lived visual effects as plain dicts in a list. `emit_burst(particles, center, preset, direction=None)` adds `preset["count"]` particles flying within `spread` degrees of `direction` (any way when it's `None`); `update_particles` moves and slows them and drops the expired ones; `draw_particles(surface, particles, camera)` shrinks each as it ages. The engine has no presets: a preset is the game's data (`game/data/particle_presets.py`), a dict of `count`, `colors`, and `(low, high)` ranges for `speed`, `lifetime` and `size`, plus `drag` and `spread` ([Data formats](data-formats.md)).
- **`renderer.py`**: `Renderer(screen_size, world_size, world_scale, tile_size, lighting)` with `present(ui_surface)`, and the module function `submit_world(world_surface, camera_offset, lights, blockers)`. Puts each frame in the window with ModernGL: the world layer (lit, GPU-scaled) and the UI layer. See [Architecture](architecture.md).
- **`shake.py`**: camera shake as a dict: `new_shake()`, `start_shake(shake, strength)` (keeps the stronger of the two, so a weak shake never cuts a strong one short), `update_shake(shake, dt)`. The strength fades by `SHAKE_FADE` (20 world pixels a second), and the offset jumps to a new random spot every `SHAKE_STEP` (1/30 s), so it looks the same at any frame rate. The game's `HitFeedback` owns one and adds `shake["offset"]` to the camera's center.

## `physics/`

- **`movement.py`**: velocity steering and wall collision. `steer(velocity, direction, max_speed, acceleration_rate, deceleration_rate, grip, dt)` returns the new velocity; `move_and_collide(rect, displacement, walls)` moves one axis at a time and returns `(hit_x, hit_y)`; `move_knockback(rect, velocity, decay_rate, walls, dt)` pushes a body, drops the push on each axis that hit a wall, and returns the slowed velocity (the player and enemies both use it); helpers `approach_fraction` and `decay_velocity` (below `STOP_SPEED`, 1 px/s, a body snaps to a stop).
- **`collision.py`**: `push_out(rect, other_rect)`, the shortest push that separates two overlapping rects (or `None`); `has_line_of_sight(start, end, walls)`, false when a wall near the line (`SIGHT_SEARCH_MARGIN`, 64 px) crosses it; `edge_walls(wall_tiles, tile_size)`, only the walls next to open space, including diagonally. Floor 1's walls fill the whole map, but only 614 of its 2570 touch a floor tile, so the rest are left out of collision.

## `io/`

- **`input.py`**: helpers for turning keys into actions; the game's bindings live in `game/rules/input.py`. `move_direction(keys_held, left, right, up, down)` is a unit vector from four held keys (zero when none or opposite ones are held); `pressed_actions(keys_just_pressed, bindings)` turns `{action: key}` into `{action: pressed this frame}`; `mouse_click_pos(button=0)` is where the button was just pressed, in game pixels, or `None`.
- **`sound.py`**: loading and playing audio. `play_music(name, loops=-1)` loops forever by default and remembers the track in `_current_music_name`. Asking for the track that is already playing does nothing, so it doesn't restart. `stop_music` clears the remembered name.. `load_sfx`, `load_music`, `play_sfx`, `play_music`, `stop_music`, `set_sfx_volume`, `set_music_volume`. `load_sfx(folder)` and `load_music(folder)` load every `.wav` and `.ogg` in the folder the game passes, keyed by file name without its extension.

## `ui/`

- **`theme.py`**: the look every widget reads. `_theme` holds plain defaults (pygame's built-in font, white text, a scale of 1, no sounds); the game calls `set_theme(...)` once at startup with its own values, and a misspelled key raises `KeyError` instead of doing nothing. `get_theme(key)` reads a value; `play_theme_sound(key)` plays `hover_sound` or `click_sound` if the game set one. Keys: `font_path`, `font_size`, `text_color`, `text_outline_color`, `hover_color`, `pixel_scale` (text snaps to it, outlines are one step wide), `button_outline_color`, `slider_empty_color`, `hover_sound`, `click_sound`, and the three `health_bar_*` colors. A widget reads the theme when it's built or drawn, never in a default argument ([Design rules](design-rules.md)).
- **`title.py`**: `make_title(text, font_size, color, screen_width, y)` returns a title image and its position, centered across the screen in the theme's font. The main menu, Options and the end screens use it.
- **`button.py`**: `Button(image, pos=(0, 0), outline_color=None, hover_image=None)`. `image` can be any surface, including text from `font.render`. Plays the theme's `hover_sound` when the mouse enters. While hovered, it draws `hover_image` instead of `image` if it was given one; otherwise it draws an outline in `outline_color` (the theme's `button_outline_color` by default) around `image`. The outline is drawn first and the image on top of it, so only the ring just outside the shape shows. Drawn the other way round, the outline covers thin shapes such as letters. On a left click it plays the theme's `click_sound` and sets `clicked_this_frame`, which `is_clicked()` returns. `set_image(image, hover_image=None)` swaps both pictures and rebuilds the outline. The new rect keeps the old `topleft`, so text that changes width would drift off center. `TextButton.set_text` corrects for that.
- **`text_button.py`**: `TextButton(text, font, midtop=(0, 0), text_color=None, hover_color=None)`, with the theme's `text_color` and `hover_color` by default, a `Button` subclass whose picture is rendered text.
  - On hover the text turns `hover_color` instead of being outlined: it renders a second copy of the text in `hover_color` and passes it to `Button` as `hover_image`. A thin 1 px outline was hard to see at the game's 3× pixel size, and a solid 3 px outline merged neighbouring letters together, while a recolor keeps every letter crisp.
  - The font is passed in rather than created here. Each state creates its fonts once in `__init__`, because building a `Font` reads the font file from disk.
  - It is placed by its `midtop` point (the middle of its top edge), so passing `(screen width // 2, y)` centers it. For any other placement, leave out `midtop` and set another anchor on `rect` afterwards, such as `rect.bottomleft`.
  - `set_text(text)` re-renders the text and its hover copy, then puts `midtop` back where it was, so a toggle like "FPS: On"/"FPS: Off" stays centered when its width changes.
- **`button_outline.py`**: `make_outline` builds a one-pixel outline surface from an image's mask. It outlines each separate shape in the mask (`mask.connected_components()`), because `mask.outline()` alone only traces the first shape, which for text would be just the first letter. Holes inside a shape, like the inside of an "A", are not outlined. `draw_outline` blits it shifted one pixel in each direction to make a thicker outline.
- **`slider.py`**: `Slider`, a draggable knob on a track between `min_value` and `max_value`. `pos` is the **center** of the track, not its top-left, so the track's left edge is `pos[0] - size[0] // 2`. The part left of the knob is drawn in `track_color` and the rest in the theme's `slider_empty_color`. The knob is drawn in `knob_color`, or the theme's `hover_color` while hovered or dragged, the same as the buttons. The options menu uses a `PALETTE_STEEL` fill and a `PALETTE_ICE` knob, so the knob stands out from the fill next to it. The track and knob have rounded corners (`TRACK_CORNER_RADIUS` 5, `KNOB_CORNER_RADIUS` 3). The knob is `KNOB_WIDTH` (20) pixels wide and sticks out `KNOB_OVERHANG` (5) pixels above and below the track. `get_current_value()` returns the value as an int.
- **`text_label.py`**: `TextLabel`, rendered text at a position (its top-left), at the theme's `font_size` unless told otherwise. `update_text` re-renders it, but does nothing if the text hasn't changed, so calling it every frame is cheap; `__init__` renders through `update_text` too, so there is one render path. With `outline_color` set (it defaults to `None`, so existing labels are unchanged), a copy of the text in that color is drawn one pixel-grid step (the theme's `pixel_scale`) up, down, left and right first, then the text on top, giving it a dark rim that reads on any background:

  ```
     ░░░
    ░▓▓▓░      ▓ = the text
    ░▓░░░      ░ = the same text in the outline color, drawn 3 px up, down, left and right first
    ░▓▓▓░
     ░░░
  ```

  Text is drawn without anti-aliasing for a pixel look. With no `font` given, it builds Silkscreen from `FONT_PATH` at `font_size` (default 24, on the 3× grid), in `color` (default `PALETTE_STEEL`). Pass a ready-made `font` to share one font object between labels, in which case `font_size` is ignored. The menus, HUD and inventory pass their own fonts; the FPS counter uses the default.
- **`text_layout.py`**: shared helpers for placing text by its **visible ink** (`get_bounding_rect()`) rather than by its surface. A rendered surface is taller than its letters, because fonts reserve space above and below them (for Silkscreen at 24 the surface is 31 px tall but the digits only run from y 10 to 25), so lining up surfaces would leave text visibly off-center.

  ```
  snap_to_grid(value)                  = value // pixel_scale × pixel_scale      (the theme's pixel_scale)
  centered_text_x(surface, center_x)   = snap(center_x − ink center x)
  centered_text_y(surface, center_y)   = snap(center_y − ink center y)
  bottom_right_text_pos(surface, right, bottom) = (right − ink right, bottom − ink bottom)
  ```

  Used by the HUD (the floor panel, the prompt, the quick-slot counts), the inventory (stack counts), the floor card in `floor_transition.py`, and the FPS counter. Each used to compute the ink rect and snap it by hand; one helper per kind of placement keeps the formula in one place.
- **`panel.py`**: `make_panel(frame_image, size, corner_size)` builds a framed panel surface of any size from the small frame image, using **9-slice** scaling. `size` is in screen pixels. Build each panel once (for example in `__init__`) and blit it every frame.

  ```
  ┌────┬─────────┬────┐
  │ TL │   top   │ TR │   corners: drawn as they are, never stretched
  ├────┼─────────┼────┤
  │left│ center  │right│  edges: stretched along their length only
  ├────┼─────────┼────┤   center: stretched both ways (it's a solid fill)
  │ BL │ bottom  │ BR │
  └────┴─────────┴────┘
  ```

  The corner size `c` is `corner_size`, in art pixels; the game passes `PANEL_CORNER_SIZE` (4), which must match the border of the `panel_frame` sprite in `tools/make_sprite.py`. The art keeps all its detail in the outer 4 pixels, so each edge is the same color all the way along and is safe to stretch. Each of the 9 pieces is a (cut from the frame, drawn on the panel) pair of rects:

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

  Every piece goes through the same loop: cut it with `subsurface` (a view into the image, no copy), resize it to its target with `pygame.transform.scale` (corners resize to their own size, so they're unchanged), and blit it. The panel is built at 1× (`size // pixel_scale`, the theme's) and scaled up by `pixel_scale` at the end, so its pixels are the same 3×3 blocks as the world. A size that isn't a multiple of 3 is rounded down (100 becomes 99), and the smallest panel is `2 × c` art pixels (24 screen pixels) each way.
- **`health_bar.py`**: `draw_health_bar(screen, health, x, y, width, height)`, used for enemy health bars (the player's health is drawn by the HUD). It draws, in order: a border (the theme's `health_bar_border_color`; the game uses `PALETTE_VOID`) `HEALTH_BAR_BORDER` (1) pixel bigger on every side, so the bar reads over floors, walls and other enemies; the full-width empty bar (`health_bar_empty_color`, `PALETTE_SHADOW`); and the fill (`health_bar_fill_color`, `PALETTE_BLOOD`). The fill is always blood red, like the player's bar, so health has one color meaning throughout the game; the bar's length already shows how hurt the enemy is. A living enemy always shows at least 1 pixel of fill, because at 16 pixels for 100 HP each pixel is worth about 6 HP, and an enemy with 3 HP left would otherwise look dead:

  ```
  fill width = int(width × current ÷ max), at least 1 while current > 0
  ```

  Enemy bars are drawn on the world surface, so every value is in art pixels and lands on whole art pixels before the world is scaled up. Unlike the HUD, which draws straight onto the screen, they need no grid snapping.
- **`fps_counter.py`**: `FpsCounter`, the debug FPS readout: an outlined `TextLabel` in the theme's default font and color, with no panel, because it's a debug readout rather than part of the game. `update(dt, fps)` refreshes the text every `FPS_REFRESH_INTERVAL` (0.5 s), since a number changing every frame is unreadable, and re-positions it by its ink: right-aligned `FPS_MARGIN` (12) from the screen's right edge, so a wider number grows to the left, and vertically centered on `FPS_CENTER_Y` (21). `draw(screen)` draws the label.

  ```
  x = screen_width − FPS_MARGIN − ink right        (screen_width is passed to FpsCounter)
  y = centered_text_y(label, FPS_CENTER_Y)
  ```
- **`cursor.py`**: `Cursor`, the custom mouse cursor, centered `CURSOR_OFFSET` (5) pixels down and right of the real mouse position.
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

## `gameplay/`

- **`health.py`**: health dict rules. `new_health`, `take_damage`, `heal`, `is_dead`, `set_max_health`.
- **`stats.py`**: base stats plus equipment bonuses. `compute_stats`.
- **`inventory.py`**: inventory dict rules. `new_inventory(slot_count, equipment_slot_names)` (the game passes its slot names), `add_item`, `remove_item`, `has_item`, `count_item`, `can_equip`.
- **`items.py`**: an item template or stack (the game's sprites that put items in the world are in `game/world/objects.py`):
  - `Item`: an item template or stack. It has `id`, `name`, `animations`, `description`, `quantity`, `max_stack`, `animation_speed`, `value_text` and `image` (first idle frame). `clone()` is a shallow copy, so a clone has its own `quantity` but shares the same images.
  - `EquipmentItem(Item)`: adds `slot` and `bonuses`, and always has `max_stack` 1.
- **`loot.py`**: rolls a loot table. `roll_loot`.

## Shared module state

Some modules hold state shared by everyone who imports them: `settings.SETTINGS`, `sound.SFX` and `sound.MUSIC`, `debug.show_hitboxes`, the theme in `theme._theme`, the submitted world in `renderer._world`, and the image and mask caches in `assets` and `masks`. Read flags through the module (`debug.show_hitboxes`), not with `from engine.core.debug import show_hitboxes`: a `from` import copies the value once at import time and never sees later toggles.

