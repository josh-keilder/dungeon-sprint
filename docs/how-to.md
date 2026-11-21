# How to add things

**A new enemy type.**
1. Add its sheet layout to `game/data/textures/enemy_texture_data.py`.
2. Add an entry to `ENEMY_TYPES` (`game/data/enemy_type_data.py`) with a key like `"Bat"`, its stats, a `behavior` (`"fly"` or `"wander_chase"`), its texture data, its starting animation name, and its `knockback_multiplier`, `knockback_decay_rate`, `blink_interval` (or `None`), `invulnerability_duration`, `loot_table` (a table in `loot_table_data.py`; use `[]` for no drops), `body`, `touch_damage`, `animation_prefix` (or `None`) and `attack` (or `None`); [Data formats](data-formats.md) explains each. Every key is required: a missing one crashes at floor load with a `KeyError` naming it.
3. In Tiled, place objects named `Enemy_Bat` in `Entity_Spawns`.
4. For a new behaviour, write a `<behavior>_velocity` function in `game/rules/enemy_ai.py` and add a branch for it in `Enemy.update_movement`.

**A new floor.**
1. Sketch it in `Assets/Maps/Source/<name>.txt` with the converter's legend ([Tooling](tooling.md)): walls at least 2 thick, doors 2 tiles in a corridor through a wall, one key of the matching color per door group (`s` for an `S` door on the main path, `g` for a `G` treasure door), one `@`, one `X`, and crates (`B`) anywhere they should block the way or hide a little loot.
2. Convert it: `.venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/<name>.txt`, which writes `Assets/Maps/<name>.tmx`. Fix any `ValueError` it reports. If it says the exit can't be reached, check that every door's key can be reached before that door.
3. Preview it: `.venv/Scripts/python -m tools.preview_map Assets/Maps/<name>.tmx`, then check `map_previews/<name>.png`.
4. Add its path to `FLOOR_ORDER` in `game/data/constants.py`, where the order is the play order.
5. Optionally polish it in Tiled, but reconverting overwrites hand edits, so make changes in the text source where possible.

**A new item.**
1. Draw its art as a new entry in `SPRITES` in `tools/make_sprite.py` (16×16, saved to `Assets/Items/`) and run the tool, then add its sheet layout to `game/data/textures/item_texture_data.py` pointing at that PNG.
2. In `initialize_item_database` (`game/data/item_database.py`), load its animations and add an `Item` (or `EquipmentItem` with `slot` and `bonuses`) under a new id.
3. To make it drop, add an entry to `CHEST_LOOT` (`game/data/loot_table_data.py`).
4. If it does something when used, add a function to `game/rules/consumables.py` and call it from the player on a new intent.

**New equipment.** Use `EquipmentItem` with `slot` set to one of `head`, `chest`, `boots` or `ability`. Its `bonuses` keys must match names in `base_stats`. For a new slot, add the name to `equipment_slot_names` in `PLAYER_DATA` (`game/data/player_data.py`). The inventory screen draws one equipment slot per name and resizes its window to fit.

**A new key binding.** Add an `action: key` entry to `ACTION_KEYS` in `game/rules/input.py` (the intent dict gets the field automatically), then react to it in `Run.handle_actions` (run-wide actions) or `Player.update` (player actions).

**A new state or menu.**
1. Create a class with `enter()`, `update(dt)` and `draw(screen)` that takes `game_state_manager`. Put its music in `enter()`, or use `pass` to keep whatever is playing.
2. Build it in `build_screens()` in `main.py` and register it with `add_state("name", state)`.
3. Switch to it from another state with `set_state("name")`.
4. For a menu, follow the existing ones: fill the screen with `MENU_BACKGROUND_COLOR`, build the title with `make_title`, create the button font once in `__init__` from `FONT_PATH` at `BUTTON_FONT_SIZE`, and use `TextButton`s. Leave out colors the theme already sets.

**A new sound or music track.** Drop a `.wav` or `.ogg` into `Assets/Sounds` or `Assets/Music` and play it by filename: `sound.play_sfx("name")` or `sound.play_music("name")`. To give a screen its own track, call `play_music` in that state's `enter()`.

**A new setting.** Add its key and default to `DEFAULT_SETTINGS` in `game/data/constants.py`, read it with `settings.get_setting("key")`, and add a toggle or slider to Options. Saved files that don't have it yet get the default.

**A new sound or effect for something that happens.** Add an `events.append({"name": "...", ...})` where it happens, with whatever the effect needs (an enemy, a position), and a branch for that name in `Feedback.handle` (`game/ui/feedback.py`) that plays the sound or bursts the particles. The logic stays free of sound and particle code.

**Player stats or values.** Edit `PLAYER_DATA` in `game/data/player_data.py`; nothing in `Player` needs to change.

**A new engine module.** Put it in the `engine/` folder for its topic, and give it no imports from `game`, `main` or `tools`: anything game-specific comes in as an argument, as data, or through the theme. The pre-commit hook rejects the commit otherwise.

## Reusing the engine

`engine/` is written to be lifted into another pygame game. It's a folder in this repo for now; when a second game starts, it becomes its own package or repo, and the generic tools (the line counter, the import check, the strip joiner) go with it, generalized to take the new game's data.

**What a new game provides.** Everything the engine reads from the game is passed in, so a new game writes its own versions of what `main.py` and `game/data/` hold:

| The engine needs | Dungeon Sprint passes | Where |
| --- | --- | --- |
| settings defaults and file | `DEFAULT_SETTINGS`, `SETTINGS_FILE_PATH` | `load_settings(defaults, file_path)` |
| window size and title | `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `WINDOW_TITLE` | `create_window(screen_size, fullscreen, title)` |
| the look of every widget | font, colors, pixel scale, button sounds | `set_theme(...)`, before any widget is built |
| render sizes and the light look | world and tile size, `GAME_SCALE`, ambient, bands, void color | `Renderer(...)` |
| light types | `LIGHT_TYPES` | `visible_lights(lights, light_types, camera, time)`, `flame_position(light_type, ...)` |
| sound folders | `SFX_FOLDER`, `MUSIC_FOLDER` | `load_sfx(folder)`, `load_music(folder)` |
| key bindings | `MOVE_KEYS`, `ACTION_KEYS` | `move_direction`, `pressed_actions` |
| particle looks | `CRATE_DEBRIS` and the rest | `emit_burst(particles, center, preset)` |
| equipment slot names | `PLAYER_DATA["equipment_slot_names"]` | `new_inventory(slot_count, equipment_slot_names)` |
| its screens | `MainMenu`, `Run`, ... | `GameStateManager`, then `GameLoop(...).run()` |

**The smallest game.** A screen is any object with `enter()`, `update(dt)` and `draw(screen)`; the engine supplies the window, the loop, the renderer and the widgets:

```python
import pygame

from engine.core.game_loop import GameLoop
from engine.core.state_manager import GameStateManager
from engine.graphics.display import create_window
from engine.graphics.renderer import Renderer
from engine.ui.text_label import TextLabel
from engine.ui.theme import set_theme


class Hello:
    def __init__(self):
        self.label = TextLabel("Hello", pos=(40, 40))

    def enter(self):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        self.label.draw(screen)


pygame.init()
set_theme(font_size=32)  # everything else keeps the plain defaults
create_window((640, 360), False, "Hello")
renderer = Renderer(
    screen_size=(640, 360),
    world_size=(320, 180),
    world_scale=2,
    tile_size=16,
    lighting={
        "ambient": (1, 1, 1),
        "max_light": 1.0,
        "bands": 0,
        "void_color": (0, 0, 0),
    },
)
screens = GameStateManager("hello")
screens.add_state("hello", Hello())
GameLoop(renderer, (640, 360), screens, frame_rate=60).run()
pygame.quit()
```

Nothing calls `submit_world` here, so the renderer only shows the UI layer. A game with a world draws it on a surface each frame and hands it over with `submit_world(surface, camera.topleft, lights, blockers)`, as `Run.draw` does.

**Keeping it reusable.** The rule that protects all of this is the one the hook enforces: nothing under `engine/` imports the game. When a change needs a game value in the engine, pass it in instead, the same way as the rows above.
