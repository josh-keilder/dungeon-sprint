# Design rules

These are the rules the project was built around. New code should follow them.

**The engine and the game.** The code is split in two, side by side, with `main.py` at the root:

```
engine/   how things work: timers, animation, movement, cameras, the renderer, particles, sound,
          input, widgets, health, inventories. Nothing in it knows it's Dungeon Sprint.
game/     what this game is: enemy types, the roll, combat, loot tables, the HUD, the floors.
main.py   Dungeon Sprint's setup: the theme, the window, the screens, then the engine's game loop.
```

- **`engine/` never imports the game.** No `game.*`, no `main`, no `tools`. When the engine needs something game-specific (the screen size, the light colors, the key bindings, the settings defaults, the particle presets, the UI colors and font), the game passes it in: as arguments (`Renderer(screen_size=..., lighting=...)`, `load_settings(DEFAULT_SETTINGS, SETTINGS_FILE_PATH)`), as data (`visible_lights(lights, LIGHT_TYPES, camera, time)`), or once at startup (`set_theme(...)`). `tools/check_engine_imports.py` enforces this before every commit ([Tooling](tooling.md)).
- **Engine = how things work. Game = what this game is.** A timer, an animation, a camera, a particle burst, a button: engine. What a Skeleton does, how the roll hurts, what a chest drops, where the HUD panels sit: game.
- The engine is a folder in this repo for now; it becomes its own package or repo when a second game starts ([How to](how-to.md), "Reusing the engine").

**Folders by topic.** The engine has `core/` (timers, settings, assets, the state manager, the game loop), `graphics/`, `physics/`, `io/` (input and sound), `ui/` (widgets and the theme) and `gameplay/` (health, stats, inventory, items, loot). The game has `data/` (every table: constants, palette, enemy types, items, loot, particles, lights, texture layouts), `rules/` (combat, the roll, the sword swing, interaction, enemy behaviours), `entities/`, `world/`, `ui/` and `states/`. No folder holds a single file.

**Behaviour lives in modules of functions.** Shared behaviour is plain functions that take the data they work on as arguments and either change it in place or return a new value: `take_damage(health, amount)` changes a health dict, `steer(...)` returns a new velocity. Small classes are used only where something holds state between frames: entities, screens, widgets, the renderer, `Feedback`, `DeathSequence`.

**State is plain data.** An entity's state is stored as simple dicts on the object, and the functions operate on those dicts:

| Dict | Created by | Used by |
| --- | --- | --- |
| `health` | `engine.gameplay.health.new_health` | `health`, `combat`, `consumables`, `health_bar` |
| `roll` | inline in `Player.__init__` (holds `direction` and two timers from `new_timer`) | `game.rules.roll`, `combat`, `Player` |
| `swing` | `game.rules.swing.new_swing` (Enemy) | `swing`, `combat`, `Enemy` |
| `invulnerability`, `stagger` | `engine.core.timer.new_timer` (Player and Enemy) | `timer`, `combat`, the `draw` methods |
| `heal_cooldown` | `engine.core.timer.new_timer` (Player) | `timer`, `consumables` |
| `animation` | `engine.graphics.animation.new_animation` | `animation` |
| `inventory` | `engine.gameplay.inventory.new_inventory` | `inventory`, `interact`, `consumables`, `inventory_ui` |
| `stats` | `engine.gameplay.stats.compute_stats` | `Player` movement and roll |
| `intent` | `game.rules.input.read_input` | `Player` and `Run` |
| `shake` | `engine.graphics.shake.new_shake` (in `Feedback`) | `shake`, `Run.update_camera` |
| `events` | a new list in `Run.update_world` each frame | `Player.update`, `Floor.update`, `combat`, `Feedback.handle` |

A timer remembers the duration it was started with, so `fraction_left(timer)` and `time_elapsed(timer)` need no extra arguments.

**Rules are separate from application.** Rules decide *what happens* (how fast you accelerate, whether a roll can start, what a chest drops). Entities and states decide *when* to apply them (the player calls `try_start_roll` when the roll intent is set). Entities keep their `update` methods as the **order** things happen each frame; the math inside moves to functions. Content such as the player's and enemies' values, loot tables and texture layouts lives in `game/data/`, separate from the logic that reads it.

**Logic records what happened; feedback is separate.** Game logic never plays a sound, bursts a particle or shakes the camera. It adds an event (`{"name": "roll_hit", "enemy": enemy}`) to the frame's `events` list, and `Feedback.handle` decides how each one looks and sounds ([One frame](frame.md), step 5). Screen changes (the pause sound, the death sequence) are the exception: they belong to the screen, not to a frame of play.

**One position per thing.** An entity's position is its `rect`, read directly (`rect.topleft`, `rect.center`) wherever it's needed. There's no second copy to keep in sync, so nothing can read a position that's a frame old.

**Code style.**
- Names are explicit and not abbreviated (`move_direction`, `game_state_manager`, `equipment_slot_x`). Short names are fine only for things like `pos`, `dt`, `x` and `y`.
- File and folder names are snake_case. Classes are PascalCase. Constants are UPPER_SNAKE_CASE.
- No type hints and no docstrings. Comments are fine when they are accurate, and section comments are plain `# Like this`.
- Module-private **caches and state** start with an underscore (`_IMAGE_CACHE`, `_MASK_CACHE`, `_theme`, `_world`), meaning "don't touch this from outside". Functions and methods never do.
- **Layout standard** (every file follows it):

  ```
  imports (isort groups)

  # Group label                     ← one comment line per group of constants
  CONSTANT = value  # unit or meaning, when it isn't obvious
  CONSTANT = value
                                    ← one blank line between groups, two after the last
  module helpers                    (only those used by this file)

  class:
      __init__: attributes in labelled groups (# Movement, # Health, ...)
      lifecycle first: run, enter, update, draw
      then the methods other files call
      then the private helpers, top-down, in the order they're called
  ```

  Function modules put their public functions first, in the order a caller uses them, then the helpers those call. The tools are the exception: helpers first, `main()` last, as Python scripts usually are. Long modules split their functions with section comments (`ascii_to_tmx.py`: reading, solvability, tile layers, decor, objects, writing, grid helpers, entry point). Magic numbers become named constants with their unit (`CURSOR_OFFSET`, the slider's `KNOB_WIDTH`, `HIT_SHAKE_STRENGTH`), so every value has a name and lives in one place.
- A default argument is evaluated once, when Python first reads the `def`, so a default that comes from the theme or a setting is written as `None` and looked up in the body (`if color is None: color = get_theme("text_color")`). Otherwise it would be frozen at import time, before `main.py` sets the theme.
- Imports are named (never `import *`), unused imports are removed, and they are grouped as standard library, then third-party, then project, alphabetical within each group.
- Formatting is done by Black with its default 88-character line length, comments included (Black doesn't wrap comments, so long ones are wrapped by hand). The pre-commit hook runs isort and Black on every staged file.
