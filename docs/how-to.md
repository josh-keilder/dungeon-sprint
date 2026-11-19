# How to add things

**A new enemy type.**
1. Add its sheet layout to `entities/enemies/enemy_texture_data.py`.
2. Add an entry to `ENEMY_TYPES` with a key like `"Bat"`, its stats, a `behavior` (`"fly"` or `"wander_chase"`), its texture data, its starting animation name, and its `knockback_multiplier`, `knockback_decay_rate`, `blink_interval` (or `None`), `invulnerability_duration`, `loot_table` (a table in `loot_table_data.py`; use `[]` for no drops), `body`, `touch_damage`, `animation_prefix` (or `None`) and `attack` (or `None`); [Data formats](data-formats.md) explains each. Every key is required: a missing one crashes at floor load with a `KeyError` naming it.
3. In Tiled, place objects named `Enemy_Bat` in `Entity_Spawns`.
4. For a new behaviour, write a `<behavior>_velocity` function in `systems/enemy_ai.py` and add a branch for it in `Enemy.update_movement`.

**A new floor.**
1. Sketch it in `Assets/Maps/Source/<name>.txt` with the converter's legend ([Tooling](tooling.md)): walls at least 2 thick, doors 2 tiles in a corridor through a wall, one key of the matching color per door group (`s` for an `S` door on the main path, `g` for a `G` treasure door), one `@`, one `X`, and crates (`B`) anywhere they should block the way or hide a little loot.
2. Convert it: `.venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/<name>.txt`, which writes `Assets/Maps/<name>.tmx`. Fix any `ValueError` it reports. If it says the exit can't be reached, check that every door's key can be reached before that door.
3. Preview it: `.venv/Scripts/python -m tools.preview_map Assets/Maps/<name>.tmx`, then check `map_previews/<name>.png`.
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
