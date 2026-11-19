# Architecture

## Startup and the main loop

`main.py` is Dungeon Sprint's setup, as small functions; the loop itself is the engine's `GameLoop`. `main()` runs in this order, and the order matters:

1. `pygame.init()`, then `settings.load_settings(DEFAULT_SETTINGS, SETTINGS_FILE_PATH)` reads `settings.json`. It must run before the window is created, because the window needs the fullscreen setting.
2. `apply_theme()` calls `set_theme(...)` with the game's font, pixel scale, colors and button sounds. It must come before any screen is built, because every widget reads the theme when it's created ([Engine reference](engine.md), `theme.py`).
3. `create_window((SCREEN_WIDTH, SCREEN_HEIGHT), fullscreen, WINDOW_TITLE)` opens an **OpenGL** window (`pygame.OPENGL | pygame.DOUBLEBUF`; in fullscreen, `FULLSCREEN` at the desktop's own resolution, `(0, 0)`) and remembers the game's drawing size for letterboxing. It must exist before any image is loaded, because `load_image` calls `convert_alpha()`, which needs a display.
4. `make_renderer()` builds the `Renderer` (it needs the window's OpenGL context), passing the screen, world and tile sizes, the world scale, and the light look from `game/data/light_types.py`.
5. `load_sound()` loads every sound effect and music track from `SFX_FOLDER` and `MUSIC_FOLDER` and applies the saved volumes. No music starts here.
6. `build_screens()` creates a `GameStateManager` starting on `"main_menu"` and registers the screens, built in this order: `MainMenu` as `"main_menu"`, `OptionsMenu` as `"options"`, `Run` as `"run"`, and `RunEndScreen` twice, as `"game_over"` ("You Died!", red, `GAME_OVER_MUSIC`) and `"run_complete"` ("You Escaped!", green, no music of its own).
7. `GameLoop(renderer, screen size, manager, FRAME_RATE, cursor_image=..., fps_setting="fps_enabled")` is built with the cursor art (`Assets/Cursors/01.png` at half scale), and `game_loop.run()` starts it. When it returns, `pygame.quit()` closes everything.

**`GameLoop`** (`engine/core/game_loop.py`) knows nothing about Dungeon Sprint. Its `__init__` makes `ui_surface`, a transparent screen-sized `SRCALPHA` surface every frame is drawn on, the clock, the FPS counter, and (when given cursor art) hides the system mouse and builds a `Cursor`. `fps_setting` is the **name** of the setting that shows the FPS counter, so the engine never needs to know the game's setting names. `run()` calls the first screen's `enter()` (the first state is set directly in `GameStateManager.__init__`, not through `set_state`, so its `enter()` has to be called by hand; this is what starts the menu music), then loops `update()` and `draw()` until `running` is false.

**`update()`:**
- Reads the event queue. A `pygame.QUIT` event (closing the window, or the Exit button) stops the loop.
- Computes `dt`, the seconds since the last frame, from `clock.tick(frame_rate)`. `FRAME_RATE` is 240. Everything that moves or counts down is multiplied by `dt`, so the game runs at the same speed at any frame rate.
- Calls `update(dt)` on the current state, then updates the cursor and the FPS counter.

**`draw()`:**
- Clears `ui_surface` to fully transparent and passes it to the current state's `draw(screen)`. States never touch the window: in an OpenGL window, the display surface can't be drawn on with pygame, so `screen` is always this offscreen surface.
- Draws the FPS counter if its setting is on, then the cursor (last, so it is on top of everything).
- `renderer.present(ui_surface)` puts the frame in the window (below), then `pygame.display.flip()` shows it: an OpenGL window draws into a back buffer and swaps it to the front. (`pygame.display.update()` is for software windows and can't be used with `OPENGL`.)

**The renderer** (`engine/graphics/renderer.py`, ModernGL). The game always draws in a 1280×720 space, and all screen coordinates in the code are in it. Getting that onto the real window is the renderer's job (it used to be `pygame.SCALED`, which can't be combined with OpenGL). A frame is two **layers**, each a **texture** (an image on the GPU) drawn on a **quad** (a rectangle):

```
Run.draw ── submit_world(world, camera offset, lights, blockers) ──▶ world layer: 427×240 texture, lit, scaled ×3 by the GPU   (only if submitted)
every state, FPS, cursor ── ui_surface ─────────────────────────────▶ UI layer:    1280×720 texture with alpha, on top
```

- **`submit_world(world_surface, camera_offset, lights, blockers)`** is a module-level function: `Run` doesn't hold the renderer, so it hands its world over through the module, like `sound.play_sfx`. Everything the world layer needs that frame is kept in one slot, `_world`, a tuple: the surface, `camera.topleft`, the visible lights and the floor's light blockers (see **Lighting** below). `present` uses it once and clears it (`_world = None`), so a menu frame with no run behind it shows only its UI. The pause menu and end screens call `run.draw`, which submits the world, and their dim overlay is drawn on the UI layer, so it darkens the world underneath.
- **A quad** is 4 corners drawn as a `TRIANGLE_STRIP` (corners 1-2-3 make one triangle, 2-3-4 the other). Each corner gives its position on screen and the point of the texture it shows. The **vertex shader** runs once per corner and passes `uv` on; the **fragment shader** runs once per pixel and reads the texture's color at that `uv`, interpolated between the corners:

  ```
  screen (OpenGL)          texture (uv)
  (-1, 1)───(1, 1)         (0,0)─────(1,0)        u: left → right
     │  ╲      │             │         │          v: top → bottom: the first row uploaded is row 0,
  (-1,-1)───(1,-1)         (0,1)─────(1,1)            and pygame's first row is the top
  ```

  There are two **programs** (a vertex shader and a fragment shader compiled together): `ui_program` (`TEXTURE_SHADER`, which just shows the texture) and `world_program` (`WORLD_SHADER`, which also lights it). `make_quad(program, uv_right, uv_bottom)` builds a quad for one of them from a flat `array("f", ...)` of 4 corners × (x, y, u, v), marked `# fmt: skip` so Black keeps it as 4 rows; `"2f 2f"` tells the GPU each corner is two floats for `in_position`, then two for `in_uv`.
- **The sizes come from the game.** `Renderer(screen_size, world_size, world_scale, tile_size, lighting)` is built by `main.py`; `lighting` is a dict of the light look (`ambient`, `max_light`, `bands`, and `void_color`, the wall art's empty color, 0–255 RGB). The world is `world_size` × `world_scale` = 427 × 3 = 1281 pixels wide, one more than the screen, so `__init__` works out how much of the world texture fits: the world quad shows it only up to `uv_right` = `screen width / (world width × world_scale)` = 1280 / 1281 of its width, so one world pixel stays exactly 3 screen pixels. (`uv_bottom` is 720 / 720 = 1.)
- **Textures** use `NEAREST` filtering, so scaled pixels stay crisp blocks instead of blurring. The UI layer is blended with `SRC_ALPHA, ONE_MINUS_SRC_ALPHA`, the normal "transparent over opaque" rule.
- **Uploading.** Each frame both surfaces are copied to their textures (`texture.write`). The world uses `pygame.image.tobytes(surface, "RGBA")`, which converts its pixels into bytes in a known order. For the UI that conversion was the slowest part of the frame, so it's skipped: the UI surface's masks are `R = 0xFF0000, G = 0xFF00, B = 0xFF, A = 0xFF000000`, which on a little-endian PC means each pixel's bytes sit in memory as **B, G, R, A**. `surface.get_view("1")` exposes that memory with no copy, and `ui_texture.swizzle = "BGRA"` tells the texture which byte is which channel, so the GPU reorders them for free. The world keeps `tobytes`: its surface has no alpha, so its fourth byte is padding, and reading that as alpha could make the world see-through; at 427×240 the conversion only costs 0.25 ms.

  ```
  measured per frame (frame budget at 240 fps: 4.17 ms)
  tobytes(ui_surface, "RGBA") + write   2.18 ms     ← before
  get_view("1") + write, BGRA swizzle   0.45 ms     ← now
  old CPU path: scale_by(world, 3)      1.02 ms     ← gone, the GPU scales
  ```

- **`present(ui_surface)`** clears the whole window to black, sets the **viewport** (the part of the window OpenGL draws into) to the letterboxed game area, then draws the world layer (if submitted: camera offset, `set_blockers`, `set_lights`, upload, draw) and the UI layer.

**Lighting** (`engine/graphics/lighting.py` for flicker, the visible-light list and the wall mask, `WORLD_SHADER` in `engine/graphics/renderer.py` for the drawing, and `game/data/light_types.py` for the look: `LIGHT_TYPES`, `AMBIENT_LIGHT`, `MAX_LIGHT`, `LIGHT_BANDS`). Mood lighting: unlit areas are dimmed a little and cooled, and torches, candlesticks and the player add colored glows on top. Everything stays visible.

```
Floor ── lights: (name, flame position) per torch / candlestick      light_blockers: 1 byte per map tile
   │                                                                   (1 = wall or closed door)
Run.draw ── visible_lights([player light] + floor.lights, LIGHT_TYPES, camera, time)
   │          player light first, then the floor's lights near the view (≤ MAX_LIGHTS = 32),
   │          each as (position on the world surface, radius, color × intensity × flicker)
   ▼
submit_world(world_surface, camera.topleft, lights, floor.light_blockers)
   ▼
renderer ── set_blockers: the mask becomes a small integer texture (72×51 on floor 1), only rebuilt when it changes
            set_lights:   the lights become uniform arrays
            WORLD_SHADER: lights every world pixel
```

- **Uniforms** are values Python hands to a shader; they're the same for every pixel of one draw. Settings that never change (`world_size`, `tile_size`, `ambient`, `void_color`, `max_light`, `bands`, and which texture slot is which: `image` 0, `blockers` 1) are set once in `Renderer.__init__`. Per frame: `camera_offset`, `light_count` and the arrays `light_positions`, `light_radii`, `light_colors`. GLSL arrays have a fixed size, so `set_lights` always sends `MAX_LIGHTS` entries, padding the unused ones (radius `1.0`, never 0, so a slip could never divide by zero), and the loop stops at `light_count`. The arrays' size comes from Python: the shader source starts with `f"#define MAX_LIGHTS {MAX_LIGHTS}\n"`, so the number is defined once, in `engine/graphics/lighting.py`; the rest of the shader is a plain string, because GLSL's `{ }` would clash with an f-string.
- **Per world pixel**, the shader works out (`pixel` is the center of the world pixel being drawn, `floor(uv × world_size) + 0.5`, so light is computed once per **art** pixel and stays in crisp 3×3 blocks):

  ```
  light   = AMBIENT_LIGHT + Σ  color_i × falloff_i            (for each light that reaches the pixel)
  falloff = clamp(1 − distance(pixel, position_i) / radius_i, 0, 1)        linear: 1 at the flame, 0 at the radius
            stepped when LIGHT_BANDS > 0:  floor(falloff × LIGHT_BANDS) / LIGHT_BANDS
  pixel   = art color × min(light, MAX_LIGHT)

  AMBIENT_LIGHT (0.78, 0.78, 0.86): unlit art shows at 78%, blue a little higher, so the dark is slightly cool
  MAX_LIGHT 1.25: lights can brighten art up to 25% above its own colors, and no further
  ```

  `LIGHT_BANDS = 0` is smooth (the default); 5 gives visible rings (`0.93 → 0.8`, `0.55 → 0.4`, `0.15 → 0`, the outer fifth unlit). Linear falloff was chosen over squared: with squared, most of each radius was too dark to read.
- **Light types** (`LIGHT_TYPES`): `radius` in world pixels, `color` as 0–1 RGB, `intensity`, the flame's `offset` from the tile center, and `flicker`. Torches are warm orange (`(1.0, 0.62, 0.32)`, radius 90, side torches 72), candlesticks a softer yellow (`(1.0, 0.85, 0.50)`, radius 56), and the player a faint cool light (`(0.80, 0.88, 1.0)`, radius 64, intensity 0.3). `flame_position(light_type, tile_center, flipped)` adds the type's offset (a side torch's flame leans left; on a mirrored, right-wall torch the x offset flips), so the loader records where the flame is, not the tile's center.
- **`visible_lights(lights, light_types, camera, time)`** takes `(type name, position)` pairs and the game's `LIGHT_TYPES`, and keeps the lights inside the camera rect grown by the largest radius on every side (a torch just off-screen still lights the edge of the view), turns their positions camera-relative (the shader works in world-surface pixels), and multiplies each color by its intensity and flicker, so the shader needs one color per light. `Run.draw` puts the player's light (`("player", player center)`) first in the list, so it's never the one cut off at `MAX_LIGHTS`.
- **Flicker.** Every frame each flame's intensity is scaled by `1 + flicker × wave`:

  ```
  wave  = 0.6 × sin(time × 7.0 + phase) + 0.4 × sin(time × 12.7 + phase × 2.3)       → −1 … 1
  phase = x × 0.37 + y × 0.73          from the light's position: fixed, different for each light

  torch flicker 0.09 → 91% to 109%      candlestick 0.06 → 94% to 106%      player 0 → steady
  ```

  Two sine waves at speeds that don't divide evenly (`FLICKER_SPEEDS`) add up to a wobble that never quite repeats, and the position-based phase keeps neighboring flames out of step. Only the intensity flickers, not the radius, so the `visible_lights` area stays exact. `time` is `pygame.time.get_ticks() / 1000`, the game clock rather than `run_time`, so flames keep moving behind the pause menu.
- **Walls block light.** `refresh_light_blockers()` (`Floor`) builds `light_blockers(map_size, tiles, TILE_SIZE)` from every wall and door tile: `((columns, rows), bytes)`, one byte per tile, row by row. The renderer turns it into a one-channel unsigned-integer texture (`dtype="u1"`, read with a `usampler2D` and `texelFetch`: whole numbers by tile, no filtering, no UV math; integer textures must use `NEAREST`). `set_blockers` compares with `is`, so the texture is only rebuilt when the floor makes a new tuple: on a new floor, or when a door opens (`unlock_door` calls `refresh_light_blockers`). Crates don't cast shadows. For each light that's close enough to matter (`falloff > 0`), the shader checks whether it **reaches** the pixel:

  ```
  start  = the light's position          target = the pixel's position
           (inside a wall: the center of the open tile in front of it, trying below, right, left, then above)

  walk from start to target in SHADOW_STEP (4 px) steps:
      a step lands on a blocker tile  →  no light from this one
      no step does                    →  the light reaches the pixel
  (off the map counts as a blocker)
  ```

  Torches sit inside wall tiles, so their walk starts from the floor tile they face; wall pixels walk to the open tile in front of them, which keeps wall faces lit from their own room while the void behind stays dark. (Without moving the target, walks along the top wall ran through the wall itself and left dark wedges between torches.) 4-pixel steps can't jump over a 16-pixel tile.
- **The empty part of a wall tile never takes light.** Wall art doesn't fill its tile: a side wall's art is 7 of its 16 pixels wide, a bottom wall's about the top half, and the rest is `PALETTE_VOID`. Lit from the room, that void glowed as a strip beside the wall. So a pixel that is inside a blocker tile **and** exactly the void color (within half a color step, `0.5 / 255`, since the shader sees colors as 0–1 decimals) skips every light and keeps only the ambient. Only inside walls: floor tiles use the same color for their grid lines, which should be lit.
- **Cost.** The whole light shader takes about 0.03 ms a frame on the GPU (RTX 4070 SUPER, 7 lights with wall checks), so lighting is effectively free; the CPU-side frame costs are in [One frame](frame.md), "Performance".

**Letterboxing and the mouse** (`engine/graphics/display.py`). `letterbox(window_size)` fits the 1280×720 game into any window at the largest scale that fits, centered, with black bars on the sides that don't fill:

```
scale = min(window_width / 1280, window_height / 720)
left  = (window_width  − 1280 × scale) / 2
top   = (window_height −  720 × scale) / 2

window 1280×720  → scale 1.0, no bars           (the normal window)
window 1920×1080 → scale 1.5, no bars
window 1920×1200 → scale 1.5, top = (1200 − 1080) / 2 = 60 px bars above and below
```

OpenGL counts the viewport's y from the **bottom** of the window, but the bars are equal, so `top` works from either end. `get_mouse_pos()` reverses the same math, from window pixels back to game pixels: `((x − left) / scale, (y − top) / scale)`. Every place that reads the mouse uses it (buttons, sliders, the cursor, the inventory, and `read_input`'s click position), so the mouse lines up in fullscreen too. In a 1280×720 window it returns exactly what `pygame.mouse.get_pos()` does. It's named `get_mouse_pos`, not `mouse_pos`, because many functions have a local variable called `mouse_pos`, and `mouse_pos = mouse_pos()` would make Python treat the name as local for the whole function, so the call would fail with `UnboundLocalError`.

Inside that, the world is drawn at its true pixel size on a small canvas and scaled up by `GAME_SCALE` (3) on the GPU, so every art pixel becomes a crisp 3×3 block. The HUD is drawn on the UI layer at full resolution, so text stays sharp and the inventory's mouse positions stay in screen pixels:

```
1. the WORLD  →  drawn on a WORLD_WIDTH × WORLD_HEIGHT surface  →  submit_world  →  GPU scales × GAME_SCALE
2. the HUD    →  drawn on ui_surface at full resolution          →  UI layer, on top
```

## State flow

A *state* is any object with `update(dt)`, `draw(screen)` and `enter()`. `enter()` runs once each time the game switches to that state, and is where a state does its "on arrival" work, such as starting its music. A state with nothing to do on arrival still needs an `enter` whose body is `pass`, or the switch crashes with `AttributeError`. `GameStateManager` (`engine/core/state_manager.py`) holds:
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

- **MainMenu** (`game/states/menus/main_menu.py`): Start goes to the run, Options goes to the options menu, Exit posts a `pygame.QUIT` event so the main loop shuts down normally. `enter()` plays `MAIN_MENU_MUSIC` (`"menu_music"`).
- **Run** (`game/states/run.py`): the dungeon. ESC switches to options and plays the `pause` sound. When the player's health reaches 0, its `DeathSequence` plays `death`, stops the music, freezes for `DEATH_DELAY` (3.0) seconds, then switches to `"game_over"` ([One frame](frame.md), step 6). Climbing down the exit ladder (F) loads the next floor from `FLOOR_ORDER`, or switches to `"run_complete"` after the last one (step 7). `enter()` plays `LEVEL_MUSIC` (`"level_music"`). Unpausing calls it again, but the track keeps going instead of restarting (see `sound.py` in the [Engine reference](engine.md)).
- **Options** (`game/states/menus/options.py`): music and SFX sliders, and toggles for the FPS counter, fullscreen, screen shake and the hurt vignette. Main Menu returns to the main menu. When the menu was opened from the run, it first calls `start_new_run()` so the abandoned run is thrown away. Back (`can_go_back()`) only appears when the previous state is `"run"`, so it acts as "resume". ESC does the same as Back, but only when the menu was opened from the run. In that case the menu is drawn over the dimmed, frozen run instead of a solid background. Both buttons save the settings file. `enter()` does nothing, so the pause menu keeps playing whatever music was already on.
- **RunEndScreen** (`game/states/menus/run_end.py`): the screen shown when a run ends, either way. It is one class created twice in `main.py`'s `build_screens` with different settings, `RunEndScreen(game_state_manager, title, title_color, music)`: the differences between the two screens are constructor arguments, not separate classes. It draws the title, the run's split times (one row per floor, then the total) and two text buttons over the frozen run. Restart and Main Menu both call `start_new_run()` (from `game/states/new_run.py`) first, then switch to `"run"` or `"main_menu"`. `enter()` reads the finished run's `splits`, `run_time` and whether it died (`run.death.is_active()`) from `game_state_manager.states["run"]` and renders the split table. If `music` is a track name, `enter()` stops the current music and plays it once, with `loops=0`. That's how the death screen plays `"game_over"`, and why Restart then starts the run's music again from the beginning. If `music` is `None`, as on the finish screen, the current track keeps playing.

All states are built once at startup and kept alive, so leaving and returning to the run normally resumes it where you left off. The exceptions are a death, and quitting to the main menu from the pause menu. `start_new_run(game_state_manager)` in `game/states/new_run.py` builds a brand new `Run(game_state_manager)`, which starts on the first floor, and registers it under `"run"` with `add_state`, which replaces the old one in the `states` dict. A rebuild resets everything the Run owns (player, enemies, chests, doors, ground items, the inventory screen) and recenters the camera, while the shared image, animation and mask caches are reused. Because the Run can be replaced, code that needs it should look it up through `game_state_manager.states["run"]` when it needs it, not keep a reference from startup.
